package config

import (
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
		return nil, err
	}

	var config Config
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, err
	}

	return &config, nil
}
