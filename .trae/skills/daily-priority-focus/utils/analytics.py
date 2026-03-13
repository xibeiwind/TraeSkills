from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter
from ..core.task_manager import Task, TaskStatus
from ..core.focus_mode import FocusSession


class TaskAnalytics:
    """任务分析工具"""

    @staticmethod
    def analyze_task_completion(tasks: List[Task]) -> Dict:
        """分析任务完成情况"""
        total_tasks = len(tasks)
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        in_progress_tasks = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        cancelled_tasks = [t for t in tasks if t.status == TaskStatus.CANCELLED]

        completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": len(completed_tasks),
            "in_progress_tasks": len(in_progress_tasks),
            "pending_tasks": len(pending_tasks),
            "cancelled_tasks": len(cancelled_tasks),
            "completion_rate": completion_rate
        }

    @staticmethod
    def analyze_priority_distribution(tasks: List[Task]) -> Dict:
        """分析优先级分布"""
        high_priority = [t for t in tasks if t.priority_score >= 75]
        medium_priority = [t for t in tasks if 50 <= t.priority_score < 75]
        low_priority = [t for t in tasks if t.priority_score < 50]

        return {
            "high_priority_count": len(high_priority),
            "medium_priority_count": len(medium_priority),
            "low_priority_count": len(low_priority),
            "high_priority_percentage": (len(high_priority) / len(tasks) * 100) if tasks else 0,
            "medium_priority_percentage": (len(medium_priority) / len(tasks) * 100) if tasks else 0,
            "low_priority_percentage": (len(low_priority) / len(tasks) * 100) if tasks else 0
        }

    @staticmethod
    def analyze_task_tags(tasks: List[Task]) -> Dict:
        """分析任务标签"""
        all_tags = []
        for task in tasks:
            all_tags.extend(task.tags)
        
        tag_counter = Counter(all_tags)
        
        return {
            "total_tags": len(all_tags),
            "unique_tags": len(tag_counter),
            "most_common_tags": tag_counter.most_common(10),
            "tag_distribution": dict(tag_counter)
        }

    @staticmethod
    def analyze_task_difficulty(tasks: List[Task]) -> Dict:
        """分析任务难度"""
        difficulty_levels = {1: 0, 2: 0, 3: 0, 4: 0}
        for task in tasks:
            difficulty_levels[task.difficulty] += 1

        return {
            "difficulty_distribution": difficulty_levels,
            "average_difficulty": sum(t.difficulty for t in tasks) / len(tasks) if tasks else 0,
            "easy_tasks": difficulty_levels[1] + difficulty_levels[2],
            "hard_tasks": difficulty_levels[3] + difficulty_levels[4]
        }

    @staticmethod
    def analyze_time_estimation_accuracy(tasks: List[Task]) -> Dict:
        """分析时间估算准确性"""
        completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        
        if not completed_tasks:
            return {"message": "没有已完成的任务"}

        accuracy_data = []
        for task in completed_tasks:
            if task.created_at and task.updated_at:
                actual_time = (task.updated_at - task.created_at).total_seconds() / 60
                estimated_time = task.estimated_time
                if estimated_time > 0:
                    accuracy = min(actual_time / estimated_time, 3.0)
                    accuracy_data.append(accuracy)

        if not accuracy_data:
            return {"message": "没有足够的时间数据"}

        return {
            "average_accuracy": sum(accuracy_data) / len(accuracy_data),
            "overestimated_count": len([a for a in accuracy_data if a < 0.8]),
            "accurate_count": len([a for a in accuracy_data if 0.8 <= a <= 1.2]),
            "underestimated_count": len([a for a in accuracy_data if a > 1.2]),
            "accuracy_distribution": {
                "very_accurate": len([a for a in accuracy_data if 0.9 <= a <= 1.1]),
                "accurate": len([a for a in accuracy_data if 0.8 <= a <= 1.2]),
                "inaccurate": len([a for a in accuracy_data if a < 0.8 or a > 1.2])
            }
        }

    @staticmethod
    def analyze_task_creation_pattern(tasks: List[Task]) -> Dict:
        """分析任务创建模式"""
        if not tasks:
            return {"message": "没有任务数据"}

        creation_hours = [t.created_at.hour for t in tasks]
        creation_days = [t.created_at.weekday() for t in tasks]

        hour_counter = Counter(creation_hours)
        day_counter = Counter(creation_days)

        day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        return {
            "most_productive_hour": hour_counter.most_common(1)[0] if hour_counter else None,
            "most_productive_day": day_counter.most_common(1)[0] if day_counter else None,
            "hourly_distribution": dict(hour_counter),
            "daily_distribution": {
                day_names[day]: count for day, count in day_counter.items()
            }
        }

    @staticmethod
    def analyze_overdue_tasks(tasks: List[Task]) -> Dict:
        """分析逾期任务"""
        now = datetime.now()
        overdue_tasks = [
            t for t in tasks
            if t.deadline and t.deadline < now and t.status != TaskStatus.COMPLETED
        ]

        if not overdue_tasks:
            return {"overdue_count": 0, "message": "没有逾期任务"}

        overdue_by_days = {}
        for task in overdue_tasks:
            days_overdue = (now - task.deadline).days
            if days_overdue not in overdue_by_days:
                overdue_by_days[days_overdue] = []
            overdue_by_days[days_overdue].append(task)

        return {
            "overdue_count": len(overdue_tasks),
            "overdue_percentage": (len(overdue_tasks) / len(tasks) * 100) if tasks else 0,
            "average_days_overdue": sum((now - t.deadline).days for t in overdue_tasks) / len(overdue_tasks),
            "overdue_by_days": overdue_by_days
        }

    @staticmethod
    def analyze_productivity_trend(tasks: List[Task], days: int = 30) -> Dict:
        """分析生产力趋势"""
        now = datetime.now()
        start_date = now - timedelta(days=days)

        daily_completion = {}
        for day in range(days):
            day_date = start_date + timedelta(days=day)
            day_key = day_date.strftime("%Y-%m-%d")
            daily_completion[day_key] = 0

        for task in tasks:
            if task.status == TaskStatus.COMPLETED and task.updated_at >= start_date:
                day_key = task.updated_at.strftime("%Y-%m-%d")
                if day_key in daily_completion:
                    daily_completion[day_key] += 1

        total_completed = sum(daily_completion.values())
        average_daily = total_completed / days if days > 0 else 0

        return {
            "period_days": days,
            "total_completed": total_completed,
            "average_daily_completion": average_daily,
            "daily_completion": daily_completion,
            "most_productive_day": max(daily_completion.items(), key=lambda x: x[1]) if daily_completion else None,
            "least_productive_day": min(daily_completion.items(), key=lambda x: x[1]) if daily_completion else None
        }


class FocusAnalytics:
    """专注分析工具"""

    @staticmethod
    def analyze_focus_sessions(sessions: List[FocusSession]) -> Dict:
        """分析专注会话"""
        if not sessions:
            return {"message": "没有专注会话数据"}

        completed_sessions = [s for s in sessions if s.status == "completed"]
        cancelled_sessions = [s for s in sessions if s.status == "cancelled"]

        total_focus_time = sum(s.get_elapsed_time() for s in completed_sessions)
        total_pause_time = sum(s.total_pause_time for s in completed_sessions)

        average_session_duration = total_focus_time / len(completed_sessions) if completed_sessions else 0

        return {
            "total_sessions": len(sessions),
            "completed_sessions": len(completed_sessions),
            "cancelled_sessions": len(cancelled_sessions),
            "completion_rate": (len(completed_sessions) / len(sessions) * 100) if sessions else 0,
            "total_focus_time": total_focus_time,
            "total_pause_time": total_pause_time,
            "average_session_duration": average_session_duration,
            "focus_efficiency": (total_focus_time / (total_focus_time + total_pause_time) * 100) if (total_focus_time + total_pause_time) > 0 else 0
        }

    @staticmethod
    def analyze_daily_focus_pattern(sessions: List[FocusSession]) -> Dict:
        """分析每日专注模式"""
        if not sessions:
            return {"message": "没有专注会话数据"}

        completed_sessions = [s for s in sessions if s.status == "completed" and s.start_time]

        daily_focus = {}
        for session in completed_sessions:
            day_key = session.start_time.strftime("%Y-%m-%d")
            if day_key not in daily_focus:
                daily_focus[day_key] = 0
            daily_focus[day_key] += session.get_elapsed_time()

        return {
            "daily_focus_minutes": daily_focus,
            "average_daily_focus": sum(daily_focus.values()) / len(daily_focus) if daily_focus else 0,
            "most_productive_day": max(daily_focus.items(), key=lambda x: x[1]) if daily_focus else None,
            "least_productive_day": min(daily_focus.items(), key=lambda x: x[1]) if daily_focus else None
        }

    @staticmethod
    def analyze_focus_by_time_of_day(sessions: List[FocusSession]) -> Dict:
        """分析按时间段的专注情况"""
        if not sessions:
            return {"message": "没有专注会话数据"}

        completed_sessions = [s for s in sessions if s.status == "completed" and s.start_time]

        hourly_focus = {}
        for session in completed_sessions:
            hour = session.start_time.hour
            if hour not in hourly_focus:
                hourly_focus[hour] = 0
            hourly_focus[hour] += session.get_elapsed_time()

        time_periods = {
            "morning": sum(v for k, v in hourly_focus.items() if 6 <= k < 12),
            "afternoon": sum(v for k, v in hourly_focus.items() if 12 <= k < 18),
            "evening": sum(v for k, v in hourly_focus.items() if 18 <= k < 24),
            "night": sum(v for k, v in hourly_focus.items() if 0 <= k < 6)
        }

        return {
            "hourly_focus_minutes": hourly_focus,
            "time_period_focus": time_periods,
            "most_productive_hour": max(hourly_focus.items(), key=lambda x: x[1]) if hourly_focus else None,
            "most_productive_period": max(time_periods.items(), key=lambda x: x[1]) if time_periods else None
        }


class ProductivityReport:
    """生产力报告生成器"""

    @staticmethod
    def generate_daily_report(tasks: List[Task], sessions: List[FocusSession] = None) -> Dict:
        """生成每日报告"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_tasks = [t for t in tasks if t.created_at >= today_start]
        today_completed = [t for t in today_tasks if t.status == TaskStatus.COMPLETED]
        
        task_analytics = TaskAnalytics.analyze_task_completion(today_tasks)
        
        focus_time = 0
        if sessions:
            today_sessions = [s for s in sessions if s.start_time and s.start_time >= today_start]
            focus_analytics = FocusAnalytics.analyze_focus_sessions(today_sessions)
            focus_time = focus_analytics.get("total_focus_time", 0)
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "tasks_created": len(today_tasks),
            "tasks_completed": len(today_completed),
            "completion_rate": task_analytics.get("completion_rate", 0),
            "focus_time_minutes": focus_time,
            "focus_time_hours": focus_time / 60 if focus_time > 0 else 0,
            "productivity_score": TaskAnalytics._calculate_productivity_score(
                len(today_completed), focus_time
            )
        }

    @staticmethod
    def generate_weekly_report(tasks: List[Task], sessions: List[FocusSession] = None) -> Dict:
        """生成周报告"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        week_tasks = [t for t in tasks if t.created_at >= week_start]
        week_completed = [t for t in week_tasks if t.status == TaskStatus.COMPLETED]
        
        task_analytics = TaskAnalytics.analyze_task_completion(week_tasks)
        productivity_trend = TaskAnalytics.analyze_productivity_trend(week_tasks, 7)
        
        focus_time = 0
        if sessions:
            week_sessions = [s for s in sessions if s.start_time and s.start_time >= week_start]
            focus_analytics = FocusAnalytics.analyze_focus_sessions(week_sessions)
            focus_time = focus_analytics.get("total_focus_time", 0)
        
        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": now.strftime("%Y-%m-%d"),
            "tasks_created": len(week_tasks),
            "tasks_completed": len(week_completed),
            "completion_rate": task_analytics.get("completion_rate", 0),
            "focus_time_minutes": focus_time,
            "focus_time_hours": focus_time / 60 if focus_time > 0 else 0,
            "average_daily_completion": productivity_trend.get("average_daily_completion", 0),
            "daily_completion": productivity_trend.get("daily_completion", {}),
            "productivity_score": TaskAnalytics._calculate_productivity_score(
                len(week_completed), focus_time, days=7
            )
        }

    @staticmethod
    def generate_monthly_report(tasks: List[Task], sessions: List[FocusSession] = None) -> Dict:
        """生成月度报告"""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        month_tasks = [t for t in tasks if t.created_at >= month_start]
        month_completed = [t for t in month_tasks if t.status == TaskStatus.COMPLETED]
        
        task_analytics = TaskAnalytics.analyze_task_completion(month_tasks)
        priority_distribution = TaskAnalytics.analyze_priority_distribution(month_tasks)
        tag_analysis = TaskAnalytics.analyze_task_tags(month_tasks)
        
        focus_time = 0
        if sessions:
            month_sessions = [s for s in sessions if s.start_time and s.start_time >= month_start]
            focus_analytics = FocusAnalytics.analyze_focus_sessions(month_sessions)
            focus_time = focus_analytics.get("total_focus_time", 0)
        
        return {
            "month": now.strftime("%Y-%m"),
            "tasks_created": len(month_tasks),
            "tasks_completed": len(month_completed),
            "completion_rate": task_analytics.get("completion_rate", 0),
            "focus_time_minutes": focus_time,
            "focus_time_hours": focus_time / 60 if focus_time > 0 else 0,
            "priority_distribution": priority_distribution,
            "tag_analysis": tag_analysis,
            "productivity_score": TaskAnalytics._calculate_productivity_score(
                len(month_completed), focus_time, days=30
            )
        }

    @staticmethod
    def _calculate_productivity_score(completed_tasks: int, focus_time: float, days: int = 1) -> float:
        """计算生产力分数"""
        if days == 0:
            return 0.0
        
        avg_tasks_per_day = completed_tasks / days
        avg_focus_per_day = focus_time / days
        
        task_score = min(avg_tasks_per_day / 5 * 50, 50)
        focus_score = min(avg_focus_per_day / 120 * 50, 50)
        
        return task_score + focus_score


class InsightsGenerator:
    """洞察生成器"""

    @staticmethod
    def generate_task_insights(tasks: List[Task]) -> List[str]:
        """生成任务洞察"""
        insights = []
        
        completion_analysis = TaskAnalytics.analyze_task_completion(tasks)
        priority_analysis = TaskAnalytics.analyze_priority_distribution(tasks)
        overdue_analysis = TaskAnalytics.analyze_overdue_tasks(tasks)
        
        if completion_analysis["completion_rate"] >= 80:
            insights.append("✅ 您的任务完成率很高，继续保持！")
        elif completion_analysis["completion_rate"] >= 50:
            insights.append("📊 您的任务完成率中等，可以考虑优化任务规划。")
        else:
            insights.append("⚠️ 您的任务完成率较低，建议重新评估任务优先级。")
        
        if priority_analysis["high_priority_percentage"] > 50:
            insights.append("🔴 您的高优先级任务较多，建议合理分配时间。")
        
        if overdue_analysis["overdue_count"] > 0:
            insights.append(f"⏰ 您有 {overdue_analysis['overdue_count']} 个逾期任务，请及时处理。")
        
        tag_analysis = TaskAnalytics.analyze_task_tags(tasks)
        if tag_analysis["unique_tags"] < 3:
            insights.append("🏷️ 建议为任务添加更多标签，便于分类管理。")
        
        return insights

    @staticmethod
    def generate_focus_insights(sessions: List[FocusSession]) -> List[str]:
        """生成专注洞察"""
        insights = []
        
        if not sessions:
            insights.append("💡 开始使用专注模式来提高工作效率！")
            return insights
        
        focus_analysis = FocusAnalytics.analyze_focus_sessions(sessions)
        time_analysis = FocusAnalytics.analyze_focus_by_time_of_day(sessions)
        
        if focus_analysis["completion_rate"] >= 80:
            insights.append("✅ 您的专注会话完成率很高，专注力很强！")
        
        if focus_analysis["focus_efficiency"] >= 80:
            insights.append("⚡ 您的专注效率很高，很少被打断。")
        elif focus_analysis["focus_efficiency"] >= 60:
            insights.append("📊 您的专注效率良好，可以尝试减少休息时间。")
        else:
            insights.append("💭 您的专注效率有待提高，建议减少干扰因素。")
        
        if time_analysis["most_productive_period"]:
            period_names = {
                "morning": "早晨",
                "afternoon": "下午",
                "evening": "晚上",
                "night": "深夜"
            }
            period = time_analysis["most_productive_period"][0]
            insights.append(f"🌟 您在{period_names.get(period, period)}时段专注力最强，建议安排重要任务。")
        
        return insights

    @staticmethod
    def generate_productivity_recommendations(tasks: List[Task], sessions: List[FocusSession] = None) -> List[str]:
        """生成生产力建议"""
        recommendations = []
        
        completion_analysis = TaskAnalytics.analyze_task_completion(tasks)
        
        if completion_analysis["pending_tasks"] > 10:
            recommendations.append("📋 待处理任务较多，建议使用重要紧急矩阵进行分类。")
        
        if sessions:
            focus_analysis = FocusAnalytics.analyze_focus_sessions(sessions)
            if focus_analysis["average_session_duration"] < 30:
                recommendations.append("⏱️ 平均专注时长较短，可以尝试延长专注时间。")
            elif focus_analysis["average_session_duration"] > 120:
                recommendations.append("🧘 平均专注时长较长，建议适当增加休息时间。")
        
        time_accuracy = TaskAnalytics.analyze_time_estimation_accuracy(tasks)
        if "average_accuracy" in time_accuracy:
            if time_accuracy["average_accuracy"] > 1.5:
                recommendations.append("⏰ 您经常低估任务时间，建议增加时间估算。")
            elif time_accuracy["average_accuracy"] < 0.7:
                recommendations.append("⏰ 您经常高估任务时间，可以更准确地估算时间。")
        
        creation_pattern = TaskAnalytics.analyze_task_creation_pattern(tasks)
        if "most_productive_hour" in creation_pattern:
            hour = creation_pattern["most_productive_hour"][0]
            recommendations.append(f"🕐 您在 {hour}:00 时段创建任务最多，可以安排更多工作。")
        
        return recommendations
