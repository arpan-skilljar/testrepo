from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    BundlingOptions
)
from constructs import Construct

class ReviewappsGithubWebhookBrokerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function
        appFunction = lambda_.Function(self, "AppFunction",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("lambda",
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_8.bundling_image,
                    command=[
                        'bash', '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -ar . /asset-output'
                    ]
                )
            ),
            handler="lambda_function.lambda_handler"
        )
        '''
        # Existing VPC and and private subnets
        vpc_name = "sandbox"
        vpc = ec2.Vpc.from_lookup(self, "VPC",
            tags={"Name": vpc_name}
        )
        vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)

        # Security group
        security_group = ec2.SecurityGroup(self, "SG",
            vpc=vpc
        )
        security_group.add_ingress_rule(ec2.Peer.ipv4("10.0.0.0/8"), ec2.Port.tcp(80))

        # Internal ALB
        alb = elbv2.ApplicationLoadBalancer(self, "ALB",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_group=security_group
        )
        http_listener = alb.add_listener("HTTPListener", port=80, open=False)
        http_listener.add_targets("TG",
            targets=[targets.LambdaTarget(appFunction)]
        )
        '''

