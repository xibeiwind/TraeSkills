import sys
import argparse
from datetime import datetime
from typing import List, Dict
from ..core.task_manager import TaskManager, Task, TaskStatus
from ..core.priority_algorithm import PriorityAlgorithm
from ..core.reminder_system import ReminderSystem
from ..core.focus_mode import FocusMode


class CLIInterface:
    def __init__(self, task_manager: TaskManager = None, 
                 priority_algorithm: PriorityAlgorithm = None,
                 reminder_system: ReminderSystem = None,
                 focus_mode: FocusMode = None):
        self.task_manager = task_manager or TaskManager()
        self.priority_algorithm = priority_algorithm or PriorityAlgorithm()
        self.reminder_system = reminder_system or ReminderSystem()
        self.focus_mode = focus_mode or FocusMode()
        
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Daily Priority Focus - 智能任务管理工具",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='可用命令')

        add_parser = subparsers.add_parser('add', help='添加新任务')
        add_parser.add_argument('title', help='任务标题')
        add_parser.add_argument('--description', '-d', default='', help='任务描述')
        add_parser.add_argument('--importance', '-i', type=int, choices=[1, 2, 3, 4], 
                                default=2, help='重要性 (1-4)')
        add_parser.add_argument('--urgency', '-u', type=int, choices=[1, 2, 3, 4], 
                                default=2, help='紧急性 (1-4)')
        add_parser.add_argument('--difficulty', '-df', type=int, choices=[1, 2, 3, 4], 
                                default=2, help='难度 (1-4)')
        add_parser.add_argument('--time', '-t', type=int, default=60, 
                                help='预计完成时间（分钟）')
        add_parser.add_argument('--deadline', '-dl', help='截止日期 (YYYY-MM-DD HH:MM)')
        add_parser.add_argument('--tags', nargs='+', help='任务标签')

        list_parser = subparsers.add_parser('list', help='列出任务')
        list_parser.add_argument('--view', '-v', choices=['list', 'timeline', 'matrix'], 
                                default='list', help='查看方式')
        list_parser.add_argument('--status', '-s', choices=['pending', 'in_progress', 
                                'completed', 'cancelled'], help='按状态筛选')
        list_parser.add_argument('--tag', help='按标签筛选')
        list_parser.add_argument('--limit', '-l', type=int, help='限制显示数量')

        show_parser = subparsers.add_parser('show', help='显示任务详情')
        show_parser.add_argument('task_id', help='任务ID')

        update_parser = subparsers.add_parser('update', help='更新任务')
        update_parser.add_argument('task_id', help='任务ID')
        update_parser.add_argument('--title', help='新标题')
        update_parser.add_argument('--description', '-d', help='新描述')
        update_parser.add_argument('--importance', '-i', type=int, choices=[1, 2, 3, 4])
        update_parser.add_argument('--urgency', '-u', type=int, choices=[1, 2, 3, 4])
        update_parser.add_argument('--difficulty', '-df', type=int, choices=[1, 2, 3, 4])
        update_parser.add_argument('--time', '-t', type=int, help='预计完成时间（分钟）')
        update_parser.add_argument('--deadline', '-dl', help='截止日期 (YYYY-MM-DD HH:MM)')
        update_parser.add_argument('--status', '-s', choices=['pending', 'in_progress', 
                                'completed', 'cancelled'])
        update_parser.add_argument('--tags', nargs='+', help='任务标签')

        delete_parser = subparsers.add_parser('delete', help='删除任务')
        delete_parser.add_argument('task_id', help='任务ID')

        focus_parser = subparsers.add_parser('focus', help='专注模式')
        focus_parser.add_argument('--task-id', help='任务ID')
        focus_parser.add_argument('--duration', '-d', type=int, default=60, 
                                  help='专注时长（分钟）')
        focus_parser.add_argument('--action', choices=['start', 'pause', 'resume', 
                                  'complete', 'cancel', 'break', 'end-break'],
                                  default='start', help='操作类型')

        stats_parser = subparsers.add_parser('stats', help='查看统计信息')
        stats_parser.add_argument('--period', '-p', choices=['day', 'week', 'month'], 
                                 default='day', help='统计周期')

        search_parser = subparsers.add_parser('search', help='搜索任务')
        search_parser.add_argument('query', help='搜索关键词')

        remind_parser = subparsers.add_parser('remind', help='提醒管理')
        remind_parser.add_argument('--task-id', help='任务ID')
        remind_parser.add_argument('--time', '-t', help='提醒时间 (YYYY-MM-DD HH:MM)')
        remind_parser.add_argument('--message', '-m', help='提醒消息')
        remind_parser.add_argument('--list', '-l', action='store_true', help='列出所有提醒')

        return parser

    def run(self, args: List[str] = None):
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return

        command_map = {
            'add': self._handle_add,
            'list': self._handle_list,
            'show': self._handle_show,
            'update': self._handle_update,
            'delete': self._handle_delete,
            'focus': self._handle_focus,
            'stats': self._handle_stats,
            'search': self._handle_search,
            'remind': self._handle_remind
        }

        handler = command_map.get(parsed_args.command)
        if handler:
            handler(parsed_args)

    def _handle_add(self, args):
        deadline = None
        if args.deadline:
            try:
                deadline = datetime.strptime(args.deadline, '%Y-%m-%d %H:%M')
            except ValueError:
                print("错误：截止日期格式应为 YYYY-MM-DD HH:MM")
                return

        task_id = f"task_{int(datetime.now().timestamp())}"
        task = Task(
            task_id=task_id,
            title=args.title,
            description=args.description,
            importance=args.importance,
            urgency=args.urgency,
            difficulty=args.difficulty,
            estimated_time=args.time,
            deadline=deadline,
            tags=args.tags or []
        )

        self.task_manager.add_task(task)
        print(f"✓ 任务已添加: {task.title}")
        print(f"  ID: {task_id}")
        print(f"  优先级评分: {task.calculate_priority_score(self.priority_algorithm.weights):.1f}")

    def _handle_list(self, args):
        tasks = self.task_manager.get_all_tasks()
        
        if args.status:
            tasks = [t for t in tasks if t.status.value == args.status]
        
        if args.tag:
            tasks = [t for t in tasks if args.tag in t.tags]

        if args.view == 'list':
            sorted_tasks = self.priority_algorithm.sort_tasks_by_priority(tasks)
            self._display_task_list(sorted_tasks, args.limit)
        elif args.view == 'timeline':
            self._display_task_timeline(tasks, args.limit)
        elif args.view == 'matrix':
            self._display_task_matrix(tasks)

    def _handle_show(self, args):
        task = self.task_manager.get_task(args.task_id)
        if task:
            self._display_task_detail(task)
        else:
            print(f"错误：未找到任务 {args.task_id}")

    def _handle_update(self, args):
        updates = {}
        if args.title:
            updates['title'] = args.title
        if args.description is not None:
            updates['description'] = args.description
        if args.importance:
            updates['importance'] = args.importance
        if args.urgency:
            updates['urgency'] = args.urgency
        if args.difficulty:
            updates['difficulty'] = args.difficulty
        if args.time:
            updates['estimated_time'] = args.time
        if args.deadline:
            try:
                updates['deadline'] = datetime.strptime(args.deadline, '%Y-%m-%d %H:%M')
            except ValueError:
                print("错误：截止日期格式应为 YYYY-MM-DD HH:MM")
                return
        if args.status:
            updates['status'] = TaskStatus(args.status)
        if args.tags:
            updates['tags'] = args.tags

        task = self.task_manager.update_task(args.task_id, **updates)
        if task:
            print(f"✓ 任务已更新: {task.title}")
        else:
            print(f"错误：未找到任务 {args.task_id}")

    def _handle_delete(self, args):
        if self.task_manager.delete_task(args.task_id):
            print(f"✓ 任务已删除: {args.task_id}")
        else:
            print(f"错误：未找到任务 {args.task_id}")

    def _handle_focus(self, args):
        if args.action == 'start':
            if args.task_id:
                task = self.task_manager.get_task(args.task_id)
                if task:
                    session = self.focus_mode.create_session(args.task_id, args.duration)
                    self.focus_mode.start_session(session.session_id)
                    print(f"✓ 已进入专注模式")
                    print(f"  任务: {task.title}")
                    print(f"  时长: {args.duration} 分钟")
                else:
                    print(f"错误：未找到任务 {args.task_id}")
            else:
                print("错误：请指定任务ID")
        elif args.action == 'pause':
            session = self.focus_mode.pause_session()
            if session:
                print("✓ 专注模式已暂停")
        elif args.action == 'resume':
            session = self.focus_mode.resume_session()
            if session:
                print("✓ 专注模式已恢复")
        elif args.action == 'complete':
            session = self.focus_mode.complete_session()
            if session:
                print("✓ 专注模式已完成")
        elif args.action == 'cancel':
            session = self.focus_mode.cancel_session()
            if session:
                print("✓ 专注模式已取消")
        elif args.action == 'break':
            session = self.focus_mode.take_break()
            if session:
                print("✓ 已开始休息")
        elif args.action == 'end-break':
            session = self.focus_mode.end_break()
            if session:
                print("✓ 休息结束，继续专注")

    def _handle_stats(self, args):
        stats = self.task_manager.get_task_statistics()
        print("\n=== 任务统计 ===")
        print(f"总任务数: {stats['total_tasks']}")
        print(f"已完成: {stats['completed_tasks']}")
        print(f"进行中: {stats['in_progress_tasks']}")
        print(f"待处理: {stats['pending_tasks']}")
        print(f"完成率: {stats['completion_rate']:.1f}%")

        focus_stats = self.focus_mode.get_session_statistics()
        print("\n=== 专注统计 ===")
        print(f"总专注会话: {focus_stats['total_sessions']}")
        print(f"总专注时间: {focus_stats['total_focus_time']:.1f} 分钟")
        print(f"平均会话时长: {focus_stats['average_session_duration']:.1f} 分钟")
        print(f"完成率: {focus_stats['completion_rate']:.1f}%")

    def _handle_search(self, args):
        tasks = self.task_manager.search_tasks(args.query)
        if tasks:
            print(f"\n找到 {len(tasks)} 个匹配的任务:")
            self._display_task_list(tasks)
        else:
            print(f"未找到匹配 '{args.query}' 的任务")

    def _handle_remind(self, args):
        if args.list:
            reminders = self.reminder_system.get_upcoming_reminders()
            print(f"\n即将到来的提醒 ({len(reminders)}):")
            for reminder in reminders:
                print(f"  {reminder.reminder_time.strftime('%Y-%m-%d %H:%M')} - {reminder.message}")
        elif args.task_id and args.time:
            try:
                reminder_time = datetime.strptime(args.time, '%Y-%m-%d %H:%M')
                reminder = self.reminder_system.create_reminder(
                    task_id=args.task_id,
                    reminder_time=reminder_time,
                    message=args.message or f"任务 {args.task_id} 的提醒"
                )
                print(f"✓ 提醒已设置: {reminder.reminder_time.strftime('%Y-%m-%d %H:%M')}")
            except ValueError:
                print("错误：提醒时间格式应为 YYYY-MM-DD HH:MM")
        else:
            print("错误：请提供任务ID和提醒时间，或使用 --list 查看所有提醒")

    def _display_task_list(self, tasks: List[Task], limit: int = None):
        if limit:
            tasks = tasks[:limit]
        
        if not tasks:
            print("没有任务")
            return

        print(f"\n{'='*80}")
        print(f"{'ID':<12} {'标题':<30} {'优先级':<8} {'状态':<12} {'截止日期'}")
        print(f"{'='*80}")
        
        for task in tasks:
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.CANCELLED: "❌"
            }.get(task.status, "❓")
            
            deadline_str = task.deadline.strftime('%m-%d %H:%M') if task.deadline else "-"
            
            print(f"{task.task_id:<12} {task.title[:28]:<30} "
                  f"{task.priority_score:>6.1f} {status_icon} {task.status.value:<10} "
                  f"{deadline_str}")

    def _display_task_timeline(self, tasks: List[Task], limit: int = None):
        if limit:
            tasks = tasks[:limit]
        
        if not tasks:
            print("没有任务")
            return

        sorted_tasks = sorted([t for t in tasks if t.deadline], key=lambda t: t.deadline)
        
        print(f"\n{'='*60}")
        print("任务时间线")
        print(f"{'='*60}")
        
        for task in sorted_tasks:
            print(f"{task.deadline.strftime('%Y-%m-%d %H:%M')} | {task.title}")

    def _display_task_matrix(self, tasks: List[Task]):
        matrix = self.priority_algorithm.get_important_urgent_matrix(tasks)
        
        print(f"\n{'='*80}")
        print("重要紧急矩阵")
        print(f"{'='*80}")
        
        print("\n【重要且紧急】")
        for task in matrix['important_urgent'][:5]:
            print(f"  • {task.title} (优先级: {task.priority_score:.1f})")
        
        print("\n【重要但不紧急】")
        for task in matrix['important_not_urgent'][:5]:
            print(f"  • {task.title} (优先级: {task.priority_score:.1f})")
        
        print("\n【不重要但紧急】")
        for task in matrix['not_important_urgent'][:5]:
            print(f"  • {task.title} (优先级: {task.priority_score:.1f})")
        
        print("\n【不重要不紧急】")
        for task in matrix['not_important_not_urgent'][:5]:
            print(f"  • {task.title} (优先级: {task.priority_score:.1f})")

    def _display_task_detail(self, task: Task):
        print(f"\n{'='*60}")
        print(f"任务详情: {task.title}")
        print(f"{'='*60}")
        print(f"ID: {task.task_id}")
        print(f"描述: {task.description or '无'}")
        print(f"重要性: {task.importance}/4")
        print(f"紧急性: {task.urgency}/4")
        print(f"难度: {task.difficulty}/4")
        print(f"预计时间: {task.estimated_time} 分钟")
        print(f"截止日期: {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else '无'}")
        print(f"状态: {task.status.value}")
        print(f"标签: {', '.join(task.tags) if task.tags else '无'}")
        print(f"优先级评分: {task.priority_score:.1f}")
        print(f"创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"更新时间: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")


def main():
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()
