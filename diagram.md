```mermaid
sequenceDiagram
    participant github
    participant aws
    participant portal
    github->>aws: PR events webhook triggers lambda
    aws->>aws: lambda stores event details in dynamo    
    aws->>github: lambda comments on PR with portal link
    portal->>aws: user CRUDs reviewapp from portal
    aws->>aws: lambda updates reviewapps using cloudformation
    aws->>aws: spin up/down ECS fargate service respective to reviewapp
    aws->>aws: lambda updates reviewapp state in dynamo
    aws->>github: lambda comments on PR when reviewapp state changes
```