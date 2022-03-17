from aws_cdk import (
    Stack,
    aws_iam,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    BundlingOptions
)
from constructs import Construct

class ReviewappsGithubWebhookBrokerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # github webhook broker Lambda function

        github_broker_lambda = lambda_.Function(self, "githubBrokerLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("lambda",
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_8.bundling_image,
                    command=[
                        'bash', '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
                    ]
                )
            ),
            handler="lambda_function.lambda_handler",
            architecture=lambda_.Architecture.ARM_64,
            environment={ "LOG_LEVEL": "info", "REVIEW_APP_PAYLOAD_TABLE": "reviewapps-github-payload",
            "REVIEW_APP_TABLE": "reviewapps", "TOPIC_ARN": "arn:aws:sns:us-west-2:420762066547:githubLambdaBroker"}
        )

        # adding managed IAM policies to lambda exec role, will tighten these later w/custom policies

        github_broker_lambda.role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"))

        github_broker_lambda.role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"))

        github_broker_lambda.role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSNSFullAccess"))

        # API Gateway

        api = apigw.LambdaRestApi(self, "githubBrokerAPI",
            handler=github_broker_lambda
        )