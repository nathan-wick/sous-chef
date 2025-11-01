package platform

import (
	"context"
	"crypto/subtle"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/xanzy/go-gitlab"
)

type GitLabPlatform struct {
	client        *gitlab.Client
	webhookSecret string
}

func NewGitLabPlatform(token, webhookSecret, url string) (*GitLabPlatform, error) {
	client, err := gitlab.NewClient(token, gitlab.WithBaseURL(url))
	if err != nil {
		return nil, err
	}

	return &GitLabPlatform{
		client:        client,
		webhookSecret: webhookSecret,
	}, nil
}

func (g *GitLabPlatform) ValidateWebhook(r *http.Request) error {
	token := r.Header.Get("X-Gitlab-Token")
	if token == "" {
		return fmt.Errorf("missing token header")
	}

	if subtle.ConstantTimeCompare([]byte(token), []byte(g.webhookSecret)) != 1 {
		return fmt.Errorf("invalid token")
	}

	return nil
}

func (g *GitLabPlatform) ParseMergeRequest(r *http.Request) (*PullRequestEvent, error) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		return nil, err
	}

	var event gitlab.MergeEvent
	if err := json.Unmarshal(body, &event); err != nil {
		return nil, err
	}

	if event.ObjectAttributes.Action != "open" && event.ObjectAttributes.Action != "update" {
		return nil, nil
	}

	projectID := event.Project.ID
	mrIID := event.ObjectAttributes.IID

	changes, _, err := g.client.MergeRequests.GetMergeRequestChanges(projectID, mrIID, nil)
	if err != nil {
		return nil, err
	}

	var fileChanges []FileChange
	for _, change := range changes.Changes {
		fileChanges = append(fileChanges, FileChange{
			Filename: change.NewPath,
			Patch:    change.Diff,
			Status:   "modified",
		})
	}

	return &PullRequestEvent{
		Owner:  fmt.Sprintf("%d", projectID),
		Repo:   event.Project.PathWithNamespace,
		Number: mrIID,
		Files:  fileChanges,
	}, nil
}

func (g *GitLabPlatform) PostComment(ctx context.Context, projectID string, mrIID int, comment string) error {
	_, _, err := g.client.Notes.CreateMergeRequestNote(projectID, mrIID, &gitlab.CreateMergeRequestNoteOptions{
		Body: gitlab.String(comment),
	})
	return err
}
