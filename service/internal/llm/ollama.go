package llm

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

type OllamaClient struct {
	host        string
	model       string
	temperature float64
	timeout     time.Duration
}

type GenerateRequest struct {
	Model       string  `json:"model"`
	Prompt      string  `json:"prompt"`
	Stream      bool    `json:"stream"`
	Temperature float64 `json:"temperature"`
}

type GenerateResponse struct {
	Response string `json:"response"`
}

func NewOllamaClient(host, model string, temperature float64, timeout int) *OllamaClient {
	return &OllamaClient{
		host:        host,
		model:       model,
		temperature: temperature,
		timeout:     time.Duration(timeout) * time.Second,
	}
}

func (c *OllamaClient) Generate(prompt string) (string, error) {
	reqBody := GenerateRequest{
		Model:       c.model,
		Prompt:      prompt,
		Stream:      false,
		Temperature: c.temperature,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %w", err)
	}

	url := fmt.Sprintf("http://%s/api/generate", c.host)
	client := &http.Client{Timeout: c.timeout}

	resp, err := client.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("failed to call ollama: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("ollama returned status %d: %s", resp.StatusCode, string(body))
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	var genResp GenerateResponse
	if err := json.Unmarshal(body, &genResp); err != nil {
		return "", fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return genResp.Response, nil
}
