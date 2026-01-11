import os
from datetime import time, datetime
from typing import Tuple
import win32api
from pydantic import BaseModel, field_validator, Field, model_validator
from dotenv import load_dotenv

ENV_PATH = "data/.env"
DEFAULT_ENV = {
    "COLOR_NORMAL": "208,208,208",
    "COLOR_GRADIENT_BOTTOM": "176,176,176",
    "COLOR_WARNING": "255,160,80",
    "COLOR_WARNING_THRESHOLD": "60",
    "COLOR_CRITICAL": "255,100,100",
    "COLOR_CRITICAL_THRESHOLD": "30",
    "SLIDE_MODE_DEFAULT_DURATION": "8",
    "NORMAL_MODE_DEFAULT_DURATION": "5",
    "COW_MODE_ODD_WEEK_LUNCH_TIME": "11:40",
    "COW_MODE_EVEN_WEEK_LUNCH_TIME": "11:55",
    "COW_MODE_AFTERNOON_OFF_TIME": "20:00",
    "COW_MODE_MOONING_ON_TIME": "8:30",
    "COW_INCOME_PER_MONTH": "3000",
    "COW_WORKING_DAYS_PER_MONTH": "25",
    "BALL_SIZE": '120'
}

if not os.path.exists(ENV_PATH):
    print(f"[INFO] 未找到 .env 文件，正在创建默认配置: {ENV_PATH}")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for k, v in DEFAULT_ENV.items():
            f.write(f"{k}={v}\n")

load_dotenv(ENV_PATH)


def reset_config():
    """
    重置 .env 配置文件为默认值
    """
    try:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            for k, v in DEFAULT_ENV.items():
                f.write(f"{k}={v}\n")

        load_dotenv(ENV_PATH)

        win32api.MessageBox(0, '配置已重置！重启软件生效！', '成功', 0)

    except Exception as e:
        print(f"[ERROR] 重置配置失败: {e}")


def preprocess_str(text):
    """标准化输入：中文标点转英文"""
    return text.replace("：", ":").replace("，", ",")


# ====== 独立校验函数（供 UI 复用）======
def validate_time_format(value: str) -> bool:
    try:
        datetime.strptime(preprocess_str(value), "%H:%M")
        return True
    except ValueError:
        return False


def validate_int_range(value: str, min_val: int = None, max_val: int = None) -> bool:
    try:
        v = int(value)
        if min_val is not None and v < min_val:
            return False
        if max_val is not None and v > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False


def validate_rgb_string(value: str) -> bool:
    try:
        parts = [int(x.strip()) for x in preprocess_str(value).split(",")]
        if len(parts) != 3:
            return False
        return all(0 <= c <= 255 for c in parts)
    except (ValueError, AttributeError):
        return False


class RGBColor(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)

    @classmethod
    def from_string(cls, value: str) -> 'RGBColor':
        value = preprocess_str(value)
        parts = [int(x.strip()) for x in value.split(",")]
        if len(parts) != 3:
            raise ValueError("RGB值必须包含3个数字")
        return cls(r=parts[0], g=parts[1], b=parts[2])

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)


class CountdownConfig(BaseModel):
    # 颜色配置（字符串格式 "r,g,b"）
    color_normal: str = Field(default="208,208,208")
    color_gradient_bottom: str = Field(default="176,176,176")
    color_warning: str = Field(default="255,160,80")
    color_critical: str = Field(default="255,100,100")

    # 阈值（秒）
    color_warning_threshold: int = Field(default=60, ge=0, le=3600)
    color_critical_threshold: int = Field(default=30, ge=0, le=3600)

    # 默认倒计时时长（分钟）
    slide_mode_default_duration: int = Field(default=8, ge=1, le=120)
    normal_mode_default_duration: int = Field(default=5, ge=1, le=120)

    # 时间配置（字符串 HH:MM）
    cow_mode_odd_week_lunch_time: str = Field(default="11:40")
    cow_mode_even_week_lunch_time: str = Field(default="11:55")
    cow_mode_afternoon_off_time: str = Field(default="20:00")
    cow_mode_mooning_on_time: str = Field(default="8:30")

    cow_income_per_month: int = Field(default="3000")  #
    cow_working_days_per_month: int = Field(default=25, ge=1, le=31)

    # 球体大小
    ball_size: int = Field(default=120, ge=1, le=500)

    # ----- 字段级校验 -----
    @field_validator(
        'cow_mode_odd_week_lunch_time',
        'cow_mode_even_week_lunch_time',
        'cow_mode_afternoon_off_time',
        'cow_mode_mooning_on_time'
    )
    def validate_time_format(cls, v):
        v = preprocess_str(v)
        try:
            datetime.strptime(v, '%H:%M')
        except ValueError:
            raise ValueError(f'时间格式无效: {v}，应为 HH:MM 格式')
        return v

    # ----- 模型级校验（所有字段加载完成后执行）-----
    @model_validator(mode='after')
    def validate_thresholds_vs_durations(self):
        warn = self.color_warning_threshold
        crit = self.color_critical_threshold
        slide_dur = self.slide_mode_default_duration
        normal_dur = self.normal_mode_default_duration

        # 计算最大倒计时时长（秒）
        max_duration_sec = max(slide_dur, normal_dur) * 60

        # 校验逻辑
        if crit >= warn:
            raise ValueError('临界阈值必须小于警告阈值')
        if warn >= max_duration_sec:
            raise ValueError(
                f'警告阈值（{warn}秒）必须小于最大倒计时时长（{max_duration_sec}秒）'
            )
        if crit >= max_duration_sec:
            raise ValueError(
                f'临界阈值（{crit}秒）必须小于最大倒计时时长（{max_duration_sec}秒）'
            )
        return self

    # ----- 辅助方法 -----
    def get_color_tuple(self, color_attr: str) -> Tuple[int, int, int]:
        color_str = getattr(self, color_attr)
        return RGBColor.from_string(color_str).to_tuple()

    def get_time_value(self, time_attr: str) -> time:
        time_str = getattr(self, time_attr)
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)


def load_config() -> CountdownConfig:
    try:
        config_data = {}
        for field_name in CountdownConfig.model_fields:
            env_value = os.getenv(field_name.upper())
            if env_value is not None:
                config_data[field_name] = env_value
        return CountdownConfig(**config_data)
    except Exception as e:
        print(f"[ERROR] 配置验证失败，使用默认配置: {e}")
        return CountdownConfig()
