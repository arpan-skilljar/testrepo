import os
import boto3
import botocore
import json
import urllib.parse
from hashlib import sha256
from hmac import HMAC, compare_digest
from github import Github
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def publish_message(topic, message, attributes):
    try:
        att_dict = {}
        for key, value in attributes.items():
            if isinstance(value, str):
                att_dict[key] = {'DataType': 'String', 'StringValue': value}
            elif isinstance(value, bytes):
                att_dict[key] = {'DataType': 'Binary', 'BinaryValue': value}
        response = topic.publish(Message=message, MessageAttributes=att_dict)
        message_id = response['MessageId']
        logger.info(
            "Published message with attributes %s to topic %s.", attributes,
            topic.arn)
    except ClientError:
        logger.exception("Couldn't publish message to topic %s.", topic.arn)
        raise
    else:
        return message_id

def get_secret_value(name, stage=None):
    secret = boto3.client('secretsmanager')

    if name is None:
        raise ValueError

    try:
        kwargs = {'SecretId': name}
        if stage is not None:
            kwargs['VersionStage'] = stage
        response = secret.get_secret_value(**kwargs)
        print('the response from secrets is ', response)
        secret_value = response['SecretString']
    except ClientError:
        print("Couldn't get value for secret %s.", name)
        raise
    else:
        return secret_value

def verify_signature(headers, body):
    try:
        secret = get_secret_value('reviewapp_github_secret').encode("utf-8")
        received = headers["X-Hub-Signature-256"].split("sha256=")[-1].strip()
        expected = HMAC(secret, body.encode("utf-8"), sha256).hexdigest()
    except (KeyError, TypeError):
        return False
    else:
        return compare_digest(received, expected)

def comment_on_pr(PR_NUMBER, comment):
    github_access_token = get_secret_value('reviewapp_github_token')
    g = Github(github_access_token)
    #for repo in g.get_user().get_repos():
    #    print(repo.name)
    repo_name = 'arpan-skilljar/testrepo'
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(PR_NUMBER)
    pr.create_issue_comment(comment)

def lambda_handler(event, context):
    print('inside lambda execution...')
    if verify_signature(event["headers"], event["body"]):
        print('verified signature success')
    else: 
        print('signature failed')
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text'},
            'body': 'this request is not coming from github',
        }

    body = event.get('body', "")
    github_event = event.get('multiValueHeaders').get('X-GitHub-Event')
    github_event = str(github_event[0])
    print('the github event is: ' + github_event)
    body = urllib.parse.unquote_plus(body)

    # get rid of 'payload='
    body = body[8:]

    print("the body is: " + body)

    # convert to json object
    body = json.loads(body)

    action = body.get('action')
    print("the action is: " + action)

    # setup SNS
    TOPIC_ARN = 'arn:aws:sns:us-west-2:420762066547:githubLambdaBroker'
    sns_resource = boto3.resource('sns')
    topic = sns_resource.Topic(TOPIC_ARN)
    
    if github_event == "pull_request":
        pull_request_num = body.get('number')
        pull_request_title = body.get('pull_request').get('title')
        pull_request_creator = body.get('pull_request').get('user').get('login')
        pull_request_commit = body.get('pull_request').get('head').get('sha')
        print("the pull request number is: " + str(pull_request_num))
        print('the pull request title is: ' + pull_request_title)
        print('the pull request creator is: ' + pull_request_creator)
        print('the pull request commit is: ' + pull_request_commit)


    # what about action == reopened when PR is reopened

    if (github_event == "pull_request") and (action == "opened" or action == "reopened"):
        print('Posted to github PR based on Git PR open event...')
        comment_on_pr(pull_request_num, "[ReviewApp] Pull Request Opened!")

        # SNS publish
        message = 'github-reviewapp-actions'
        attributes = {'action': 'open', 'pr_number': str(pull_request_num), \
            'commit_sha': pull_request_commit, \
            'creator': pull_request_creator}
        publish_message(topic, message, attributes)

    if (github_event == "pull_request") and (action == "synchronize"):
        print('Posted to github PR based on Git PR synchronize event...')
        comment = "[ReviewApp] Pull Request Updated!  Commit -> " + pull_request_commit
        comment_on_pr(pull_request_num, comment)

        # SNS publish
        message = 'github-reviewapp-actions'
        attributes = {'action': 'updated', 'pr_number': str(pull_request_num), \
            'commit_sha': pull_request_commit, \
            'creator': pull_request_creator}
        publish_message(topic, message, attributes)        

    if (github_event == "pull_request") and (action == "closed"):
        print('Posted to github PR based on Git PR closed event...')
        comment_on_pr(pull_request_num, "[ReviewApp] Pull Request Closed!")

        # SNS publish
        message = 'github-reviewapp-actions'
        attributes = {'action': 'closed', 'pr_number': str(pull_request_num), \
            'commit_sha': pull_request_commit, \
            'creator': pull_request_creator}
        publish_message(topic, message, attributes)   

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(event),
    }