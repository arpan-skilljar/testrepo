from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as api_gw,
    BundlingOptions
)

from constructs import Construct

class FlaskLambdaStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        reviewapps_flask_api = _lambda.Function(self, "ReviewAppsPortalFlask2",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambdas",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_8.bundling_image,
                    command=[
                        'bash', '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
                    ]
                )
            ),
            handler="lambdalith.handler"
        )

        api_gw.LambdaRestApi(self, 'ReviewAppsPortalFlaskAPI',
                             handler=reviewapps_flask_api
                             )