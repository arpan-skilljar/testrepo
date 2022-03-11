```ReviewApp
sequenceDiagram
    participant Github
    participant AWS-Lambdas
    participant ReviewApp-Portal
    Github->>AWS-Lambdas: loads html w/ AWS-Lambdas url
    AWS-Lambdas->>ReviewApp-Portal: request template
    ReviewApp-Portal->>AWS-Lambdas: html & javascript
    AWS-Lambdas->>Github: AWS-Lambdas ready
    Github->>AWS-Lambdas: set mermaid data on AWS-Lambdas
    AWS-Lambdas->>AWS-Lambdas: render mermaid
```