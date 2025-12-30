// Package syncer provides file synchronization functionality for metadata and image files,
// as well as orphan detection and deletion.
package syncer

import (
	"context"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

// SyncResult holds the result of a sync operation.
type SyncResult struct {
	Copied  int
	Skipped int
	Deleted int
	Errors  int
}

// CopyStatus represents the status of a file copy operation.
type CopyStatus string

const (
	CopyStatusSuccess CopyStatus = "success"
	CopyStatusSkipped CopyStatus = "skipped"
	CopyStatusFailed  CopyStatus = "failed"
)

// CopyResult holds the result of a single file copy operation.
type CopyResult struct {
	Src    string
	Dst    string
	Status CopyStatus
	Error  error
}

// Syncer defines the interface for file synchronization operations.
type Syncer interface {
	// CopyFile copies a file from src to dst.
	// Returns skipped status if the target file already exists (Requirement 5.2).
	CopyFile(ctx context.Context, src, dst string) CopyResult

	// DeleteOrphans deletes the specified orphan files.
	DeleteOrphans(ctx context.Context, orphans []string) (deleted int, errors int)

	// FindOrphans returns files that exist in 'existing' but not in 'current'.
	// This identifies STRM files whose source media files no longer exist (Requirement 6.1).
	FindOrphans(existing map[string]bool, current map[string]bool) []string

	// FindMissing returns files that exist in 'current' but not in 'existing'.
	// This identifies media files that don't have corresponding STRM files (Requirement 6.2).
	FindMissing(existing map[string]bool, current map[string]bool) []string
}

// syncer implements the Syncer interface.
type syncer struct{}

// New creates a new Syncer instance.
func New() Syncer {
	return &syncer{}
}

// CopyFile copies a file from src to dst.
// Behavior:
//   - Creates the target directory if it doesn't exist
//   - Skips copying if the target file already exists (Requirement 5.2)
//   - Returns error if copying fails (Requirement 5.3)
func (s *syncer) CopyFile(ctx context.Context, src, dst string) CopyResult {
	// Check for context cancellation
	select {
	case <-ctx.Done():
		return CopyResult{
			Src:    src,
			Dst:    dst,
			Status: CopyStatusFailed,
			Error:  ctx.Err(),
		}
	default:
	}

	// Check if target file already exists (Requirement 5.2)
	// Optimization: We still need to check existence, but we can do it efficiently.
	// We check Stat first.
	if _, err := os.Stat(dst); err == nil {
		return CopyResult{
			Src:    src,
			Dst:    dst,
			Status: CopyStatusSkipped,
			Error:  nil,
		}
	}

	// Create target directory if needed
	dir := filepath.Dir(dst)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return CopyResult{
			Src:    src,
			Dst:    dst,
			Status: CopyStatusFailed,
			Error:  fmt.Errorf("failed to create directory %s: %w", dir, err),
		}
	}

	// Open source file
	srcFile, err := os.Open(src)
	if err != nil {
		return CopyResult{
			Src:    src,
			Dst:    dst,
			Status: CopyStatusFailed,
			Error:  fmt.Errorf("failed to open source file %s: %w", src, err),
		}
	}
	defer srcFile.Close()

	// Create destination file
	// Use O_EXCL to ensure we don't overwrite if it was created concurrently
	// although our logic above already checks Stat, this is safer.
	// For S3 mounts, O_EXCL might not be fully supported or might be expensive,
	// so standard Create is fine as we checked Stat.
	dstFile, err := os.Create(dst)
	if err != nil {
		return CopyResult{
			Src:    src,
			Dst:    dst,
			Status: CopyStatusFailed,
			Error:  fmt.Errorf("failed to create destination file %s: %w", dst, err),
		}
	}
	defer dstFile.Close()

	// Copy content with larger buffer for S3 performance
	// S3 latency is high, so larger chunks help throughput.
	// 128KB buffer
	buf := make([]byte, 128*1024)
	if _, err := io.CopyBuffer(dstFile, srcFile, buf); err != nil {
		// Clean up partial file on error
		os.Remove(dst)
		return CopyResult{
			Src:    src,
			Dst:    dst,
			Status: CopyStatusFailed,
			Error:  fmt.Errorf("failed to copy file content: %w", err),
		}
	}

	// Sync to ensure data is written to disk
	// For S3 fuse mounts, Sync might trigger the actual upload/flush.
	if err := dstFile.Sync(); err != nil {
		return CopyResult{
			Src:    src,
			Dst:    dst,
			Status: CopyStatusFailed,
			Error:  fmt.Errorf("failed to sync file: %w", err),
		}
	}

	return CopyResult{
		Src:    src,
		Dst:    dst,
		Status: CopyStatusSuccess,
		Error:  nil,
	}
}

// DeleteOrphans deletes the specified orphan files.
// Returns the count of successfully deleted files and errors.
func (s *syncer) DeleteOrphans(ctx context.Context, orphans []string) (deleted int, errors int) {
	for _, path := range orphans {
		// Check for context cancellation
		select {
		case <-ctx.Done():
			return deleted, errors
		default:
		}

		if err := os.Remove(path); err != nil {
			if !os.IsNotExist(err) {
				errors++
			}
			// If file doesn't exist, we don't count it as an error
		} else {
			deleted++
		}
	}
	return deleted, errors
}

// FindOrphans returns files that exist in 'existing' but not in 'current'.
// This identifies STRM files whose source media files no longer exist (Requirement 6.1).
//
// Property 5: Orphan Detection Correctness
// For any set of existing STRM files and current S3 media files,
// the orphan detection SHALL return exactly the set difference (existing - current).
func (s *syncer) FindOrphans(existing map[string]bool, current map[string]bool) []string {
	var orphans []string
	for path := range existing {
		if !current[path] {
			orphans = append(orphans, path)
		}
	}
	return orphans
}

// FindMissing returns files that exist in 'current' but not in 'existing'.
// This identifies media files that don't have corresponding STRM files (Requirement 6.2).
//
// Property 6: Missing Detection Correctness
// For any set of existing STRM files and current S3 media files,
// the missing detection SHALL return exactly the set difference (current - existing).
func (s *syncer) FindMissing(existing map[string]bool, current map[string]bool) []string {
	var missing []string
	for path := range current {
		if !existing[path] {
			missing = append(missing, path)
		}
	}
	return missing
}
