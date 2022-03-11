```mermaid
sequenceDiagram
    participant github
    participant iframe
    participant viewscreen
    github->>iframe: loads html w/ iframe url
    iframe->>viewscreen: request template
    viewscreen->>iframe: html & javascript
    iframe->>github: iframe ready
    github->>iframe: set mermaid data on iframe
    iframe->>iframe: render mermaid
```