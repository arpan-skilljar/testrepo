import json

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    print('the message is: ' + message)
    #bucket = message['Records'][0]['s3']['bucket']['name']
    #key = message['Records'][0]['s3']['object']['key']