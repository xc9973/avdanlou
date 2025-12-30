// Package scanner provides file scanning functionality for the STRM generator.
package scanner

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"strm-generator/pkg/models"
)

// Scanner defines the interface for file scanning operations.
type Scanner interface {
	// Scan recursively scans a directory and returns files through channels.
	// Returns a channel of FileInfo for found files and a channel for errors.
	Scan(ctx context.Context, path string) (<-chan models.FileInfo, <-chan error)

	// ScanSince scans only files/directories modified since the given time.
	// This reduces S3 API calls by skipping unchanged directories.
	ScanSince(ctx context.Context, path string, since time.Time) (<-chan models.FileInfo, <-chan error)

	// ClassifyFile determines the type of a file based on its extension.
	ClassifyFile(path string) models.FileType
}

// ScanResult holds the aggregated results of a scan operation.
type ScanResult struct {
	MediaCount    int
	MetadataCount int
	ImageCount    int
	UnknownCount  int
	Errors        []error
}

// scanner implements the Scanner interface.
type scanner struct {
	mu sync.Mutex
}

// New creates a new Scanner instance.
func New() Scanner {
	return &scanner{}
}


// ClassifyFile determines the type of a file based on its extension.
// Returns FileTypeMedia, FileTypeMetadata, FileTypeImage, or FileTypeUnknown.
func (s *scanner) ClassifyFile(path string) models.FileType {
	ext := strings.ToLower(filepath.Ext(path))
	if ext == "" {
		return models.FileTypeUnknown
	}

	if models.MediaExtensions[ext] {
		return models.FileTypeMedia
	}
	if models.MetadataExtensions[ext] {
		return models.FileTypeMetadata
	}
	if models.ImageExtensions[ext] {
		return models.FileTypeImage
	}
	return models.FileTypeUnknown
}

// Scan recursively scans a directory and sends FileInfo through the returned channel.
// It handles errors gracefully by logging warnings and continuing with other directories.
// The scan can be cancelled via the context.
func (s *scanner) Scan(ctx context.Context, path string) (<-chan models.FileInfo, <-chan error) {
	fileChan := make(chan models.FileInfo, 100)
	errChan := make(chan error, 10)

	go func() {
		defer close(fileChan)
		defer close(errChan)

		s.scanDir(ctx, path, fileChan, errChan)
	}()

	return fileChan, errChan
}

// scanDir recursively scans a directory and sends results through channels.
func (s *scanner) scanDir(ctx context.Context, path string, fileChan chan<- models.FileInfo, errChan chan<- error) {
	s.scanDirSince(ctx, path, time.Time{}, fileChan, errChan)
}

// ScanSince scans only files/directories modified since the given time.
func (s *scanner) ScanSince(ctx context.Context, path string, since time.Time) (<-chan models.FileInfo, <-chan error) {
	fileChan := make(chan models.FileInfo, 100)
	errChan := make(chan error, 10)

	go func() {
		defer close(fileChan)
		defer close(errChan)

		s.scanDirSince(ctx, path, since, fileChan, errChan)
	}()

	return fileChan, errChan
}

// scanDirSince recursively scans a directory, optionally filtering by modification time.
func (s *scanner) scanDirSince(ctx context.Context, path string, since time.Time, fileChan chan<- models.FileInfo, errChan chan<- error) {
	// Check for context cancellation
	select {
	case <-ctx.Done():
		return
	default:
	}

	// Remove sleep for performance optimization on S3 mounts
	// time.Sleep(5 * time.Millisecond)

	entries, err := os.ReadDir(path)
	if err != nil {
		// Log warning and continue with other directories (Requirement 2.3)
		select {
		case errChan <- err:
		default:
			// Error channel full, skip this error
		}
		return
	}

	for _, entry := range entries {
		// Check for context cancellation
		select {
		case <-ctx.Done():
			return
		default:
		}

		fullPath := filepath.Join(path, entry.Name())

		// Optimization: Only call Info() if we need ModTime or Size
		// This significantly reduces S3 API calls (HEAD requests)
		var modTime time.Time
		var size int64
		var isDir bool

		// Check if it's a directory based on DirentType if possible
		// Note: On some systems/filesystems entry.IsDir() might fallback to Lstat/Stat
		// But usually it's cheaper than full Info()
		isDir = entry.IsDir()

		// If we have a 'since' filter, we MUST get Info() to check ModTime
		// If it's a file, we might need Size later, but for now we prioritize reducing calls
		needInfo := !since.IsZero()

		if needInfo {
			info, err := entry.Info()
			if err != nil {
				select {
				case errChan <- err:
				default:
				}
				continue
			}
			modTime = info.ModTime()
			size = info.Size()
		}

		if isDir {
			// If since is set, skip directories that haven't been modified
			// Note: S3 directories (prefixes) might not have meaningful modTimes,
			// so this optimization depends on the filesystem adapter.
			// Conservatively, we might want to recurse anyway if modTime is zero/unavailable.
			if !since.IsZero() && !modTime.IsZero() && modTime.Before(since) {
				continue // Skip this directory entirely
			}
			// Recursively scan subdirectories (Requirement 2.1)
			s.scanDirSince(ctx, fullPath, since, fileChan, errChan)
			continue
		}

		// If since is set, skip files that haven't been modified
		if !since.IsZero() && modTime.Before(since) {
			continue
		}

		// Classify and send file info (Requirement 2.2)
		fileType := s.ClassifyFile(fullPath)

		// Optimization: If we didn't get info yet, and it's a relevant file type,
		// we might need to get it now if downstream consumers require Size/ModTime.
		// However, for STRM generation, we often just need the Path.
		// If we return zero values, make sure consumers can handle it.
		//
		// BUT: pkg/models/models.go defines FileInfo with ModTime and Size.
		// If we return 0/empty, state tracking might break if it relies on ModTime.
		// Let's check: State.MediaFiles maps path -> mtime.
		// So we DO need ModTime for MediaFiles to support incremental scans.

		if fileType != models.FileTypeUnknown && !needInfo {
			// We found a relevant file, and we haven't fetched Info yet.
			// We MUST fetch it now to populate FileInfo correctly for state tracking.
			info, err := entry.Info()
			if err != nil {
				select {
				case errChan <- err:
				default:
				}
				continue
			}
			modTime = info.ModTime()
			size = info.Size()
		}

		// For Unknown files, we skip getting Info (optimization), but we MUST pass them through
		// if we want them to be counted in ScanResult (Requirement 2.4).
		// However, usually we don't care about unknown files in the output stream unless
		// we specifically want to count them.
		// The test expects UnknownCount to be correct, so we must emit them.

		fileInfo := models.FileInfo{
			Path:    fullPath,
			Type:    fileType,
			ModTime: modTime,
			Size:    size,
		}

		select {
		case <-ctx.Done():
			return
		case fileChan <- fileInfo:
		}
	}
}


// ScanAndCollect performs a scan and collects all results into a ScanResult.
// This is a convenience method that aggregates the streaming results.
func (s *scanner) ScanAndCollect(ctx context.Context, path string) (*ScanResult, []models.FileInfo) {
	fileChan, errChan := s.Scan(ctx, path)

	result := &ScanResult{}
	var files []models.FileInfo

	// Collect errors in background
	var errors []error
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		for err := range errChan {
			errors = append(errors, err)
		}
	}()

	// Collect files and count by type (Requirement 2.4)
	for file := range fileChan {
		files = append(files, file)
		switch file.Type {
		case models.FileTypeMedia:
			result.MediaCount++
		case models.FileTypeMetadata:
			result.MetadataCount++
		case models.FileTypeImage:
			result.ImageCount++
		default:
			result.UnknownCount++
		}
	}

	wg.Wait()
	result.Errors = errors

	return result, files
}

// ClassifyFileStatic is a standalone function for classifying files without a scanner instance.
// Useful for testing and one-off classifications.
func ClassifyFileStatic(path string) models.FileType {
	ext := strings.ToLower(filepath.Ext(path))
	if ext == "" {
		return models.FileTypeUnknown
	}

	if models.MediaExtensions[ext] {
		return models.FileTypeMedia
	}
	if models.MetadataExtensions[ext] {
		return models.FileTypeMetadata
	}
	if models.ImageExtensions[ext] {
		return models.FileTypeImage
	}
	return models.FileTypeUnknown
}
