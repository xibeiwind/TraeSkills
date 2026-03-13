"""
Daily Priority Focus - 每日工作优先级聚焦技能

这是一个智能的任务管理工具，帮助用户聚焦每日工作优先级。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .core.task_manager import TaskManager, Task, TaskStatus
from .core.priority_algorithm import PriorityAlgorithm
from .core.reminder_system import ReminderSystem, Reminder
from .core.focus_mode import FocusMode, FocusSession
from .ui.cli import CLIInterface
from .ui.gui import GUIInterface
from .ui.voice import VoiceInterface
from .integrations.calendar import CalendarManager, LocalCalendarIntegration, CalendarEvent
from .integrations.todo_apps import TodoManager, LocalTodoIntegration, TodoItem
from .config.settings import SettingsManager, Settings
from .config.templates import (
    TaskTemplates, PriorityPresets, FocusSessionTemplates,
    ReminderTemplates, WorkflowTemplates
)
from .utils.display import (
    TaskDisplayFormatter, ProgressDisplayFormatter,
    CalendarDisplayFormatter, RecommendationDisplayFormatter
)
from .utils.analytics import (
    TaskAnalytics, FocusAnalytics, ProductivityReport, InsightsGenerator
)


__version__ = "1.0.0"
__author__ = "Daily Priority Focus Team"
__description__ = "智能任务管理工具，帮助您聚焦每日工作优先级"


class DailyPriorityFocus:
    """Daily Priority Focus 主类"""

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "..", "..", "data")
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.settings_manager = SettingsManager(self.config_dir)
        self.task_manager = TaskManager(self.config_dir)
        self.priority_algorithm = PriorityAlgorithm(
            self.settings_manager.get_priority_weights()
        )
        self.reminder_system = ReminderSystem()
        self.focus_mode = FocusMode()
        self.calendar_manager = CalendarManager()
        self.todo_manager = TodoManager()
        
        self._setup_integrations()
        self._setup_callbacks()

    def _setup_integrations(self):
        """设置集成"""
        calendar_integration = LocalCalendarIntegration(self.config_dir)
        self.calendar_manager.add_integration("local", calendar_integration)
        self.calendar_manager.set_active_integration("local")
        
        todo_integration = LocalTodoIntegration(self.config_dir)
        self.todo_manager.add_integration("local", todo_integration)
        self.todo_manager.set_active_integration("local")

    def _setup_callbacks(self):
        """设置回调函数"""
        self.reminder_system.add_callback(self._on_reminder_triggered)
        self.focus_mode.add_callback(self._on_focus_event)

    def _on_reminder_triggered(self, reminder: Reminder):
        """提醒触发回调"""
        print(f"提醒: {reminder.message}")

    def _on_focus_event(self, event_type: str, session: FocusSession):
        """专注事件回调"""
        print(f"专注事件: {event_type}")

    def get_settings(self) -> Settings:
        """获取设置"""
        return self.settings_manager.get_settings()

    def update_settings(self, **kwargs):
        """更新设置"""
        self.settings_manager.update_settings(**kwargs)

    def add_task(self, task: Task) -> Task:
        """添加任务"""
        return self.task_manager.add_task(task)

    def get_task(self, task_id: str):
        """获取任务"""
        return self.task_manager.get_task(task_id)

    def update_task(self, task_id: str, **kwargs):
        """更新任务"""
        return self.task_manager.update_task(task_id, **kwargs)

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        return self.task_manager.delete_task(task_id)

    def get_all_tasks(self):
        """获取所有任务"""
        return self.task_manager.get_all_tasks()

    def get_sorted_tasks(self):
        """获取排序后的任务"""
        return self.task_manager.get_sorted_tasks(self.priority_algorithm.weights)

    def start_focus_mode(self, task_id: str, duration_minutes: int = 60):
        """开始专注模式"""
        session = self.focus_mode.create_session(task_id, duration_minutes)
        return self.focus_mode.start_session(session.session_id)

    def pause_focus_mode(self):
        """暂停专注模式"""
        return self.focus_mode.pause_session()

    def resume_focus_mode(self):
        """恢复专注模式"""
        return self.focus_mode.resume_session()

    def complete_focus_mode(self):
        """完成专注模式"""
        return self.focus_mode.complete_session()

    def get_task_statistics(self):
        """获取任务统计"""
        return self.task_manager.get_task_statistics()

    def get_focus_statistics(self):
        """获取专注统计"""
        return self.focus_mode.get_session_statistics()

    def generate_daily_report(self):
        """生成每日报告"""
        tasks = self.get_all_tasks()
        sessions = self.focus_mode.get_session_history()
        return ProductivityReport.generate_daily_report(tasks, sessions)

    def generate_weekly_report(self):
        """生成周报告"""
        tasks = self.get_all_tasks()
        sessions = self.focus_mode.get_session_history()
        return ProductivityReport.generate_weekly_report(tasks, sessions)

    def generate_insights(self):
        """生成洞察"""
        tasks = self.get_all_tasks()
        sessions = self.focus_mode.get_session_history()
        
        task_insights = InsightsGenerator.generate_task_insights(tasks)
        focus_insights = InsightsGenerator.generate_focus_insights(sessions)
        recommendations = InsightsGenerator.generate_productivity_recommendations(tasks, sessions)
        
        return {
            "task_insights": task_insights,
            "focus_insights": focus_insights,
            "recommendations": recommendations
        }

    def run_cli(self, args=None):
        """运行命令行界面"""
        cli = CLIInterface(
            self.task_manager,
            self.priority_algorithm,
            self.reminder_system,
            self.focus_mode
        )
        cli.run(args)

    def run_gui(self):
        """运行图形界面"""
        gui = GUIInterface(
            self.task_manager,
            self.priority_algorithm,
            self.reminder_system,
            self.focus_mode
        )
        gui.run()

    def run_voice(self):
        """运行语音界面"""
        voice = VoiceInterface(
            self.task_manager,
            self.priority_algorithm
        )
        voice.start()

    def start_reminder_system(self):
        """启动提醒系统"""
        self.reminder_system.start()

    def stop_reminder_system(self):
        """停止提醒系统"""
        self.reminder_system.stop()

    def sync_with_calendar(self):
        """与日历同步"""
        if self.calendar_manager.get_active_integration():
            events = self.calendar_manager.get_upcoming_events(hours=24)
            synced_count = 0
            for event in events:
                task = Task(
                    task_id=f"cal_{event.event_id}",
                    title=event.title,
                    description=event.description,
                    deadline=event.start_time
                )
                if not self.task_manager.get_task(task.task_id):
                    self.task_manager.add_task(task)
                    synced_count += 1
            return synced_count
        return 0

    def sync_with_todo(self):
        """与待办事项同步"""
        if self.todo_manager.get_active_integration():
            todo_items = self.todo_manager.get_items()
            synced_count = self.todo_manager.sync_from_todo_to_tasks(
                todo_items, self.task_manager
            )
            return synced_count
        return 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Priority Focus - 每日工作优先级聚焦工具")
    parser.add_argument("--interface", "-i", choices=["cli", "gui", "voice"], 
                       default="cli", help="选择界面类型")
    parser.add_argument("--config-dir", help="配置目录路径")
    
    args = parser.parse_args()
    
    dpf = DailyPriorityFocus(args.config_dir)
    
    if args.interface == "cli":
        dpf.run_cli()
    elif args.interface == "gui":
        dpf.run_gui()
    elif args.interface == "voice":
        dpf.run_voice()


if __name__ == "__main__":
    main()
