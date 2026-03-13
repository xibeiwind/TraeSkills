from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .task_manager import Task, TaskStatus


class PriorityAlgorithm:
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "importance": 0.30,
            "urgency": 0.25,
            "difficulty": 0.20,
            "time": 0.15,
            "dependencies": 0.10
        }
        self.validate_weights()

    def validate_weights(self):
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def update_weights(self, weights: Dict[str, float]):
        self.weights.update(weights)
        self.validate_weights()

    def calculate_task_priority(self, task: Task) -> float:
        return task.calculate_priority_score(self.weights)

    def calculate_all_priorities(self, tasks: List[Task]) -> List[Task]:
        for task in tasks:
            task.calculate_priority_score(self.weights)
        return tasks

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        sorted_tasks = self.calculate_all_priorities(tasks)
        return sorted(sorted_tasks, key=lambda t: t.priority_score, reverse=True)

    def get_top_n_tasks(self, tasks: List[Task], n: int) -> List[Task]:
        sorted_tasks = self.sort_tasks_by_priority(tasks)
        return sorted_tasks[:n]

    def get_important_urgent_matrix(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        matrix = {
            "important_urgent": [],
            "important_not_urgent": [],
            "not_important_urgent": [],
            "not_important_not_urgent": []
        }

        for task in tasks:
            is_important = task.importance >= 3
            is_urgent = task.urgency >= 3
            
            if task.deadline:
                time_until_deadline = (task.deadline - datetime.now()).total_seconds() / 3600
                if time_until_deadline <= 24:
                    is_urgent = True

            if is_important and is_urgent:
                matrix["important_urgent"].append(task)
            elif is_important and not is_urgent:
                matrix["important_not_urgent"].append(task)
            elif not is_important and is_urgent:
                matrix["not_important_urgent"].append(task)
            else:
                matrix["not_important_not_urgent"].append(task)

        return matrix

    def get_daily_focus_tasks(self, tasks: List[Task], max_tasks: int = 5) -> List[Task]:
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        sorted_tasks = self.sort_tasks_by_priority(pending_tasks)
        
        focus_tasks = []
        total_time = 0
        max_daily_time = 8 * 60

        for task in sorted_tasks:
            if total_time + task.estimated_time <= max_daily_time:
                focus_tasks.append(task)
                total_time += task.estimated_time
                if len(focus_tasks) >= max_tasks:
                    break

        return focus_tasks

    def get_weekly_plan(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        weekly_plan = {}
        now = datetime.now()
        
        for day in range(7):
            day_date = now + timedelta(days=day)
            day_key = day_date.strftime("%Y-%m-%d")
            weekly_plan[day_key] = []

        for task in tasks:
            if task.deadline:
                deadline_date = task.deadline.strftime("%Y-%m-%d")
                if deadline_date in weekly_plan:
                    weekly_plan[deadline_date].append(task)

        for day_key in weekly_plan:
            weekly_plan[day_key] = self.sort_tasks_by_priority(weekly_plan[day_key])

        return weekly_plan

    def get_task_recommendations(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        recommendations = {
            "do_now": [],
            "schedule": [],
            "delegate": [],
            "eliminate": []
        }

        matrix = self.get_important_urgent_matrix(tasks)
        
        recommendations["do_now"] = self.sort_tasks_by_priority(matrix["important_urgent"])
        recommendations["schedule"] = self.sort_tasks_by_priority(matrix["important_not_urgent"])
        recommendations["delegate"] = self.sort_tasks_by_priority(matrix["not_important_urgent"])
        recommendations["eliminate"] = matrix["not_important_not_urgent"]

        return recommendations

    def analyze_task_distribution(self, tasks: List[Task]) -> Dict:
        if not tasks:
            return {}

        total_importance = sum(t.importance for t in tasks)
        total_urgency = sum(t.urgency for t in tasks)
        total_difficulty = sum(t.difficulty for t in tasks)
        total_time = sum(t.estimated_time for t in tasks)

        status_distribution = {}
        for status in TaskStatus:
            status_distribution[status.value] = len([t for t in tasks if t.status == status])

        return {
            "average_importance": total_importance / len(tasks),
            "average_urgency": total_urgency / len(tasks),
            "average_difficulty": total_difficulty / len(tasks),
            "total_estimated_time": total_time,
            "average_estimated_time": total_time / len(tasks),
            "status_distribution": status_distribution,
            "high_priority_count": len([t for t in tasks if t.priority_score >= 75]),
            "medium_priority_count": len([t for t in tasks if 50 <= t.priority_score < 75]),
            "low_priority_count": len([t for t in tasks if t.priority_score < 50])
        }

    def get_time_based_priorities(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        now = datetime.now()
        
        result = {
            "overdue": [],
            "today": [],
            "tomorrow": [],
            "this_week": [],
            "next_week": [],
            "later": []
        }

        for task in tasks:
            if not task.deadline:
                result["later"].append(task)
                continue

            time_diff = task.deadline - now
            hours_diff = time_diff.total_seconds() / 3600

            if hours_diff < 0:
                result["overdue"].append(task)
            elif hours_diff <= 24:
                result["today"].append(task)
            elif hours_diff <= 48:
                result["tomorrow"].append(task)
            elif hours_diff <= 168:
                result["this_week"].append(task)
            elif hours_diff <= 336:
                result["next_week"].append(task)
            else:
                result["later"].append(task)

        for key in result:
            result[key] = self.sort_tasks_by_priority(result[key])

        return result

    def optimize_task_order(self, tasks: List[Task]) -> List[Task]:
        pending_tasks = [t for t in tasks if t.status == TaskStatus.PENDING]
        
        task_order = []
        remaining_tasks = set(pending_tasks)

        while remaining_tasks:
            available_tasks = [
                task for task in remaining_tasks
                if all(dep not in remaining_tasks for dep in task.dependencies)
            ]

            if not available_tasks:
                available_tasks = list(remaining_tasks)

            sorted_available = self.sort_tasks_by_priority(available_tasks)
            next_task = sorted_available[0]
            
            task_order.append(next_task)
            remaining_tasks.remove(next_task)

        return task_order
