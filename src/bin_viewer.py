import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QHBoxLayout, QFrame, QMessageBox, 
                             QMenu, QAction, QToolTip, QComboBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent, QDragEnterEvent, QDropEvent, QFont

from .comparison_window import ComparisonWindow
from .plot_window import PlotWindow
from .tensor_concat_window import TensorConcatWindow
from .config import Config
from .style_manager import StyleManager
from .file_handler import FileHandler
from .window_manager import WindowManager
from .language_manager import language_manager, get_text
from .theme_manager import theme_manager
from PyQt5.QtGui import QIcon

# 设置文件大小限制（单位：MB）
MAX_FILE_SIZE_MB = 50  # 限制为50MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 转换为字节

# ---------------------- 修复1：高分辨率适配工具函数（确保返回整数） ----------------------
def get_scaled_value(base_value, dpi):
    """根据屏幕DPI缩放数值（以96DPI为基准，返回整数）"""
    return int(round(base_value * (dpi / 96)))  # 四舍五入避免小数

def get_scaled_font_size(base_size, dpi):
    """根据屏幕DPI缩放字体大小（返回整数，确保QFont兼容）"""
    scaled = base_size * (dpi / 96)
    return max(int(round(scaled)), base_size)  # 转为整数，且不小于基础大小

# ---------------------- 动态生成全局样式（支持高DPI） ----------------------
def generate_minimal_style(dpi):
    scaled_font_size = get_scaled_font_size(11, dpi)
    scaled_small_font = get_scaled_font_size(10, dpi)
    scaled_btn_padding = get_scaled_value(5, dpi)
    scaled_border_radius = get_scaled_value(2, dpi)
    
    return f"""
QWidget {{
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: {scaled_font_size}px;
    color: #333;
    background-color: #fff;
}}

QMainWindow {{
    border: 1px solid #eee;
}}

QPushButton {{
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: {scaled_border_radius}px;
    padding: {scaled_btn_padding}px {get_scaled_value(10, dpi)}px;
    min-height: {get_scaled_value(24, dpi)}px;
}}

QPushButton:hover {{
    background-color: #eee;
}}

QPushButton#PrimaryButton {{
    background-color: #4285f4;
    color: white;
    border: none;
}}

QPushButton#PrimaryButton:hover {{
    background-color: #3367d6;
}}

QComboBox {{
    border: 1px solid #ddd;
    border-radius: {scaled_border_radius}px;
    padding: {get_scaled_value(3, dpi)}px {get_scaled_value(20, dpi)}px {get_scaled_value(3, dpi)}px {get_scaled_value(6, dpi)}px;
    min-width: {get_scaled_value(100, dpi)}px;
    min-height: {get_scaled_value(24, dpi)}px;
}}

QFrame#ControlBar {{
    background-color: #f9f9f9;
    border-bottom: 1px solid #eee;
    padding: {get_scaled_value(6, dpi)}px;
}}

QLabel#WindowTitle {{
    font-weight: 500;
    padding: 0 {get_scaled_value(12, dpi)}px;
    font-size: {scaled_font_size}px;
}}

QLabel#DropLabel {{
    border: 2px dashed #ccc;
    border-radius: {get_scaled_value(5, dpi)}px;
    padding: {get_scaled_value(25, dpi)}px;
    color: #666;
    margin: {get_scaled_value(12, dpi)}px;
    font-size: {scaled_small_font}px;
}}

QLabel#DropLabel:hover, QLabel#DropLabel#Active {{
    border-color: #4285f4;
    color: #4285f4;
}}

QSplitter::handle {{
    background-color: #eee;
}}

QSplitter::handle:horizontal {{
    height: {get_scaled_value(4, dpi)}px;
}}

QSplitter::handle:vertical {{
    width: {get_scaled_value(4, dpi)}px;
}}


"""

class BinViewer(QMainWindow):
    """主程序窗口，支持拖放功能"""
    def __init__(self, screen_dpi):
        super().__init__()
        self.window_manager = WindowManager()
        self.screen_dpi = screen_dpi
        
        # 计算缩放后的尺寸
        self.scaled_width = Config.get_scaled_value(Config.BASE_WINDOW_WIDTH, self.screen_dpi)
        self.scaled_height = Config.get_scaled_value(Config.BASE_WINDOW_HEIGHT, self.screen_dpi)
        self.scaled_btn_height = Config.get_scaled_value(Config.BASE_BTN_HEIGHT, self.screen_dpi)
        
        # 设置窗口属性
        self.setAcceptDrops(True)
        self.setWindowTitle("BIN查看器")
        self.resize(self.scaled_width, self.scaled_height)
        
        # 应用主题样式
        self.setStyleSheet(theme_manager.generate_style(self.screen_dpi))
        
        # UI布局重构（左区域+右按钮）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(
            Config.get_scaled_value(20, self.screen_dpi),
            Config.get_scaled_value(20, self.screen_dpi),
            Config.get_scaled_value(20, self.screen_dpi),
            Config.get_scaled_value(20, self.screen_dpi)
        )
        self.main_layout.setSpacing(Config.get_scaled_value(15, self.screen_dpi))
        
        # 顶部布局（标题+语言选择）
        top_layout = QHBoxLayout()
        
        # 标题标签
        self.title_label = QLabel(get_text('main_title'))
        scaled_title_size = Config.get_scaled_font_size(14, self.screen_dpi)
        self.title_label.setFont(QFont(self.title_label.font().family(), scaled_title_size, QFont.Bold))
        top_layout.addWidget(self.title_label)
        
        top_layout.addStretch()
        
        # 设置选项
        settings_layout = QHBoxLayout()
        
        # 主题选择
        self.theme_label = QLabel(get_text('theme') + ":")
        self.theme_label.setStyleSheet(f"font-size: {Config.get_scaled_font_size(10, self.screen_dpi)}px;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(theme_manager.get_theme_display_names())
        current_theme_index = list(theme_manager.get_theme_names()).index(theme_manager.get_theme())
        self.theme_combo.setCurrentIndex(current_theme_index)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        self.theme_combo.setFixedWidth(Config.get_scaled_value(90, self.screen_dpi))
        
        settings_layout.addWidget(self.theme_label)
        settings_layout.addWidget(self.theme_combo)
        settings_layout.addSpacing(Config.get_scaled_value(15, self.screen_dpi))
        
        # 语言选择
        self.lang_label = QLabel(get_text('language') + ":")
        self.lang_label.setStyleSheet(f"font-size: {Config.get_scaled_font_size(10, self.screen_dpi)}px;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([get_text('chinese'), get_text('english')])
        self.lang_combo.setCurrentIndex(0 if language_manager.get_language() == 'zh' else 1)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        self.lang_combo.setFixedWidth(Config.get_scaled_value(80, self.screen_dpi))
        
        settings_layout.addWidget(self.lang_label)
        settings_layout.addWidget(self.lang_combo)
        top_layout.addLayout(settings_layout)
        
        self.main_layout.addLayout(top_layout)
        
        # 拖放区域
        self.drop_label = QLabel()
        self.drop_label.setObjectName("DropLabel")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setWordWrap(True)
        self.update_drop_label_text()
        self.main_layout.addWidget(self.drop_label)
        
        # 功能按钮（打开/对比）
        self.open_btn = QPushButton()
        self.open_btn.setObjectName("PrimaryButton")
        self.open_btn.setMinimumHeight(self.scaled_btn_height)
        self.open_btn.clicked.connect(self.open_file_dialog)
        self.main_layout.addWidget(self.open_btn)
        
        self.compare_btn = QPushButton()
        self.compare_btn.setMinimumHeight(get_scaled_value(32, self.screen_dpi))
        self.compare_btn.clicked.connect(self.compare_two_files)
        self.main_layout.addWidget(self.compare_btn)
        
        self.tensor_concat_btn = QPushButton()
        self.tensor_concat_btn.setMinimumHeight(get_scaled_value(32, self.screen_dpi))
        self.tensor_concat_btn.clicked.connect(self.open_tensor_concat)
        self.main_layout.addWidget(self.tensor_concat_btn)
        
        # 提示信息
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"color: #666; font-size: {get_scaled_font_size(10, self.screen_dpi)}px;")
        self.main_layout.addWidget(self.info_label)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: #666; font-size: {get_scaled_font_size(10, self.screen_dpi)}px; margin-top: 5px;")
        self.main_layout.addWidget(self.status_label)
        
        # 更新所有文本
        self.update_ui_text()
        
        self.show()
        # 设置图标
        icon = Config.load_icon()
        if icon:
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)




    
    # 拖放功能实现
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if os.path.splitext(path)[1].lower() == '.bin':
                        self.drop_label.setObjectName("DropLabel Active")
                        event.acceptProposedAction()
                        return
        self.drop_label.setObjectName("DropLabel")
        event.ignore()
    
    def dragLeaveEvent(self, event):
        self.drop_label.setObjectName("DropLabel")
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        self.drop_label.setObjectName("DropLabel")
        
        valid_files, errors = FileHandler.process_dropped_files(event.mimeData().urls())
        
        # 显示错误信息
        for error in errors:
            QMessageBox.warning(self, "文件错误", error)
        
        if len(valid_files) == 1:
            self.open_file(valid_files[0])
        elif len(valid_files) == 2:
            comparison_window = ComparisonWindow(valid_files[0], valid_files[1], parent=None)
            comparison_window.show()
        elif len(valid_files) > 2:
            QMessageBox.information(self, "提示", "不支持3个及以上文件对比")
            
        event.acceptProposedAction()
    
    def open_file(self, file_path):
        """打开文件并创建新窗口"""
        from .plot_window import PlotWindow
        
        new_index = self.window_manager.get_next_index()
        new_window = PlotWindow(file_path, new_index, parent=None, screen_dpi=self.screen_dpi)
        self.window_manager.register_window(new_window)
        
        new_window.show()
        self.update_status(get_text('file_opened').format(os.path.basename(file_path), new_index))
    
    def open_file_dialog(self):
        """打开文件选择对话框"""
        file_path, error_msg = FileHandler.select_bin_file(self)
        if file_path:
            self.open_file(file_path)
    
    def compare_two_files(self):
        """直接选择两个文件进行对比"""
        file1_path, _ = FileHandler.select_bin_file(self, get_text('select_first_file'))
        if not file1_path:
            return
            
        file2_path, _ = FileHandler.select_bin_file(self, get_text('select_second_file'))
        if not file2_path:
            return
            
        comparison_window = ComparisonWindow(file1_path, file2_path, parent=None)
        comparison_window.show()
    
    def open_tensor_concat(self):
        """打开张量拼接工具"""
        tensor_window = TensorConcatWindow(parent=self, screen_dpi=self.screen_dpi)
        tensor_window.exec_()
    
    def on_window_closed(self, window):
        """处理窗口关闭事件"""
        self.window_manager.unregister_window(window)
        if self.window_manager.get_window_count() == 0:
            self.update_status(get_text('no_files'))
            
    def on_theme_changed(self, index):
        """主题切换事件"""
        theme_names = theme_manager.get_theme_names()
        new_theme = theme_names[index]
        theme_manager.set_theme(new_theme)
        self.setStyleSheet(theme_manager.generate_style(self.screen_dpi))
        
    def on_language_changed(self, index):
        """语言切换事件"""
        new_lang = 'zh' if index == 0 else 'en'
        language_manager.set_language(new_lang)
        # 更新主题下拉框选项
        current_theme_index = self.theme_combo.currentIndex()
        self.theme_combo.clear()
        self.theme_combo.addItems(theme_manager.get_theme_display_names())
        self.theme_combo.setCurrentIndex(current_theme_index)
        self.update_ui_text()
        
    def update_ui_text(self):
        """更新界面文本"""
        self.setWindowTitle(get_text('main_title'))
        self.title_label.setText(get_text('main_title'))
        self.theme_label.setText(get_text('theme') + ":")
        self.lang_label.setText(get_text('language') + ":")
        self.update_drop_label_text()
        self.open_btn.setText(get_text('open_file'))
        self.compare_btn.setText(get_text('compare_files'))
        self.tensor_concat_btn.setText(get_text('tensor_concat'))
        self.info_label.setText(get_text('tips'))
        
    def update_drop_label_text(self):
        """更新拖放区域文本"""
        self.drop_label.setText(get_text('drag_hint').format(Config.MAX_FILE_SIZE_MB))
        
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.setText(message)
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)