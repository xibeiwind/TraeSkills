import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PriorityWeights:
    importance: float = 0.30
    urgency: float = 0.25
    difficulty: float = 0.20
    time: float = 0.15
    dependencies: float = 0.10

    def validate(self):
        total = sum(asdict(self).values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"权重总和必须为1.0，当前为{total}")


@dataclass
class ReminderSettings:
    enabled: bool = True
    check_interval: int = 60
    default_reminder_times: list = None
    reminder_sound: bool = True
    reminder_notification: bool = True

    def __post_init__(self):
        if self.default_reminder_times is None:
            self.default_reminder_times = [60, 1440, 4320]


@dataclass
class FocusModeSettings:
    default_duration: int = 60
    break_reminder_interval: int = 25
    break_duration: int = 5
    auto_start_break: bool = True
    block_notifications: bool = True
    focus_sound_enabled: bool = True


@dataclass
class UISettings:
    default_view: str = "list"
    theme: str = "light"
    language: str = "zh-CN"
    show_completed_tasks: bool = True
    task_list_limit: int = 50


@dataclass
class IntegrationSettings:
    calendar_enabled: bool = False
    calendar_type: str = "local"
    todo_enabled: bool = False
    todo_type: str = "local"
    todoist_api_token: Optional[str] = None
    auto_sync: bool = False
    sync_interval: int = 3600


@dataclass
class VoiceSettings:
    enabled: bool = False
    language: str = "zh-CN"
    voice_rate: int = 200
    voice_volume: float = 0.9
    voice_id: Optional[str] = None


@dataclass
class Settings:
    priority_weights: PriorityWeights = None
    reminder_settings: ReminderSettings = None
    focus_mode_settings: FocusModeSettings = None
    ui_settings: UISettings = None
    integration_settings: IntegrationSettings = None
    voice_settings: VoiceSettings = None

    def __post_init__(self):
        if self.priority_weights is None:
            self.priority_weights = PriorityWeights()
        if self.reminder_settings is None:
            self.reminder_settings = ReminderSettings()
        if self.focus_mode_settings is None:
            self.focus_mode_settings = FocusModeSettings()
        if self.ui_settings is None:
            self.ui_settings = UISettings()
        if self.integration_settings is None:
            self.integration_settings = IntegrationSettings()
        if self.voice_settings is None:
            self.voice_settings = VoiceSettings()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority_weights": asdict(self.priority_weights),
            "reminder_settings": asdict(self.reminder_settings),
            "focus_mode_settings": asdict(self.focus_mode_settings),
            "ui_settings": asdict(self.ui_settings),
            "integration_settings": asdict(self.integration_settings),
            "voice_settings": asdict(self.voice_settings)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        return cls(
            priority_weights=PriorityWeights(**data.get("priority_weights", {})),
            reminder_settings=ReminderSettings(**data.get("reminder_settings", {})),
            focus_mode_settings=FocusModeSettings(**data.get("focus_mode_settings", {})),
            ui_settings=UISettings(**data.get("ui_settings", {})),
            integration_settings=IntegrationSettings(**data.get("integration_settings", {})),
            voice_settings=VoiceSettings(**data.get("voice_settings", {}))
        )


class SettingsManager:
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "..", "..", "config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.settings = Settings()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = Settings.from_dict(data)
            except Exception as e:
                print(f"加载设置失败: {e}")
                self.settings = Settings()

    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def get_settings(self) -> Settings:
        return self.settings

    def update_settings(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save_settings()

    def reset_to_defaults(self):
        self.settings = Settings()
        self.save_settings()

    def export_settings(self, file_path: str):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出设置失败: {e}")
            return False

    def import_settings(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.settings = Settings.from_dict(data)
                self.save_settings()
            return True
        except Exception as e:
            print(f"导入设置失败: {e}")
            return False

    def get_priority_weights(self) -> Dict[str, float]:
        return asdict(self.settings.priority_weights)

    def update_priority_weights(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.settings.priority_weights, key):
                setattr(self.settings.priority_weights, key, value)
        self.settings.priority_weights.validate()
        self.save_settings()

    def get_reminder_settings(self) -> ReminderSettings:
        return self.settings.reminder_settings

    def get_focus_mode_settings(self) -> FocusModeSettings:
        return self.settings.focus_mode_settings

    def get_ui_settings(self) -> UISettings:
        return self.settings.ui_settings

    def get_integration_settings(self) -> IntegrationSettings:
        return self.settings.integration_settings

    def get_voice_settings(self) -> VoiceSettings:
        return self.settings.voice_settings


def get_default_settings() -> Settings:
    return Settings()


def create_sample_settings_file(output_path: str):
    settings = Settings()
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"创建示例设置文件失败: {e}")
        return False
