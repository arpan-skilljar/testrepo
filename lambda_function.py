import json
import urllib.parse

def lambda_handler(event, context):
    print('inside lambda execution...')
    print("Received event: " + json.dumps(event, indent=2))

    body = event.get('body', "")
    body = urllib.parse.unquote_plus(body)
    print('body of request is..')
    print(body)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(event),
    }