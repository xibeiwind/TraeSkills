import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class CalendarEvent:
    def __init__(
        self,
        event_id: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = "",
        attendees: List[str] = None,
        reminder_minutes: int = 15
    ):
        self.event_id = event_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.location = location
        self.attendees = attendees or []
        self.reminder_minutes = reminder_minutes

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "description": self.description,
            "location": self.location,
            "attendees": self.attendees,
            "reminder_minutes": self.reminder_minutes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CalendarEvent':
        return cls(
            event_id=data["event_id"],
            title=data["title"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            description=data.get("description", ""),
            location=data.get("location", ""),
            attendees=data.get("attendees", []),
            reminder_minutes=data.get("reminder_minutes", 15)
        )


class CalendarIntegration(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def get_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        pass

    @abstractmethod
    def add_event(self, event: CalendarEvent) -> bool:
        pass

    @abstractmethod
    def update_event(self, event_id: str, event: CalendarEvent) -> bool:
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass


class LocalCalendarIntegration(CalendarIntegration):
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.events_file = os.path.join(self.data_dir, "calendar_events.json")
        self.events: Dict[str, CalendarEvent] = {}
        self._connected = False
        self.load_events()

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def load_events(self):
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.events = {
                        event_id: CalendarEvent.from_dict(event_data)
                        for event_id, event_data in data.items()
                    }
            except Exception as e:
                print(f"Error loading calendar events: {e}")
                self.events = {}

    def save_events(self):
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {event_id: event.to_dict() for event_id, event in self.events.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            print(f"Error saving calendar events: {e}")

    def get_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        return [
            event for event in self.events.values()
            if start_date <= event.start_time <= end_date
        ]

    def get_all_events(self) -> List[CalendarEvent]:
        return list(self.events.values())

    def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        return self.events.get(event_id)

    def add_event(self, event: CalendarEvent) -> bool:
        self.events[event.event_id] = event
        self.save_events()
        return True

    def update_event(self, event_id: str, event: CalendarEvent) -> bool:
        if event_id in self.events:
            self.events[event_id] = event
            self.save_events()
            return True
        return False

    def delete_event(self, event_id: str) -> bool:
        if event_id in self.events:
            del self.events[event_id]
            self.save_events()
            return True
        return False

    def get_upcoming_events(self, hours: int = 24) -> List[CalendarEvent]:
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        return self.get_events(now, end_time)

    def get_events_for_day(self, date: datetime) -> List[CalendarEvent]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        return self.get_events(start_of_day, end_of_day)

    def get_events_for_week(self, start_date: datetime) -> List[CalendarEvent]:
        end_date = start_date + timedelta(days=7)
        return self.get_events(start_date, end_date)

    def get_events_for_month(self, year: int, month: int) -> List[CalendarEvent]:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        return self.get_events(start_date, end_date)

    def search_events(self, query: str) -> List[CalendarEvent]:
        query = query.lower()
        return [
            event for event in self.events.values()
            if query in event.title.lower() or query in event.description.lower()
        ]

    def get_free_time_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        min_duration_minutes: int = 30
    ) -> List[Dict]:
        events = self.get_events(start_date, end_date)
        sorted_events = sorted(events, key=lambda e: e.start_time)
        
        free_slots = []
        current_time = start_date
        
        for event in sorted_events:
            if event.start_time > current_time:
                duration = (event.start_time - current_time).total_seconds() / 60
                if duration >= min_duration_minutes:
                    free_slots.append({
                        "start_time": current_time,
                        "end_time": event.start_time,
                        "duration_minutes": duration
                    })
            current_time = max(current_time, event.end_time)
        
        if end_date > current_time:
            duration = (end_date - current_time).total_seconds() / 60
            if duration >= min_duration_minutes:
                free_slots.append({
                    "start_time": current_time,
                    "end_time": end_date,
                    "duration_minutes": duration
                })
        
        return free_slots

    def create_event_from_task(
        self,
        task_id: str,
        task_title: str,
        task_description: str = "",
        estimated_minutes: int = 60,
        preferred_start_time: Optional[datetime] = None
    ) -> Optional[CalendarEvent]:
        if preferred_start_time:
            start_time = preferred_start_time
        else:
            now = datetime.now()
            start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        end_time = start_time + timedelta(minutes=estimated_minutes)
        
        event_id = f"cal_event_{task_id}_{int(datetime.now().timestamp())}"
        event = CalendarEvent(
            event_id=event_id,
            title=f"任务: {task_title}",
            start_time=start_time,
            end_time=end_time,
            description=task_description,
            reminder_minutes=15
        )
        
        if self.add_event(event):
            return event
        return None

    def get_conflicting_events(self, event: CalendarEvent) -> List[CalendarEvent]:
        conflicting_events = []
        
        for existing_event in self.events.values():
            if existing_event.event_id == event.event_id:
                continue
            
            if (event.start_time < existing_event.end_time and 
                event.end_time > existing_event.start_time):
                conflicting_events.append(existing_event)
        
        return conflicting_events

    def get_calendar_statistics(self) -> Dict:
        events = self.get_all_events()
        total_events = len(events)
        
        now = datetime.now()
        today_events = len(self.get_events_for_day(now))
        week_events = len(self.get_events_for_week(now))
        
        total_duration = sum(
            (event.end_time - event.start_time).total_seconds() / 3600
            for event in events
        )
        
        return {
            "total_events": total_events,
            "today_events": today_events,
            "week_events": week_events,
            "total_duration_hours": total_duration,
            "average_event_duration_hours": total_duration / total_events if total_events > 0 else 0
        }


class CalendarManager:
    def __init__(self):
        self.integrations: Dict[str, CalendarIntegration] = {}
        self.active_integration: Optional[CalendarIntegration] = None

    def add_integration(self, name: str, integration: CalendarIntegration):
        self.integrations[name] = integration

    def remove_integration(self, name: str):
        if name in self.integrations:
            del self.integrations[name]

    def set_active_integration(self, name: str) -> bool:
        if name in self.integrations:
            self.active_integration = self.integrations[name]
            return self.active_integration.connect()
        return False

    def get_active_integration(self) -> Optional[CalendarIntegration]:
        return self.active_integration

    def get_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.get_events(start_date, end_date)
        return []

    def add_event(self, event: CalendarEvent) -> bool:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.add_event(event)
        return False

    def update_event(self, event_id: str, event: CalendarEvent) -> bool:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.update_event(event_id, event)
        return False

    def delete_event(self, event_id: str) -> bool:
        if self.active_integration and self.active_integration.is_connected():
            return self.active_integration.delete_event(event_id)
        return False

    def get_upcoming_events(self, hours: int = 24) -> List[CalendarEvent]:
        if self.active_integration and self.active_integration.is_connected():
            if hasattr(self.active_integration, 'get_upcoming_events'):
                return self.active_integration.get_upcoming_events(hours)
        return []

    def get_free_time_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        min_duration_minutes: int = 30
    ) -> List[Dict]:
        if self.active_integration and self.active_integration.is_connected():
            if hasattr(self.active_integration, 'get_free_time_slots'):
                return self.active_integration.get_free_time_slots(
                    start_date, end_date, min_duration_minutes
                )
        return []
