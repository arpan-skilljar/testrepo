import os
import boto3
import botocore
import json
import urllib.parse
from hashlib import sha256
from hmac import HMAC, compare_digest

def verify_signature(headers, body):
    try:
        secret = os.environ.get("GITHUB_SECRET").encode("utf-8")
        received = headers["X-Hub-Signature-256"].split("sha256=")[-1].strip()
        expected = HMAC(secret, body.encode("utf-8"), sha256).hexdigest()
    except (KeyError, TypeError):
        return False
    else:
        return compare_digest(received, expected)

def lambda_handler(event, context):
    print('inside lambda execution...')
    if verify_signature(event["headers"], event["body"]):
        print('verified signature success')
    else: 
        print('signature failed')
    #print("Received event: " + json.dumps(event, indent=2))

    body = event.get('body', "")
    github_event = event.get('multiValueHeaders').get('X-GitHub-Event')
    github_event = str(github_event[0])
    print('the github event is: ' + github_event)
    body = urllib.parse.unquote_plus(body)
    
    #print('body of request is..')
    #print(body)
    body = body[8:]
    #print("body after substring: " + body)
    body_json = json.loads(body)
    
    action = body_json.get('action')
    print("the action is: " + action)
    
    if github_event == "pull_request":

        pull_request_num = str(body_json.get('number'))
        pull_request_title = body_json.get('pull_request').get('title')
        
        print("the pull request number is: " + pull_request_num)
        print('the pull request title is: ' + pull_request_title)
        
    elif github_event == "issue_comment":
        
        pull_request_num = str(body_json.get('issue').get('number'))
        issue_comment = body_json.get('comment').get('body')
        print("the pull request number is: " + pull_request_num)
        print('the comment on the pull request is: ' + issue_comment)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(event),
    }
    #elif route == "/":
    #    print('inside /webhook')
    #    print(json.dumps(event))
    #    # TODO Write webhook receiver code
    #    pass