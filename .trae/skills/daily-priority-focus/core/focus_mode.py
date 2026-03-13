import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, List
from .task_manager import Task, TaskStatus


class FocusSession:
    def __init__(
        self,
        session_id: str,
        task_id: str,
        duration_minutes: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: str = "pending"
    ):
        self.session_id = session_id
        self.task_id = task_id
        self.duration_minutes = duration_minutes
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.paused_duration = 0
        self.pause_start_time: Optional[datetime] = None
        self.breaks_taken = 0
        self.total_pause_time = 0

    def start(self):
        self.start_time = datetime.now()
        self.status = "active"

    def pause(self):
        if self.status == "active":
            self.status = "paused"
            self.pause_start_time = datetime.now()

    def resume(self):
        if self.status == "paused" and self.pause_start_time:
            pause_duration = (datetime.now() - self.pause_start_time).total_seconds() / 60
            self.total_pause_time += pause_duration
            self.pause_start_time = None
            self.status = "active"

    def complete(self):
        self.end_time = datetime.now()
        self.status = "completed"

    def cancel(self):
        self.end_time = datetime.now()
        self.status = "cancelled"

    def get_elapsed_time(self) -> float:
        if not self.start_time:
            return 0.0
        
        end_time = self.end_time or datetime.now()
        elapsed = (end_time - self.start_time).total_seconds() / 60
        return max(0, elapsed - self.total_pause_time)

    def get_remaining_time(self) -> float:
        elapsed = self.get_elapsed_time()
        return max(0, self.duration_minutes - elapsed)

    def get_progress_percentage(self) -> float:
        elapsed = self.get_elapsed_time()
        return min(100, (elapsed / self.duration_minutes) * 100)

    def is_active(self) -> bool:
        return self.status == "active"

    def is_paused(self) -> bool:
        return self.status == "paused"

    def is_completed(self) -> bool:
        return self.status == "completed"

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "duration_minutes": self.duration_minutes,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "paused_duration": self.paused_duration,
            "total_pause_time": self.total_pause_time,
            "breaks_taken": self.breaks_taken,
            "elapsed_time": self.get_elapsed_time(),
            "remaining_time": self.get_remaining_time(),
            "progress_percentage": self.get_progress_percentage()
        }


class FocusMode:
    def __init__(self):
        self.sessions: Dict[str, FocusSession] = {}
        self.current_session: Optional[FocusSession] = None
        self.callbacks: List[Callable] = []
        self.running = False
        self.check_interval = 1
        self.thread: Optional[threading.Thread] = None
        self.break_reminder_interval = 25
        self.break_duration = 5

    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def create_session(
        self,
        task_id: str,
        duration_minutes: int = 60
    ) -> FocusSession:
        session_id = f"session_{task_id}_{int(datetime.now().timestamp())}"
        session = FocusSession(
            session_id=session_id,
            task_id=task_id,
            duration_minutes=duration_minutes
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[FocusSession]:
        return self.sessions.get(session_id)

    def start_session(self, session_id: str) -> Optional[FocusSession]:
        session = self.sessions.get(session_id)
        if session and session.status == "pending":
            if self.current_session and self.current_session.is_active():
                self.current_session.pause()
            
            session.start()
            self.current_session = session
            self._notify_callbacks("session_started", session)
            
            if not self.running:
                self.start()
            
            return session
        return None

    def pause_session(self, session_id: str = None) -> Optional[FocusSession]:
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session
        
        if session and session.is_active():
            session.pause()
            self._notify_callbacks("session_paused", session)
            return session
        return None

    def resume_session(self, session_id: str = None) -> Optional[FocusSession]:
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session
        
        if session and session.is_paused():
            session.resume()
            self.current_session = session
            self._notify_callbacks("session_resumed", session)
            return session
        return None

    def complete_session(self, session_id: str = None) -> Optional[FocusSession]:
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session
        
        if session and (session.is_active() or session.is_paused()):
            session.complete()
            self._notify_callbacks("session_completed", session)
            
            if self.current_session == session:
                self.current_session = None
            
            return session
        return None

    def cancel_session(self, session_id: str = None) -> Optional[FocusSession]:
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session
        
        if session and (session.is_active() or session.is_paused()):
            session.cancel()
            self._notify_callbacks("session_cancelled", session)
            
            if self.current_session == session:
                self.current_session = None
            
            return session
        return None

    def take_break(self, session_id: str = None) -> Optional[FocusSession]:
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session
        
        if session and session.is_active():
            session.pause()
            session.breaks_taken += 1
            self._notify_callbacks("break_started", session)
            return session
        return None

    def end_break(self, session_id: str = None) -> Optional[FocusSession]:
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session
        
        if session and session.is_paused():
            session.resume()
            self._notify_callbacks("break_ended", session)
            return session
        return None

    def get_current_session(self) -> Optional[FocusSession]:
        return self.current_session

    def get_session_history(self, task_id: str = None) -> List[FocusSession]:
        sessions = list(self.sessions.values())
        if task_id:
            sessions = [s for s in sessions if s.task_id == task_id]
        return sorted(sessions, key=lambda s: s.start_time or datetime.min, reverse=True)

    def get_session_statistics(self) -> Dict:
        total_sessions = len(self.sessions)
        completed_sessions = len([s for s in self.sessions.values() if s.is_completed()])
        cancelled_sessions = len([s for s in self.sessions.values() if s.status == "cancelled"])
        
        total_focus_time = sum(s.get_elapsed_time() for s in self.sessions.values())
        total_pause_time = sum(s.total_pause_time for s in self.sessions.values())
        
        average_session_duration = total_focus_time / completed_sessions if completed_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "cancelled_sessions": cancelled_sessions,
            "active_sessions": len([s for s in self.sessions.values() if s.is_active()]),
            "paused_sessions": len([s for s in self.sessions.values() if s.is_paused()]),
            "total_focus_time": total_focus_time,
            "total_pause_time": total_pause_time,
            "average_session_duration": average_session_duration,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        }

    def _notify_callbacks(self, event_type: str, session: FocusSession):
        for callback in self.callbacks:
            try:
                callback(event_type, session)
            except Exception as e:
                print(f"Error in focus mode callback: {e}")

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
                self._check_sessions()
            except Exception as e:
                print(f"Error checking focus sessions: {e}")
            time.sleep(self.check_interval)

    def _check_sessions(self):
        if self.current_session and self.current_session.is_active():
            elapsed = self.current_session.get_elapsed_time()
            
            if elapsed >= self.current_session.duration_minutes:
                self.complete_session()
            elif elapsed > 0 and int(elapsed) % self.break_reminder_interval == 0 and int(elapsed) > 0:
                if not hasattr(self, '_last_reminder_time') or \
                   (datetime.now() - self._last_reminder_time).total_seconds() >= self.break_reminder_interval * 60:
                    self._notify_callbacks("break_reminder", self.current_session)
                    self._last_reminder_time = datetime.now()

    def set_break_settings(self, reminder_interval: int, break_duration: int):
        self.break_reminder_interval = reminder_interval
        self.break_duration = break_duration

    def get_focus_recommendations(self, tasks: List[Task]) -> List[Dict]:
        recommendations = []
        
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        sorted_tasks = sorted(pending_tasks, key=lambda t: t.priority_score, reverse=True)
        
        for task in sorted_tasks[:5]:
            recommended_duration = min(task.estimated_time, 90)
            recommendations.append({
                "task": task,
                "recommended_duration": recommended_duration,
                "reason": f"High priority task with score {task.priority_score:.1f}",
                "estimated_completion": datetime.now() + timedelta(minutes=recommended_duration)
            })
        
        return recommendations

    def get_daily_focus_plan(self, tasks: List[Task]) -> Dict:
        focus_sessions = []
        current_time = datetime.now()
        end_of_day = current_time.replace(hour=18, minute=0, second=0, microsecond=0)
        
        available_time = (end_of_day - current_time).total_seconds() / 60
        
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        sorted_tasks = sorted(pending_tasks, key=lambda t: t.priority_score, reverse=True)
        
        total_planned_time = 0
        for task in sorted_tasks:
            if total_planned_time >= available_time:
                break
            
            session_duration = min(task.estimated_time, 90)
            if total_planned_time + session_duration <= available_time:
                focus_sessions.append({
                    "task": task,
                    "start_time": current_time + timedelta(minutes=total_planned_time),
                    "duration": session_duration,
                    "end_time": current_time + timedelta(minutes=total_planned_time + session_duration)
                })
                total_planned_time += session_duration + self.break_duration
        
        return {
            "sessions": focus_sessions,
            "total_focus_time": total_planned_time,
            "available_time": available_time,
            "utilization_rate": (total_planned_time / available_time * 100) if available_time > 0 else 0
        }
