package config

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Platform PlatformConfig `yaml:"platform"`
	Ollama   OllamaConfig   `yaml:"ollama"`
	Service  ServiceConfig  `yaml:"service"`
	Review   ReviewConfig   `yaml:"review"`
}

type PlatformConfig struct {
	Url           string `yaml:"url"`
	Token         string `yaml:"token"`
	WebhookSecret string `yaml:"webhook_secret"`
}

type OllamaConfig struct {
	Host        string  `yaml:"host"`
	Model       string  `yaml:"model"`
	Temperature float64 `yaml:"temperature"`
	Timeout     int     `yaml:"timeout"`
}

type ServiceConfig struct {
	Port string `yaml:"port"`
	Host string `yaml:"host"`
}

type ReviewConfig struct {
	MaxFiles              int    `yaml:"max_files"`
	MaxFileSizeCharacters int    `yaml:"max_file_size"`
	ReviewPrompt          string `yaml:"review_prompt"`
}

func LoadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var config Config
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	if err := loadEnvVariables(&config); err != nil {
		return nil, fmt.Errorf("failed to load environment variables: %w", err)
	}

	if err := validateConfig(&config); err != nil {
		return nil, fmt.Errorf("config validation failed: %w", err)
	}

	return &config, nil
}

func loadEnvVariables(config *Config) error {
	if val := os.Getenv("PLATFORM_URL"); val != "" {
		config.Platform.Url = val
	}
	if val := os.Getenv("PLATFORM_TOKEN"); val != "" {
		config.Platform.Token = val
	}
	if val := os.Getenv("PLATFORM_WEBHOOK_SECRET"); val != "" {
		config.Platform.WebhookSecret = val
	}

	return nil
}

func validateConfig(config *Config) error {
	if config.Platform.Token == "" {
		return fmt.Errorf("platform token is required (set PLATFORM_TOKEN secrets.env variable)")
	}
	if config.Platform.WebhookSecret == "" {
		return fmt.Errorf("platform webhook secret is required (set PLATFORM_WEBHOOK_SECRET secrets.env variable)")
	}
	if config.Platform.Url == "" {
		return fmt.Errorf("platform URL is required (set PLATFORM_URL secrets.env variable)")
	}

	return nil
}
