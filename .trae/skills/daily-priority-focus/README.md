# Daily Priority Focus - 每日工作优先级聚焦技能

一个智能的任务管理工具，帮助您聚焦每日工作优先级，提高工作效率。

## 功能特性

### 核心功能
- **智能任务排序**：基于综合评分算法（重要性、紧急性、难度、时间）自动排序任务
- **提醒功能**：在任务截止前或特定时间提醒用户
- **专注模式**：提供专注模式，屏蔽干扰，专注于当前任务
- **进度跟踪**：跟踪任务完成进度和效率统计

### 交互方式
- **命令行界面 (CLI)**：快速操作和自动化
- **图形界面 (GUI)**：可视化的任务管理和优先级展示
- **语音交互**：通过语音命令与技能交互

### 任务收集方式
- **手动输入**：用户手动输入任务信息
- **语音录入**：通过语音录入任务信息
- **从其他应用同步**：从待办事项应用（如Todoist、Microsoft To Do等）同步任务

### 展示方式
- **列表形式**：以列表形式展示任务，清晰易读
- **时间轴**：以时间轴形式展示任务，直观显示时间安排
- **重要紧急矩阵**：使用四象限矩阵分类任务
- **可视化图表**：使用图表（饼图、柱状图等）可视化展示任务分布

### 集成功能
- **日历应用集成**：与日历应用集成，同步日程安排
- **待办事项软件集成**：与待办事项软件（如Todoist、Microsoft To Do等）集成

## 安装

### 依赖项

```bash
pip install speechrecognition pyttsx3 requests
```

### 安装技能

技能已经安装在 `.trae/skills/daily-priority-focus/` 目录下。

## 使用方法

### 命令行界面

```bash
# 添加任务
python -m .trae.skills.daily-priority-focus add "完成项目报告" --importance high --urgency medium --difficulty medium

# 查看任务列表
python -m .trae.skills.daily-priority-focus list --view timeline

# 进入专注模式
python -m .trae.skills.daily-priority-focus focus --task-id task_123 --duration 60

# 查看进度统计
python -m .trae.skills.daily-priority-focus stats --period week
```

### 图形界面

```bash
python -m .trae.skills.daily-priority-focus --interface gui
```

### 语音交互

```bash
python -m .trae.skills.daily-priority-focus --interface voice
```

## 优先级算法

技能使用综合评分算法来确定任务优先级，考虑以下因素：

1. **重要性**（权重：30%）：任务的重要程度
2. **紧急性**（权重：25%）：任务的紧急程度和截止日期
3. **难度**（权重：20%）：任务的难度和复杂度
4. **时间**（权重：15%）：任务预计完成时间
5. **依赖关系**（权重：10%）：任务之间的依赖关系

## 文件结构

```
.trae/skills/daily-priority-focus/
├── SKILL.md                      # 技能描述文件
├── __init__.py                   # 主模块
├── core/                         # 核心功能模块
│   ├── task_manager.py          # 任务管理核心模块
│   ├── priority_algorithm.py    # 优先级算法
│   ├── reminder_system.py       # 提醒系统
│   └── focus_mode.py            # 专注模式
├── ui/                           # 用户界面模块
│   ├── cli.py                   # 命令行界面
│   ├── gui.py                   # 图形界面
│   └── voice.py                 # 语音交互
├── integrations/                 # 集成模块
│   ├── calendar.py              # 日历集成
│   └── todo_apps.py             # 待办事项应用集成
├── config/                       # 配置模块
│   ├── settings.py              # 配置文件
│   └── templates.py             # 模板文件
└── utils/                        # 工具模块
    ├── display.py               # 展示工具
    └── analytics.py             # 分析工具
```

## 配置

您可以通过配置文件自定义以下选项：

- 优先级算法权重
- 提醒时间和方式
- 专注模式设置
- 界面主题和布局
- 集成应用配置

配置文件位于 `config/settings.json`。

## 模板

技能提供了多种模板来帮助您快速创建任务：

### 任务模板
- 工作任务模板（会议、报告、邮件、演示文稿、审查）
- 学习任务模板（阅读、作业、研究、练习）
- 个人任务模板（运动、购物、清洁、预约）

### 优先级预设
- 紧急重要
- 重要不紧急
- 紧急不重要
- 不紧急不重要
- 快速任务
- 复杂任务

### 专注会话模板
- 番茄钟（25分钟专注，5分钟休息）
- 深度工作（90分钟深度工作，每45分钟休息10分钟）
- 短时专注（15分钟专注，3分钟休息）
- 长时会话（2小时工作，每小时休息15分钟）
- 早晨例程（1小时早晨工作，每30分钟休息5分钟）

## 最佳实践

1. **每日规划**：每天开始时，使用技能查看和规划任务
2. **定期更新**：定期更新任务状态和进度
3. **专注模式**：利用专注模式提高工作效率
4. **查看统计**：定期查看进度统计，优化工作流程
5. **保持同步**：保持与日历和待办事项应用的同步

## API 使用示例

```python
from .trae.skills.daily-priority_focus import DailyPriorityFocus, Task, TaskStatus

# 初始化
dpf = DailyPriorityFocus()

# 创建任务
task = Task(
    task_id="task_001",
    title="完成项目报告",
    description="撰写Q4季度项目报告",
    importance=4,
    urgency=3,
    difficulty=3,
    estimated_time=120
)
dpf.add_task(task)

# 获取排序后的任务
sorted_tasks = dpf.get_sorted_tasks()

# 开始专注模式
dpf.start_focus_mode("task_001", duration_minutes=60)

# 生成报告
daily_report = dpf.generate_daily_report()
print(daily_report)

# 生成洞察
insights = dpf.generate_insights()
print(insights)
```

## 注意事项

- 首次使用需要配置集成应用
- 语音交互需要麦克风权限
- 专注模式期间会屏蔽通知
- 建议定期备份数据
- 确保系统时间准确，以便正确计算截止日期

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求！

## 联系方式

如有问题或建议，请联系开发团队。
