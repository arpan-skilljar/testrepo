```mermaid
sequenceDiagram
    participant github
    participant aws-lambda
    participant viewscreen
    github->>aws-lambda: loads html w/ iframe url
    aws-lambda->>viewscreen: request template
    viewscreen->>aws-lambda: html & javascript
    aws-lambda->>github: iframe ready
    github->>aws-lambda: set mermaid data on iframe
    aws-lambda->>aws-lambda: render mermaid
```