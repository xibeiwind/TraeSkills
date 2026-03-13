from typing import List, Dict, Optional
from datetime import datetime
from ..core.task_manager import Task, TaskStatus


class TaskDisplayFormatter:
    """任务显示格式化工具"""

    @staticmethod
    def format_task_list(tasks: List[Task], limit: Optional[int] = None) -> str:
        """格式化任务列表为文本"""
        if limit:
            tasks = tasks[:limit]
        
        if not tasks:
            return "没有任务"
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"{'ID':<12} {'标题':<30} {'优先级':<8} {'状态':<12} {'截止日期'}")
        lines.append("=" * 80)
        
        for task in tasks:
            status_icon = TaskDisplayFormatter._get_status_icon(task.status)
            deadline_str = task.deadline.strftime('%m-%d %H:%M') if task.deadline else "-"
            
            lines.append(
                f"{task.task_id:<12} {task.title[:28]:<30} "
                f"{task.priority_score:>6.1f} {status_icon} {task.status.value:<10} "
                f"{deadline_str}"
            )
        
        return "\n".join(lines)

    @staticmethod
    def format_task_detail(task: Task) -> str:
        """格式化任务详情为文本"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"任务详情: {task.title}")
        lines.append("=" * 60)
        lines.append(f"ID: {task.task_id}")
        lines.append(f"描述: {task.description or '无'}")
        lines.append(f"重要性: {task.importance}/4")
        lines.append(f"紧急性: {task.urgency}/4")
        lines.append(f"难度: {task.difficulty}/4")
        lines.append(f"预计时间: {task.estimated_time} 分钟")
        lines.append(f"截止日期: {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else '无'}")
        lines.append(f"状态: {task.status.value}")
        lines.append(f"标签: {', '.join(task.tags) if task.tags else '无'}")
        lines.append(f"优先级评分: {task.priority_score:.1f}")
        lines.append(f"创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"更新时间: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(lines)

    @staticmethod
    def format_task_timeline(tasks: List[Task]) -> str:
        """格式化任务时间线为文本"""
        tasks_with_deadline = [t for t in tasks if t.deadline]
        sorted_tasks = sorted(tasks_with_deadline, key=lambda t: t.deadline)
        
        if not sorted_tasks:
            return "没有带截止日期的任务"
        
        lines = []
        lines.append("=" * 60)
        lines.append("任务时间线")
        lines.append("=" * 60)
        
        for task in sorted_tasks:
            lines.append(f"{task.deadline.strftime('%Y-%m-%d %H:%M')} | {task.title}")
        
        return "\n".join(lines)

    @staticmethod
    def format_task_matrix(matrix: Dict[str, List[Task]]) -> str:
        """格式化重要紧急矩阵为文本"""
        lines = []
        lines.append("=" * 80)
        lines.append("重要紧急矩阵")
        lines.append("=" * 80)
        
        categories = {
            "important_urgent": "【重要且紧急】",
            "important_not_urgent": "【重要但不紧急】",
            "not_important_urgent": "【不重要但紧急】",
            "not_important_not_urgent": "【不重要不紧急】"
        }
        
        for key, category_name in categories.items():
            tasks = matrix.get(key, [])
            if tasks:
                lines.append(f"\n{category_name}")
                for task in tasks[:5]:
                    lines.append(f"  • {task.title} (优先级: {task.priority_score:.1f})")
        
        return "\n".join(lines)

    @staticmethod
    def format_task_statistics(stats: Dict) -> str:
        """格式化任务统计为文本"""
        lines = []
        lines.append("\n=== 任务统计 ===")
        lines.append(f"总任务数: {stats['total_tasks']}")
        lines.append(f"已完成: {stats['completed_tasks']}")
        lines.append(f"进行中: {stats['in_progress_tasks']}")
        lines.append(f"待处理: {stats['pending_tasks']}")
        lines.append(f"完成率: {stats['completion_rate']:.1f}%")
        
        return "\n".join(lines)

    @staticmethod
    def format_focus_statistics(stats: Dict) -> str:
        """格式化专注统计为文本"""
        lines = []
        lines.append("\n=== 专注统计 ===")
        lines.append(f"总专注会话: {stats['total_sessions']}")
        lines.append(f"总专注时间: {stats['total_focus_time']:.1f} 分钟")
        lines.append(f"平均会话时长: {stats['average_session_duration']:.1f} 分钟")
        lines.append(f"完成率: {stats['completion_rate']:.1f}%")
        
        return "\n".join(lines)

    @staticmethod
    def _get_status_icon(status: TaskStatus) -> str:
        """获取状态图标"""
        icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.CANCELLED: "❌"
        }
        return icons.get(status, "❓")

    @staticmethod
    def format_priority_score(score: float) -> str:
        """格式化优先级分数"""
        if score >= 75:
            return f"🔴 {score:.1f} (高)"
        elif score >= 50:
            return f"🟡 {score:.1f} (中)"
        else:
            return f"🟢 {score:.1f} (低)"

    @staticmethod
    def format_duration(minutes: int) -> str:
        """格式化时长"""
        if minutes < 60:
            return f"{minutes}分钟"
        elif minutes < 1440:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}小时{mins}分钟" if mins > 0 else f"{hours}小时"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            return f"{days}天{hours}小时" if hours > 0 else f"{days}天"

    @staticmethod
    def format_time_remaining(deadline: datetime) -> str:
        """格式化剩余时间"""
        now = datetime.now()
        delta = deadline - now
        
        if delta.total_seconds() < 0:
            return "已过期"
        
        total_minutes = int(delta.total_seconds() / 60)
        return TaskDisplayFormatter.format_duration(total_minutes)


class ProgressDisplayFormatter:
    """进度显示格式化工具"""

    @staticmethod
    def format_progress_bar(progress: float, width: int = 50) -> str:
        """格式化进度条"""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {progress:.1f}%"

    @staticmethod
    def format_session_progress(session) -> str:
        """格式化会话进度"""
        elapsed = session.get_elapsed_time()
        remaining = session.get_remaining_time()
        progress = session.get_progress_percentage()
        
        lines = []
        lines.append(f"会话进度: {ProgressDisplayFormatter.format_progress_bar(progress)}")
        lines.append(f"已用时间: {elapsed:.1f} 分钟")
        lines.append(f"剩余时间: {remaining:.1f} 分钟")
        
        return "\n".join(lines)

    @staticmethod
    def format_daily_progress(completed: int, total: int) -> str:
        """格式化每日进度"""
        if total == 0:
            progress = 0
        else:
            progress = (completed / total) * 100
        
        lines = []
        lines.append(f"今日进度: {ProgressDisplayFormatter.format_progress_bar(progress)}")
        lines.append(f"已完成: {completed}/{total} 个任务")
        
        return "\n".join(lines)


class CalendarDisplayFormatter:
    """日历显示格式化工具"""

    @staticmethod
    def format_day_schedule(events: List, tasks: List) -> str:
        """格式化日程安排"""
        lines = []
        lines.append("=" * 60)
        lines.append("今日日程")
        lines.append("=" * 60)
        
        all_items = []
        
        for event in events:
            all_items.append({
                "time": event.start_time,
                "title": event.title,
                "type": "event"
            })
        
        for task in tasks:
            if task.deadline:
                all_items.append({
                    "time": task.deadline,
                    "title": task.title,
                    "type": "task"
                })
        
        sorted_items = sorted(all_items, key=lambda x: x["time"])
        
        for item in sorted_items:
            time_str = item["time"].strftime("%H:%M")
            type_icon = "📅" if item["type"] == "event" else "📋"
            lines.append(f"{time_str} {type_icon} {item['title']}")
        
        return "\n".join(lines)

    @staticmethod
    def format_week_schedule(weekly_plan: Dict) -> str:
        """格式化周计划"""
        lines = []
        lines.append("=" * 80)
        lines.append("周计划")
        lines.append("=" * 80)
        
        for day_key, tasks in weekly_plan.items():
            if tasks:
                lines.append(f"\n{day_key}:")
                for task in tasks[:3]:
                    lines.append(f"  • {task.title} ({task.priority_score:.1f})")
        
        return "\n".join(lines)


class RecommendationDisplayFormatter:
    """推荐显示格式化工具"""

    @staticmethod
    def format_task_recommendations(recommendations: Dict[str, List[Task]]) -> str:
        """格式化任务推荐"""
        lines = []
        lines.append("=" * 80)
        lines.append("任务推荐")
        lines.append("=" * 80)
        
        categories = {
            "do_now": "🔴 立即处理",
            "schedule": "🟡 安排时间",
            "delegate": "🟢 委托他人",
            "eliminate": "⚪ 考虑删除"
        }
        
        for key, category_name in categories.items():
            tasks = recommendations.get(key, [])
            if tasks:
                lines.append(f"\n{category_name}")
                for task in tasks[:3]:
                    lines.append(f"  • {task.title} (优先级: {task.priority_score:.1f})")
        
        return "\n".join(lines)

    @staticmethod
    def format_focus_recommendations(recommendations: List[Dict]) -> str:
        """格式化专注推荐"""
        lines = []
        lines.append("=" * 60)
        lines.append("专注推荐")
        lines.append("=" * 60)
        
        for i, rec in enumerate(recommendations, 1):
            task = rec["task"]
            duration = rec["recommended_duration"]
            lines.append(f"\n{i}. {task.title}")
            lines.append(f"   推荐时长: {duration} 分钟")
            lines.append(f"   原因: {rec['reason']}")
            lines.append(f"   预计完成: {rec['estimated_completion'].strftime('%H:%M')}")
        
        return "\n".join(lines)
