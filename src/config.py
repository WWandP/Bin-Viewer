# 全局配置管理
import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class Config:
    # 文件限制
    MAX_FILE_SIZE_MB = 50
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # 显示阈值
    SHOW_DATA_THRESHOLD = 200
    MAX_DOWNSAMPLE_POINTS = 200000
    
    # 基础尺寸（96DPI基准）
    BASE_WINDOW_WIDTH = 600
    BASE_WINDOW_HEIGHT = 400
    BASE_PLOT_WIDTH = 900
    BASE_PLOT_HEIGHT = 650
    BASE_BTN_HEIGHT = 40
    
    @staticmethod
    def get_scaled_value(base_value, dpi):
        return int(round(base_value * (dpi / 96)))
    
    @staticmethod
    def get_scaled_font_size(base_size, dpi):
        scaled = base_size * (dpi / 96)
        return max(int(round(scaled)), base_size)
    
    @staticmethod
    def setup_high_dpi():
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    @staticmethod
    def setup_matplotlib(dpi):
        import matplotlib
        matplotlib.rcParams["font.family"] = ["sans-serif"]
        matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
        matplotlib.rcParams['figure.dpi'] = dpi
        matplotlib.rcParams['savefig.dpi'] = dpi * 2
    
    @staticmethod
    def load_icon():
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "bin.ico")
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                icon_path = os.path.join(base_dir, "assets", "icons", "bin.ico")
            
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            return QIcon.fromTheme("application-x-executable")
        except Exception:
            return None