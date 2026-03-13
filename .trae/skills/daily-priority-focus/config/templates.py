from typing import Dict, List, Optional
from datetime import datetime


class TaskTemplates:
    """任务模板，用于快速创建常见类型的任务"""

    @staticmethod
    def get_work_task_templates() -> Dict[str, Dict]:
        """工作相关任务模板"""
        return {
            "meeting": {
                "title": "会议",
                "description": "参加会议",
                "importance": 3,
                "urgency": 3,
                "difficulty": 2,
                "estimated_time": 60,
                "tags": ["工作", "会议"]
            },
            "report": {
                "title": "报告",
                "description": "撰写报告",
                "importance": 4,
                "urgency": 3,
                "difficulty": 4,
                "estimated_time": 120,
                "tags": ["工作", "报告"]
            },
            "email": {
                "title": "邮件",
                "description": "处理邮件",
                "importance": 2,
                "urgency": 2,
                "difficulty": 1,
                "estimated_time": 30,
                "tags": ["工作", "邮件"]
            },
            "presentation": {
                "title": "演示文稿",
                "description": "准备演示文稿",
                "importance": 4,
                "urgency": 4,
                "difficulty": 3,
                "estimated_time": 180,
                "tags": ["工作", "演示"]
            },
            "review": {
                "title": "审查",
                "description": "审查文档或代码",
                "importance": 3,
                "urgency": 2,
                "difficulty": 3,
                "estimated_time": 90,
                "tags": ["工作", "审查"]
            }
        }

    @staticmethod
    def get_study_task_templates() -> Dict[str, Dict]:
        """学习相关任务模板"""
        return {
            "reading": {
                "title": "阅读",
                "description": "阅读学习资料",
                "importance": 3,
                "urgency": 2,
                "difficulty": 2,
                "estimated_time": 60,
                "tags": ["学习", "阅读"]
            },
            "homework": {
                "title": "作业",
                "description": "完成作业",
                "importance": 4,
                "urgency": 4,
                "difficulty": 3,
                "estimated_time": 90,
                "tags": ["学习", "作业"]
            },
            "research": {
                "title": "研究",
                "description": "进行研究工作",
                "importance": 3,
                "urgency": 2,
                "difficulty": 4,
                "estimated_time": 120,
                "tags": ["学习", "研究"]
            },
            "practice": {
                "title": "练习",
                "description": "练习技能",
                "importance": 3,
                "urgency": 2,
                "difficulty": 2,
                "estimated_time": 45,
                "tags": ["学习", "练习"]
            }
        }

    @staticmethod
    def get_personal_task_templates() -> Dict[str, Dict]:
        """个人生活相关任务模板"""
        return {
            "exercise": {
                "title": "运动",
                "description": "进行体育锻炼",
                "importance": 3,
                "urgency": 2,
                "difficulty": 2,
                "estimated_time": 60,
                "tags": ["个人", "健康", "运动"]
            },
            "shopping": {
                "title": "购物",
                "description": "购买日常用品",
                "importance": 2,
                "urgency": 2,
                "difficulty": 1,
                "estimated_time": 45,
                "tags": ["个人", "购物"]
            },
            "cleaning": {
                "title": "清洁",
                "description": "打扫卫生",
                "importance": 2,
                "urgency": 2,
                "difficulty": 2,
                "estimated_time": 60,
                "tags": ["个人", "清洁"]
            },
            "appointment": {
                "title": "预约",
                "description": "预约医生或其他服务",
                "importance": 3,
                "urgency": 3,
                "difficulty": 1,
                "estimated_time": 30,
                "tags": ["个人", "预约"]
            }
        }

    @staticmethod
    def get_all_templates() -> Dict[str, Dict]:
        """获取所有任务模板"""
        templates = {}
        templates.update(TaskTemplates.get_work_task_templates())
        templates.update(TaskTemplates.get_study_task_templates())
        templates.update(TaskTemplates.get_personal_task_templates())
        return templates

    @staticmethod
    def get_template_by_name(template_name: str) -> Optional[Dict]:
        """根据名称获取任务模板"""
        all_templates = TaskTemplates.get_all_templates()
        return all_templates.get(template_name)

    @staticmethod
    def get_templates_by_category(category: str) -> Dict[str, Dict]:
        """根据类别获取任务模板"""
        if category == "work":
            return TaskTemplates.get_work_task_templates()
        elif category == "study":
            return TaskTemplates.get_study_task_templates()
        elif category == "personal":
            return TaskTemplates.get_personal_task_templates()
        return {}


class PriorityPresets:
    """优先级预设，用于快速设置任务优先级"""

    @staticmethod
    def get_presets() -> Dict[str, Dict]:
        """获取所有优先级预设"""
        return {
            "urgent_important": {
                "name": "紧急重要",
                "importance": 4,
                "urgency": 4,
                "difficulty": 3,
                "description": "需要立即处理的重要任务"
            },
            "important_not_urgent": {
                "name": "重要不紧急",
                "importance": 4,
                "urgency": 2,
                "difficulty": 3,
                "description": "重要但可以稍后处理的任务"
            },
            "urgent_not_important": {
                "name": "紧急不重要",
                "importance": 2,
                "urgency": 4,
                "difficulty": 2,
                "description": "需要快速处理但不重要的任务"
            },
            "not_urgent_not_important": {
                "name": "不紧急不重要",
                "importance": 2,
                "urgency": 2,
                "difficulty": 1,
                "description": "可以延后或委托的任务"
            },
            "quick_task": {
                "name": "快速任务",
                "importance": 2,
                "urgency": 2,
                "difficulty": 1,
                "estimated_time": 15,
                "description": "可以在15分钟内完成的简单任务"
            },
            "complex_task": {
                "name": "复杂任务",
                "importance": 3,
                "urgency": 2,
                "difficulty": 4,
                "estimated_time": 180,
                "description": "需要较长时间和精力的复杂任务"
            }
        }

    @staticmethod
    def get_preset_by_name(preset_name: str) -> Optional[Dict]:
        """根据名称获取优先级预设"""
        presets = PriorityPresets.get_presets()
        return presets.get(preset_name)


class FocusSessionTemplates:
    """专注会话模板"""

    @staticmethod
    def get_templates() -> Dict[str, Dict]:
        """获取所有专注会话模板"""
        return {
            "pomodoro": {
                "name": "番茄钟",
                "duration": 25,
                "break_interval": 25,
                "break_duration": 5,
                "description": "25分钟专注，5分钟休息"
            },
            "deep_work": {
                "name": "深度工作",
                "duration": 90,
                "break_interval": 45,
                "break_duration": 10,
                "description": "90分钟深度工作，每45分钟休息10分钟"
            },
            "short_focus": {
                "name": "短时专注",
                "duration": 15,
                "break_interval": 15,
                "break_duration": 3,
                "description": "15分钟专注，3分钟休息"
            },
            "long_session": {
                "name": "长时会话",
                "duration": 120,
                "break_interval": 60,
                "break_duration": 15,
                "description": "2小时工作，每小时休息15分钟"
            },
            "morning_routine": {
                "name": "早晨例程",
                "duration": 60,
                "break_interval": 30,
                "break_duration": 5,
                "description": "1小时早晨工作，每30分钟休息5分钟"
            }
        }

    @staticmethod
    def get_template_by_name(template_name: str) -> Optional[Dict]:
        """根据名称获取专注会话模板"""
        templates = FocusSessionTemplates.get_templates()
        return templates.get(template_name)


class ReminderTemplates:
    """提醒模板"""

    @staticmethod
    def get_templates() -> Dict[str, Dict]:
        """获取所有提醒模板"""
        return {
            "deadline_reminders": {
                "name": "截止日期提醒",
                "reminder_times": [60, 1440, 4320],
                "description": "在截止日期前1小时、1天、3天提醒"
            },
            "meeting_reminders": {
                "name": "会议提醒",
                "reminder_times": [15, 60],
                "description": "在会议前15分钟、1小时提醒"
            },
            "daily_check": {
                "name": "每日检查",
                "reminder_times": [360],
                "description": "每天检查一次任务"
            },
            "weekly_review": {
                "name": "每周回顾",
                "reminder_times": [10080],
                "description": "每周回顾一次任务"
            }
        }

    @staticmethod
    def get_template_by_name(template_name: str) -> Optional[Dict]:
        """根据名称获取提醒模板"""
        templates = ReminderTemplates.get_templates()
        return templates.get(template_name)


class WorkflowTemplates:
    """工作流模板，用于快速设置常见的工作流程"""

    @staticmethod
    def get_templates() -> Dict[str, Dict]:
        """获取所有工作流模板"""
        return {
            "daily_planning": {
                "name": "每日规划",
                "description": "规划一天的任务",
                "steps": [
                    {"action": "review_tasks", "description": "查看所有任务"},
                    {"action": "set_priorities", "description": "设置任务优先级"},
                    {"action": "schedule_focus", "description": "安排专注时间"},
                    {"action": "set_reminders", "description": "设置提醒"}
                ]
            },
            "weekly_review": {
                "name": "每周回顾",
                "description": "回顾一周的工作",
                "steps": [
                    {"action": "review_completed", "description": "查看已完成的任务"},
                    {"action": "review_pending", "description": "查看待处理的任务"},
                    {"action": "update_priorities", "description": "更新任务优先级"},
                    {"action": "plan_next_week", "description": "规划下周任务"}
                ]
            },
            "project_planning": {
                "name": "项目规划",
                "description": "规划新项目",
                "steps": [
                    {"action": "define_goals", "description": "定义项目目标"},
                    {"action": "break_down_tasks", "description": "分解任务"},
                    {"action": "set_deadlines", "description": "设置截止日期"},
                    {"action": "assign_priorities", "description": "分配优先级"},
                    {"action": "schedule_tasks", "description": "安排任务时间"}
                ]
            }
        }

    @staticmethod
    def get_template_by_name(template_name: str) -> Optional[Dict]:
        """根据名称获取工作流模板"""
        templates = WorkflowTemplates.get_templates()
        return templates.get(template_name)


def get_all_templates() -> Dict[str, Dict]:
    """获取所有模板"""
    return {
        "task_templates": TaskTemplates.get_all_templates(),
        "priority_presets": PriorityPresets.get_presets(),
        "focus_session_templates": FocusSessionTemplates.get_templates(),
        "reminder_templates": ReminderTemplates.get_templates(),
        "workflow_templates": WorkflowTemplates.get_templates()
    }
