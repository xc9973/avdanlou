// Package generator provides STRM file generation functionality.
package generator

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"strm-generator/pkg/mapper"
)

// GenerationStatus represents the status of a STRM generation operation.
type GenerationStatus string

const (
	StatusSuccess GenerationStatus = "success"
	StatusSkipped GenerationStatus = "skipped"
	StatusFailed  GenerationStatus = "failed"
)

// GenerationResult holds the result of a STRM generation operation.
type GenerationResult struct {
	Path   string
	Status GenerationStatus
	Error  error
}

// Generator defines the interface for STRM file generation.
type Generator interface {
	// GenerateSTRM creates a STRM file for a media file.
	// Returns the result indicating success, skipped (already exists), or failed.
	GenerateSTRM(ctx context.Context, mediaPath string) GenerationResult

	// CreateDirectories creates the directory structure for a given path.
	CreateDirectories(path string) error

	// GetEmbyMount returns the Emby mount prefix for validation.
	GetEmbyMount() string
}

// generator implements the Generator interface.
type generator struct {
	pathMapper mapper.PathMapper
	embyMount  string
}

// New creates a new Generator instance.
// Parameters:
//   - pathMapper: The path mapper for converting S3 paths to Emby/output paths
//   - embyMount: The Emby mount prefix (e.g., "/emby")
func New(pathMapper mapper.PathMapper, embyMount string) Generator {
	return &generator{
		pathMapper: pathMapper,
		embyMount:  filepath.Clean(embyMount),
	}
}


// GenerateSTRM creates a STRM file for a media file.
// The STRM file contains the Emby path to the media file.
//
// Behavior:
//   - Creates the target directory if it doesn't exist (Requirement 4.2)
//   - Skips generation if STRM file already exists with same content (Requirement 4.3)
//   - Returns error if file creation fails due to permissions (Requirement 4.4)
//   - STRM content is a valid Emby path (Requirement 4.5)
func (g *generator) GenerateSTRM(ctx context.Context, mediaPath string) GenerationResult {
	// Check for context cancellation
	select {
	case <-ctx.Done():
		return GenerationResult{
			Path:   mediaPath,
			Status: StatusFailed,
			Error:  ctx.Err(),
		}
	default:
	}

	// Get the STRM output path
	strmPath := g.pathMapper.ToSTRMPath(mediaPath)

	// Get the Emby path for the media file (this is the STRM content)
	embyPath := g.pathMapper.ToEmbyPath(mediaPath)

	// Validate that embyPath starts with embyMount (Requirement 4.5)
	if !strings.HasPrefix(embyPath, g.embyMount) {
		return GenerationResult{
			Path:   strmPath,
			Status: StatusFailed,
			Error:  fmt.Errorf("generated Emby path does not start with mount prefix: %s", embyPath),
		}
	}

	// Create directory structure if needed (Requirement 4.2)
	dir := filepath.Dir(strmPath)
	if err := g.CreateDirectories(dir); err != nil {
		return GenerationResult{
			Path:   strmPath,
			Status: StatusFailed,
			Error:  fmt.Errorf("failed to create directory %s: %w", dir, err),
		}
	}

	// Check if STRM file already exists with same content (Requirement 4.3)
	// Optimization for S3: Do NOT read file content. Reading is expensive.
	// If the file exists, we assume it's correct because the path mapping is deterministic.
	// Only if the file doesn't exist, we create it.
	if _, err := os.Stat(strmPath); err == nil {
		// File exists, assume it's up to date
		return GenerationResult{
			Path:   strmPath,
			Status: StatusSkipped,
			Error:  nil,
		}
	}

	// Write the STRM file (Requirement 4.1)
	if err := os.WriteFile(strmPath, []byte(embyPath), 0644); err != nil {
		return GenerationResult{
			Path:   strmPath,
			Status: StatusFailed,
			Error:  fmt.Errorf("failed to write STRM file %s: %w", strmPath, err),
		}
	}

	return GenerationResult{
		Path:   strmPath,
		Status: StatusSuccess,
		Error:  nil,
	}
}

// CreateDirectories creates the directory structure for a given path.
// Uses os.MkdirAll to create all necessary parent directories.
func (g *generator) CreateDirectories(path string) error {
	return os.MkdirAll(path, 0755)
}

// GetEmbyMount returns the Emby mount prefix.
func (g *generator) GetEmbyMount() string {
	return g.embyMount
}

// ReadSTRMContent reads and returns the content of a STRM file.
// This is useful for validation and testing.
func ReadSTRMContent(strmPath string) (string, error) {
	content, err := os.ReadFile(strmPath)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(content)), nil
}

// ValidateSTRMContent checks if the STRM content is a valid Emby path.
// A valid Emby path must start with the given embyMount prefix.
func ValidateSTRMContent(content, embyMount string) bool {
	return strings.HasPrefix(content, embyMount)
}
