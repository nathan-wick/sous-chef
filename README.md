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

- [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) account with admin access to repositories
- Domain name with admin access to DNS records
- Server with [Git](https://git-scm.com/install/linux) and [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) installed
  - System RAM: Minimum 8 GB; 32 GB recommended for stable and responsive performance
  - GPU VRAM: Minimum 14 GB; 24 GB recommended for faster inference and larger context windows
  - Storage: NVMe SSD (500 GB recommended) for fast model loading and data access
  - Operating System: Latest [Ubuntu Server](https://ubuntu.com/download/server) recommended for efficiency, compatibility, and long-term support

### Step 1: Clone the Development Assistant

From your server, open a new terminal, and run the following command to clone the Development Assistant repository:

```bash
git clone https://github.com/nathan-wick/development-assistant.git
```

### Step 2: Get the Payload URL

The payload URL is your server's publicly accessible URL where your Development Assistant service will be hosted.

#### Port Forwarding

Create 2 new port forwarding rules on your network's router with the following values for port `443` and `80`:

TODO May only need 443

Port `443`:

- Service Name: This can be anything, for example, `Development Assistant`
- External Port: `443`
- Internal IP: Your server's **local** IP address
- Internal Port: `443`
- Protocol: `TCP`
- Status: `Enabled`

Port `80`:

- Service Name: This can be anything, for example, `Development Assistant`
- External Port: `80`
- Internal IP: Your server's **local** IP address
- Internal Port: `80`
- Protocol: `TCP`
- Status: `Enabled`

#### Dynamic DNS

Since your public IP changes, use a Dynamic DNS (DDNS) service to get a persistent domain name. Any DDNS service will do, but for this example, we'll be using [Cloudflare](https://www.cloudflare.com/) (free).

##### DNS Record

1. If you haven't already, [create a Cloudflare account](https://dash.cloudflare.com/sign-up), and [add your domain](https://developers.cloudflare.com/fundamentals/manage-domains/add-site/)
2. From your [Cloudflare Dashboard](https://dash.cloudflare.com), navigate to your domain's DNS records, and add a record with the following values:
   - Type: `A`
   - Name: `development-assistant`
   - IPv4 Address: Your server's [**public** IP address](https://www.showmyip.com/)
   - Proxy Status: `false` (DNS only)
   - TTL: `Auto`

##### Cloudflare API Token

1. Navigate to your [Cloudflare profile's API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Create a new token using the `Edit zone DNS` template with the following values:
   - Permissions: `Zone` / `DNS` / `Edit`
   - Zone Resources: `Include` / `Specific zone` / Your domain name
3. Continue until the token is displayed
4. Copy the token, you'll need it in [step 4](#step-4-define-variables)

##### Zone ID

1. From your [Cloudflare Dashboard](https://dash.cloudflare.com), navigate to your domain's API section (right side)
2. Copy the `Zone ID`, you'll need it in [step 4](#step-4-define-variables)

##### Automatic Updates

TODO Make the `cloudflare-ddns-update.sh` script run every minute.

### Step 3: Configure the Repository

#### Webhook

1. Open [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) and navigate to the Webhooks section of your repository/project's settings
2. Add a webhook with the following values:
   - Payload URL: Your payload URL from [step 2](#step-2-get-the-payload-url) with the `webhook` path, for example, `development-assistant.yourdomain.com/webhook`
   - Content Type: `application/json`
   - Secret: This can be anything, but you'll need to know it in [step 4](#step-4-define-variables)
   - Event/Trigger: `pull/merge requests`

#### Access Token

1. Open [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) and navigate to the Access Tokens section of your account's settings
2. Add an access token with `repo`/`api` scope
3. Copy the token, you'll need it in [step 4](#step-4-define-variables)

TODO Specify the exact permissions needed

### Step 4: Define Variables

#### Secrets

Create a `secrets.env` file at the repository's root.

For example:

```env
PLATFORM_URL=https://github.com
PLATFORM_TOKEN=
PLATFORM_WEBHOOK_SECRET=

DOMAIN_NAME=development-assistant.yourdomain.com
DOMAIN_DNS_TOKEN=
DOMAIN_ZONE_ID=
```

#### Preferences

Update the following values in the preferences.env file to match your preferences:

- `OLLAMA_MODEL`: The LLM used. `codellama:7b` is a happy medium between speed and quality. If you have more resources and prefer deeper insights, `codellama:13b` is a better option.
- `OLLAMA_TEMPERATURE`: The creativity or variability of responses. Lower values (`0.2`–`0.4`) make responses more focused and deterministic. Higher values (`0.6`–`0.8`) make them more exploratory.
- `OLLAMA_TIMEOUT`: Maximum number of seconds to wait for a response.
- `REVIEW_MAX_FILES`: Maximum number of files the AI will review per request. Helps prevent excessive load on the service when large pull requests are submitted.
- `REVIEW_MAX_FILE_SIZE`: Maximum number of characters per file the AI will review. Files larger than this will be skipped to keep responses fast and relevant.
- `REVIEW_PROMPT`: Defines how the AI should approach its code review. You can customize this to match your team’s tone or focus areas (e.g., emphasize readability, security, or test coverage).

### Step 5: Build and Start Containers

Run the following command to build and start containers:

```bash
docker-compose up -d
```

## Troubleshooting

### Docker Uses Too Much Storage

If you start to run low on storage, try clearing your Docker cache by running the following command:

```bash
docker builder prune -f
```

### Nonsense Errors

If you're getting errors that don't make sense, your build cache might be incorrect. Run the following command to rebuild without cache.

```bash
docker-compose build --no-cache
```
