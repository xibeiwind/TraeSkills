import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class TodoItem:
    def __init__(
        self,
        item_id: str,
        title: str,
        description: str = "",
        completed: bool = False,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: List[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.item_id = item_id
        self.title = title
        self.description = description
        self.completed = completed
        self.priority = priority
        self.due_date = due_date
        self.tags = tags or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> Dict:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        return cls(
            item_id=data["item_id"],
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
            priority=data.get("priority", "medium"),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )


class TodoAppIntegration(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def get_items(self) -> List[TodoItem]:
        pass

    @abstractmethod
    def add_item(self, item: TodoItem) -> bool:
        pass

    @abstractmethod
    def update_item(self, item_id: str, item: TodoItem) -> bool:
        pass

    @abstractmethod
    def delete_item(self, item_id: str) -> bool:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass


class LocalTodoIntegration(TodoAppIntegration):
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.items_file = os.path.join(self.data_dir, "todo_items.json")
        self.items: Dict[str, TodoItem] = {}
        self._connected = False
        self.load_items()

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def load_items(self):
        if os.path.exists(self.items_file):
            try:
                with open(self.items_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = {
                        item_id: TodoItem.from_dict(item_data)
                        for item_id, item_data in data.items()
                    }
            except Exception as e:
                print(f"Error loading todo items: {e}")
                self.items = {}

    def save_items(self):
        try:
            with open(self.items_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {item_id: item.to_dict() for item_id, item in self.items.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            print(f"Error saving todo items: {e}")

    def get_items(self) -> List[TodoItem]:
        return list(self.items.values())

    def get_item(self, item_id: str) -> Optional[TodoItem]:
        return self.items.get(item_id)

    def add_item(self, item: TodoItem) -> bool:
        self.items[item.item_id] = item
        self.save_items()
        return True

    def update_item(self, item_id: str, item: TodoItem) -> bool:
        if item_id in self.items:
            self.items[item_id] = item
            self.save_items()
            return True
        return False

    def delete_item(self, item_id: str) -> bool:
        if item_id in self.items:
            del self.items[item_id]
            self.save_items()
            return True
        return False

    def get_active_items(self) -> List[TodoItem]:
        return [item for item in self.items.values() if not item.completed]

    def get_completed_items(self) -> List[TodoItem]:
        return [item for item in self.items.values() if item.completed]

    def get_items_by_priority(self, priority: str) -> List[TodoItem]:
        return [item for item in self.items.values() if item.priority == priority]

    def get_items_by_tag(self, tag: str) -> List[TodoItem]:
        return [item for item in self.items.values() if tag in item.tags]

    def get_overdue_items(self) -> List[TodoItem]:
        now = datetime.now()
        return [
            item for item in self.items.values()
            if item.due_date and item.due_date < now and not item.completed
        ]

    def get_due_today_items(self) -> List[TodoItem]:
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day.replace(hour=23, minute=59, second=59)
        
        return [
            item for item in self.items.values()
            if item.due_date and start_of_day <= item.due_date <= end_of_day
        ]

    def search_items(self, query: str) -> List[TodoItem]:
        query = query.lower()
        return [
            item for item in self.items.values()
            if query in item.title.lower() or query in item.description.lower()
        ]

    def toggle_complete(self, item_id: str) -> Optional[TodoItem]:
        item = self.items.get(item_id)
        if item:
            item.completed = not item.completed
            item.updated_at = datetime.now()
            self.save_items()
            return item
        return None

    def mark_complete(self, item_id: str) -> Optional[TodoItem]:
        item = self.items.get(item_id)
        if item:
            item.completed = True
            item.updated_at = datetime.now()
            self.save_items()
            return item
        return None

    def mark_incomplete(self, item_id: str) -> Optional[TodoItem]:
        item = self.items.get(item_id)
        if item:
            item.completed = False
            item.updated_at = datetime.now()
            self.save_items()
            return item
        return None

    def get_statistics(self) -> Dict:
        total_items = len(self.items)
        completed_items = len(self.get_completed_items())
        active_items = len(self.get_active_items())
        
        priority_distribution = {}
        for item in self.items.values():
            priority = item.priority
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        return {
            "total_items": total_items,
            "completed_items": completed_items,
            "active_items": active_items,
            "completion_rate": (completed_items / total_items * 100) if total_items > 0 else 0,
            "priority_distribution": priority_distribution
        }


class TodoistIntegration(TodoAppIntegration):
    def __init__(self, api_token: str = None):
        self.api_token = api_token
        self._connected = False
        self.base_url = "https://api.todoist.com/rest/v2"

    def connect(self) -> bool:
        if self.api_token:
            self._connected = True
            return True
        return False

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def get_items(self) -> List[TodoItem]:
        if not self._connected:
            return []
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(f"{self.base_url}/tasks", headers=headers)
            
            if response.status_code == 200:
                tasks = response.json()
                return [
                    TodoItem(
                        item_id=str(task["id"]),
                        title=task["content"],
                        description=task.get("description", ""),
                        completed=task.get("completed", False),
                        priority=self._convert_priority(task.get("priority", 4)),
                        due_date=datetime.fromisoformat(task["due"]["datetime"]) if task.get("due") else None
                    )
                    for task in tasks
                ]
        except Exception as e:
            print(f"Error fetching Todoist items: {e}")
        
        return []

    def add_item(self, item: TodoItem) -> bool:
        if not self._connected:
            return False
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            data = {
                "content": item.title,
                "description": item.description,
                "priority": self._convert_priority_to_todoist(item.priority)
            }
            if item.due_date:
                data["due_string"] = item.due_date.isoformat()
            
            response = requests.post(f"{self.base_url}/tasks", headers=headers, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error adding Todoist item: {e}")
            return False

    def update_item(self, item_id: str, item: TodoItem) -> bool:
        if not self._connected:
            return False
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            data = {
                "content": item.title,
                "description": item.description,
                "priority": self._convert_priority_to_todoist(item.priority)
            }
            if item.due_date:
                data["due_string"] = item.due_date.isoformat()
            
            response = requests.post(f"{self.base_url}/tasks/{item_id}", headers=headers, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating Todoist item: {e}")
            return False

    def delete_item(self, item_id: str) -> bool:
        if not self._connected:
            return False
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
            response = requests.delete(f"{self.base_url}/tasks/{item_id}", headers=headers)
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting Todoist item: {e}")
            return False

    def _convert_priority(self, todoist_priority: int) -> str:
        priority_map = {
            4: "high",
            3: "medium",
            2: "low",
            1: "low"
        }
        return priority_map.get(todoist_priority, "medium")

    def _convert_priority_to_todoist(self, priority: str) -> int:
        priority_map = {
            "high": 4,
            "medium": 3,
            "low": 2
        }
        return priority_map.get(priority, 3)


class TodoManager:
    def __init__(self):
        self.integrations: Dict[str, TodoAppIntegration] = {}
        self.active_integration: Optional[TodoAppIntegration] = None

    def add_integration(self, name: str, integration: TodoAppIntegration):
        self.integrations[name] = integration

    def remove_integration(self, name: str):
        if name in self.integrations:
            del self.integrations[name]

    def set_active_integration(self, name: str) -> bool:
        if name in self.integrations:
            self.active_integration = self.integrations[name]
            return self.active_integration.connect()
        return False

    def get_active_integration(self) -> Optional[TodoAppIntegration]:
        return self.active_integration

    def get_items(self) -> List[TodoItem]:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.get_items()
        return []

    def add_item(self, item: TodoItem) -> bool:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.add_item(item)
        return False

    def update_item(self, item_id: str, item: TodoItem) -> bool:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.update_item(item_id, item)
        return False

    def delete_item(self, item_id: str) -> bool:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.delete_item(item_id)
        return False

    def sync_from_todo_to_tasks(self, todo_items: List[TodoItem], task_manager) -> int:
        synced_count = 0
        for todo_item in todo_items:
            from ..core.task_manager import Task, TaskStatus
            
            existing_task = task_manager.get_task(todo_item.item_id)
            if not existing_task:
                task = Task(
                    task_id=todo_item.item_id,
                    title=todo_item.title,
                    description=todo_item.description,
                    status=TaskStatus.COMPLETED if todo_item.completed else TaskStatus.PENDING,
                    tags=todo_item.tags
                )
                task_manager.add_task(task)
                synced_count += 1
        
        return synced_count

    def sync_from_tasks_to_todo(self, tasks, todo_integration: TodoAppIntegration) -> int:
        synced_count = 0
        for task in tasks:
            todo_item = TodoItem(
                item_id=task.task_id,
                title=task.title,
                description=task.description,
                completed=task.status.value == "completed",
                priority=self._convert_task_priority_to_todo(task.priority_score),
                due_date=task.deadline,
                tags=task.tags
            )
            if todo_integration.add_item(todo_item):
                synced_count += 1
        
        return synced_count

    def _convert_task_priority_to_todo(self, priority_score: float) -> str:
        if priority_score >= 75:
            return "high"
        elif priority_score >= 50:
            return "medium"
        else:
            return "low"
