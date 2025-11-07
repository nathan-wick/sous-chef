# Development Assistant

**Professional AI-powered code review for modern development teams** — by [Nathan Wick](https://nathanwick.com)

### Table of Contents

- [Features](#features)
  - [Code Reviewer](#code-reviewer)
  - [IDE Advanced Autocomplete](#ide-advanced-autocomplete)
  - [Chat Bot](#chat-bot)
- [Estimated Cost](#estimated-cost)
- [Getting Started](#getting-started)

## Features

### Code Reviewer

The average software developer spends **5 hours per week** reviewing code. Meanwhile, subtle bugs, security vulnerabilities, and technical debt slip through even the most careful human reviews.

The Development Assistant Code Reviewer serves as an always-available senior developer on your team, reviewing code 24/7 without fatigue, bias, or delays.

Other software development teams have observed many benefits from similar AI code reviewers:
- Microsoft's large-scale internal implementation observed a significant improvement in code quality, developer learning, and a 10 - 20% quicker median review completion time. ([source](https://devblogs.microsoft.com/engineering-at-microsoft/enhancing-code-quality-at-scale-with-ai-powered-code-reviews/))

### IDE Advanced Autocomplete

Coming soon!

### Chat Bot

Coming soon!

## How It Works

![diagram](https://github.com/nathan-wick/development-assistant/blob/main/development-assistant.png)

## Estimated Cost

### Self-Hosted LLM

Running a self-hosted LLM gives you **full control** and **privacy**, but requires substantial compute resources and maintenance.

Total upfront hardware cost: ~$5,000, depending on configuration.

Monthly power and maintenance cost: ~$100, depending on GPU load and local rates.

### API-based LLM

Using an API-based LLM requires **no additional hardware** and **scales automatically**, but you pay per request or per token generated.

Monthly cost per full-time developer: ~$1, depending on usage.

## Getting Started

### Prerequisites

- [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) account with admin access to repositories
- Domain name with admin access to DNS records
- Server with [Git](https://git-scm.com/install/linux) and [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) installed
  - Operating System: Latest [Ubuntu Server](https://ubuntu.com/download/server) recommended for efficiency, compatibility, and long-term support.
  - If you're self-hosting the LLM, you'll need the following hardware. Otherwise, minimal hardware will suffice.
    - System RAM: Minimum 32 GB recommended for stable and responsive performance.
    - GPU VRAM: Minimum 24 GB recommended for faster inference and larger context windows.
    - Storage: NVMe SSD (minimum 500 GB recommended) for fast model loading and data access.

### Step 1: Clone the Development Assistant

From your server, open a new terminal, and run the following command to clone the Development Assistant repository:

```bash
git clone https://github.com/nathan-wick/development-assistant.git
```

### Step 2: Get the Payload URL

The payload URL is your server's publicly accessible URL where your Development Assistant service will be hosted.

#### Port Forwarding

Create 2 new port forwarding rules on your network's router with the following values for port `443`:

- Service Name: This can be anything, for example, `Development Assistant`
- External Port: `443`
- Internal IP: Your server's **local** IP address
- Internal Port: `443`
- Protocol: `TCP`
- Status: `Enabled`

#### DNS Record

Navigate to your domain's DNS records, and add the following record:

- Type: `A`
- Name: `development-assistant`
- IPv4 Address: Your server's [**public** IP address](https://www.showmyip.com/)
- Proxy Status: `false` (DNS only)
- TTL: `Auto`

#### Dynamic DNS

If your public IP address is dynamic (not static), you'll need a Dynamic DNS (DDNS) service to get a persistent domain name. Development Assistant has a built-in DDNS service that integrates with [Cloudflare](https://www.cloudflare.com/) (free).

##### Move Your Domain To Cloudflare

If you haven't already, [create a Cloudflare account](https://dash.cloudflare.com/sign-up), and [add your domain](https://developers.cloudflare.com/fundamentals/manage-domains/add-site/)

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

### Step 3: Configure the Repository

#### Webhook

1. Open [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) and navigate to the Webhooks section of your repository/project's settings
2. Add a webhook with the following values:
   - Payload URL: Your payload URL from [step 2](#step-2-get-the-payload-url) with the `webhook` path, for example, `https://development-assistant.yourdomain.com/webhook`
   - Content Type: `application/json`
   - Secret: This can be anything, but you'll need to know it in [step 4](#step-4-define-variables)
   - Event/Trigger: `pull/merge requests`

#### Access Token

1. Open [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) and navigate to the Access Tokens section of your account's settings
2. Add an access token with `repo`/`api` scope, and the following permissions:
   - Read repository files
   - Write pull/merge request comments
3. Copy the token, you'll need it in [step 4](#step-4-define-variables)

### Step 4: Define Variables

#### Secrets

Create a `secrets.env` file at the repository's root with the following values:

- `PLATFORM_TOKEN`: Your git hosting platform's API token from [step 3](#step-3-configure-the-repository).
- `PLATFORM_WEBHOOK_SECRET`: The webhook secret you set in [step 3](#step-3-configure-the-repository).
- `DOMAIN_DNS_TOKEN`: Your Cloudflare API token from [step 2](#step-2-get-the-payload-url). If you have a static public IP or don't need the DDNS service, don't add this variable.
- `DOMAIN_ZONE_ID`: Your Zone ID from [step 2](#step-2-get-the-payload-url). If you have a static public IP or don't need the DDNS service, don't add this variable.
- `LLM_API_KEY`: Your API-based LLM's API key. If you're self-hosting your LLM, don't add this variable.

#### Settings

Update the following values in the settings.env file to match your settings:

- `PLATFORM_URL`: The URL to your git hosting platform (GitHub/GitLab).
- `DOMAIN_NAME`: Your payload URL's domain name from [step 2](#step-2-get-the-payload-url), for example, `development-assistant.yourdomain.com`
- `LLM_MODEL`: The LLM model used.
  - If you're using Ollama, any model in [Ollama's library](https://ollama.com/library) will work, but `codellama:13b` or better is recommended.
  - If you're using Gemini, any model in [Gemini's library](https://ai.google.dev/gemini-api/docs/models) will work.
- `LLM_TEMPERATURE`: The creativity or variability of responses. Lower values (`0.2`–`0.4`) make responses more focused and deterministic. Higher values (`0.6`–`0.8`) make them more exploratory.
- `LLM_TIMEOUT`: Maximum number of seconds to wait for a response.
- `REVIEW_MAX_FILES`: Maximum number of files the LLM will review per request. Helps prevent excessive load on the service when large pull requests are submitted.
- `REVIEW_MAX_FILE_SIZE`: Maximum number of characters per file the LLM will review. Files larger than this will be skipped to keep responses fast and relevant.
- `REVIEW_PROMPT`: Defines how the LLM should approach its code review. You can customize this to match your team’s tone or focus areas (e.g., emphasize readability, security, or test coverage).

### Step 5: Start!

Run the following command to build and start the container:

```bash
sh start.sh
```
