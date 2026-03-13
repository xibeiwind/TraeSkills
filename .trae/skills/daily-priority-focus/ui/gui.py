import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import List, Dict, Optional
from ..core.task_manager import TaskManager, Task, TaskStatus
from ..core.priority_algorithm import PriorityAlgorithm
from ..core.reminder_system import ReminderSystem
from ..core.focus_mode import FocusMode


class GUIInterface:
    def __init__(self, task_manager: TaskManager = None,
                 priority_algorithm: PriorityAlgorithm = None,
                 reminder_system: ReminderSystem = None,
                 focus_mode: FocusMode = None):
        self.task_manager = task_manager or TaskManager()
        self.priority_algorithm = priority_algorithm or PriorityAlgorithm()
        self.reminder_system = reminder_system or ReminderSystem()
        self.focus_mode = focus_mode or FocusMode()
        
        self.root = tk.Tk()
        self.root.title("Daily Priority Focus")
        self.root.geometry("1200x800")
        
        self.current_view = "list"
        self.selected_task = None
        
        self._setup_ui()
        self._refresh_tasks()

    def _setup_ui(self):
        self._create_menu()
        self._create_main_layout()
        self._create_toolbar()
        self._create_task_list()
        self._create_task_detail()
        self._create_status_bar()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建任务", command=self._show_add_task_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="列表视图", command=lambda: self._change_view("list"))
        view_menu.add_command(label="时间轴视图", command=lambda: self._change_view("timeline"))
        view_menu.add_command(label="矩阵视图", command=lambda: self._change_view("matrix"))
        menubar.add_cascade(label="视图", menu=view_menu)
        
        focus_menu = tk.Menu(menubar, tearoff=0)
        focus_menu.add_command(label="进入专注模式", command=self._start_focus_mode)
        focus_menu.add_command(label="暂停专注", command=self._pause_focus_mode)
        focus_menu.add_command(label="结束专注", command=self._complete_focus_mode)
        menubar.add_cascade(label="专注", menu=focus_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)

    def _create_main_layout(self):
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.left_frame = ttk.Frame(self.main_paned)
        self.right_frame = ttk.Frame(self.main_paned)
        
        self.main_paned.add(self.left_frame, weight=2)
        self.main_paned.add(self.right_frame, weight=1)

    def _create_toolbar(self):
        toolbar = ttk.Frame(self.left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="➕ 新建任务", command=self._show_add_task_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ 编辑", command=self._edit_selected_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ 删除", command=self._delete_selected_task).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="🔄 刷新", command=self._refresh_tasks).pack(side=tk.LEFT, padx=2)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        ttk.Entry(toolbar, textvariable=self.search_var).pack(side=tk.RIGHT, padx=2)
        ttk.Label(toolbar, text="搜索:").pack(side=tk.RIGHT)

    def _create_task_list(self):
        list_frame = ttk.LabelFrame(self.left_frame, text="任务列表")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("title", "priority", "status", "deadline")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        self.task_tree.heading("title", text="标题")
        self.task_tree.heading("priority", text="优先级")
        self.task_tree.heading("status", text="状态")
        self.task_tree.heading("deadline", text="截止日期")
        
        self.task_tree.column("title", width=300)
        self.task_tree.column("priority", width=80)
        self.task_tree.column("status", width=100)
        self.task_tree.column("deadline", width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_tree.bind('<<TreeviewSelect>>', self._on_task_select)
        self.task_tree.bind('<Double-1>', self._on_task_double_click)

    def _create_task_detail(self):
        detail_frame = ttk.LabelFrame(self.right_frame, text="任务详情")
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, state=tk.DISABLED)
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _refresh_tasks(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        tasks = self.task_manager.get_all_tasks()
        sorted_tasks = self.priority_algorithm.sort_tasks_by_priority(tasks)
        
        for task in sorted_tasks:
            status_text = {
                TaskStatus.PENDING: "⏳ 待处理",
                TaskStatus.IN_PROGRESS: "🔄 进行中",
                TaskStatus.COMPLETED: "✅ 已完成",
                TaskStatus.CANCELLED: "❌ 已取消"
            }.get(task.status, task.status.value)
            
            deadline_text = task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else "-"
            
            self.task_tree.insert("", tk.END, values=(
                task.title,
                f"{task.priority_score:.1f}",
                status_text,
                deadline_text
            ), tags=(task.task_id,))
        
        self.status_bar.config(text=f"共 {len(tasks)} 个任务")

    def _on_search(self, *args):
        search_query = self.search_var.get().lower()
        
        for item in self.task_tree.get_children():
            task_id = self.task_tree.item(item, "tags")[0]
            task = self.task_manager.get_task(task_id)
            
            if search_query:
                if (search_query in task.title.lower() or 
                    search_query in task.description.lower()):
                    self.task_tree.item(item, open=True)
                else:
                    self.task_tree.delete(item)
            else:
                self._refresh_tasks()

    def _on_task_select(self, event):
        selection = self.task_tree.selection()
        if selection:
            item = selection[0]
            task_id = self.task_tree.item(item, "tags")[0]
            task = self.task_manager.get_task(task_id)
            self.selected_task = task
            self._show_task_detail(task)

    def _on_task_double_click(self, event):
        if self.selected_task:
            self._edit_selected_task()

    def _show_task_detail(self, task: Task):
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        detail = f"""标题: {task.title}
ID: {task.task_id}

描述:
{task.description or '无'}

优先级信息:
  重要性: {task.importance}/4
  紧急性: {task.urgency}/4
  难度: {task.difficulty}/4
  综合评分: {task.priority_score:.1f}

时间信息:
  预计时间: {task.estimated_time} 分钟
  截止日期: {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else '无'}
  创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M')}
  更新时间: {task.updated_at.strftime('%Y-%m-%d %H:%M')}

状态: {task.status.value}
标签: {', '.join(task.tags) if task.tags else '无'}
"""
        self.detail_text.insert(1.0, detail)
        self.detail_text.config(state=tk.DISABLED)

    def _show_add_task_dialog(self):
        dialog = TaskDialog(self.root, "新建任务")
        if dialog.result:
            task_data = dialog.result
            task_id = f"task_{int(datetime.now().timestamp())}"
            
            deadline = None
            if task_data.get('deadline'):
                try:
                    deadline = datetime.strptime(task_data['deadline'], '%Y-%m-%d %H:%M')
                except ValueError:
                    pass
            
            task = Task(
                task_id=task_id,
                title=task_data['title'],
                description=task_data.get('description', ''),
                importance=task_data.get('importance', 2),
                urgency=task_data.get('urgency', 2),
                difficulty=task_data.get('difficulty', 2),
                estimated_time=task_data.get('estimated_time', 60),
                deadline=deadline,
                tags=task_data.get('tags', [])
            )
            
            self.task_manager.add_task(task)
            self._refresh_tasks()
            messagebox.showinfo("成功", f"任务 '{task.title}' 已添加")

    def _edit_selected_task(self):
        if not self.selected_task:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
        
        dialog = TaskDialog(self.root, "编辑任务", self.selected_task)
        if dialog.result:
            task_data = dialog.result
            
            updates = {}
            if 'title' in task_data:
                updates['title'] = task_data['title']
            if 'description' in task_data:
                updates['description'] = task_data['description']
            if 'importance' in task_data:
                updates['importance'] = task_data['importance']
            if 'urgency' in task_data:
                updates['urgency'] = task_data['urgency']
            if 'difficulty' in task_data:
                updates['difficulty'] = task_data['difficulty']
            if 'estimated_time' in task_data:
                updates['estimated_time'] = task_data['estimated_time']
            if 'deadline' in task_data and task_data['deadline']:
                try:
                    updates['deadline'] = datetime.strptime(task_data['deadline'], '%Y-%m-%d %H:%M')
                except ValueError:
                    pass
            if 'status' in task_data:
                updates['status'] = TaskStatus(task_data['status'])
            if 'tags' in task_data:
                updates['tags'] = task_data['tags']
            
            self.task_manager.update_task(self.selected_task.task_id, **updates)
            self._refresh_tasks()
            messagebox.showinfo("成功", f"任务 '{self.selected_task.title}' 已更新")

    def _delete_selected_task(self):
        if not self.selected_task:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除任务 '{self.selected_task.title}' 吗？"):
            self.task_manager.delete_task(self.selected_task.task_id)
            self.selected_task = None
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.config(state=tk.DISABLED)
            self._refresh_tasks()

    def _start_focus_mode(self):
        if not self.selected_task:
            messagebox.showwarning("警告", "请先选择一个任务")
            return
        
        duration = simpledialog.askinteger("专注模式", "专注时长（分钟）:", initialvalue=60, minvalue=1, maxvalue=480)
        if duration:
            session = self.focus_mode.create_session(self.selected_task.task_id, duration)
            self.focus_mode.start_session(session.session_id)
            messagebox.showinfo("专注模式", f"已进入专注模式\n任务: {self.selected_task.title}\n时长: {duration} 分钟")

    def _pause_focus_mode(self):
        session = self.focus_mode.pause_session()
        if session:
            messagebox.showinfo("专注模式", "专注模式已暂停")
        else:
            messagebox.showwarning("警告", "没有活动的专注会话")

    def _complete_focus_mode(self):
        session = self.focus_mode.complete_session()
        if session:
            messagebox.showinfo("专注模式", "专注模式已完成")
        else:
            messagebox.showwarning("警告", "没有活动的专注会话")

    def _change_view(self, view_type: str):
        self.current_view = view_type
        if view_type == "list":
            self._refresh_tasks()
        elif view_type == "timeline":
            self._show_timeline_view()
        elif view_type == "matrix":
            self._show_matrix_view()

    def _show_timeline_view(self):
        tasks = [t for t in self.task_manager.get_all_tasks() if t.deadline]
        sorted_tasks = sorted(tasks, key=lambda t: t.deadline)
        
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for task in sorted_tasks:
            self.task_tree.insert("", tk.END, values=(
                task.title,
                f"{task.priority_score:.1f}",
                task.status.value,
                task.deadline.strftime('%Y-%m-%d %H:%M')
            ), tags=(task.task_id,))

    def _show_matrix_view(self):
        tasks = self.task_manager.get_all_tasks()
        matrix = self.priority_algorithm.get_important_urgent_matrix(tasks)
        
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for category, task_list in matrix.items():
            if task_list:
                self.task_tree.insert("", tk.END, values=(
                    f"【{category}】",
                    "",
                    "",
                    ""
                ), tags=())
                
                for task in task_list:
                    self.task_tree.insert("", tk.END, values=(
                        f"  {task.title}",
                        f"{task.priority_score:.1f}",
                        task.status.value,
                        task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else "-"
                    ), tags=(task.task_id,))

    def _show_about(self):
        about_text = """Daily Priority Focus v1.0

智能任务管理工具，帮助您聚焦每日工作优先级。

功能特性：
• 智能任务排序
• 提醒功能
• 专注模式
• 进度跟踪

© 2024 Daily Priority Focus"""
        messagebox.showinfo("关于", about_text)

    def run(self):
        self.root.mainloop()


class TaskDialog:
    def __init__(self, parent, title: str, task: Task = None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets(task)
        
        self.dialog.wait_window()

    def _create_widgets(self, task: Task = None):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="标题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=task.title if task else "")
        ttk.Entry(main_frame, textvariable=self.title_var, width=50).grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="描述:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(main_frame, width=50, height=5)
        self.description_text.grid(row=1, column=1, sticky=tk.EW, pady=5)
        if task:
            self.description_text.insert(1.0, task.description)
        
        ttk.Label(main_frame, text="重要性 (1-4):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.importance_var = tk.IntVar(value=task.importance if task else 2)
        ttk.Scale(main_frame, from_=1, to=4, variable=self.importance_var, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="紧急性 (1-4):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.urgency_var = tk.IntVar(value=task.urgency if task else 2)
        ttk.Scale(main_frame, from_=1, to=4, variable=self.urgency_var, orient=tk.HORIZONTAL).grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="难度 (1-4):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.difficulty_var = tk.IntVar(value=task.difficulty if task else 2)
        ttk.Scale(main_frame, from_=1, to=4, variable=self.difficulty_var, orient=tk.HORIZONTAL).grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="预计时间（分钟）:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.IntVar(value=task.estimated_time if task else 60)
        ttk.Spinbox(main_frame, from_=5, to=480, textvariable=self.time_var, width=10).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="截止日期 (YYYY-MM-DD HH:MM):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.deadline_var = tk.StringVar(value=task.deadline.strftime('%Y-%m-%d %H:%M') if task and task.deadline else "")
        ttk.Entry(main_frame, textvariable=self.deadline_var, width=20).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="状态:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value=task.status.value if task else "pending")
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var, 
                                   values=["pending", "in_progress", "completed", "cancelled"], 
                                   state="readonly", width=15)
        status_combo.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="标签（用逗号分隔）:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.tags_var = tk.StringVar(value=', '.join(task.tags) if task and task.tags else "")
        ttk.Entry(main_frame, textvariable=self.tags_var, width=50).grid(row=8, column=1, sticky=tk.EW, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self._on_cancel).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)

    def _on_ok(self):
        tags = [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()]
        
        self.result = {
            'title': self.title_var.get(),
            'description': self.description_text.get(1.0, tk.END).strip(),
            'importance': self.importance_var.get(),
            'urgency': self.urgency_var.get(),
            'difficulty': self.difficulty_var.get(),
            'estimated_time': self.time_var.get(),
            'deadline': self.deadline_var.get(),
            'status': self.status_var.get(),
            'tags': tags
        }
        
        if not self.result['title']:
            messagebox.showwarning("警告", "标题不能为空")
            return
        
        self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()


def main():
    app = GUIInterface()
    app.run()


if __name__ == "__main__":
    main()
