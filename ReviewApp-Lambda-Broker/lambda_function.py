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
import time

# configure logger
log_level = os.environ['LOG_LEVEL']
logger = logging.getLogger()
if log_level == "info":
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.ERROR)

# configure secrets manager client
secret = boto3.client('secretsmanager')

# configure SNS client
TOPIC_ARN = os.environ['TOPIC_ARN']
sns_resource = boto3.resource('sns')
topic = sns_resource.Topic(TOPIC_ARN)

# configure DynamoDB client
dynamodb = boto3.client('dynamodb')
table_name = os.environ['REVIEW_APP_TABLE']

# configure epoch time
epoch_time = str(round(time.time()))
logger.info('got epoch time ' + epoch_time)

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
    if name is None:
        raise ValueError
    try:
        kwargs = {'SecretId': name}
        if stage is not None:
            kwargs['VersionStage'] = stage
        response = secret.get_secret_value(**kwargs)
        secret_value = response['SecretString']
    except ClientError:
        logger.exception("Couldn't get value for secret %s.", name)
        raise
    else:
        return secret_value

def verify_signature(headers, body):
    try:
        secret = get_secret_value('reviewapp_github_secret').encode("utf-8")
        received = headers["X-Hub-Signature-256"].split("sha256=")[-1].strip()
        expected = HMAC(secret, body.encode("utf-8"), sha256).hexdigest()
    except (KeyError, TypeError):
        logger.exception("Couldn't verify github signature")
        return False
    else:
        return compare_digest(received, expected)

def comment_on_pr(PR_NUMBER, comment, repo_name):
    github_access_token = get_secret_value('reviewapp_github_token')
    g = Github(github_access_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(PR_NUMBER)
    pr.create_issue_comment(comment)
 
def add_github_payload_to_dynamo(table_name, attributes):
    dynamodb.put_item(
    TableName = table_name, Item = {
      'payload_uuid':{'S' : attributes['uid']},
      'github_payload':{'S' : "testing..."},
      'pr_num':{'N' : attributes["pr_number"]},
      'commit_utc_sha':{'S' : attributes['commit_utc_sha']}
      })

def lambda_handler(event, context):
    logger.info('inside lambda execution...')

    #logger.info('Event: %s' % json.dumps(event))

    if verify_signature(event["headers"], event["body"]):
        logger.info('verified signature success')
    else: 
        logger.exception('signature failed')
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text'},
            'body': 'this request is not coming from github',
        }

    body = event.get('body', "")
    github_event = event.get('multiValueHeaders').get('X-GitHub-Event')

    # get UID from github payload
    uid = event.get('multiValueHeaders').get('X-GitHub-Delivery')
    uid = str(uid[0])

    github_event = str(github_event[0])
    logger.info('the github event is: ' + github_event)
    body = urllib.parse.unquote_plus(body)

    # get rid of 'payload='
    body = body[8:]

    logger.info("the body is: " + body)

    # convert to json object
    body = json.loads(body)

    action = body.get('action')
    logger.info("the action is: " + action)
    
    if github_event == "pull_request":
        pull_request_num = body.get('number')
        pull_request_title = body.get('pull_request').get('title')
        pull_request_creator = body.get('pull_request').get('user').get('login')
        pull_request_branch = body.get('pull_request').get('head').get('ref')
        pull_request_commit = body.get('pull_request').get('head').get('sha')
        pull_request_repo = body.get('repository').get('full_name')        
        logger.info('the pull request number is: ' + str(pull_request_num))
        logger.info('the pull request title is: ' + pull_request_title)
        logger.info('the pull request creator is: ' + pull_request_creator)
        logger.info('the pull request branch is: ' + pull_request_branch)        
        logger.info('the pull request commit is: ' + pull_request_commit)
        logger.info('the pull request repo is: ' + pull_request_repo)    

        commit_utc_sha = epoch_time + '_' + pull_request_commit

        attributes = {'commit_utc_sha': commit_utc_sha, \
            'uid': uid, \
            'pr_number': str(pull_request_num), \
            'commit_sha': pull_request_commit, \
            'creator': pull_request_creator, \
            'pull_request_branch': pull_request_branch,   \
            'pull_request_title': pull_request_title}

        logger.info('adding github payload to dynamo...')
        add_github_payload_to_dynamo(table_name, attributes)

    if (github_event == "pull_request") and (action == "opened" or action == "reopened"):
        logger.info('Posted to github PR based on Git PR open event...')
        comment_on_pr(pull_request_num, "[ReviewApp] Pull Request Opened!", pull_request_repo)

        # SNS publish
        message = 'github-reviewapp-actions'
        attributes["action"] = "open"
        publish_message(topic, message, attributes)

    if (github_event == "pull_request") and (action == "synchronize"):
        logger.info('Posted to github PR based on Git PR synchronize event...')
        comment = "[ReviewApp] Pull Request Updated!  Commit -> " + pull_request_commit
        comment_on_pr(pull_request_num, comment, pull_request_repo)

        # SNS publish
        message = 'github-reviewapp-actions'
        attributes["action"] = "updated"
        publish_message(topic, message, attributes)        

    if (github_event == "pull_request") and (action == "closed"):
        logger.info('Posted to github PR based on Git PR closed event...')
        comment_on_pr(pull_request_num, "[ReviewApp] Pull Request Closed!", pull_request_repo)

        # SNS publish
        message = 'github-reviewapp-actions'
        attributes["action"] = "closed"
        publish_message(topic, message, attributes)   

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(attributes),
    }