package platform

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/google/go-github/v57/github"
)

type GitHubPlatform struct {
	client        *github.Client
	webhookSecret string
}

type PullRequestEvent struct {
	Owner  string
	Repo   string
	Number int
	Files  []FileChange
}

type FileChange struct {
	Filename string
	Patch    string
	Status   string
}

func NewGitHubPlatform(token, webhookSecret string) *GitHubPlatform {
	client := github.NewClient(nil).WithAuthToken(token)
	return &GitHubPlatform{
		client:        client,
		webhookSecret: webhookSecret,
	}
}

func (g *GitHubPlatform) ValidateWebhook(r *http.Request) error {
	signature := r.Header.Get("X-Hub-Signature-256")
	if signature == "" {
		return fmt.Errorf("missing signature header")
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		return err
	}
	r.Body = io.NopCloser(strings.NewReader(string(body)))

	mac := hmac.New(sha256.New, []byte(g.webhookSecret))
	mac.Write(body)
	expectedMAC := "sha256=" + hex.EncodeToString(mac.Sum(nil))

	if !hmac.Equal([]byte(signature), []byte(expectedMAC)) {
		return fmt.Errorf("invalid signature")
	}

	return nil
}

func (g *GitHubPlatform) ParsePullRequest(r *http.Request) (*PullRequestEvent, error) {
	var payload github.PullRequestEvent
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		return nil, err
	}

	if payload.GetAction() != "opened" && payload.GetAction() != "synchronize" {
		return nil, nil
	}

	pr := payload.GetPullRequest()
	files, _, err := g.client.PullRequests.ListFiles(
		context.Background(),
		payload.Repo.Owner.GetLogin(),
		payload.Repo.GetName(),
		pr.GetNumber(),
		nil,
	)
	if err != nil {
		return nil, err
	}

	var fileChanges []FileChange
	for _, file := range files {
		fileChanges = append(fileChanges, FileChange{
			Filename: file.GetFilename(),
			Patch:    file.GetPatch(),
			Status:   file.GetStatus(),
		})
	}

	return &PullRequestEvent{
		Owner:  payload.Repo.Owner.GetLogin(),
		Repo:   payload.Repo.GetName(),
		Number: pr.GetNumber(),
		Files:  fileChanges,
	}, nil
}

func (g *GitHubPlatform) PostComment(ctx context.Context, owner, repo string, number int, comment string) error {
	_, _, err := g.client.Issues.CreateComment(ctx, owner, repo, number, &github.IssueComment{
		Body: github.String(comment),
	})
	return err
}
