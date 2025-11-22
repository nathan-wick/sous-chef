# Development Assistant

An automated code reviewer that provides instant, intelligent feedback on every pull/merge request.

Created by [Nathan Wick](https://nathanwick.com)

### Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Estimated Cost](#estimated-cost)
- [Getting Started](#getting-started)

## Features

### Code Reviewer

The average software developer spends **5 hours per week** reviewing code. Meanwhile, subtle bugs, security vulnerabilities, and technical debt slip through even the most careful human reviews.

The Development Assistant Code Reviewer serves as an always-available first-pass reviewer on your team, reviewing code 24/7 without fatigue, bias, or delays.

Other software development teams have observed many benefits from similar machine learning (ML) code review tools:

- **Microsoft**: Large-scale internal deployment showed significant code quality improvements, accelerated developer learning, and **10-20% faster median review completion time** ([source](https://devblogs.microsoft.com/engineering-at-microsoft/enhancing-code-quality-at-scale-with-ai-powered-code-reviews/)).
- **Google**: Tested ML code review tools, and found that **40% of suggestions led to developers modifying their code** to address the flagged issues ([source](https://newsletter.getdx.com/p/ai-assisted-code-reviews-at-google)).
- **Industry-wide**: Studies show ML coding assistants give developers a **26% increase in productivity**, freeing them from repetitive checks to focus on architectural decisions and complex components ([source](https://www.infoq.com/news/2024/09/copilot-developer-productivity/)).

#### Live Example

View [this example](https://github.com/nathan-wick/test-development-assistant/pull/9#issuecomment-3509078039) to see Code Reviewer in action!

## How It Works

![diagram](https://github.com/nathan-wick/development-assistant/blob/main/assets/images/diagram.png)

## Estimated Cost

### 🏠 Self-Hosted LLM

Running a self-hosted LLM gives you **full control** and **privacy**, but requires substantial compute resources and maintenance.

#### 💰 Estimated Cost Per 1-50 Developers by Model

| Category              | codellama:70b | gpt-oss:120b | deepseek-r1:671b |
| --------------------- | ------------- | ------------ | ---------------- |
| **Upfront Hardware**  | $15,750       | $27,000      | $150,975         |
| **Monthly Operating** | $543          | $931         | $5,204           |
| **Monthly API Fees**  | $0            | $0           | $0               |

`deepseek-r1:671b` is similar to Gemini 2.5 Pro in performance.

### ☁️ API-Based LLM

Using an API-based LLM requires **no additional hardware**, **scales automatically**, and is significantly **more economical** than self-hosting.

#### 💰 Estimated Cost Per 10 Developers by Model

| Category              | Gemini 2.5 Flash | Gemini 2.5 Pro | Sonnet 4.5 |
| --------------------- | ---------------- | -------------- | ---------- |
| **Upfront Hardware**  | $40              | $40            | $40        |
| **Monthly Operating** | $5               | $5             | $5         |
| **Monthly API Fees**  | $1               | $4             | $6         |

(as of November 2025)

#### 🤔 Why So Affordable?

API LLM providers can offer services at costs that self-hosting cannot beat for the following reasons:

- **Economies of Scale**. Providers run massive inference clusters serving thousands of customers simultaneously.
- **Competition**. The API LLM market is competitive, and providers strategically set prices to gain market share.

#### 🕵️‍♂️ Data Privacy

If sending code to an external service concerns you, here's why Code Reviewer's approach is designed with security in mind:

- **Minimal data exposure**. Code Reviewer sends only the specific lines that changed. Each file is reviewed in a separate request, making it practically impossible for anyone to reconstruct your codebase from fragmented patches scattered across isolated API calls.
- **You stay in control**. Exclude sensitive files, directories, or patterns entirely. If certain code should never leave your environment, Code Reviewer will never send it.
- **Zero retention**. Most providers offer Zero Data Retention (ZDR) to prevent any training from, or storage of, your data. With ZDR, code is processed in memory and immediately discarded.
- **Verified security**. Leading providers maintain SOC 2 Type II and ISO 27001 certifications, which require ongoing third-party security audits.
- **Legal and financial incentives**. Leading providers have multi-billion-dollar valuations at stake. A single data breach or misuse scandal would be catastrophic for their business.
- **Comparison**. 84% of developers are using or planning to use AI tools in their development process ([source](https://survey.stackoverflow.co/2025/ai#sentiment-and-usage-ai-sel-prof)). Many of these tools send entire codebases externally. Controlled API calls with ZDR offer more security than browser-based tools or unvetted extensions.

## Getting Started

Development Assistant can be set up in **5 straightforward steps**, generally taking about **one hour to complete**.

### Prerequisites

- [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) account with admin access to repositories
- Domain name with admin access to DNS records or nameservers
- If using an API-Based LLM, [Gemini](https://aistudio.google.com/) or [Claude](https://console.anthropic.com/dashboard) account and API key
- Server with [Git](https://git-scm.com/install/linux) and [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) installed
  - Operating System: Latest [Ubuntu Server](https://ubuntu.com/download/server) recommended for efficiency, compatibility, and long-term support.
  - Hardware: See the [following hardware minimum requirements](#server-hardware-minimum-requirements).

#### Server Hardware Minimum Requirements

| Component      | API-Based LLM        | Self-Hosted 70B LLM |
| -------------- | -------------------- | ------------------- |
| **System RAM** | 2 GB                 | 48 GB               |
| **GPU VRAM**   | Any modern processor | 64 GB               |
| **Storage**    | 50 GB                | NVMe SSD, 1 TB      |

### Step 1: Clone the Development Assistant

From your server, open a new terminal, and run the following command to clone the Development Assistant repository:

```bash
git clone https://github.com/nathan-wick/development-assistant.git
```

### Step 2: Get the Payload URL

The payload URL is your server's publicly accessible URL where your Development Assistant service will be hosted.

#### Port Forwarding

Create a new port forwarding rule on your network's router:

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
  - If you're self-hosting your LLM, any model in [Ollama's library](https://ollama.com/library) will work.
  - If you're using an API-based LLM, any model in [Gemini's library](https://ai.google.dev/gemini-api/docs/models) or [Claude's library](https://docs.claude.com/en/docs/about-claude/models/overview) will work.
- `LLM_TEMPERATURE`: The creativity or variability of responses. Lower values (`0.2`–`0.4`) make responses more focused and deterministic. Higher values (`0.6`–`0.8`) make them more exploratory.
- `LLM_TIMEOUT`: Maximum number of seconds to wait for a response.
- `REVIEW_MAX_FILES`: Maximum number of files the LLM will review per request. Helps prevent excessive load on the service when large pull requests are submitted.
- `REVIEW_MAX_FILE_SIZE`: Maximum number of characters per file the LLM will review. Files larger than this will be skipped to keep responses fast and relevant.
- `BLOCKED_FILE_PATH_KEYWORDS`: Comma-separated keywords to exclude files from review. Files whose paths contain any of these keywords (case-insensitive) will be skipped and not sent to the LLM. Useful for excluding generated code, dependencies, or sensitive files.
- `REVIEW_PROMPT`: Defines how the LLM should approach its code review. You can customize this to match your team’s tone or focus areas (e.g., emphasize readability, security, or test coverage).

### Step 5: Start!

Run the following command to build and start the container:

```bash
sh start.sh
```
