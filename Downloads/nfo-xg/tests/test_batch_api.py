"""Tests for batch editing API endpoints."""
import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from web.app import app


client = TestClient(app)


def _create_nfo(path: Path, title: str, studio: str = "Old Studio", genre: str = "Action") -> None:
    path.write_text(
        f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<movie>
    <title>{title}</title>
    <studio>{studio}</studio>
    <genre>{genre}</genre>
</movie>""",
        encoding="utf-8"
    )


class TestBatchPreviewEndpoint:
    """Tests for /api/batch/preview endpoint."""

    def test_preview_returns_task_and_samples(self, tmp_path):
        """Preview returns task_id, total_files, and sample_files with new_value."""
        _create_nfo(tmp_path / "movie1.nfo", "Movie 1")
        _create_nfo(tmp_path / "movie2.nfo", "Movie 2")

        response = client.post(
            "/api/batch/preview",
            json={
                "directory": str(tmp_path),
                "field": "studio",
                "value": "Disney",
                "mode": "overwrite"
            },
            auth=("test", "test")
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 2
        assert len(data["sample_files"]) == 2
        assert data["sample_files"][0]["new_value"] == "Disney"

    def test_preview_invalid_directory(self, tmp_path):
        """Preview returns 404 for missing directory."""
        missing_dir = tmp_path / "missing"

        response = client.post(
            "/api/batch/preview",
            json={
                "directory": str(missing_dir),
                "field": "studio",
                "value": "Disney",
                "mode": "overwrite"
            },
            auth=("test", "test")
        )

        assert response.status_code == 404


class TestBatchApplyEndpoint:
    """Tests for /api/batch/apply endpoint."""

    def test_apply_starts_task(self, tmp_path):
        """Apply returns running status for valid task."""
        _create_nfo(tmp_path / "movie1.nfo", "Movie 1")

        preview = client.post(
            "/api/batch/preview",
            json={
                "directory": str(tmp_path),
                "field": "studio",
                "value": "Disney",
                "mode": "overwrite"
            },
            auth=("test", "test")
        )
        task_id = preview.json()["task_id"]

        response = client.post(
            "/api/batch/apply",
            json={"task_id": task_id, "confirmed": True},
            auth=("test", "test")
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "running"

    def test_apply_invalid_task(self):
        """Apply returns 404 for invalid task id."""
        response = client.post(
            "/api/batch/apply",
            json={"task_id": "missing-task", "confirmed": True},
            auth=("test", "test")
        )

        assert response.status_code == 404


class TestBatchStatusEndpoint:
    """Tests for /api/batch/status endpoint."""

    def test_status_returns_task(self, tmp_path):
        """Status returns current task details."""
        _create_nfo(tmp_path / "movie1.nfo", "Movie 1")

        preview = client.post(
            "/api/batch/preview",
            json={
                "directory": str(tmp_path),
                "field": "studio",
                "value": "Disney",
                "mode": "overwrite"
            },
            auth=("test", "test")
        )
        task_id = preview.json()["task_id"]

        response = client.get(
            f"/api/batch/status/{task_id}",
            auth=("test", "test")
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "pending"
        assert data["total"] == 1

    def test_status_invalid_task(self):
        """Status returns 404 for invalid task id."""
        response = client.get(
            "/api/batch/status/missing-task",
            auth=("test", "test")
        )

        assert response.status_code == 404


class TestScanDepthLimit:
    """Tests for recursion depth limit in _scan_nfo_files."""

    def test_scan_depth_limit_raises_error(self, tmp_path):
        """Deeply nested directories should raise RuntimeError."""
        from nfo_editor.batch.processor import BatchProcessor
        from nfo_editor.utils.xml_parser import XmlParser

        processor = BatchProcessor(XmlParser())

        # Create deeply nested structure (deeper than MAX_SCAN_DEPTH)
        current = tmp_path
        for i in range(60):  # Exceeds MAX_SCAN_DEPTH of 50
            current = current / f"level_{i}"
            current.mkdir()

        # Add an NFO file at the bottom
        (current / "movie.nfo").write_text(
            '<?xml version="1.0" encoding="UTF-8"?><movie><title>Deep Movie</title></movie>',
            encoding="utf-8"
        )

        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Maximum scan depth"):
            processor.preview(str(tmp_path), "studio", "TestStudio")
