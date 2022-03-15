#!/usr/bin/env python3

import os
import aws_cdk as cdk

from reviewapps_github_webhook_broker.reviewapps_github_webhook_broker_stack import ReviewappsGithubWebhookBrokerStack

# Environment
account = "420762066547"
region = "us-west-2"
env=cdk.Environment(account=account, region=region)

app = cdk.App()
ReviewappsGithubWebhookBrokerStack(app, "reviewapps-github-webhook-broker",
    env=env)

app.synth()