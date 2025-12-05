# 重构后的PlotWindow
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QComboBox, 
                             QHBoxLayout, QFrame, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QDragEnterEvent, QDropEvent

from .comparison_window import ComparisonWindow
from .config import Config
from .style_manager import StyleManager
from .data_manager import DataManager
from .plot_manager import PlotManager
from .file_handler import FileHandler
from .window_manager import WindowManager
from .language_manager import get_text

class PlotWindow(QMainWindow):
    closed = pyqtSignal(int)
    
    def __init__(self, file_path, index, dtype="float32", parent=None, screen_dpi=None):
        super().__init__(parent)
        self.file_path = file_path
        self.index = index
        self.dtype = dtype
        self.screen_dpi = screen_dpi or QApplication.desktop().logicalDpiX()
        
        # 初始化管理器
        self.data_manager = DataManager()
        self.plot_manager = PlotManager(self, self.screen_dpi)
        self.window_manager = WindowManager()
        
        # 设置窗口
        self._setup_window()
        self._init_ui()
        self._load_data()
    
    def _fallback_load_data(self):
        """备用数据加载方法"""
        import src.bin_utils as bin_utils
        import numpy as np
        
        try:
            # 读取原始数据
            raw_data = bin_utils.handle_invalid_values(
                bin_utils.read_bin_file(self.file_path, dtype=np.dtype(self.dtype))
            )
            # 降采样
            data = self._downsample_data(raw_data, Config.MAX_DOWNSAMPLE_POINTS)
            self.plot_manager.set_data(data)
            
            title = f"{os.path.basename(self.file_path)} ({self.dtype}) - length: {len(data)}"
            self.plot_manager.plot_data(title=title)
        except Exception as e:
            pass
    
    def _downsample_data(self, data, max_points):
        """数据降采样"""
        if len(data) <= max_points:
            return data
        step = (len(data) + max_points - 1) // max_points
        return data[::step]
        
        # 设置图标
        icon = Config.load_icon()
        if icon:
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)
    
    def _setup_window(self):
        """设置窗口属性"""
        self.setAcceptDrops(True)
        self.setWindowTitle(f"BIN Viewer - {os.path.basename(self.file_path)}")
        
        width = Config.get_scaled_value(Config.BASE_PLOT_WIDTH, self.screen_dpi)
        height = Config.get_scaled_value(Config.BASE_PLOT_HEIGHT, self.screen_dpi)
        self.resize(width, height)
        
        self.setStyleSheet(StyleManager.generate_plot_style(self.screen_dpi))
        self.window_manager.register_window(self)
    
    def _init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self._init_control_bar()
        self._init_plot_area()
    
    def _init_control_bar(self):
        """初始化控制栏"""
        control_bar = QFrame()
        control_bar.setObjectName("ControlBar")
        layout = QHBoxLayout(control_bar)
        
        margin = Config.get_scaled_value(5, self.screen_dpi)
        layout.setContentsMargins(margin, 3, margin, 3)
        layout.setSpacing(Config.get_scaled_value(8, self.screen_dpi))
        
        # 标题
        title_label = QLabel(f"{get_text('file')} {self.index}: {os.path.basename(self.file_path)}")
        title_label.setObjectName("WindowTitle")
        title_label.setFont(QFont(
            title_label.font().family(),
            Config.get_scaled_font_size(11, self.screen_dpi)
        ))
        layout.addWidget(title_label)
        
        # 数据类型选择
        dtype_label = QLabel(get_text('data_type_label'))
        dtype_label.setFont(QFont(
            dtype_label.font().family(),
            Config.get_scaled_font_size(10, self.screen_dpi)
        ))
        layout.addWidget(dtype_label)
        
        self.dtype_combo = QComboBox()
        self.dtype_combo.addItems(["int8", "int16", "float32"])
        self.dtype_combo.setCurrentText(self.dtype)
        self.dtype_combo.currentTextChanged.connect(self._on_dtype_changed)
        layout.addWidget(self.dtype_combo)
        
        # 功能按钮
        compare_btn = QPushButton(get_text('select_compare_file'))
        compare_btn.setObjectName("PrimaryButton")
        compare_btn.clicked.connect(self._select_compare_file)
        layout.addWidget(compare_btn)
        
        open_btn = QPushButton(get_text('open_new_file'))
        open_btn.clicked.connect(self._open_new_file)
        layout.addWidget(open_btn)
        
        layout.addStretch(1)
        self.main_layout.addWidget(control_bar)
    
    def _init_plot_area(self):
        """初始化绘图区域"""
        self.main_layout.addWidget(self.plot_manager.canvas, 1)
    

    
    def _load_data(self):
        """加载数据"""
        import src.bin_utils as bin_utils
        import numpy as np
        
        try:
            # 读取原始数据
            raw_data = bin_utils.handle_invalid_values(
                bin_utils.read_bin_file(self.file_path, dtype=np.dtype(self.dtype))
            )

            
            # 降采样
            data = self._downsample_data(raw_data, Config.MAX_DOWNSAMPLE_POINTS)
            
            if data is not None and len(data) > 0:
                self.plot_manager.set_data(data)
                title = f"{os.path.basename(self.file_path)} ({self.dtype}) - length: {len(data)}"
                self.plot_manager.plot_data(title=title)
        except Exception:
            pass
    def _on_dtype_changed(self, dtype):
        """数据类型改变"""
        self.dtype = dtype
        self._load_data()  # 直接重新加载数据
    
    def _select_compare_file(self, file_path=None):
        """选择对比文件"""
        if not file_path:
            file_path, _ = FileHandler.select_bin_file(self, get_text('select_compare_bin'))
        
        if file_path:
            comparison_window = ComparisonWindow(
                self.file_path, file_path,
                self.dtype, "float32",
                parent=self.parent()
            )
            comparison_window.show()
    
    def _open_new_file(self):
        """打开新文件"""
        file_path, _ = FileHandler.select_bin_file(self)
        if file_path:
            new_index = self.window_manager.get_next_index()
            new_window = PlotWindow(
                file_path, new_index, dtype=self.dtype,
                parent=None, screen_dpi=self.screen_dpi
            )
            new_window.show()
    

    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and os.path.splitext(url.toLocalFile())[1].lower() == '.bin':
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        valid_files, errors = FileHandler.process_dropped_files(event.mimeData().urls())
        
        for error in errors:
            QMessageBox.warning(self, get_text('file_error'), error)
        
        if len(valid_files) == 1:
            self._select_compare_file(valid_files[0])
        elif len(valid_files) > 1:
            QMessageBox.information(self, get_text('hint'), get_text('not_support_3_files'))
        
        event.acceptProposedAction()
    
    def keyPressEvent(self, event: QKeyEvent):
        """按键事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """关闭事件"""
        self.closed.emit(self.index)
        self.window_manager.unregister_window(self)
        event.accept()