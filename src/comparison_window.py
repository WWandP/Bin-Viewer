# 每个文件开头都加这一段
import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QComboBox, 
                             QHBoxLayout, QFrame, QMessageBox, QSplitter, 
                             QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent, QTime
from PyQt5.QtGui import QKeyEvent, QDragEnterEvent, QDropEvent, QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import src.bin_utils as bin_utils # 你的自定义工具类
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from .language_manager import get_text

# 设置文件大小限制（单位：MB）
MAX_FILE_SIZE_MB = 50  # 限制为50MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 转换为字节

# ---------------------- 高分辨率适配工具函数 ----------------------
def get_scaled_value(base_value, dpi):
    """根据屏幕DPI缩放数值（以96DPI为基准，返回整数）"""
    return int(round(base_value * (dpi / 96)))

def get_scaled_font_size(base_size, dpi):
    """根据屏幕DPI缩放字体大小（返回整数）"""
    scaled = base_size * (dpi / 96)
    return max(int(round(scaled)), base_size)

# ---------------------- 动态生成样式（支持高DPI） ----------------------
def generate_comparison_style(dpi):
    scaled_font_size = get_scaled_font_size(11, dpi)
    scaled_small_font = get_scaled_font_size(10, dpi)
    scaled_tiny_font = get_scaled_font_size(8, dpi)
    scaled_btn_padding = get_scaled_value(3, dpi)
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
    padding: {scaled_btn_padding}px {get_scaled_value(8, dpi)}px;
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
    padding: {get_scaled_value(2, dpi)}px {get_scaled_value(20, dpi)}px {get_scaled_value(2, dpi)}px {get_scaled_value(4, dpi)}px;
    min-width: {get_scaled_value(90, dpi)}px;
}}

QFrame#ControlBar {{
    background-color: #f9f9f9;
    border-bottom: 1px solid #eee;
    padding: {get_scaled_value(5, dpi)}px;
}}

QLabel#WindowTitle {{
    font-weight: 500;
    padding: 0 {get_scaled_value(10, dpi)}px;
}}

QLabel#DropLabel {{
    border: 2px dashed #ccc;
    border-radius: {get_scaled_value(5, dpi)}px;
    padding: {get_scaled_value(20, dpi)}px;
    color: #666;
    margin: {get_scaled_value(10, dpi)}px;
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

class ComparisonWindow(QMainWindow):
    """独立的文件对比窗口，支持图片保存和DPI适配"""
    def __init__(self, file1_path, file2_path, dtype1="float32", dtype2="float32", parent=None, screen_dpi=None):
        # 禁用跨显示器DPI动态调整
        super().__init__(parent)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)
        
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.dtype1 = dtype1
        self.dtype2 = dtype2
        
        # 固定窗口创建时的DPI，不随显示器变化
        self.screen_dpi = screen_dpi or QApplication.desktop().logicalDpiX()
        self.initial_dpi = self.screen_dpi  # 保存初始DPI
        
        # 基础尺寸计算（只在初始化时计算一次）
        self.base_window_width = 1000
        self.base_window_height = 800
        self.base_frame_min_height = 200
        self.base_splitter_sizes = [250, 250, 300]
        self.base_figure_size = (8, 3)
        
        # 计算缩放后的尺寸
        self.scaled_width = get_scaled_value(self.base_window_width, self.initial_dpi)
        self.scaled_height = get_scaled_value(self.base_window_height, self.initial_dpi)
        self.scaled_frame_min_height = get_scaled_value(self.base_frame_min_height, self.initial_dpi)
        self.scaled_splitter_sizes = [
            get_scaled_value(size, self.initial_dpi) 
            for size in self.base_splitter_sizes
        ]
        self.scaled_figure_size = (
            get_scaled_value(self.base_figure_size[0], self.initial_dpi) / 100,
            get_scaled_value(self.base_figure_size[1], self.initial_dpi) / 100
        )
        
        # 设置窗口属性
        self.setWindowTitle(f"{get_text('bin_comparison')} - {os.path.basename(file1_path)} {get_text('vs')} {os.path.basename(file2_path)}")
        self.resize(self.scaled_width, self.scaled_height)
        self.setStyleSheet(generate_comparison_style(self.initial_dpi))
        
        # 移动优化相关变量
        self.is_moving = False
        self.last_paint_time = QTime.currentTime()
        self.move_timer = QTimer(self)
        self.move_timer.setSingleShot(True)
        self.move_timer.timeout.connect(self.on_move_end)
        self.tooltip = {
            "file1": None,    # 存储每个区域的提示框对象
            "file2": None,
            "compare": None
        }
        self.last_annotated_index = {
            "file1": -1,      # 记录每个区域最后标注的索引（避免重复绘制）
            "file2": -1,
            "compare": -1
        }
        self.tooltip_threshold = 200  # 显示提示框的阈值：可见点数≤200时才显示（可调整）
        # 初始化UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.init_control_bar(main_layout)
        self.init_plot_area(main_layout)
        self.load_and_plot_data()
        
        # 安装事件过滤器，优化重绘
        self.installEventFilter(self)
        self.is_panning = {
        "file1": False, "file2": False, "compare": False
        }  # 每个Canvas的平移状态
        self.last_x = {
            "file1": None, "file2": None, "compare": None
        }  # 每个Canvas的平移起始x坐标
        self.zoom_factor = 1.2
        # 加载图标
        self.load_window_icon()
    
    def load_window_icon(self):
        """加载窗口图标，适配打包环境"""
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "bin.ico")
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin.ico")
            
            if os.path.exists(icon_path):
                app_icon = QIcon(icon_path)
                self.setWindowIcon(app_icon)
                QApplication.instance().setWindowIcon(app_icon)
            else:
                pass
        except Exception:
            pass
    
    # ---------------------- 窗口移动优化 ----------------------
    def eventFilter(self, obj, event):
        # 窗口移动时禁用重绘
        if event.type() == QEvent.Move:
            if not self.is_moving:
                self.is_moving = True
                # 隐藏所有画布减少重绘
                self.file1_canvas.setVisible(False)
                self.file2_canvas.setVisible(False)
                self.compare_canvas.setVisible(False)
            self.move_timer.start(50)  # 50ms无移动则认为结束
            return True
        # 限制重绘频率（最高60fps）
        elif event.type() == QEvent.Paint:
            current_time = QTime.currentTime()
            if self.last_paint_time.msecsTo(current_time) < 16:
                return True
            self.last_paint_time = current_time
        return super().eventFilter(obj, event)
    
    def on_move_end(self):
        """移动结束后恢复显示"""
        self.is_moving = False
        self.file1_canvas.setVisible(True)
        self.file2_canvas.setVisible(True)
        self.compare_canvas.setVisible(True)
    
    def _optimized_draw_idle(self, canvas):
        """优化的重绘方法：移动时不重绘"""
        def draw_wrapper():
            if not self.is_moving:
                canvas.draw()
        return draw_wrapper
    def should_show_tooltip(self, ax, data_len):
        """严格按可见点数判断是否显示提示框"""
        if data_len == 0:
            return False
        x_start, x_end = ax.get_xlim()
        # 计算可见点数（取整后加1，确保包含首尾）
        visible_start = max(0, int(round(x_start)))
        visible_end = min(data_len - 1, int(round(x_end)))
        visible_points = visible_end - visible_start + 1
        # 只有可见点数≤阈值时才显示
        return visible_points <= self.tooltip_threshold
    def show_data_tooltip(self, event, canvas_key, data1=None, data2=None):
        """
        显示数据提示框
        :param event: 鼠标事件对象
        :param canvas_key: 绘图区标识（"file1"/"file2"/"compare"）
        :param data1: file1的数据（仅compare区需要）
        :param data2: file2的数据（仅compare区需要）
        """
        # 1. 获取当前绘图区的ax和对应数据
        ax = getattr(self, f"{canvas_key}_ax")
        if canvas_key == "file1":
            data = data1 if data1 is not None else self.data1  # 正确：只判断是否为None
        elif canvas_key == "file2":
            data = data2 if data2 is not None else self.data2  # 正确：只判断是否为None
        else:  # compare区，需要同时用两个数据
            data = (data1 if data1 is not None else self.data1, 
                    data2 if data2 is not None else self.data2)
        data_len = len(data) if canvas_key != "compare" else min(len(data[0]), len(data[1]))
        
        # 2. 先判断是否需要显示提示框，不需要则移除已有的
        if not self.should_show_tooltip(ax, data_len) or event.inaxes != ax:
            if self.tooltip[canvas_key]:
                self.tooltip[canvas_key].remove()  # 移除旧提示框
                self.tooltip[canvas_key] = None
                self.last_annotated_index[canvas_key] = -1
                getattr(self, f"{canvas_key}_canvas").draw()  # 重绘
            return
        
        # 3. 计算鼠标对应的X轴数据索引（四舍五入到最近的整数索引）
        x_idx = int(round(event.xdata))
        # 检查索引是否有效，且和上次标注的索引不同（避免重复绘制）
        if x_idx < 0 or x_idx >= data_len or x_idx == self.last_annotated_index[canvas_key]:
            return
        bg_color = "yellow"
        # 4. 移除旧提示框（避免多个提示框叠加）
        if self.tooltip[canvas_key]:
            self.tooltip[canvas_key].remove()
        
        # 5. 生成提示框内容（不同区域显示不同内容）
    # 5. 分区域生成提示框（重点优化compare区）
        if canvas_key == "compare":
            # compare区：获取两个文件的当前值
            val1 = data[0][x_idx] if x_idx < len(data[0]) else None
            val2 = data[1][x_idx] if x_idx < len(data[1]) else None
            # 跳过无效值
            if val1 is None and val2 is None:
                return
            
            # 核心：计算鼠标Y坐标与两个值的距离，判断靠近哪个
            mouse_y = event.ydata
            dist1 = abs(mouse_y - val1) if val1 is not None else float('inf')
            dist2 = abs(mouse_y - val2) if val2 is not None else float('inf')
            
            # 选择距离近的文件显示提示框
            if dist1 <= dist2 and val1 is not None:
                # 靠近file1：蓝色提示框（与数据线同色）
                tooltip_text = f"Index: {x_idx}\nfile1 Value: {val1:.6f}"
                bg_color = "#4285f4"  # file1蓝色
                y_pos = val1  # 提示框指向file1的数据点
            else:
                # 靠近file2：红色提示框（与数据线同色）
                tooltip_text = f"Index: {x_idx}\nfile2 Value: {val2:.6f}"
                bg_color = "#ea4335"  # file2红色
                y_pos = val2  # 提示框指向file2的数据点
        else:
            # file1/file2区：只显示当前文件的数值
            val = data[x_idx]
            tooltip_text = f"Index: {x_idx}\nValue: {val:.6f}"
            y_pos = val  # 提示框Y轴位置和数据点一致
        
        # 6. 创建新提示框（黄色背景+箭头指向数据点，适配DPI）
        self.tooltip[canvas_key] = ax.annotate(
        tooltip_text,
        xy=(x_idx, y_pos),  # 指向对应数据点
        xytext=(10, 10),    # 提示框偏移（右10px，下10px）
        textcoords="offset points",
        bbox=dict(
            boxstyle="round,pad=0.5",
            fc=bg_color,          # 背景色（文件专属色）
            alpha=0.7,            # 半透明（不遮挡数据）
        ),
        arrowprops=dict(
            arrowstyle="->",
            connectionstyle="arc3,rad=0",
        ),
        fontsize=get_scaled_font_size(8, self.initial_dpi),
        zorder=100,     # 最上层，不被遮挡
        weight="bold"   # 文字加粗，更醒目
        )
        
        # 7. 更新最后标注的索引，并重绘画布
        self.last_annotated_index[canvas_key] = x_idx
        getattr(self, f"{canvas_key}_canvas").draw()
    # ---------------------- UI初始化 ----------------------
    def init_control_bar(self, parent_layout):
        """初始化顶部控制栏（带DPI缩放）"""
        control_bar = QFrame()
        control_bar.setObjectName("ControlBar")
        layout = QHBoxLayout(control_bar)
        layout.setContentsMargins(
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi),
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi)
        )
        layout.setSpacing(get_scaled_value(15, self.initial_dpi))
        
        # 文件1信息和数据类型
        file1_layout = QHBoxLayout()
        file1_layout.setSpacing(get_scaled_value(5, self.initial_dpi))
        file1_label = QLabel(f"file1: {os.path.basename(self.file1_path)}")
        file1_label.setFont(QFont(
            file1_label.font().family(),
            get_scaled_font_size(10, self.initial_dpi)
        ))
        file1_layout.addWidget(file1_label)
        
        dtype1_label = QLabel(get_text('type'))
        dtype1_label.setFont(QFont(
            dtype1_label.font().family(),
            get_scaled_font_size(10, self.initial_dpi)
        ))
        file1_layout.addWidget(dtype1_label)
        
        self.dtype1_combo = QComboBox()
        self.dtype1_combo.addItems(["int8", "int16", "float32"])
        self.dtype1_combo.setCurrentText(self.dtype1)
        self.dtype1_combo.setMinimumWidth(get_scaled_value(90, self.initial_dpi))
        self.dtype1_combo.currentTextChanged.connect(self.on_dtype1_changed)
        file1_layout.addWidget(self.dtype1_combo)
        layout.addLayout(file1_layout)
        
        # 文件2信息和数据类型
        file2_layout = QHBoxLayout()
        file2_layout.setSpacing(get_scaled_value(5, self.initial_dpi))
        file2_label = QLabel(f"file2: {os.path.basename(self.file2_path)}")
        file2_label.setFont(QFont(
            file2_label.font().family(),
            get_scaled_font_size(10, self.initial_dpi)
        ))
        file2_layout.addWidget(file2_label)
        
        dtype2_label = QLabel(get_text('type'))
        dtype2_label.setFont(QFont(
            dtype2_label.font().family(),
            get_scaled_font_size(10, self.initial_dpi)
        ))
        file2_layout.addWidget(dtype2_label)
        
        self.dtype2_combo = QComboBox()
        self.dtype2_combo.addItems(["int8", "int16", "float32"])
        self.dtype2_combo.setCurrentText(self.dtype2)
        self.dtype2_combo.setMinimumWidth(get_scaled_value(90, self.initial_dpi))
        self.dtype2_combo.currentTextChanged.connect(self.on_dtype2_changed)
        file2_layout.addWidget(self.dtype2_combo)
        layout.addLayout(file2_layout)
        
        layout.addStretch(1)
        parent_layout.addWidget(control_bar)
        
    def init_plot_area(self, parent_layout):
        main_splitter = QSplitter(Qt.Vertical)
        
        # ---------------------- 1. 文件1的图形（修复ax创建顺序） ----------------------
        self.file1_frame = QFrame()
        self.file1_frame.setMinimumHeight(self.scaled_frame_min_height)
        file1_layout = QVBoxLayout(self.file1_frame)
        file1_layout.setContentsMargins(
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi),
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi)
        )
        
        # 正确顺序：1. 创建Figure → 2. 创建Canvas → 3. 初始化ax → 4. 操作ax
        self.file1_figure = Figure(
            figsize=self.scaled_figure_size,
            dpi=self.initial_dpi,
            facecolor='white'
        )
        # 2. 创建Canvas（绑定Figure）
        self.file1_canvas = FigureCanvas(self.file1_figure)
        # 3. 初始化ax（这一步才创建self.file1_ax属性）
        self.file1_ax = self.file1_figure.add_subplot(111)
        # 4. 现在才能操作ax：禁用默认交互（修复错误的核心）
        self.file1_ax.set_navigate_mode(None)
        
        # 创建工具栏 → 禁用 → 隐藏（原有逻辑不变）
        self.file1_toolbar = NavigationToolbar(self.file1_canvas, self.file1_frame)
        self.file1_toolbar.setStyleSheet(f"font-size: {get_scaled_font_size(9, self.initial_dpi)}px;")
        self.file1_toolbar.setEnabled(False)
        self.file1_toolbar.setVisible(False)
        file1_layout.addWidget(self.file1_toolbar)
        
        # Canvas配置（原有逻辑不变）
        self.file1_canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file1_canvas.customContextMenuRequested.connect(
            lambda pos: self.show_comparison_menu(pos, "file1")
        )
        self.file1_canvas.draw_idle = self._optimized_draw_idle(self.file1_canvas)
        file1_layout.addWidget(self.file1_canvas)
        
        # ---------------------- 2. 文件2的图形（同理修复ax顺序） ----------------------
        self.file2_frame = QFrame()
        self.file2_frame.setMinimumHeight(self.scaled_frame_min_height)
        file2_layout = QVBoxLayout(self.file2_frame)
        file2_layout.setContentsMargins(
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi),
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi)
        )
        
        # 正确顺序：Figure → Canvas → Ax → Ax操作
        self.file2_figure = Figure(
            figsize=self.scaled_figure_size,
            dpi=self.initial_dpi,
            facecolor='white'
        )
        self.file2_canvas = FigureCanvas(self.file2_figure)
        self.file2_ax = self.file2_figure.add_subplot(111)
        # 修复：在ax创建后再调用set_navigate_mode
        self.file2_ax.set_navigate_mode(None)
        
        # 创建工具栏 → 禁用 → 隐藏（原有逻辑不变）
        self.file2_toolbar = NavigationToolbar(self.file2_canvas, self.file2_frame)
        self.file2_toolbar.setStyleSheet(f"font-size: {get_scaled_font_size(9, self.initial_dpi)}px;")
        self.file2_toolbar.setEnabled(False)
        self.file2_toolbar.setVisible(False)
        file2_layout.addWidget(self.file2_toolbar)
        
        # Canvas配置（原有逻辑不变）
        self.file2_canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file2_canvas.customContextMenuRequested.connect(
            lambda pos: self.show_comparison_menu(pos, "file2")
        )
        self.file2_canvas.draw_idle = self._optimized_draw_idle(self.file2_canvas)
        file2_layout.addWidget(self.file2_canvas)
        
        # ---------------------- 3. 对比图形（补充ax禁用交互） ----------------------
        self.compare_frame = QFrame()
        self.compare_frame.setMinimumHeight(self.scaled_frame_min_height)
        compare_layout = QVBoxLayout(self.compare_frame)
        compare_layout.setContentsMargins(
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi),
            get_scaled_value(5, self.initial_dpi),
            get_scaled_value(3, self.initial_dpi)
        )
        
        # 正确顺序：Figure → Canvas → Ax → Ax操作
        self.compare_figure = Figure(
            figsize=self.scaled_figure_size,
            dpi=self.initial_dpi,
            facecolor='white'
        )
        self.compare_canvas = FigureCanvas(self.compare_figure)
        self.compare_ax = self.compare_figure.add_subplot(111)
        # 补充：禁用默认交互（与file1/file2保持一致）
        self.compare_ax.set_navigate_mode(None)
        
        # 创建工具栏 → 禁用 → 隐藏（原有逻辑不变）
        self.compare_toolbar = NavigationToolbar(self.compare_canvas, self.compare_frame)
        self.compare_toolbar.setStyleSheet(f"font-size: {get_scaled_font_size(9, self.initial_dpi)}px;")
        self.compare_toolbar.setEnabled(False)
        self.compare_toolbar.setVisible(False)
        compare_layout.addWidget(self.compare_toolbar)
        
        # Canvas配置（原有逻辑不变）
        self.compare_canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.compare_canvas.customContextMenuRequested.connect(
            lambda pos: self.show_comparison_menu(pos, "compare")
        )
        self.compare_canvas.draw_idle = self._optimized_draw_idle(self.compare_canvas)
        compare_layout.addWidget(self.compare_canvas)
        
        # ---------------------- 4. 绑定鼠标事件（原有逻辑不变） ----------------------
        # file1_canvas事件绑定
        self.file1_canvas.mpl_connect('scroll_event', lambda event: self.on_mouse_scroll(event, "file1"))
        self.file1_canvas.mpl_connect('button_press_event', lambda event: self.on_mouse_press(event, "file1"))
        self.file1_canvas.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event, "file1"))
        self.file1_canvas.mpl_connect('button_release_event', lambda event: self.on_mouse_release(event, "file1"))
        
        # file2_canvas事件绑定
        self.file2_canvas.mpl_connect('scroll_event', lambda event: self.on_mouse_scroll(event, "file2"))
        self.file2_canvas.mpl_connect('button_press_event', lambda event: self.on_mouse_press(event, "file2"))
        self.file2_canvas.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event, "file2"))
        self.file2_canvas.mpl_connect('button_release_event', lambda event: self.on_mouse_release(event, "file2"))
        
        # compare_canvas事件绑定
        self.compare_canvas.mpl_connect('scroll_event', lambda event: self.on_mouse_scroll(event, "compare"))
        self.compare_canvas.mpl_connect('button_press_event', lambda event: self.on_mouse_press(event, "compare"))
        self.compare_canvas.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event, "compare"))
        self.compare_canvas.mpl_connect('button_release_event', lambda event: self.on_mouse_release(event, "compare"))
        
        # 添加到splitter（原有逻辑不变）
        main_splitter.addWidget(self.file1_frame)
        main_splitter.addWidget(self.file2_frame)
        main_splitter.addWidget(self.compare_frame)
        main_splitter.setSizes(self.scaled_splitter_sizes)
        parent_layout.addWidget(main_splitter, 1)
    # ---------------------- 功能实现 ----------------------
    def show_comparison_menu(self, position, plot_type):
        """显示对比图形的右键菜单"""
        menu = QMenu()
        save_action = QAction(get_text('save_image'), self)
        save_action.triggered.connect(lambda: self.save_comparison_image(plot_type))
        menu.addAction(save_action)
        if plot_type == "file1":
            menu.exec_(self.file1_canvas.mapToGlobal(position))
        elif plot_type == "file2":
            menu.exec_(self.file2_canvas.mapToGlobal(position))
        else:
            menu.exec_(self.compare_canvas.mapToGlobal(position))
        
    def save_comparison_image(self, plot_type):
        file1_name = os.path.splitext(os.path.basename(self.file1_path))[0]
        file2_name = os.path.splitext(os.path.basename(self.file2_path))[0]
        
        # （保留原有默认文件名逻辑）
        if plot_type == "file1":
            default_name = f"{file1_name}_{self.dtype1}.svg"  # 默认矢量格式SVG
            figure = self.file1_figure
        elif plot_type == "file2":
            default_name = f"{file2_name}_{self.dtype2}.svg"
            figure = self.file2_figure
        else:
            default_name = f"{file1_name}_vs_{file2_name}.svg"
            figure = self.compare_figure
        
        # 新增：文件格式选项，包含矢量图（SVG/PDF）和位图（PNG/JPG）
        file_path, _ = QFileDialog.getSaveFileName(
            self, get_text('save_image_title'), default_name, 
            get_text('save_image_filter')
        )
        
        if file_path:
            # 矢量图无需设置dpi（dpi是位图概念），添加bbox_inches避免元素截断
            figure.savefig(
                file_path, 
                bbox_inches='tight',  # 关键：防止标题/坐标轴被截断
                facecolor='white',    # 背景色（避免透明）
                edgecolor='none'      # 无边框
            )
            QMessageBox.information(
                self, get_text('save_success'), 
                get_text('save_success_msg').format(os.path.basename(file_path))
            )     
    def downsample_data(self, data, max_points=200000):
        if len(data) <= max_points:
            return data
        step = (len(data) + max_points - 1) // max_points  # 向上取整，避免超量
        return data[::step]
    def load_and_plot_data(self):
        """加载并绘制所有数据"""
        # 读取文件数据
        self.data1 = self.downsample_data(  # 👇 加降采样
            bin_utils.handle_invalid_values(
                bin_utils.read_bin_file(self.file1_path, dtype=np.dtype(self.dtype1))
            )
        )
        self.data2 = self.downsample_data(  # 👇 加降采样
            bin_utils.handle_invalid_values(
                bin_utils.read_bin_file(self.file2_path, dtype=np.dtype(self.dtype2))
            )
        )
        # 绘制图形（不变）
        self.plot_file1()
        self.plot_file2()
        self.plot_comparison()
    def should_show_data_points(self, ax, data_len):
        x_start, x_end = ax.get_xlim()
        visible_points = int(x_end - x_start) + 1  # 当前视图的点数
        return visible_points <= 200  # 显示≤50个点时，显示散点（可调整阈值）
    def plot_file1(self):
        """绘制文件1的图形（带DPI适配）"""
        self.file1_ax.clear()
        self.file1_ax.plot(
            self.data1, 
            color="#4285f4", 
            linewidth=get_scaled_value(1.0, self.initial_dpi)
        )
            # 2. 新增：缩放足够小时，显示散点
        if self.should_show_data_points(self.file1_ax, len(self.data1)):
            x_start, x_end = self.file1_ax.get_xlim()
            start_idx = max(0, int(round(x_start)))
            end_idx = min(len(self.data1)-1, int(round(x_end)))
            # 绘制红色散点（突出单个数据点）
            self.file1_ax.scatter(
                np.arange(start_idx, end_idx+1),  # x轴索引
                self.data1[start_idx:end_idx+1],  # y轴值
                color="#ff4444",  # 红色散点
                s=30,  # 点大小
                zorder=10  # 散点在数据线之上
            )
        self.file1_ax.set_title(
            f"file1: {os.path.basename(self.file1_path)} ({self.dtype1}) - length: {len(self.data1)}", 
            fontsize=get_scaled_font_size(10, self.initial_dpi)
        )
        self.file1_ax.set_xlabel(
            get_text('index'), 
            fontsize=get_scaled_font_size(9, self.initial_dpi)
        )
        self.file1_ax.set_ylabel(
            get_text('value'), 
            fontsize=get_scaled_font_size(9, self.initial_dpi)
        )
        self.file1_ax.grid(True, alpha=0.2)
        self.file1_ax.tick_params(
            axis='both', 
            labelsize=get_scaled_font_size(8, self.initial_dpi)
        )
        try:
            self.file1_figure.tight_layout()
        except Exception:
            pass
        self.file1_canvas.draw()
        
    def plot_file2(self):
        """绘制文件2的图形（带DPI适配）"""
        self.file2_ax.clear()
        self.file2_ax.plot(
            self.data2, 
            color="#ea4335", 
            linewidth=get_scaled_value(1.0, self.initial_dpi)
        )
        self.file2_ax.set_title(
            f"file2: {os.path.basename(self.file2_path)} ({self.dtype2}) - length: {len(self.data2)}", 
            fontsize=get_scaled_font_size(10, self.initial_dpi)
        )
        self.file2_ax.set_xlabel(
            get_text('index'), 
            fontsize=get_scaled_font_size(9, self.initial_dpi)
        )
        self.file2_ax.set_ylabel(
            get_text('value'), 
            fontsize=get_scaled_font_size(9, self.initial_dpi)
        )
        self.file2_ax.grid(True, alpha=0.2)
        self.file2_ax.tick_params(
            axis='both', 
            labelsize=get_scaled_font_size(8, self.initial_dpi)
        )
        try:
            self.file2_figure.tight_layout()
        except Exception:
            pass
        self.file2_canvas.draw()
    def on_mouse_scroll(self, event, canvas_key):
        """鼠标滚轮缩放：向上放大（聚焦鼠标），向下缩小（直到满窗口）"""
        # 1. 跳过无效情况（窗口移动中、无数据、鼠标不在绘图区域、无ax对象）
        if (self.is_moving 
            or not hasattr(self, 'data1') 
            or event.inaxes != getattr(self, f"{canvas_key}_ax")
            or event.xdata is None):  # 避免鼠标在边缘时xdata为None
            return

        # 2. 获取当前Canvas的ax和对应数据长度
        ax = getattr(self, f"{canvas_key}_ax")
        data_len = len(self.data1) if canvas_key in ["file1", "compare"] else len(self.data2)
        if data_len == 0:
            return
        
        # 3. 获取当前视图范围（x轴）
        current_xlim = ax.get_xlim()
        x_start, x_end = current_xlim
        x_range = x_end - x_start  # 当前视图的索引跨度
        
        # 4. 计算缩放后的范围（聚焦鼠标位置，避免缩放时视图跳走）
        mouse_x = event.xdata  # 鼠标所在的x轴数据坐标（索引）
        zoom_step = 1.2  # 每次缩放20%（可调整）
        is_full_view = (x_start <= 0) and (x_end >= data_len - 1)

        if event.button == 'up':
            # 滚轮向上：放大（缩小视图跨度，聚焦鼠标）
            new_x_start = mouse_x - (mouse_x - x_start) / zoom_step
            new_x_end = mouse_x + (x_end - mouse_x) / zoom_step
            # 限制最小跨度（避免放大过度，至少显示10个数据点）
            # min_range = max(10, data_len * 0.01)  # 最小跨度：10个点或数据长度的1%（取大值）
            # if (new_x_end - new_x_start) < min_range:
            #     new_x_start = mouse_x - min_range / 2
            #     new_x_end = mouse_x + min_range / 2
        else:
            if is_full_view:
                return  # 直接返回，不执行缩小操作
            # 滚轮向下：缩小（扩大视图跨度，直到显示全部数据）
            new_x_start = mouse_x - (mouse_x - x_start) * zoom_step
            new_x_end = mouse_x + (x_end - mouse_x) * zoom_step
            # 限制最大跨度（不超过全部数据范围）
            new_x_start = max(0, new_x_start)
            new_x_end = min(data_len - 1, new_x_end)
        
        # 5. 更新视图并重绘（y轴不变，避免缩放时y轴忽大忽小）
        ax.set_xlim(new_x_start, new_x_end)
        ax.autoscale_view(scaley=False)  # 固定y轴范围
        getattr(self, f"{canvas_key}_canvas").draw()
    def on_mouse_move(self, event, canvas_key):
        if canvas_key == "compare":
            # compare区需要传两个数据
            self.show_data_tooltip(event, canvas_key, self.data1, self.data2)
        else:
            # file1/file2区传单个数据
            self.show_data_tooltip(event, canvas_key)
        """鼠标拖动平移：仅当视图未显示全部数据时生效"""
        # 1. 未处于平移状态或无起始坐标，直接返回
        if not self.is_panning[canvas_key] or self.last_x[canvas_key] is None:
            return
        
        # 2. 获取当前Canvas的ax和对应数据长度
        ax = getattr(self, f"{canvas_key}_ax")
        data_len = len(self.data1) if canvas_key in ["file1", "compare"] else len(self.data2)
        if data_len == 0 or event.xdata is None:
            return
        
        # 3. 鼠标移出当前绘图区域，停止平移
        if event.inaxes != ax:
            self.is_panning[canvas_key] = False
            self.last_x[canvas_key] = None
            return
        
        # 4. 关键判断：当前是否已显示全部数据（满窗口）→ 若满窗口则不平移
        current_xlim = ax.get_xlim()
        x_start, x_end = current_xlim
        # 允许1%的误差（避免浮点精度问题导致判断失效）
        is_full_window = (x_start <= 0 + data_len * 0.01) and (x_end >= data_len - 1 - data_len * 0.01)
        if is_full_window:
            return  # 满窗口，不执行平移
        
        # 5. 计算x轴偏移量（当前位置 - 起始位置）
        current_x = event.xdata
        x_offset = current_x - self.last_x[canvas_key]  # 正值=鼠标向右拖，视图向左移
        
        # 6. 更新起始位置（用于下一次移动计算）
        self.last_x[canvas_key] = current_x
        
        # 7. 调整视图范围（x轴整体偏移，y轴不变）
        new_x_start = x_start - x_offset
        new_x_end = x_end - x_offset
        
        # 8. 限制范围不超出数据索引（0 ~ 数据长度-1）
        new_x_start = max(0, new_x_start)
        new_x_end = min(data_len - 1, new_x_end)
        
        # 9. 更新视图并重绘（只更新当前Canvas）
        ax.set_xlim(new_x_start, new_x_end)
        getattr(self, f"{canvas_key}_canvas").draw()


    def on_mouse_release(self, event, canvas_key):
        """鼠标释放：结束对应Canvas的平移状态"""
        # 只响应左键释放（Matplotlib中左键为1）
        if event.button == 1:
            self.is_panning[canvas_key] = False
            self.last_x[canvas_key] = None  # 清除起始坐标
    def on_mouse_press(self, event, canvas_key):
        if event.button != 1:
            return
        if self.is_moving or not hasattr(self, 'data1') or event.inaxes != getattr(self, f"{canvas_key}_ax"):
            return
        self.is_panning[canvas_key] = True
        self.last_x[canvas_key] = event.xdata

    # on_mouse_move 和 on_mouse_release 同理，均需通过 canvas_key 区分状态
    def plot_comparison(self):
        """绘制对比图形（带DPI适配+散点）"""
        self.compare_ax.clear()
        len1, len2 = len(self.data1), len(self.data2)
        min_len = min(len1, len2)  # 取较短数据的长度，避免索引超出
        
        # 1. 绘制两条数据线（原有逻辑不变）
        self.compare_ax.plot(
            self.data1, 
            color="#4285f4", 
            linewidth=get_scaled_value(1.0, self.initial_dpi),
            alpha=0.7,
            label=f"file1 ({self.dtype1})"
        )
        self.compare_ax.plot(
            self.data2, 
            color="#ea4335", 
            linewidth=get_scaled_value(1.0, self.initial_dpi),
            alpha=0.7,
            label=f"file2 ({self.dtype2})"
        )
        
        # 2. 新增：缩放足够小时，显示两个文件的散点
        if self.should_show_data_points(self.compare_ax, min_len):
            x_start, x_end = self.compare_ax.get_xlim()
            start_idx = max(0, int(round(x_start)))
            end_idx = min(min_len - 1, int(round(x_end)))  # 不超出较短数据的长度
            visible_indices = np.arange(start_idx, end_idx + 1)
            
            # 绘制file1散点（蓝色，与数据线同色）
            self.compare_ax.scatter(
                visible_indices,
                self.data1[start_idx:end_idx+1],
                color="#4285f4",
                s=30,
                zorder=10,  # 散点在数据线之上
                alpha=0.8
            )
            # 绘制file2散点（红色，与数据线同色）
            self.compare_ax.scatter(
                visible_indices,
                self.data2[start_idx:end_idx+1],
                color="#ea4335",
                s=30,
                zorder=10,
                alpha=0.8
            )
        
        # 3. 原有标题、指标计算、坐标轴设置（不变）
        if len1 != len2:
            self.compare_ax.set_title(
                get_text('file_length_mismatch').format(len1, len2), 
                fontsize=get_scaled_font_size(10, self.initial_dpi)
            )
        else:
            try:
                cos_sim = bin_utils.cosine_similarity([self.data1], [self.data2])[0][0]
                mse = bin_utils.mean_squared_error(self.data1, self.data2)
                mae = bin_utils.mean_absolute_error(self.data1, self.data2)
                self.compare_ax.set_title(
                    get_text('similarity').format(cos_sim, mse, mae), 
                    fontsize=get_scaled_font_size(10, self.initial_dpi)
                )
            except Exception as e:
                self.compare_ax.set_title(
                    get_text('calc_error').format(str(e)), 
                    fontsize=get_scaled_font_size(10, self.initial_dpi)
                )
        
        self.compare_ax.set_xlabel(
            get_text('index'), 
            fontsize=get_scaled_font_size(9, self.initial_dpi)
        )
        self.compare_ax.set_ylabel(
            get_text('value'), 
            fontsize=get_scaled_font_size(9, self.initial_dpi)
        )
        self.compare_ax.grid(True, alpha=0.2)
        self.compare_ax.legend(fontsize=get_scaled_font_size(8, self.initial_dpi))
        try:
            self.compare_figure.tight_layout()
        except Exception:
            pass
        self.compare_canvas.draw()    
    def on_dtype1_changed(self, dtype):
        self.dtype1 = dtype
        self.data1 = self.downsample_data(  # 记得之前加的降采样
            bin_utils.handle_invalid_values(
                bin_utils.read_bin_file(self.file1_path, dtype=np.dtype(self.dtype1))
            )
        )
        # 清理file1和compare区的提示框
        for key in ["file1", "compare"]:
            if self.tooltip[key]:
                self.tooltip[key].remove()
                self.tooltip[key] = None
                self.last_annotated_index[key] = -1
        # 重绘
        self.plot_file1()
        self.plot_comparison()
        
    def on_dtype2_changed(self, dtype):
        self.dtype2 = dtype
        self.data2 = self.downsample_data(
            bin_utils.handle_invalid_values(
                bin_utils.read_bin_file(self.file2_path, dtype=np.dtype(self.dtype2))
            )
        )
        # 清理file2和compare区的提示框
        for key in ["file2", "compare"]:
            if self.tooltip[key]:
                self.tooltip[key].remove()
                self.tooltip[key] = None
                self.last_annotated_index[key] = -1
        # 重绘
        self.plot_file2()
        self.plot_comparison()
    def closeEvent(self, event):
        # 清理所有提示框（避免内存残留）
        for key in ["file1", "file2", "compare"]:
            if self.tooltip[key]:
                self.tooltip[key].remove()
                self.tooltip[key] = None
        event.accept()
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)
