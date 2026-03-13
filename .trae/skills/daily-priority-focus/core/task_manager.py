import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Task:
    def __init__(
        self,
        task_id: str,
        title: str,
        description: str = "",
        importance: int = 2,
        urgency: int = 2,
        difficulty: int = 2,
        estimated_time: int = 60,
        deadline: Optional[datetime] = None,
        dependencies: List[str] = None,
        tags: List[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.importance = importance
        self.urgency = urgency
        self.difficulty = difficulty
        self.estimated_time = estimated_time
        self.deadline = deadline
        self.dependencies = dependencies or []
        self.tags = tags or []
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.priority_score = 0

    def calculate_priority_score(self, weights: Dict[str, float]) -> float:
        weight_importance = weights.get("importance", 0.30)
        weight_urgency = weights.get("urgency", 0.25)
        weight_difficulty = weights.get("difficulty", 0.20)
        weight_time = weights.get("time", 0.15)
        weight_dependencies = weights.get("dependencies", 0.10)

        normalized_importance = self.importance / 4.0
        normalized_urgency = self.urgency / 4.0
        normalized_difficulty = self.difficulty / 4.0
        normalized_time = min(self.estimated_time / 480.0, 1.0)
        
        urgency_bonus = 0
        if self.deadline:
            time_until_deadline = (self.deadline - datetime.now()).total_seconds() / 3600
            if time_until_deadline <= 2:
                urgency_bonus = 1.0
            elif time_until_deadline <= 24:
                urgency_bonus = 0.5
            elif time_until_deadline <= 72:
                urgency_bonus = 0.25

        dependency_penalty = 0
        if self.dependencies:
            dependency_penalty = 0.2 * len(self.dependencies)

        self.priority_score = (
            normalized_importance * weight_importance +
            (normalized_urgency + urgency_bonus) * weight_urgency +
            normalized_difficulty * weight_difficulty +
            (1 - normalized_time) * weight_time +
            (1 - dependency_penalty) * weight_dependencies
        ) * 100

        return self.priority_score

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "importance": self.importance,
            "urgency": self.urgency,
            "difficulty": self.difficulty,
            "estimated_time": self.estimated_time,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "priority_score": self.priority_score
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            importance=data.get("importance", 2),
            urgency=data.get("urgency", 2),
            difficulty=data.get("difficulty", 2),
            estimated_time=data.get("estimated_time", 60),
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )


class TaskManager:
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.tasks_file = os.path.join(self.data_dir, "tasks.json")
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: Task.from_dict(task_data)
                        for task_id, task_data in data.items()
                    }
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = {}

    def save_tasks(self):
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, task: Task) -> Task:
        self.tasks[task.task_id] = task
        self.save_tasks()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now()
            self.save_tasks()
            return task
        return None

    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            return True
        return False

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        return [task for task in self.tasks.values() if tag in task.tags]

    def get_tasks_by_deadline(self, start_date: datetime, end_date: datetime) -> List[Task]:
        return [
            task for task in self.tasks.values()
            if task.deadline and start_date <= task.deadline <= end_date
        ]

    def get_sorted_tasks(self, weights: Dict[str, float] = None) -> List[Task]:
        weights = weights or {
            "importance": 0.30,
            "urgency": 0.25,
            "difficulty": 0.20,
            "time": 0.15,
            "dependencies": 0.10
        }
        
        tasks = list(self.tasks.values())
        for task in tasks:
            task.calculate_priority_score(weights)
        
        return sorted(tasks, key=lambda t: t.priority_score, reverse=True)

    def get_task_statistics(self) -> Dict:
        total_tasks = len(self.tasks)
        completed_tasks = len(self.get_tasks_by_status(TaskStatus.COMPLETED))
        in_progress_tasks = len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS))
        pending_tasks = len(self.get_tasks_by_status(TaskStatus.PENDING))
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": completion_rate
        }

    def search_tasks(self, query: str) -> List[Task]:
        query = query.lower()
        return [
            task for task in self.tasks.values()
            if query in task.title.lower() or query in task.description.lower()
        ]

    def get_upcoming_tasks(self, hours: int = 24) -> List[Task]:
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        return self.get_tasks_by_deadline(now, end_time)

    def get_overdue_tasks(self) -> List[Task]:
        now = datetime.now()
        return [
            task for task in self.tasks.values()
            if task.deadline and task.deadline < now and task.status != TaskStatus.COMPLETED
        ]
