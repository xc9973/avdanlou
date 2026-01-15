"""Batch editing data models."""
from datetime import datetime
from dataclasses import dataclass
from typing import List
from enum import Enum

from pydantic import BaseModel


class TaskStatus(Enum):
    """Batch task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BatchTask:
    """Batch task data model for tracking batch operations."""
    task_id: str
    status: TaskStatus
    total_files: int
    processed_files: int
    success_count: int
    failed_count: int
    errors: List[str]
    created_at: datetime
    field: str
    value: str
    mode: str
    directory: str

    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if self.total_files == 0:
            return 0.0
        return self.processed_files / self.total_files * 100


class BatchPreviewRequest(BaseModel):
    """Batch preview request model."""
    directory: str
    field: str
    value: str
    mode: str = "overwrite"


class BatchApplyRequest(BaseModel):
    """Batch apply request model."""
    task_id: str
    confirmed: bool = True


class BatchPreviewResponse(BaseModel):
    """Batch preview response model."""
    task_id: str
    total_files: int
    sample_files: List[dict]


class BatchStatusResponse(BaseModel):
    """Batch status response model."""
    task_id: str
    status: str
    progress: float
    processed: int
    total: int
    success: int
    failed: int
    errors: List[str]
