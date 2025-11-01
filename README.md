# Development Assistant

Self-hosted LLM software development assistant by [Nathan Wick](https://nathanwick.com).

TODO

### Table of Contents

TODO

## Features

### 1. Code Reviewer

TODO

### 2. IDE Advanced Autocomplete

TODO

### 3. Chat Bot

TODO

## Getting Started

### Prerequisites

- Server with Git and Docker installed
- GitHub or GitLab account with admin access to repositories

### Clone

Clone the repository:

```bash
git clone https://github.com/nathan-wick/development-assistant.git
```

### Configure

#### Configure GitHub

If you're using Git**Lab** instead, skip to the [Configure GitLab section](#configure-gitlab).

##### Create Webhook

1. Go to your repository → Settings → Webhooks → Add webhook
2. Payload URL: http://your-server:8080/webhook
3. Content type: application/json
4. Secret: Use the same secret from values.yaml
5. Events: Select "Pull requests"

##### Create Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens
2. Generate new token with `repo` scope
3. Copy token to values.yaml

#### Configure GitLab

If you're using Git**Hub** instead, skip to the [Configure Service section](#configure-gitlab).

##### Create Webhook

1. Go to your project → Settings → Webhooks
2. URL: http://your-server:8080/webhook
3. Secret token: Use the same secret from values.yaml
4. Trigger: Check "Merge request events"
5. Click "Add webhook"

##### Create Access Token

1. GitLab → Preferences → Access Tokens
2. Create token with `api` scope
3. Copy token to values.yaml

#### Configure Service

TODO

### Start

Build and start containers

```bash
docker-compose up -d
```
