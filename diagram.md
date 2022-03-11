```mermaid
sequenceDiagram
    participant github
    participant aws
    participant viewscreen
    github->>aws: pull request events trigger lambda
    aws->>aws: lambda stores event details in dynamo
    viewscreen->>aws: html & javascript
    aws->>github: iframe ready
    github->>aws: set mermaid data on iframe
    aws->>aws: render mermaid
```