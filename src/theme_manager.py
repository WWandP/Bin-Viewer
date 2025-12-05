# 主题管理器
import json
import os
import sys
from .config import Config

class ThemeManager:
    _instance = None
    _current_theme = "dark_cyber"
    _config_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        """初始化配置文件路径"""
        if hasattr(sys, '_MEIPASS'):
            config_dir = os.path.expanduser("~/.binviewer")
        else:
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        self._config_file = os.path.join(config_dir, "theme_config.json")
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._current_theme = config.get('theme', 'embedded')
        except Exception:
            self._current_theme = 'embedded'
    
    def _save_config(self):
        """保存配置"""
        try:
            config = {'theme': self._current_theme}
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def get_theme(self):
        """获取当前主题"""
        return self._current_theme
    
    def set_theme(self, theme):
        """设置主题"""
        if theme in THEMES:
            self._current_theme = theme
            self._save_config()
    
    def get_theme_names(self):
        """获取所有主题名称"""
        return list(THEMES.keys())
    
    def get_theme_display_names(self):
        """获取主题显示名称"""
        from .language_manager import language_manager
        current_lang = language_manager.get_language()
        return [THEME_NAMES[theme][current_lang] for theme in THEMES.keys()]
    
    def generate_style(self, dpi):
        """生成当前主题的样式"""
        # 兼容旧主题名称
        if self._current_theme not in THEMES:
            self._current_theme = 'embedded'
            self._save_config()
        theme = THEMES[self._current_theme]
        return theme['generator'](dpi)

# 主题样式生成器
def generate_embedded_style(dpi):
    """嵌入式风格主题"""
    scaled_font_size = Config.get_scaled_font_size(11, dpi)
    scaled_small_font = Config.get_scaled_font_size(10, dpi)
    scaled_btn_padding = Config.get_scaled_value(6, dpi)
    scaled_border_radius = Config.get_scaled_value(3, dpi)
    
    return f"""
QWidget {{
    font-family: 'Microsoft YaHei UI', 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    font-size: {scaled_font_size}px;
    color: #c9d1d9;
    background-color: #0d1117;
    font-weight: 400;
}}

QMainWindow {{
    border: 1px solid #30363d;
    background-color: #0d1117;
}}

QPushButton {{
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: {scaled_border_radius}px;
    padding: {scaled_btn_padding}px {Config.get_scaled_value(12, dpi)}px;
    min-height: {Config.get_scaled_value(28, dpi)}px;
    color: #c9d1d9;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #30363d;
    border-color: #58a6ff;
}}

QPushButton#PrimaryButton {{
    background-color: #238636;
    border-color: #238636;
    color: #ffffff;
}}

QPushButton#PrimaryButton:hover {{
    background-color: #2ea043;
    border-color: #2ea043;
}}

QComboBox {{
    border: 1px solid #30363d;
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(4, dpi)}px {Config.get_scaled_value(8, dpi)}px;
    min-width: {Config.get_scaled_value(100, dpi)}px;
    min-height: {Config.get_scaled_value(24, dpi)}px;
    background-color: #21262d;
    color: #c9d1d9;
}}

QComboBox:hover {{
    border-color: #58a6ff;
}}

QGroupBox {{
    border: 1px solid #30363d;
    border-radius: {Config.get_scaled_value(6, dpi)}px;
    margin-top: {Config.get_scaled_value(8, dpi)}px;
    padding-top: {Config.get_scaled_value(12, dpi)}px;
    background-color: #161b22;
    color: #f0f6fc;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: {Config.get_scaled_value(8, dpi)}px;
    padding: 0 {Config.get_scaled_value(5, dpi)}px;
    color: #58a6ff;
}}

QLabel#DropLabel {{
    border: 2px dashed #30363d;
    border-radius: {Config.get_scaled_value(6, dpi)}px;
    padding: {Config.get_scaled_value(25, dpi)}px;
    color: #8b949e;
    margin: {Config.get_scaled_value(12, dpi)}px;
    font-size: {scaled_small_font}px;
    background-color: #161b22;
}}

QLabel#DropLabel:hover {{
    border-color: #58a6ff;
    color: #58a6ff;
}}

QSpinBox, QLineEdit {{
    border: 1px solid #30363d;
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(4, dpi)}px {Config.get_scaled_value(8, dpi)}px;
    background-color: #0d1117;
    color: #c9d1d9;
}}

QSpinBox:focus, QLineEdit:focus {{
    border-color: #58a6ff;
}}
"""

def generate_ai_style(dpi):
    """AI风格主题"""
    scaled_font_size = Config.get_scaled_font_size(11, dpi)
    scaled_small_font = Config.get_scaled_font_size(10, dpi)
    scaled_btn_padding = Config.get_scaled_value(8, dpi)
    scaled_border_radius = Config.get_scaled_value(8, dpi)
    
    return f"""
QWidget {{
    font-family: 'Microsoft YaHei UI', 'SF Pro Display', 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: {scaled_font_size}px;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
    font-weight: 400;
}}

QMainWindow {{
    border: none;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
}}

QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #667eea, stop:1 #764ba2);
    border: none;
    border-radius: {scaled_border_radius}px;
    padding: {scaled_btn_padding}px {Config.get_scaled_value(16, dpi)}px;
    min-height: {Config.get_scaled_value(32, dpi)}px;
    color: #ffffff;
    font-weight: 600;
    font-size: {scaled_font_size}px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c8cff, stop:1 #8a5fbf);
}}

QPushButton#PrimaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ff6b6b, stop:1 #ffa726);
}}

QPushButton#PrimaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ff8a80, stop:1 #ffb74d);
}}

QComboBox {{
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(6, dpi)}px {Config.get_scaled_value(12, dpi)}px;
    min-width: {Config.get_scaled_value(100, dpi)}px;
    min-height: {Config.get_scaled_value(28, dpi)}px;
    background: rgba(255,255,255,0.05);
    color: #ffffff;
}}

QComboBox:hover {{
    border-color: rgba(255,255,255,0.3);
    background: rgba(255,255,255,0.1);
}}

QGroupBox {{
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: {Config.get_scaled_value(12, dpi)}px;
    margin-top: {Config.get_scaled_value(12, dpi)}px;
    padding-top: {Config.get_scaled_value(16, dpi)}px;
    background: rgba(255,255,255,0.03);
    color: #ffffff;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: {Config.get_scaled_value(12, dpi)}px;
    padding: 0 {Config.get_scaled_value(8, dpi)}px;
    color: #667eea;
    font-weight: 700;
}}

QLabel#DropLabel {{
    border: 2px dashed rgba(255,255,255,0.2);
    border-radius: {Config.get_scaled_value(12, dpi)}px;
    padding: {Config.get_scaled_value(32, dpi)}px;
    color: rgba(255,255,255,0.7);
    margin: {Config.get_scaled_value(12, dpi)}px;
    font-size: {scaled_small_font}px;
    background: rgba(255,255,255,0.02);
}}

QLabel#DropLabel:hover {{
    border-color: #667eea;
    color: #667eea;
    background: rgba(102,126,234,0.1);
}}

QSpinBox, QLineEdit {{
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(6, dpi)}px {Config.get_scaled_value(12, dpi)}px;
    background: rgba(255,255,255,0.05);
    color: #ffffff;
}}

QSpinBox:focus, QLineEdit:focus {{
    border-color: #667eea;
    background: rgba(255,255,255,0.08);
}}
"""

def generate_minimal_style(dpi):
    """极简风格主题"""
    scaled_font_size = Config.get_scaled_font_size(11, dpi)
    scaled_small_font = Config.get_scaled_font_size(10, dpi)
    scaled_btn_padding = Config.get_scaled_value(8, dpi)
    scaled_border_radius = Config.get_scaled_value(6, dpi)
    
    return f"""
QWidget {{
    font-family: 'Microsoft YaHei UI', 'SF Pro Display', 'Segoe UI', sans-serif;
    font-size: {scaled_font_size}px;
    color: #2d3748;
    background-color: #ffffff;
    font-weight: 400;
}}

QMainWindow {{
    border: none;
    background-color: #ffffff;
}}

QPushButton {{
    background-color: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: {scaled_border_radius}px;
    padding: {scaled_btn_padding}px {Config.get_scaled_value(16, dpi)}px;
    min-height: {Config.get_scaled_value(32, dpi)}px;
    color: #4a5568;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #edf2f7;
    border-color: #cbd5e0;
}}

QPushButton#PrimaryButton {{
    background-color: #38a169;
    border-color: #38a169;
    color: #ffffff;
}}

QPushButton#PrimaryButton:hover {{
    background-color: #2f855a;
    border-color: #2f855a;
}}

QComboBox {{
    border: 1px solid #e2e8f0;
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(6, dpi)}px {Config.get_scaled_value(12, dpi)}px;
    min-width: {Config.get_scaled_value(100, dpi)}px;
    min-height: {Config.get_scaled_value(28, dpi)}px;
    background-color: #ffffff;
    color: #4a5568;
}}

QComboBox:hover {{
    border-color: #cbd5e0;
}}

QComboBox:focus {{
    border-color: #38a169;
}}

QGroupBox {{
    border: 1px solid #e2e8f0;
    border-radius: {Config.get_scaled_value(8, dpi)}px;
    margin-top: {Config.get_scaled_value(12, dpi)}px;
    padding-top: {Config.get_scaled_value(16, dpi)}px;
    background-color: #ffffff;
    color: #2d3748;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: {Config.get_scaled_value(12, dpi)}px;
    padding: 0 {Config.get_scaled_value(8, dpi)}px;
    color: #718096;
    font-weight: 500;
}}

QLabel#DropLabel {{
    border: 2px dashed #cbd5e0;
    border-radius: {Config.get_scaled_value(8, dpi)}px;
    padding: {Config.get_scaled_value(32, dpi)}px;
    color: #718096;
    margin: {Config.get_scaled_value(12, dpi)}px;
    font-size: {scaled_small_font}px;
    background-color: #f7fafc;
}}

QLabel#DropLabel:hover {{
    border-color: #38a169;
    color: #38a169;
    background-color: #f0fff4;
}}

QSpinBox, QLineEdit {{
    border: 1px solid #e2e8f0;
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(6, dpi)}px {Config.get_scaled_value(12, dpi)}px;
    background-color: #ffffff;
    color: #4a5568;
}}

QSpinBox:focus, QLineEdit:focus {{
    border-color: #38a169;
}}
"""

def generate_github_style(dpi):
    """GitHub风格主题"""
    scaled_font_size = Config.get_scaled_font_size(11, dpi)
    scaled_small_font = Config.get_scaled_font_size(10, dpi)
    scaled_btn_padding = Config.get_scaled_value(6, dpi)
    scaled_border_radius = Config.get_scaled_value(6, dpi)
    
    return f"""
QWidget {{
    font-family: 'Microsoft YaHei UI', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
    font-size: {scaled_font_size}px;
    color: #24292f;
    background-color: #ffffff;
    font-weight: 400;
}}

QMainWindow {{
    border: 1px solid #d0d7de;
    background-color: #ffffff;
}}

QPushButton {{
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: {scaled_border_radius}px;
    padding: {scaled_btn_padding}px {Config.get_scaled_value(16, dpi)}px;
    min-height: {Config.get_scaled_value(32, dpi)}px;
    color: #24292f;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #f3f4f6;
    border-color: #d0d7de;
}}

QPushButton#PrimaryButton {{
    background-color: #2da44e;
    border-color: #2da44e;
    color: #ffffff;
}}

QPushButton#PrimaryButton:hover {{
    background-color: #2c974b;
    border-color: #2c974b;
}}

QComboBox {{
    border: 1px solid #d0d7de;
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(5, dpi)}px {Config.get_scaled_value(12, dpi)}px;
    min-width: {Config.get_scaled_value(100, dpi)}px;
    min-height: {Config.get_scaled_value(28, dpi)}px;
    background-color: #ffffff;
    color: #24292f;
}}

QComboBox:hover {{
    border-color: #8c959f;
}}

QComboBox:focus {{
    border-color: #0969da;
}}

QGroupBox {{
    border: 1px solid #d0d7de;
    border-radius: {Config.get_scaled_value(6, dpi)}px;
    margin-top: {Config.get_scaled_value(10, dpi)}px;
    padding-top: {Config.get_scaled_value(12, dpi)}px;
    background-color: #f6f8fa;
    color: #24292f;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: {Config.get_scaled_value(10, dpi)}px;
    padding: 0 {Config.get_scaled_value(5, dpi)}px;
    color: #656d76;
    font-weight: 600;
}}

QLabel#DropLabel {{
    border: 2px dashed #d0d7de;
    border-radius: {Config.get_scaled_value(6, dpi)}px;
    padding: {Config.get_scaled_value(24, dpi)}px;
    color: #656d76;
    margin: {Config.get_scaled_value(12, dpi)}px;
    font-size: {scaled_small_font}px;
    background-color: #f6f8fa;
}}

QLabel#DropLabel:hover {{
    border-color: #0969da;
    color: #0969da;
    background-color: #dbeafe;
}}

QSpinBox, QLineEdit {{
    border: 1px solid #d0d7de;
    border-radius: {scaled_border_radius}px;
    padding: {Config.get_scaled_value(5, dpi)}px {Config.get_scaled_value(12, dpi)}px;
    background-color: #ffffff;
    color: #24292f;
}}

QSpinBox:focus, QLineEdit:focus {{
    border-color: #0969da;
}}
"""

# 主题名称多语言
THEME_NAMES = {
    'embedded': {'zh': '嵌入式风格', 'en': 'Embedded Style'},
    'ai_style': {'zh': 'AI风格', 'en': 'AI Style'},
    'minimal': {'zh': '极简风格', 'en': 'Minimal Style'},
    'github': {'zh': 'GitHub风格', 'en': 'GitHub Style'}
}

# 主题定义
THEMES = {
    'embedded': {
        'generator': generate_embedded_style
    },
    'ai_style': {
        'generator': generate_ai_style
    },
    'minimal': {
        'generator': generate_minimal_style
    },
    'github': {
        'generator': generate_github_style
    }
}

# 全局实例
theme_manager = ThemeManager()