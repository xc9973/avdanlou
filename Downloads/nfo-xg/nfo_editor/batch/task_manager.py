"""Task manager for batch editing operations."""
import threading
from datetime import datetime, timedelta
from typing import List, Optional

from nfo_editor.batch.models import BatchTask


class TaskManager:
    """Singleton manager for batch tasks with thread-safe operations."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Implement thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tasks = {}
                    cls._instance._TTL_SECONDS = 1800  # 30 minutes
        return cls._instance

    def add(self, task: BatchTask) -> None:
        """Add a task to the manager.

        Args:
            task: The BatchTask to add.
        """
        self._tasks[task.task_id] = task

    def get(self, task_id: str) -> Optional[BatchTask]:
        """Get a task by ID.

        Args:
            task_id: The task ID to retrieve.

        Returns:
            The BatchTask if found, None otherwise.
        """
        return self._tasks.get(task_id)

    def delete(self, task_id: str) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID to delete.

        Returns:
            True if the task was deleted, False if it didn't exist.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def list_all(self) -> List[BatchTask]:
        """List all tasks.

        Returns:
            A list of all BatchTask objects.
        """
        return list(self._tasks.values())

    def cleanup_expired(self) -> int:
        """Clean up expired tasks based on TTL.

        Tasks are considered expired if they were created more than
        _TTL_SECONDS seconds ago.

        Returns:
            The number of tasks that were cleaned up.
        """
        expired_threshold = datetime.now() - timedelta(seconds=self._TTL_SECONDS)
        expired_ids = [
            task_id
            for task_id, task in self._tasks.items()
            if task.created_at < expired_threshold
        ]

        for task_id in expired_ids:
            del self._tasks[task_id]

        return len(expired_ids)
