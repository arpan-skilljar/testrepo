```mermaid
sequenceDiagram
    participant github
    participant aws
    participant portal
    github->>aws: pull request events trigger lambda
    aws->>github: comment on PR with portal link
    portal->>aws: user CRUDs reviewapp from portal
    portal->>aws: html & javascript
    aws->>github: iframe ready
    github->>aws: set mermaid data on iframe
    aws->>aws: render mermaid
```