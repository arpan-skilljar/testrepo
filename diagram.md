```mermaid
sequenceDiagram
    participant github
    participant aws
    participant portal
    github->>aws: PR events webhook triggers lambda
    aws->>aws: lambda stores event details in dynamo    
    aws->>github: lambda comments on PR with portal link
    portal->>aws: user CRUDs reviewapp from portal
    aws->>aws: lambda updates reviewapps using cloudformation (ECS Fargate Services)
    aws->>aws: lambda updates reviewapp state details in dynamo    
    aws->>github: lambda comments on PR when reviewapp state changes
```