
# Reviewapps Github Webhook Broker 

The PyGithub dependency does not work when using bundling options.  The 
lambda will be deployed by building the deployment package zip prior to 
running cdk deploy.

# Building Lambda Deployment Package
```
# run a ubuntu container with a bind mount to lambda dir
docker run -v "$(pwd)"/lambda:/lambda -it --rm ubuntu  

# install python3, pip, git
apt-get update && apt-get install -y -qq python3-pip git \
&& cd /usr/local/bin && ln -s /usr/bin/python3 python \
&& python3 -m pip install --upgrade pip \
&& python3 -m pip install ipython \
&& rm -rf /var/lib/apt/lists/*

# install all dependencies required by the lambda
cd /lambda
pip install -t . -r requirements.txt

# exit the container 
exit 

# zip up the directory as a lambda depoloyment package
cd lambda
zip -r9 my-deployment-package.zip .

 aws lambda update-function-code --function-name githubWebHook --zip-file fileb://my-deployment-package.zip  

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
