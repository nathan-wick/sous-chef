# Development Assistant

Automated code reviewer for modern development teams - by [Nathan Wick](https://nathanwick.com).

### Table of Contents

- [Features](#features)
  - [Code Reviewer](#code-reviewer)
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

| Category                         | Estimated Cost Per 1-50 Developers |
| -------------------------------- | ---------------------------------- |
| **Upfront Hardware**             | $12,000                            |
| **Monthly Hardware Maintenance** | $100                               |
| **Monthly Power**                | $250                               |
| **Monthly API Fees**             | $0                                 |
| **Total**                        | $12,000 upfront + $350 monthly     |

### ☁️ API-Based LLM

Using an API-based LLM requires **no additional hardware**, **scales automatically**, and is significantly more **economical** than self-hosting.

| Category                         | Estimated Cost Per 10 Developers |
| -------------------------------- | -------------------------------- |
| **Upfront Hardware**             | $40                              |
| **Monthly Hardware Maintenance** | $1                               |
| **Monthly Power**                | $5                               |
| **Monthly API Fees**             | $4                               |
| **Total**                        | $40 upfront + $10 monthly        |

#### 🧮 Estimated Monthly API Cost Formula

``` python
average_lines_per_hour = 20
average_hours_per_day = 8
average_input_tokens_per_line = 10
average_output_tokens_per_line = 10
input_token_cost_per_million = 1.25
output_token_cost_per_million = 10
number_of_developers = 10
average_working_days_per_month = 22

developer_daily_input_cost = (
    average_lines_per_hour
    * average_hours_per_day
    * average_input_tokens_per_line
    * (input_token_cost_per_million / 1_000_000)
)

developer_daily_output_cost = (
    average_lines_per_hour
    * average_hours_per_day
    * average_output_tokens_per_line
    * (output_token_cost_per_million / 1_000_000)
)

developer_daily_cost = developer_daily_input_cost + developer_daily_output_cost

estimated_monthly_api_cost = (
    developer_daily_cost * number_of_developers * average_working_days_per_month
)

print(f"Estimated Monthly API Cost: ${estimated_monthly_api_cost:.2f}")
```

#### 🤔 Why So Cheap?

API LLM providers can offer services at costs that self-hosting cannot beat for many reasons:

- **Economies of Scale**: Providers run massive inference clusters serving thousands of customers simultaneously. This allows them to:
  - Amortize fixed costs (data center buildout, power infrastructure, networking) across a huge customer base.
  - Negotiate better pricing on hardware, electricity, and bandwidth due to volume.
  - Achieve much higher GPU utilization rates.
  - Group many user requests together to process them in parallel.
  - Cache common requests, significantly reducing redundant computations.
  - Use techniques like quantization, pruning, and knowledge distillation to reduce the size of models.
- **Competition**: The API LLM market is competitive, and providers strategically set prices to gain market share.

#### 🕵️‍♂️ Data Privacy

Code Reviewer will send patches of your code to your API LLM provider. **If handling sensitive data, opt into Zero Data Retention (ZDR)** to prevent any training from, or storage of, your data.

If sending code patches to an external service concerns you, consider:

- **Major providers have strong legal and financial incentives to protect your data**. Companies like Anthropic, OpenAI, and Google have multi-billion-dollar valuations that would be destroyed by a data breach or misuse scandal. Their entire business model depends on trust.
- **Verified security**. SOC 2 Type II and ISO 27001 certifications require regular third-party audits.
- **Zero retention**. With ZDR, code is processed in memory and immediately discarded—no storage, training, or logs.
- **You're likely already exposed**. GitHub Copilot and similar tools send entire codebases externally. Developers routinely share code on Stack Overflow and GitHub. Controlled API calls with ZDR are arguably safer.
- **Blacklisting available**. Code Reviewer can ignore files by keyword.

## Getting Started

Development Assistant can be set up in **5 straightforward steps**, generally taking about **one hour to complete**.

### Prerequisites

- [GitHub](https://github.com/) or [GitLab](https://about.gitlab.com/) account with admin access to repositories
- Domain name with admin access to DNS records or nameservers
- Server with [Git](https://git-scm.com/install/linux) and [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) installed
  - Operating System: Latest [Ubuntu Server](https://ubuntu.com/download/server) recommended for efficiency, compatibility, and long-term support.
  - Hardware: See the [following hardware minimum requirements](#server-hardware-minimum-requirements) for stable and responsive performance, faster inference, and larger context windows, and model loading and data access.

#### Server Hardware Minimum Requirements

| Component      | API-Based LLM        | Self-Hosted 30B Model | Self-Hosted 70B Model |
| -------------- | -------------------- | --------------------- | --------------------- |
| **System RAM** | 2 GB                 | 20 GB                 | 48 GB                 |
| **GPU VRAM**   | Any modern processor | 32 GB                 | 64 GB                 |
| **Storage**    | 50 GB                | NVMe SSD, 500 GB      | NVMe SSD, 1 TB        |

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
  - If you're self-hosting your LLM, any model in [Ollama's library](https://ollama.com/library) will work, but `codellama:34b` or better is recommended.
  - If you're using an API-based LLM, any model in [Gemini's library](https://ai.google.dev/gemini-api/docs/models) will work.
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
