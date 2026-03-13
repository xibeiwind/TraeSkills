import speech_recognition as sr
import pyttsx3
from typing import Dict, List, Optional, Callable
from datetime import datetime
from ..core.task_manager import TaskManager, Task, TaskStatus
from ..core.priority_algorithm import PriorityAlgorithm


class VoiceInterface:
    def __init__(self, task_manager: TaskManager = None,
                 priority_algorithm: PriorityAlgorithm = None):
        self.task_manager = task_manager or TaskManager()
        self.priority_algorithm = priority_algorithm or PriorityAlgorithm()
        
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
        self.commands = {
            'add': self._handle_add_command,
            'list': self._handle_list_command,
            'show': self._handle_show_command,
            'update': self._handle_update_command,
            'delete': self._handle_delete_command,
            'start': self._handle_start_command,
            'pause': self._handle_pause_command,
            'complete': self._handle_complete_command,
            'stats': self._handle_stats_command,
            'search': self._handle_search_command,
            'help': self._handle_help_command,
            'exit': self._handle_exit_command
        }
        
        self.running = False
        self.callbacks: List[Callable] = []

    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def speak(self, text: str):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"语音合成错误: {e}")
            print(f"文本: {text}")

    def listen(self, timeout: int = 5) -> Optional[str]:
        with sr.Microphone() as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                return text.lower()
            except sr.WaitTimeoutError:
                self.speak("没有听到您的声音，请重试")
                return None
            except sr.UnknownValueError:
                self.speak("无法识别您的语音，请重试")
                return None
            except sr.RequestError as e:
                self.speak("语音识别服务不可用")
                print(f"语音识别错误: {e}")
                return None
            except Exception as e:
                print(f"监听错误: {e}")
                return None

    def start(self):
        self.running = True
        self.speak("欢迎使用每日优先级聚焦系统。请说出您的指令，或者说'帮助'查看可用指令。")
        
        while self.running:
            try:
                user_input = self.listen()
                if user_input:
                    self._process_command(user_input)
            except KeyboardInterrupt:
                self.speak("再见！")
                self.running = False
            except Exception as e:
                print(f"处理错误: {e}")
                self.speak("发生错误，请重试")

    def stop(self):
        self.running = False

    def _process_command(self, user_input: str):
        command = self._parse_command(user_input)
        
        if command:
            command_name = command.get('command')
            params = command.get('params', {})
            
            handler = self.commands.get(command_name)
            if handler:
                try:
                    handler(params)
                except Exception as e:
                    self.speak(f"处理命令时出错: {str(e)}")
            else:
                self.speak(f"未知命令: {command_name}。请说'帮助'查看可用命令。")
        else:
            self.speak("无法理解您的指令，请重试或说'帮助'查看可用命令。")

    def _parse_command(self, user_input: str) -> Optional[Dict]:
        user_input = user_input.strip()
        
        if '添加' in user_input or '新建' in user_input or 'add' in user_input:
            return self._parse_add_command(user_input)
        elif '列表' in user_input or '查看' in user_input or 'list' in user_input:
            return self._parse_list_command(user_input)
        elif '显示' in user_input or '详情' in user_input or 'show' in user_input:
            return self._parse_show_command(user_input)
        elif '更新' in user_input or '修改' in user_input or 'update' in user_input:
            return self._parse_update_command(user_input)
        elif '删除' in user_input or 'delete' in user_input:
            return self._parse_delete_command(user_input)
        elif '开始' in user_input or '启动' in user_input or 'start' in user_input:
            return {'command': 'start', 'params': {}}
        elif '暂停' in user_input or 'pause' in user_input:
            return {'command': 'pause', 'params': {}}
        elif '完成' in user_input or 'complete' in user_input:
            return {'command': 'complete', 'params': {}}
        elif '统计' in user_input or 'stats' in user_input:
            return {'command': 'stats', 'params': {}}
        elif '搜索' in user_input or 'search' in user_input:
            return self._parse_search_command(user_input)
        elif '帮助' in user_input or 'help' in user_input:
            return {'command': 'help', 'params': {}}
        elif '退出' in user_input or 'exit' in user_input or '再见' in user_input:
            return {'command': 'exit', 'params': {}}
        
        return None

    def _parse_add_command(self, user_input: str) -> Dict:
        params = {}
        
        if '重要' in user_input:
            if '非常' in user_input:
                params['importance'] = 4
            else:
                params['importance'] = 3
        elif '不重要' in user_input:
            params['importance'] = 1
        else:
            params['importance'] = 2
        
        if '紧急' in user_input:
            if '非常' in user_input:
                params['urgency'] = 4
            else:
                params['urgency'] = 3
        elif '不紧急' in user_input:
            params['urgency'] = 1
        else:
            params['urgency'] = 2
        
        if '困难' in user_input:
            if '非常' in user_input:
                params['difficulty'] = 4
            else:
                params['difficulty'] = 3
        elif '简单' in user_input:
            params['difficulty'] = 1
        else:
            params['difficulty'] = 2
        
        task_title = user_input.replace('添加', '').replace('新建', '').replace('add', '')
        task_title = task_title.replace('重要', '').replace('不重要', '')
        task_title = task_title.replace('紧急', '').replace('不紧急', '')
        task_title = task_title.replace('困难', '').replace('简单', '')
        task_title = task_title.replace('非常', '').replace('任务', '')
        task_title = task_title.strip()
        
        params['title'] = task_title
        
        return {'command': 'add', 'params': params}

    def _parse_list_command(self, user_input: str) -> Dict:
        params = {}
        
        if '待处理' in user_input or 'pending' in user_input:
            params['status'] = 'pending'
        elif '进行中' in user_input or 'in_progress' in user_input:
            params['status'] = 'in_progress'
        elif '已完成' in user_input or 'completed' in user_input:
            params['status'] = 'completed'
        
        return {'command': 'list', 'params': params}

    def _parse_show_command(self, user_input: str) -> Dict:
        params = {}
        
        if '第一个' in user_input:
            tasks = self.priority_algorithm.sort_tasks_by_priority(self.task_manager.get_all_tasks())
            if tasks:
                params['task_id'] = tasks[0].task_id
        elif '第二个' in user_input:
            tasks = self.priority_algorithm.sort_tasks_by_priority(self.task_manager.get_all_tasks())
            if len(tasks) >= 2:
                params['task_id'] = tasks[1].task_id
        elif '第三个' in user_input:
            tasks = self.priority_algorithm.sort_tasks_by_priority(self.task_manager.get_all_tasks())
            if len(tasks) >= 3:
                params['task_id'] = tasks[2].task_id
        
        return {'command': 'show', 'params': params}

    def _parse_update_command(self, user_input: str) -> Dict:
        return {'command': 'update', 'params': {}}

    def _parse_delete_command(self, user_input: str) -> Dict:
        return {'command': 'delete', 'params': {}}

    def _parse_search_command(self, user_input: str) -> Dict:
        query = user_input.replace('搜索', '').replace('search', '').strip()
        return {'command': 'search', 'params': {'query': query}}

    def _handle_add_command(self, params: Dict):
        title = params.get('title', '新任务')
        importance = params.get('importance', 2)
        urgency = params.get('urgency', 2)
        difficulty = params.get('difficulty', 2)
        
        task_id = f"task_{int(datetime.now().timestamp())}"
        task = Task(
            task_id=task_id,
            title=title,
            importance=importance,
            urgency=urgency,
            difficulty=difficulty
        )
        
        self.task_manager.add_task(task)
        priority_score = task.calculate_priority_score(self.priority_algorithm.weights)
        
        self.speak(f"已添加任务：{title}，优先级评分：{priority_score:.1f}")

    def _handle_list_command(self, params: Dict):
        tasks = self.task_manager.get_all_tasks()
        status = params.get('status')
        
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        
        sorted_tasks = self.priority_algorithm.sort_tasks_by_priority(tasks)
        
        if not sorted_tasks:
            self.speak("没有找到任务")
            return
        
        self.speak(f"找到 {len(sorted_tasks)} 个任务：")
        for i, task in enumerate(sorted_tasks[:5], 1):
            self.speak(f"第{i}个：{task.title}，优先级 {task.priority_score:.1f}")

    def _handle_show_command(self, params: Dict):
        task_id = params.get('task_id')
        
        if not task_id:
            self.speak("请指定要显示的任务")
            return
        
        task = self.task_manager.get_task(task_id)
        if not task:
            self.speak("未找到该任务")
            return
        
        detail = f"任务详情：{task.title}。重要性：{task.importance}，紧急性：{task.urgency}，难度：{task.difficulty}。优先级评分：{task.priority_score:.1f}"
        if task.deadline:
            detail += f"。截止日期：{task.deadline.strftime('%Y年%m月%d日 %H点%M分')}"
        
        self.speak(detail)

    def _handle_update_command(self, params: Dict):
        self.speak("更新功能需要更多信息，请使用图形界面或命令行界面")

    def _handle_delete_command(self, params: Dict):
        self.speak("删除功能需要更多信息，请使用图形界面或命令行界面")

    def _handle_start_command(self, params: Dict):
        tasks = self.priority_algorithm.sort_tasks_by_priority(
            [t for t in self.task_manager.get_all_tasks() if t.status == TaskStatus.PENDING]
        )
        
        if not tasks:
            self.speak("没有待处理的任务")
            return
        
        task = tasks[0]
        self.speak(f"开始专注任务：{task.title}")
        
        for callback in self.callbacks:
            try:
                callback('start_focus', {'task_id': task.task_id})
            except Exception as e:
                print(f"回调错误: {e}")

    def _handle_pause_command(self, params: Dict):
        self.speak("专注模式已暂停")
        
        for callback in self.callbacks:
            try:
                callback('pause_focus', {})
            except Exception as e:
                print(f"回调错误: {e}")

    def _handle_complete_command(self, params: Dict):
        self.speak("专注模式已完成")
        
        for callback in self.callbacks:
            try:
                callback('complete_focus', {})
            except Exception as e:
                print(f"回调错误: {e}")

    def _handle_stats_command(self, params: Dict):
        stats = self.task_manager.get_task_statistics()
        
        stats_text = f"任务统计：总任务数 {stats['total_tasks']} 个，已完成 {stats['completed_tasks']} 个，进行中 {stats['in_progress_tasks']} 个，待处理 {stats['pending_tasks']} 个。完成率 {stats['completion_rate']:.1f}%"
        
        self.speak(stats_text)

    def _handle_search_command(self, params: Dict):
        query = params.get('query', '')
        
        if not query:
            self.speak("请提供搜索关键词")
            return
        
        tasks = self.task_manager.search_tasks(query)
        
        if not tasks:
            self.speak(f"未找到包含 '{query}' 的任务")
            return
        
        self.speak(f"找到 {len(tasks)} 个匹配的任务：")
        for i, task in enumerate(tasks[:3], 1):
            self.speak(f"第{i}个：{task.title}")

    def _handle_help_command(self, params: Dict):
        help_text = """可用命令：
添加任务：说"添加 [任务名称]"，可以加上"重要"、"紧急"、"困难"等描述
查看任务：说"列表"或"查看任务"
显示详情：说"显示第一个任务"或"显示任务详情"
开始专注：说"开始"或"开始专注"
暂停专注：说"暂停"
完成专注：说"完成"
查看统计：说"统计"或"查看统计"
搜索任务：说"搜索 [关键词]"
帮助：说"帮助"
退出：说"退出"或"再见"
"""
        self.speak("以下是可用命令：添加任务、查看任务、显示详情、开始专注、暂停、完成、查看统计、搜索任务、帮助、退出")

    def _handle_exit_command(self, params: Dict):
        self.speak("再见！")
        self.running = False

    def set_voice_properties(self, rate: int = None, volume: float = None):
        if rate:
            self.engine.setProperty('rate', rate)
        if volume:
            self.engine.setProperty('volume', volume)

    def get_available_voices(self) -> List[str]:
        voices = self.engine.getProperty('voices')
        return [voice.id for voice in voices]

    def set_voice(self, voice_id: str):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice.id == voice_id:
                self.engine.setProperty('voice', voice.id)
                break


def main():
    voice_interface = VoiceInterface()
    voice_interface.start()


if __name__ == "__main__":
    main()
