package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/nathan-wick/development-assistant/internal/config"
	"github.com/nathan-wick/development-assistant/internal/llm"
	"github.com/nathan-wick/development-assistant/internal/platform"
	"github.com/nathan-wick/development-assistant/internal/reviewer"
)

type Service struct {
	config   *config.Config
	reviewer *reviewer.Reviewer
	github   *platform.GitHubPlatform
	gitlab   *platform.GitLabPlatform
}

func detectPlatformFromToken(token string) string {
	token = strings.TrimSpace(token)

	if strings.HasPrefix(token, "ghp_") ||
		strings.HasPrefix(token, "github_pat_") ||
		strings.HasPrefix(token, "gho_") ||
		strings.HasPrefix(token, "ghu_") ||
		strings.HasPrefix(token, "ghs_") ||
		strings.HasPrefix(token, "ghr_") {
		return "github"
	}

	if strings.HasPrefix(token, "glpat-") ||
		strings.HasPrefix(token, "gloas-") ||
		strings.HasPrefix(token, "glgat-") ||
		strings.HasPrefix(token, "gldt-") ||
		strings.HasPrefix(token, "glagent-") {
		return "gitlab"
	}

	if len(token) >= 20 && len(token) <= 26 {
		// Could be GitLab legacy token
		return "gitlab"
	}

	return ""
}

func main() {
	cfg, err := config.LoadConfig("/config/values.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	llmClient := llm.NewOllamaClient(
		cfg.Ollama.Host,
		cfg.Ollama.Model,
		cfg.Ollama.Temperature,
		cfg.Ollama.Timeout,
	)

	rev := reviewer.NewReviewer(llmClient, cfg)

	svc := &Service{
		config:   cfg,
		reviewer: rev,
	}

	detectedPlatform := detectPlatformFromToken(cfg.Platform.Token)
	if detectedPlatform == "github" {
		svc.github = platform.NewGitHubPlatform(cfg.Platform.Token, cfg.Platform.WebhookSecret)
	} else {
		glPlatform, err := platform.NewGitLabPlatform(cfg.Platform.Token, cfg.Platform.WebhookSecret, cfg.Platform.Url)
		if err != nil {
			log.Fatalf("Failed to initialize GitLab: %v", err)
		}
		svc.gitlab = glPlatform
	}

	http.HandleFunc("/webhook", svc.handleWebhook)
	http.HandleFunc("/health", svc.handleHealth)

	server := &http.Server{
		Addr:    fmt.Sprintf("%s:%s", cfg.Service.Host, cfg.Service.Port),
		Handler: http.DefaultServeMux,
	}

	go func() {
		log.Printf("Starting server on %s:%s", cfg.Service.Host, cfg.Service.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server failed: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("Shutting down server...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited")
}

func (s *Service) handleWebhook(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var event *platform.PullRequestEvent
	var err error

	detectedPlatform := detectPlatformFromToken(s.config.Platform.Token)
	if detectedPlatform == "github" {
		if err := s.github.ValidateWebhook(r); err != nil {
			log.Printf("Webhook validation failed: %v", err)
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		event, err = s.github.ParsePullRequest(r)
	} else {
		if err := s.gitlab.ValidateWebhook(r); err != nil {
			log.Printf("Webhook validation failed: %v", err)
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		event, err = s.gitlab.ParseMergeRequest(r)
	}

	if err != nil {
		log.Printf("Failed to parse event: %v", err)
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	if event == nil {
		w.WriteHeader(http.StatusOK)
		return
	}

	go s.processReview(event)

	w.WriteHeader(http.StatusOK)
}

func (s *Service) processReview(event *platform.PullRequestEvent) {
	ctx := context.Background()

	log.Printf("Processing review for %s/%s #%d", event.Owner, event.Repo, event.Number)

	review, err := s.reviewer.ReviewPullRequest(ctx, event)
	if err != nil {
		log.Printf("Review failed: %v", err)
		return
	}

	detectedPlatform := detectPlatformFromToken(s.config.Platform.Token)
	if detectedPlatform == "github" {
		err = s.github.PostComment(ctx, event.Owner, event.Repo, event.Number, review)
	} else {
		err = s.gitlab.PostComment(ctx, event.Owner, event.Number, review)
	}

	if err != nil {
		log.Printf("Failed to post comment: %v", err)
		return
	}

	log.Printf("Review completed for %s/%s #%d", event.Owner, event.Repo, event.Number)
}

func (s *Service) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}
