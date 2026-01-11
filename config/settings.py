
from config.env import load_config

class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config = load_config()
        self.COLOR_NORMAL = config.get_color_tuple('color_normal')
        self.COLOR_GRADIENT_BOTTOM = config.get_color_tuple('color_gradient_bottom')
        self.COLOR_WARNING = config.get_color_tuple('color_warning')
        self.COLOR_CRITICAL = config.get_color_tuple('color_critical')
        self.WARNING_THRESHOLD = config.color_warning_threshold
        self.CRITICAL_THRESHOLD = config.color_critical_threshold
        self.SLIDE_MODE_DEFAULT_DURATION = config.slide_mode_default_duration
        self.NORMAL_MODE_DEFAULT_DURATION = config.normal_mode_default_duration
        self.COW_MODE_ODD_WEEK_LUNCH_TIME = config.get_time_value('cow_mode_odd_week_lunch_time')
        self.COW_MODE_EVEN_WEEK_LUNCH_TIME = config.get_time_value('cow_mode_even_week_lunch_time')
        self.COW_MODE_AFTERNOON_OFF_TIME = config.get_time_value('cow_mode_afternoon_off_time')
        self.COW_MODE_MOONING_ON_TIME = config.get_time_value('cow_mode_mooning_on_time')
        self.INCOME_PER_MONTH = config.cow_income_per_month
        self.WORKING_DAYS_PER_MONTH = config.cow_working_days_per_month
        self.BALL_SIZE = config.ball_size

    def reload(self):
        """重新加载配置"""
        self._load_config()

    def get(self, key, default=None):
        """
        获取配置项的值

        Args:
            key (str): 配置项名称
            default: 默认值

        Returns:
            配置项的值，如果不存在则返回默认值
        """
        return getattr(self, key, default)


# 创建单例实例
APP_CONFIG = AppConfig()