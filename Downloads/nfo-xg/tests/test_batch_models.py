"""Tests for batch editing models."""
import pytest
from datetime import datetime
from nfo_editor.batch.models import (
    TaskStatus,
    BatchTask,
    BatchPreviewRequest,
    BatchApplyRequest,
    BatchPreviewResponse,
    BatchStatusResponse,
)


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_status_values(self):
        """Test that TaskStatus has correct values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"

    def test_status_members(self):
        """Test that TaskStatus has all required members."""
        assert hasattr(TaskStatus, 'PENDING')
        assert hasattr(TaskStatus, 'RUNNING')
        assert hasattr(TaskStatus, 'COMPLETED')
        assert hasattr(TaskStatus, 'FAILED')


class TestBatchTask:
    """Test BatchTask dataclass."""

    def test_batch_task_creation(self):
        """Test creating a BatchTask instance."""
        task = BatchTask(
            task_id="test-task-1",
            status=TaskStatus.PENDING,
            total_files=10,
            processed_files=0,
            success_count=0,
            failed_count=0,
            errors=[],
            created_at=datetime.now(),
            field="studio",
            value="Disney",
            mode="overwrite",
            directory="/movies"
        )

        assert task.task_id == "test-task-1"
        assert task.status == TaskStatus.PENDING
        assert task.total_files == 10
        assert task.processed_files == 0
        assert task.success_count == 0
        assert task.failed_count == 0
        assert task.errors == []
        assert task.field == "studio"
        assert task.value == "Disney"
        assert task.mode == "overwrite"
        assert task.directory == "/movies"

    def test_progress_calculation(self):
        """Test progress property calculation."""
        task = BatchTask(
            task_id="test-task-2",
            status=TaskStatus.RUNNING,
            total_files=10,
            processed_files=5,
            success_count=4,
            failed_count=1,
            errors=["Error 1"],
            created_at=datetime.now(),
            field="genre",
            value="Action",
            mode="append",
            directory="/movies"
        )

        assert task.progress == 50.0

    def test_progress_zero_total(self):
        """Test progress calculation when total_files is 0."""
        task = BatchTask(
            task_id="test-task-3",
            status=TaskStatus.PENDING,
            total_files=0,
            processed_files=0,
            success_count=0,
            failed_count=0,
            errors=[],
            created_at=datetime.now(),
            field="director",
            value="Nolan",
            mode="overwrite",
            directory="/movies"
        )

        assert task.progress == 0.0

    def test_progress_completed(self):
        """Test progress when task is completed."""
        task = BatchTask(
            task_id="test-task-4",
            status=TaskStatus.COMPLETED,
            total_files=20,
            processed_files=20,
            success_count=18,
            failed_count=2,
            errors=["Error 1", "Error 2"],
            created_at=datetime.now(),
            field="studio",
            value="Warner",
            mode="overwrite",
            directory="/movies"
        )

        assert task.progress == 100.0


class TestBatchPreviewRequest:
    """Test BatchPreviewRequest model."""

    def test_batch_preview_request_creation(self):
        """Test creating a BatchPreviewRequest instance."""
        request = BatchPreviewRequest(
            directory="/movies",
            field="studio",
            value="Disney",
            mode="overwrite"
        )

        assert request.directory == "/movies"
        assert request.field == "studio"
        assert request.value == "Disney"
        assert request.mode == "overwrite"

    def test_batch_preview_request_default_mode(self):
        """Test that mode defaults to 'overwrite'."""
        request = BatchPreviewRequest(
            directory="/movies",
            field="genre",
            value="Action"
        )

        assert request.mode == "overwrite"

    def test_batch_preview_request_append_mode(self):
        """Test creating request with append mode."""
        request = BatchPreviewRequest(
            directory="/tv",
            field="genre",
            value="Drama",
            mode="append"
        )

        assert request.mode == "append"


class TestBatchApplyRequest:
    """Test BatchApplyRequest model."""

    def test_batch_apply_request_creation(self):
        """Test creating a BatchApplyRequest instance."""
        request = BatchApplyRequest(
            task_id="preview-task-123",
            confirmed=True
        )

        assert request.task_id == "preview-task-123"
        assert request.confirmed is True

    def test_batch_apply_request_default_confirmed(self):
        """Test that confirmed defaults to True."""
        request = BatchApplyRequest(task_id="preview-task-456")

        assert request.confirmed is True

    def test_batch_apply_request_confirmed_false(self):
        """Test creating request with confirmed=False."""
        request = BatchApplyRequest(
            task_id="preview-task-789",
            confirmed=False
        )

        assert request.confirmed is False


class TestBatchPreviewResponse:
    """Test BatchPreviewResponse model."""

    def test_batch_preview_response_creation(self):
        """Test creating a BatchPreviewResponse instance."""
        sample_files = [
            {"path": "/movies/movie1.nfo", "title": "Movie 1"},
            {"path": "/movies/movie2.nfo", "title": "Movie 2"}
        ]

        response = BatchPreviewResponse(
            task_id="preview-task-1",
            total_files=10,
            sample_files=sample_files
        )

        assert response.task_id == "preview-task-1"
        assert response.total_files == 10
        assert len(response.sample_files) == 2
        assert response.sample_files[0]["title"] == "Movie 1"

    def test_batch_preview_response_empty_samples(self):
        """Test creating response with empty sample files."""
        response = BatchPreviewResponse(
            task_id="preview-task-2",
            total_files=0,
            sample_files=[]
        )

        assert response.total_files == 0
        assert response.sample_files == []


class TestBatchStatusResponse:
    """Test BatchStatusResponse model."""

    def test_batch_status_response_creation(self):
        """Test creating a BatchStatusResponse instance."""
        response = BatchStatusResponse(
            task_id="task-123",
            status="running",
            progress=50.0,
            processed=5,
            total=10,
            success=4,
            failed=1,
            errors=["File not found: /movies/missing.nfo"]
        )

        assert response.task_id == "task-123"
        assert response.status == "running"
        assert response.progress == 50.0
        assert response.processed == 5
        assert response.total == 10
        assert response.success == 4
        assert response.failed == 1
        assert len(response.errors) == 1
        assert response.errors[0] == "File not found: /movies/missing.nfo"

    def test_batch_status_response_completed(self):
        """Test creating response for completed task."""
        response = BatchStatusResponse(
            task_id="task-456",
            status="completed",
            progress=100.0,
            processed=20,
            total=20,
            success=20,
            failed=0,
            errors=[]
        )

        assert response.status == "completed"
        assert response.progress == 100.0
        assert response.errors == []

    def test_batch_status_response_failed(self):
        """Test creating response for failed task."""
        response = BatchStatusResponse(
            task_id="task-789",
            status="failed",
            progress=25.0,
            processed=5,
            total=20,
            success=3,
            failed=2,
            errors=["Error 1", "Error 2", "Error 3"]
        )

        assert response.status == "failed"
        assert response.progress == 25.0
        assert len(response.errors) == 3


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_batch_preview_request_serialization(self):
        """Test BatchPreviewRequest can be serialized to dict."""
        request = BatchPreviewRequest(
            directory="/movies",
            field="studio",
            value="Disney",
            mode="overwrite"
        )

        data = request.model_dump()

        assert data["directory"] == "/movies"
        assert data["field"] == "studio"
        assert data["value"] == "Disney"
        assert data["mode"] == "overwrite"

    def test_batch_apply_request_serialization(self):
        """Test BatchApplyRequest can be serialized to dict."""
        request = BatchApplyRequest(
            task_id="task-123",
            confirmed=True
        )

        data = request.model_dump()

        assert data["task_id"] == "task-123"
        assert data["confirmed"] is True

    def test_batch_preview_response_serialization(self):
        """Test BatchPreviewResponse can be serialized to dict."""
        response = BatchPreviewResponse(
            task_id="preview-1",
            total_files=5,
            sample_files=[{"path": "/test.nfo"}]
        )

        data = response.model_dump()

        assert data["task_id"] == "preview-1"
        assert data["total_files"] == 5
        assert len(data["sample_files"]) == 1

    def test_batch_status_response_serialization(self):
        """Test BatchStatusResponse can be serialized to dict."""
        response = BatchStatusResponse(
            task_id="task-1",
            status="completed",
            progress=100.0,
            processed=10,
            total=10,
            success=10,
            failed=0,
            errors=[]
        )

        data = response.model_dump()

        assert data["task_id"] == "task-1"
        assert data["status"] == "completed"
        assert data["progress"] == 100.0
        assert data["errors"] == []

    def test_batch_preview_request_from_dict(self):
        """Test BatchPreviewRequest can be created from dict."""
        data = {
            "directory": "/movies",
            "field": "genre",
            "value": "Action",
            "mode": "append"
        }

        request = BatchPreviewRequest(**data)

        assert request.directory == "/movies"
        assert request.field == "genre"
        assert request.value == "Action"
        assert request.mode == "append"
