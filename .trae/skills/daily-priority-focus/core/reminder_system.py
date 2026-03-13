import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional
from .task_manager import Task, TaskStatus


class Reminder:
    def __init__(
        self,
        reminder_id: str,
        task_id: str,
        reminder_time: datetime,
        message: str = "",
        reminder_type: str = "deadline",
        recurring: bool = False,
        recurring_interval: Optional[timedelta] = None
    ):
        self.reminder_id = reminder_id
        self.task_id = task_id
        self.reminder_time = reminder_time
        self.message = message
        self.reminder_type = reminder_type
        self.recurring = recurring
        self.recurring_interval = recurring_interval
        self.is_active = True
        self.triggered_count = 0

    def should_trigger(self) -> bool:
        if not self.is_active:
            return False
        return datetime.now() >= self.reminder_time

    def trigger(self) -> bool:
        if self.should_trigger():
            self.triggered_count += 1
            if self.recurring and self.recurring_interval:
                self.reminder_time = datetime.now() + self.recurring_interval
            else:
                self.is_active = False
            return True
        return False

    def to_dict(self) -> Dict:
        return {
            "reminder_id": self.reminder_id,
            "task_id": self.task_id,
            "reminder_time": self.reminder_time.isoformat(),
            "message": self.message,
            "reminder_type": self.reminder_type,
            "recurring": self.recurring,
            "recurring_interval": self.recurring_interval.total_seconds() if self.recurring_interval else None,
            "is_active": self.is_active,
            "triggered_count": self.triggered_count
        }


class ReminderSystem:
    def __init__(self):
        self.reminders: Dict[str, Reminder] = {}
        self.callbacks: List[Callable] = []
        self.running = False
        self.check_interval = 60
        self.thread: Optional[threading.Thread] = None

    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def add_reminder(self, reminder: Reminder) -> Reminder:
        self.reminders[reminder.reminder_id] = reminder
        return reminder

    def create_reminder(
        self,
        task_id: str,
        reminder_time: datetime,
        message: str = "",
        reminder_type: str = "deadline",
        recurring: bool = False,
        recurring_interval: Optional[timedelta] = None
    ) -> Reminder:
        reminder_id = f"reminder_{task_id}_{int(datetime.now().timestamp())}"
        reminder = Reminder(
            reminder_id=reminder_id,
            task_id=task_id,
            reminder_time=reminder_time,
            message=message,
            reminder_type=reminder_type,
            recurring=recurring,
            recurring_interval=recurring_interval
        )
        return self.add_reminder(reminder)

    def get_reminder(self, reminder_id: str) -> Optional[Reminder]:
        return self.reminders.get(reminder_id)

    def get_task_reminders(self, task_id: str) -> List[Reminder]:
        return [r for r in self.reminders.values() if r.task_id == task_id]

    def update_reminder(self, reminder_id: str, **kwargs) -> Optional[Reminder]:
        reminder = self.reminders.get(reminder_id)
        if reminder:
            for key, value in kwargs.items():
                if hasattr(reminder, key):
                    setattr(reminder, key, value)
            return reminder
        return None

    def delete_reminder(self, reminder_id: str) -> bool:
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            return True
        return False

    def delete_task_reminders(self, task_id: str) -> int:
        to_delete = [rid for rid, r in self.reminders.items() if r.task_id == task_id]
        for rid in to_delete:
            del self.reminders[rid]
        return len(to_delete)

    def get_active_reminders(self) -> List[Reminder]:
        return [r for r in self.reminders.values() if r.is_active]

    def get_upcoming_reminders(self, hours: int = 24) -> List[Reminder]:
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        return [
            r for r in self.reminders.values()
            if r.is_active and now <= r.reminder_time <= end_time
        ]

    def check_reminders(self) -> List[Reminder]:
        triggered_reminders = []
        for reminder in self.reminders.values():
            if reminder.trigger():
                triggered_reminders.append(reminder)
        
        for reminder in triggered_reminders:
            self._notify_callbacks(reminder)
        
        return triggered_reminders

    def _notify_callbacks(self, reminder: Reminder):
        for callback in self.callbacks:
            try:
                callback(reminder)
            except Exception as e:
                print(f"Error in reminder callback: {e}")

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def _run_loop(self):
        while self.running:
            try:
                self.check_reminders()
            except Exception as e:
                print(f"Error checking reminders: {e}")
            time.sleep(self.check_interval)

    def create_task_reminders(
        self,
        task: Task,
        reminder_times: List[timedelta] = None
    ) -> List[Reminder]:
        if not task.deadline:
            return []

        reminder_times = reminder_times or [
            timedelta(hours=1),
            timedelta(hours=24),
            timedelta(days=3)
        ]

        reminders = []
        for offset in reminder_times:
            reminder_time = task.deadline - offset
            if reminder_time > datetime.now():
                message = f"Task '{task.title}' is due in {offset}"
                reminder = self.create_reminder(
                    task_id=task.task_id,
                    reminder_time=reminder_time,
                    message=message,
                    reminder_type="deadline"
                )
                reminders.append(reminder)

        return reminders

    def create_start_reminder(self, task: Task, start_time: datetime) -> Reminder:
        message = f"Time to start working on: {task.title}"
        return self.create_reminder(
            task_id=task.task_id,
            reminder_time=start_time,
            message=message,
            reminder_type="start"
        )

    def create_recurring_reminder(
        self,
        task_id: str,
        start_time: datetime,
        interval: timedelta,
        message: str = ""
    ) -> Reminder:
        return self.create_reminder(
            task_id=task_id,
            reminder_time=start_time,
            message=message,
            reminder_type="recurring",
            recurring=True,
            recurring_interval=interval
        )

    def get_reminder_statistics(self) -> Dict:
        total_reminders = len(self.reminders)
        active_reminders = len(self.get_active_reminders())
        total_triggered = sum(r.triggered_count for r in self.reminders.values())

        type_distribution = {}
        for reminder in self.reminders.values():
            reminder_type = reminder.reminder_type
            type_distribution[reminder_type] = type_distribution.get(reminder_type, 0) + 1

        return {
            "total_reminders": total_reminders,
            "active_reminders": active_reminders,
            "inactive_reminders": total_reminders - active_reminders,
            "total_triggered": total_triggered,
            "type_distribution": type_distribution
        }

    def cleanup_old_reminders(self, days: int = 30) -> int:
        cutoff_time = datetime.now() - timedelta(days=days)
        to_delete = [
            rid for rid, r in self.reminders.items()
            if not r.is_active and r.reminder_time < cutoff_time
        ]
        
        for rid in to_delete:
            del self.reminders[rid]
        
        return len(to_delete)
