package reviewer

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/nathan-wick/development-assistant/internal/config"
	"github.com/nathan-wick/development-assistant/internal/llm"
	"github.com/nathan-wick/development-assistant/internal/platform"
)

type Reviewer struct {
	llm            llm.Client
	config         *config.Config
	githubPlatform *platform.GitHubPlatform
	gitlabPlatform *platform.GitLabPlatform
}

func NewReviewer(llmClient llm.Client, cfg *config.Config) *Reviewer {
	return &Reviewer{
		llm:    llmClient,
		config: cfg,
	}
}

func (r *Reviewer) SetGitHubPlatform(p *platform.GitHubPlatform) {
	r.githubPlatform = p
}

func (r *Reviewer) SetGitLabPlatform(p *platform.GitLabPlatform) {
	r.gitlabPlatform = p
}

func (r *Reviewer) postComment(ctx context.Context, event *platform.PullRequestEvent, message string) error {
	if r.githubPlatform != nil {
		return r.githubPlatform.PostComment(ctx, event.Owner, event.Repo, event.Number, message)
	} else if r.gitlabPlatform != nil {
		return r.gitlabPlatform.PostComment(ctx, event.Owner, event.Number, message)
	}
	return nil
}

func (r *Reviewer) ReviewPullRequest(ctx context.Context, event *platform.PullRequestEvent) (string, error) {
	greetingMsg := "🤖 Hello! I'm reviewing your changes now. This may take a moment..."
	_ = r.postComment(ctx, event, greetingMsg)

	var reviews []string
	fileCount := 0

	reviews = append(reviews, "# 🤖 Automated Review\n\nPlease note that while I strive for accuracy, it's important to **verify all recommendations before implementing them**. This review is not meant to replace human review, but to accelerate it by catching common issues early.")

	for _, file := range event.Files {
		if fileCount >= r.config.Review.MaxFiles {
			reviews = append(reviews, fmt.Sprintf("🛑 Too many files to review. Only reviewed the first %d files.", r.config.Review.MaxFiles))
			break
		}

		patchSize := len(file.Patch)
		if patchSize > r.config.Review.MaxFileSizeCharacters {
			reviews = append(reviews, fmt.Sprintf("### 🐘 📄 %s\n\nFile changes are too large to review. It contains %d characters, exceeding the %d-character limit.", file.Filename, patchSize, r.config.Review.MaxFileSizeCharacters))
			continue
		}

		if file.Status == "removed" {
			continue
		}

		review, err := r.reviewFileWithProgress(ctx, event, file)
		if err != nil {
			reviews = append(reviews, fmt.Sprintf("### 🛑 📄 %s\n\nError reviewing: %v", file.Filename, err))
			continue
		}

		if review == "" || strings.Contains(strings.ToLower(review), "no issues") {
			reviews = append(reviews, fmt.Sprintf("### ✅ 📄 %s\n\n%s", file.Filename, review))
		} else {
			reviews = append(reviews, fmt.Sprintf("### ⚠️ 📄 %s\n\n%s", file.Filename, review))
		}

		fileCount++
	}

	if len(reviews) == 0 {
		reviews = append(reviews, "No changes to review.")
	}

	return strings.Join(reviews, "\n\n---\n\n"), nil
}

func (r *Reviewer) reviewFileWithProgress(ctx context.Context, event *platform.PullRequestEvent, file platform.FileChange) (string, error) {
	resultChan := make(chan string, 1)
	errChan := make(chan error, 1)

	go func() {
		response, err := r.reviewFile(file)
		if err != nil {
			errChan <- err
			return
		}
		resultChan <- response
	}()

	ticker := time.NewTicker(7 * time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return "", ctx.Err()
		case response := <-resultChan:
			return response, nil
		case err := <-errChan:
			return "", err
		case <-ticker.C:
			progressMsg := fmt.Sprintf("🔄 Still reviewing `%s`... Thanks for your patience!", file.Filename)
			_ = r.postComment(ctx, event, progressMsg)
		}
	}
}

func (r *Reviewer) reviewFile(file platform.FileChange) (string, error) {
	prompt := fmt.Sprintf("%s\n\nFile: %s\n\nChanges:\n```\n%s\n```",
		r.config.Review.ReviewPrompt,
		file.Filename,
		file.Patch,
	)

	response, err := r.llm.Generate(prompt)
	if err != nil {
		return "", err
	}

	return strings.TrimSpace(response), nil
}
