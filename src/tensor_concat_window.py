import os
import numpy as np
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QComboBox, QListWidget, 
                             QMessageBox, QFileDialog, QGroupBox, QSpinBox,
                             QListWidgetItem, QFrame, QSplitter, QWidget, QCheckBox,
                             QApplication, QSlider, QGridLayout)
from PyQt5.QtCore import Qt, QMimeData, QSize, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QPainter, QPen, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from .config import Config
from .theme_manager import theme_manager
from .language_manager import get_text
import src.bin_utils as bin_utils
import re

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class FileBlockWidget(QWidget):
    """文件积木块显示组件 - 极简风格"""
    def __init__(self, filename, color, index, parent_window):
        super().__init__()
        self.filename = filename
        self.color = color
        self.index = index
        self.parent_window = parent_window
        self.setFixedSize(450, 40)  # 简化高度
        self._opacity = 1.0
        self.init_ui()
        
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
        
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()
        
    def paintEvent(self, event):
        if self._opacity < 1.0:
            painter = QPainter(self)
            painter.setOpacity(self._opacity)
            painter.fillRect(self.rect(), self.palette().window())
        super().paintEvent(event)
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # 删除按钮 - 使用可点击文本
        self.delete_btn = QLabel(get_text('delete'))
        self.delete_btn.setFixedSize(32, 28)
        self.delete_btn.setAlignment(Qt.AlignCenter)
        self.delete_btn.setStyleSheet("""
            QLabel {
                border: 1px solid #dc3545;
                border-radius: 4px;
                background: #fff5f5;
                color: #dc3545;
                font-size: 10px;
                font-weight: 500;
            }
            QLabel:hover {
                background: #dc3545;
                color: white;
            }
        """)
        self.delete_btn.setToolTip(get_text('delete') + "文件")
        self.delete_btn.mousePressEvent = lambda e: self.delete_file()
        layout.addWidget(self.delete_btn)
        
        # 序号标签
        self.index_label = QLabel(f"{self.index + 1}")
        self.index_label.setFixedSize(28, 28)
        self.index_label.setAlignment(Qt.AlignCenter)
        self.index_label.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                color: #6c757d;
                font-size: 11px;
                font-weight: normal;
            }
        """)
        layout.addWidget(self.index_label)
        
        # 文件名标签
        self.file_label = QLabel()
        self.file_label.setFixedSize(200, 28)
        self.update_file_display()
        layout.addWidget(self.file_label)
        
        # 调整按钮 - 使用可点击文本
        self.up_btn = QLabel(get_text('move_up'))
        self.up_btn.setFixedSize(32, 28)
        self.up_btn.setAlignment(Qt.AlignCenter)
        self.up_btn.setStyleSheet("""
            QLabel {
                border: 1px solid #6c757d;
                border-radius: 4px;
                background: #f8f9fa;
                color: #6c757d;
                font-size: 10px;
                font-weight: 500;
            }
            QLabel:hover {
                background: #6c757d;
                color: white;
            }
        """)
        self.up_btn.setToolTip(get_text('move_up'))
        self.up_btn.mousePressEvent = lambda e: self.move_up() if self.index > 0 else None
        layout.addWidget(self.up_btn)
        
        self.down_btn = QLabel(get_text('move_down'))
        self.down_btn.setFixedSize(32, 28)
        self.down_btn.setAlignment(Qt.AlignCenter)
        self.down_btn.setStyleSheet(self.up_btn.styleSheet())
        self.down_btn.setToolTip(get_text('move_down'))
        self.down_btn.mousePressEvent = lambda e: self.move_down() if self.index < len(self.parent_window.file_list) - 1 else None
        layout.addWidget(self.down_btn)
        
    def delete_file(self):
        self.parent_window.remove_file(self.index)
        
    def update_file_display(self):
        display_name = self.filename
        if len(display_name) > 22:
            display_name = display_name[:19] + "..."
            
        self.file_label.setStyleSheet(f"""
            QLabel {{
                background: {self.color};
                border: 1px solid {QColor(self.color).darker(110).name()};
                border-radius: 4px;
                color: white;
                font-size: 11px;
                font-weight: normal;
                padding-left: 8px;
            }}
        """)
        
        self.file_label.setText(display_name)
        self.file_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
    def move_up(self):
        if self.index > 0:
            self.animate_move()
            self.parent_window.move_file_to_position(self.index, self.index - 1)
            
    def move_down(self):
        if self.index < len(self.parent_window.file_list) - 1:
            self.animate_move()
            self.parent_window.move_file_to_position(self.index, self.index + 1)
            
    def animate_move(self):
        """移动动画效果"""
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1.0)
        self.animation.setKeyValueAt(0.5, 0.6)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
            
    def update_buttons(self):
        # 更新按钮样式以反映启用/禁用状态
        if self.index > 0:
            self.up_btn.setStyleSheet("""
                QLabel {
                    border: 1px solid #6c757d;
                    border-radius: 4px;
                    background: #f8f9fa;
                    color: #6c757d;
                    font-size: 10px;
                    font-weight: 500;
                }
                QLabel:hover {
                    background: #6c757d;
                    color: white;
                }
            """)
        else:
            self.up_btn.setStyleSheet("""
                QLabel {
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    background: #f8f9fa;
                    color: #adb5bd;
                    font-size: 10px;
                    font-weight: 500;
                }
            """)
            
        if self.index < len(self.parent_window.file_list) - 1:
            self.down_btn.setStyleSheet("""
                QLabel {
                    border: 1px solid #6c757d;
                    border-radius: 4px;
                    background: #f8f9fa;
                    color: #6c757d;
                    font-size: 10px;
                    font-weight: 500;
                }
                QLabel:hover {
                    background: #6c757d;
                    color: white;
                }
            """)
        else:
            self.down_btn.setStyleSheet("""
                QLabel {
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    background: #f8f9fa;
                    color: #adb5bd;
                    font-size: 10px;
                    font-weight: 500;
                }
            """)
        
    def update_index(self, new_index):
        self.index = new_index
        self.update_buttons()
        self.index_label.setText(f"{self.index + 1}")
        self.update_file_display()
        
    def update_text(self):
        """更新按钮文本"""
        self.delete_btn.setText(get_text('delete'))
        self.up_btn.setText(get_text('move_up'))
        self.down_btn.setText(get_text('move_down'))
        self.delete_btn.setToolTip(get_text('delete') + "文件")
        

        


class DropZoneWidget(QLabel):  # 改成继承 QLabel！
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setObjectName("DropLabel")  # 使用你自己写的样式！
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        
        # 文字内容
        self.update_text()
        
    def update_text(self):
        self.setText(get_text('drag_bin_files'))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setObjectName("DropLabel")  # 恢复样式
            self.setProperty("class", "Active")  # 触发 hover 效果
            self.style().polish(self)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setProperty("class", "")
        self.style().polish(self)

    def dropEvent(self, event):
        self.setProperty("class", "")
        self.style().polish(self)
        
        if event.mimeData().hasUrls():
            files = []
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith('.bin'):
                    files.append(url.toLocalFile())
            if files:
                remaining = 4 - len(self.main_window.file_list)
                files = files[:remaining]
                self.main_window.add_files_from_drop(files)
            event.acceptProposedAction()
class SmartShapeInput(QWidget):
    def __init__(self, filename, color, file_path, parent_window):
        super().__init__()
        self.filename = filename
        self.color = color
        self.file_path = file_path
        self.parent_window = parent_window
        self.setFixedSize(450, 44)  # 与文件块组件保持一致的宽度
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 占位空间（与序号对齐）
        spacer = QLabel()
        spacer.setFixedSize(32, 32)  # 与更新后的序号标签宽度保持一致
        layout.addWidget(spacer)
        
        # 实时形状显示
        self.shape_display = QLabel("[Shape]")
        self.shape_display.setFixedSize(80, 32)
        self.shape_display.setAlignment(Qt.AlignCenter)
        self.shape_display.setStyleSheet("""
            QLabel {
                background: #f0f8ff;
                border: 1px solid #4285f4;
                border-radius: 2px;
                color: #4285f4;
                font-size: 10px;
                font-weight: 500;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        layout.addWidget(self.shape_display)
        
        # 输入框
        self.input = QLineEdit()
        self.input.setFixedSize(180, 32)  # 调整宽度以适应形状显示
        self.input.setPlaceholderText(get_text('shape_placeholder'))
        self.input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 2px;
                padding: 0 8px;
                font-size: 11px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4285f4;
            }
        """)
        self.input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.input)
        
        # 状态指示器
        self.status_indicator = QLabel("●")
        self.status_indicator.setFixedSize(32, 32)  # 与删除按钮宽度保持一致
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 16px;
                border: 1px solid #eee;
                border-radius: 2px;
                background: #fafafa;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        layout.addWidget(self.status_indicator)
        
    def parse_shape(self, text):
        """模糊解析形状"""
        if not text.strip():
            return None, "Empty input"
            
        # 提取数字
        numbers = re.findall(r'\d+', text)
        if not numbers:
            return None, "No numbers found"
            
        try:
            shape = tuple(map(int, numbers))
            return shape, f"Parsed: {shape}"
        except ValueError:
            return None, "Invalid numbers"
            
    def on_text_changed(self, text):
        shape, message = self.parse_shape(text)
        
        # 更新形状显示
        if shape:
            shape_text = str(list(shape))
            if len(shape_text) > 12:
                shape_text = shape_text[:9] + "..."
            self.shape_display.setText(shape_text)
            
            try:
                file_size = os.path.getsize(self.file_path)
                dtype = np.dtype(self.parent_window.dtype_combo.currentText())
                expected_size = np.prod(shape) * dtype.itemsize
                
                if file_size == expected_size:
                    self.status_indicator.setText("✓")
                    self.status_indicator.setStyleSheet("""
                        QLabel {
                            color: #34a853;
                            font-size: 16px;
                            font-weight: bold;
                            border: 1px solid #34a853;
                            border-radius: 2px;
                            background: #f0fff4;
                        }
                    """)
                    self.status_indicator.setToolTip(f"形状: {shape}\n大小匹配: {np.prod(shape)} 个元素")
                    self.parent_window.file_shapes[self.filename] = ','.join(map(str, shape))
                else:
                    self.status_indicator.setText("✗")
                    self.status_indicator.setStyleSheet("""
                        QLabel {
                            color: #ea4335;
                            font-size: 16px;
                            font-weight: bold;
                            border: 1px solid #ea4335;
                            border-radius: 2px;
                            background: #fff5f5;
                        }
                    """)
                    actual_elements = file_size // dtype.itemsize
                    expected_elements = np.prod(shape)
                    self.status_indicator.setToolTip(f"形状: {shape}\n大小不匹配: 实际 {actual_elements} 个元素 vs 期望 {expected_elements} 个元素")
                    self.parent_window.file_shapes[self.filename] = ','.join(map(str, shape))
            except Exception as e:
                self.status_indicator.setText("⚠")
                self.status_indicator.setStyleSheet("""
                    QLabel {
                        color: #ff9800;
                        font-size: 16px;
                        font-weight: bold;
                        border: 1px solid #ff9800;
                        border-radius: 2px;
                        background: #fff8e1;
                    }
                """)
                self.status_indicator.setToolTip(f"Error: {str(e)}")
        else:
            self.shape_display.setText("[]")
            self.status_indicator.setText("●")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    color: #ccc;
                    font-size: 16px;
                    border: 1px solid #eee;
                    border-radius: 2px;
                    background: #fafafa;
                }
            """)
            self.status_indicator.setToolTip(message if message != "Empty input" else "Enter shape dimensions")
            self.parent_window.file_shapes[self.filename] = ""
            
        self.parent_window.validate_all()
        
    def set_text(self, text):
        self.input.setText(text)

class ResultPreviewWindow(QDialog):
    def __init__(self, parent, result_tensor, title="拼接结果预览"):
        super().__init__(parent)
        self.result_tensor = result_tensor
        self.setWindowTitle(title)
        self.resize(700, 500)
        self.position_near_parent()
        self.init_ui()
        self.update_plot()
        
    def position_near_parent(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            screen = QApplication.desktop().screenGeometry()
            
            x = parent_rect.right() + 10
            y = parent_rect.top()
            
            if x + self.width() > screen.right():
                x = parent_rect.left() - self.width() - 10
                
            if x < screen.left():
                x = parent_rect.left()
                y = parent_rect.bottom() + 10
                
            if y + self.height() > screen.bottom():
                y = parent_rect.top() - self.height() - 10
                
            x = max(screen.left(), min(x, screen.right() - self.width()))
            y = max(screen.top(), min(y, screen.bottom() - self.height()))
            
            self.move(x, y)
            
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 信息标签
        info_label = QLabel(f"形状: {self.result_tensor.shape}  |  大小: {self.result_tensor.nbytes:,} 字节")
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(info_label)
        
        self.figure = Figure(figsize=(8, 5), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        try:
            # 将多维张量展平为1D进行可视化
            data = self.result_tensor.flatten()
            
            # 智能下采样
            if len(data) > 3000:
                target_points = 2000
                step = max(1, len(data) // target_points)
                indices = np.arange(0, len(data), step)
                data = data[indices]
                
            ax.plot(data, linewidth=1.5, color='#4285f4', alpha=0.8)
            ax.set_title("Concatenation Result (Flattened)", fontsize=12)
            ax.set_xlabel("Index")
            ax.set_ylabel("Value")
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'绘制错误\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
                
        self.figure.tight_layout()
        self.canvas.draw()

class PreviewWindow(QDialog):
    def __init__(self, parent, file_list, colors):
        super().__init__(parent)
        self.file_list = file_list
        self.colors = colors
        self.setWindowTitle(get_text('data_preview'))
        self.resize(800, 600)
        self.position_near_parent()
        self.init_ui()
        self.update_plots()
        
    def position_near_parent(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            screen = QApplication.desktop().screenGeometry()
            
            # 尝试右侧放置
            x = parent_rect.right() + 10
            y = parent_rect.top()
            
            # 如果右侧空间不够，尝试左侧
            if x + self.width() > screen.right():
                x = parent_rect.left() - self.width() - 10
                
            # 如果左侧也不够，尝试下方
            if x < screen.left():
                x = parent_rect.left()
                y = parent_rect.bottom() + 10
                
            # 如果下方也不够，尝试上方
            if y + self.height() > screen.bottom():
                y = parent_rect.top() - self.height() - 10
                
            # 确保窗口在屏幕内
            x = max(screen.left(), min(x, screen.right() - self.width()))
            y = max(screen.top(), min(y, screen.bottom() - self.height()))
            
            self.move(x, y)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.figure = Figure(figsize=(10, 8), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
    def update_plots(self):
        self.figure.clear()
        
        if not self.file_list:
            return
            
        n_files = len(self.file_list)
        if n_files == 1:
            rows, cols = 1, 1
        elif n_files == 2:
            rows, cols = 2, 1
        elif n_files <= 4:
            rows, cols = 2, 2
        else:
            rows, cols = 3, 2
            
        for i, file_path in enumerate(self.file_list):
            ax = self.figure.add_subplot(rows, cols, i + 1)
            
            try:
                # 使用float32作为默认类型
                data = bin_utils.read_bin_file(file_path, dtype=np.dtype('float32'))
                
                # 智能下采样
                if len(data) > 2000:
                    # 使用更智能的下采样策略
                    target_points = 1500
                    step = max(1, len(data) // target_points)
                    indices = np.arange(0, len(data), step)
                    data = data[indices]
                    
                ax.plot(data, linewidth=2.0, color=self.colors[i % len(self.colors)], alpha=0.9)
                ax.set_title(f"{i+1}. {os.path.basename(file_path)}", fontsize=10)
                ax.tick_params(labelsize=8)
                ax.grid(True, alpha=0.3)
                
            except Exception as e:
                ax.text(0.5, 0.5, f'Error loading\n{os.path.basename(file_path)}', 
                       ha='center', va='center', transform=ax.transAxes)
                
        self.figure.tight_layout()
        self.canvas.draw()

class TensorConcatWindow(QDialog):
    def __init__(self, parent=None, screen_dpi=None):
        super().__init__(parent)
        self.screen_dpi = screen_dpi or 96
        self.file_list = []
        self.file_colors = {}  # 文件名 -> 颜色的映射
        self.file_shapes = {}  # 文件名 -> 形状的映射
        self.shape_widgets = []  # 存储形状输入组件
        self.block_widgets = []  # 存储积木块组件
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(get_text('tensor_concat_title'))
        self.resize(
            Config.get_scaled_value(900, self.screen_dpi),
            Config.get_scaled_value(650, self.screen_dpi)
        )
        
        # 应用主题样式
        self.setStyleSheet(theme_manager.generate_style(self.screen_dpi))
        
        layout = QVBoxLayout(self)
        
        # 拖拽区域（顶部）
        drop_container = QWidget()
        drop_layout = QVBoxLayout(drop_container)
        drop_layout.setContentsMargins(0, 0, 0, 0)
        drop_layout.setSpacing(8)
        
        # 拖拽区域
        self.drop_zone = DropZoneWidget(self)
        self.drop_zone.setMinimumHeight(Config.get_scaled_value(140, self.screen_dpi))
        drop_layout.addWidget(self.drop_zone)
        
        # 添加文件按钮（长条形）
        self.add_file_btn = QPushButton(get_text('add_bin_file'))
        self.add_file_btn.setObjectName("PrimaryButton")
        self.add_file_btn.setFixedHeight(Config.get_scaled_value(40, self.screen_dpi))
        self.add_file_btn.setCursor(Qt.PointingHandCursor)
        self.add_file_btn.clicked.connect(self.add_file)
        drop_layout.addWidget(self.add_file_btn)
        
        layout.addWidget(drop_container)
        
        # 主要内容区域（水平分割）
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 文件区域
        self.files_group = QGroupBox(get_text('file_list'))
        files_layout = QVBoxLayout(self.files_group)
        
        # 文件列表区域（统一布局）
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setContentsMargins(10, 10, 10, 10)
        self.files_layout.setSpacing(8)
        self.files_layout.setAlignment(Qt.AlignTop)
        
        files_layout.addWidget(self.files_container)
        

        
        left_layout.addWidget(self.files_group)
        
        # 配置区域
        self.config_group = QGroupBox(get_text('config_options'))
        config_layout = QGridLayout(self.config_group)
        config_layout.setSpacing(Config.get_scaled_value(8, self.screen_dpi))
        
        # 数据类型
        self.dtype_label = QLabel(get_text('data_type'))
        config_layout.addWidget(self.dtype_label, 0, 0)
        self.dtype_combo = QComboBox()
        self.dtype_combo.addItems(["float32", "int8", "int16", "float64"])
        self.dtype_combo.currentTextChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.dtype_combo, 0, 1)
        
        # 拼接模式
        self.mode_label = QLabel(get_text('concat_mode'))
        config_layout.addWidget(self.mode_label, 1, 0)
        self.mode_combo = QComboBox()
        self.update_mode_combo_items()
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        config_layout.addWidget(self.mode_combo, 1, 1)
        

        
        # 拼接维度
        self.axis_label = QLabel(get_text('concat_axis'))
        config_layout.addWidget(self.axis_label, 2, 0)
        self.axis_spinbox = QSpinBox()
        self.axis_spinbox.setMinimum(0)
        self.axis_spinbox.setMaximum(10)
        self.axis_spinbox.setValue(0)
        self.axis_spinbox.valueChanged.connect(self.validate_shape)
        config_layout.addWidget(self.axis_spinbox, 2, 1)
        
        # 预览选项
        self.preview_btn_toggle = QPushButton(get_text('show_preview'))
        self.preview_btn_toggle.clicked.connect(self.show_preview_window)
        self.preview_btn_toggle.setEnabled(False)
        config_layout.addWidget(self.preview_btn_toggle, 3, 0, 1, 2)
        
        # 状态显示
        self.status_label = QLabel(get_text('add_files'))
        self.status_label.setStyleSheet("color: #666; font-size: 11px; padding: 8px; border-radius: 4px;")
        self.status_label.setWordWrap(True)
        config_layout.addWidget(self.status_label, 4, 0, 1, 2)
        
        # 配置区域已移到右侧
        
        self.preview_window = None
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.preview_btn = QPushButton(get_text('preview_result'))
        self.preview_btn.setObjectName("PrimaryButton")
        self.preview_btn.clicked.connect(self.preview_concat)
        self.preview_btn.setEnabled(False)
        
        self.save_btn = QPushButton(get_text('save_result'))
        self.save_btn.clicked.connect(self.save_result)
        self.save_btn.setEnabled(False)
        
        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch()
        left_layout.addLayout(btn_layout)
        
        # 右侧区域（配置区域）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(self.config_group)
        right_layout.addStretch()
        
        # 添加到分割器
        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([400, 300])
        
        layout.addWidget(content_splitter)
        
        self.result_tensor = None
        self.base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        self.on_mode_changed()
        self.update_file_blocks()
        
    def update_mode_combo_items(self):
        """更新拼接模式下拉框选项"""
        current_index = self.mode_combo.currentIndex() if hasattr(self, 'mode_combo') else 0
        self.mode_combo.clear()
        self.mode_combo.addItems([get_text('simple_concat'), get_text('tensor_concat_mode')])
        self.mode_combo.setCurrentIndex(current_index)
        
    def add_file(self):
        remaining_slots = 4 - len(self.file_list)
        if remaining_slots <= 0:
            QMessageBox.warning(self, get_text('hint'), get_text('max_files_warning'))
            return
            
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, f"Select BIN Files (can add {remaining_slots} more)", "", "BIN Files (*.bin);;All Files (*)"
        )
        if file_paths:
            if len(file_paths) > remaining_slots:
                QMessageBox.information(self, get_text('hint'), 
                                       f"Can only add {remaining_slots} more files, selected first {remaining_slots}")
                file_paths = file_paths[:remaining_slots]
            self.add_files_from_drop(file_paths)
            
    def add_files_from_drop(self, file_paths):
        for file_path in file_paths:
            if file_path not in self.file_list and len(self.file_list) < 4:
                self.file_list.append(file_path)
                # 为新文件分配颜色
                filename = os.path.basename(file_path)
                if filename not in self.file_colors:
                    color_index = len(self.file_colors) % len(self.base_colors)
                    self.file_colors[filename] = self.base_colors[color_index]
                    self.file_shapes[filename] = ""  # 初始化形状
        self.update_file_blocks()
        # 如果预览窗口打开，更新预览
        if self.preview_window and self.preview_window.isVisible():
            self.preview_window.file_list = self.file_list.copy()
            self.preview_window.colors = [self.file_colors[os.path.basename(f)] for f in self.file_list]
            self.preview_window.update_plots()
        self.validate_all()
        
    def remove_file(self, index):
        """删除指定索引的文件"""
        if 0 <= index < len(self.file_list):
            file_path = self.file_list.pop(index)
            filename = os.path.basename(file_path)
            
            # 清理相关数据
            if filename in self.file_colors:
                del self.file_colors[filename]
            if filename in self.file_shapes:
                del self.file_shapes[filename]
            
            # 更新界面
            self.update_file_blocks()
            
            # 如果预览窗口打开，更新预览
            if self.preview_window and self.preview_window.isVisible():
                if self.file_list:
                    self.preview_window.file_list = self.file_list.copy()
                    self.preview_window.colors = [self.file_colors[os.path.basename(f)] for f in self.file_list]
                    self.preview_window.update_plots()
                else:
                    self.preview_window.close()
            
            # 重新验证
            self.validate_all()
        
    def move_file_to_position(self, from_index, to_index):
        """移动文件到指定位置并添加动画效果"""
        if 0 <= from_index < len(self.file_list) and 0 <= to_index < len(self.file_list) and from_index != to_index:
            # 移动文件
            file_path = self.file_list.pop(from_index)
            self.file_list.insert(to_index, file_path)
            
            # 延迟更新界面，等待动画完成
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self.update_file_blocks)
            
            # 如果预览窗口打开，更新预览
            if self.preview_window and self.preview_window.isVisible():
                def update_preview():
                    self.preview_window.file_list = self.file_list.copy()
                    self.preview_window.colors = [self.file_colors[os.path.basename(f)] for f in self.file_list]
                    self.preview_window.update_plots()
                QTimer.singleShot(150, update_preview)
            

        
    def update_file_blocks(self):
        # 清除旧的组件
        for i in reversed(range(self.files_layout.count())):
            child = self.files_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.shape_widgets.clear()
                
        if not self.file_list:
            # 优雅的空状态显示
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setContentsMargins(30, 40, 30, 40)
            empty_layout.setSpacing(15)
            
            # 图标
            icon_label = QLabel("📁")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    color: #ddd;
                    margin-bottom: 10px;
                    background: transparent;
                }
            """)
            empty_layout.addWidget(icon_label)
            
            # 主要提示文本
            main_text = QLabel(get_text('no_files_empty'))
            main_text.setAlignment(Qt.AlignCenter)
            main_text.setStyleSheet("""
                QLabel {
                    color: #999;
                    font-size: 16px;
                    font-weight: 500;
                    margin-bottom: 5px;
                    background: transparent;
                }
            """)
            empty_layout.addWidget(main_text)
            
            # 次要提示文本
            hint_text = QLabel(get_text('drag_hint_empty'))
            hint_text.setAlignment(Qt.AlignCenter)
            hint_text.setStyleSheet("""
                QLabel {
                    color: #bbb;
                    font-size: 12px;
                    background: transparent;
                }
            """)
            empty_layout.addWidget(hint_text)
            
            self.files_layout.addWidget(empty_widget)
            self.preview_btn_toggle.setEnabled(False)
        else:
            is_tensor_mode = get_text('tensor_concat_mode') in self.mode_combo.currentText()
            
            for i, file_path in enumerate(self.file_list):
                filename = os.path.basename(file_path)
                color = self.file_colors[filename]
                
                # 创建文件块
                block = FileBlockWidget(filename, color, i, self)
                self.files_layout.addWidget(block)
                
                # 在张量模式下添加形状输入
                if is_tensor_mode:
                    shape_widget = SmartShapeInput(filename, color, file_path, self)
                    shape_widget.set_text(self.file_shapes.get(filename, ""))
                    self.files_layout.addWidget(shape_widget)
                    self.shape_widgets.append((filename, shape_widget))
                    
            self.preview_btn_toggle.setEnabled(True)
            
            # 更新所有文件块的索引
            block_index = 0
            for i in range(self.files_layout.count()):
                widget = self.files_layout.itemAt(i).widget()
                if isinstance(widget, FileBlockWidget):
                    widget.update_index(block_index)
                    widget.update_buttons()
                    widget.update_text()  # 更新按钮文本
                    block_index += 1
            
    def on_mode_changed(self):
        is_tensor_mode = get_text('tensor_concat_mode') in self.mode_combo.currentText()
        # 显示/隐藏拼接轴控件
        self.axis_label.setVisible(is_tensor_mode)
        self.axis_spinbox.setVisible(is_tensor_mode)
        self.update_file_blocks()
        self.validate_all()
        
    def on_config_changed(self):
        self.validate_all()
        
    def show_preview_window(self):
        if not self.file_list:
            return
            
        colors = [self.file_colors[os.path.basename(f)] for f in self.file_list]
        if self.preview_window is None or not self.preview_window.isVisible():
            self.preview_window = PreviewWindow(self, self.file_list.copy(), colors)
            self.preview_window.show()
        else:
            self.preview_window.raise_()
            self.preview_window.activateWindow()
        
    def validate_shape(self):
        self.validate_all()
        
    def validate_all(self):
        if not self.file_list:
            self.status_label.setText(get_text('add_files'))
            self.status_label.setStyleSheet("color: #ea4335;")
            self.preview_btn.setEnabled(False)
            return
            
        is_tensor_mode = get_text('tensor_concat_mode') in self.mode_combo.currentText()
        dtype = np.dtype(self.dtype_combo.currentText())
        
        if is_tensor_mode:
            # 检查每个文件的形状
            axis = self.axis_spinbox.value()
            
            for file_path in self.file_list:
                filename = os.path.basename(file_path)
                shape_text = self.file_shapes.get(filename, "").strip()
                
                if not shape_text:
                    self.status_label.setText(get_text('file_need_shape').format(filename))
                    self.status_label.setStyleSheet("color: #ea4335;")
                    self.preview_btn.setEnabled(False)
                    return
                    
                try:
                    shape = tuple(map(int, shape_text.split(',')))
                    
                    if axis >= len(shape):
                        self.status_label.setText(get_text('axis_out_of_range').format(axis, filename))
                        self.status_label.setStyleSheet("color: #ea4335;")
                        self.preview_btn.setEnabled(False)
                        return
                        
                    expected_size = np.prod(shape) * dtype.itemsize
                    file_size = os.path.getsize(file_path)
                    if file_size != expected_size:
                        actual_elements = file_size // dtype.itemsize
                        expected_elements = np.prod(shape)
                        self.status_label.setText(
                            get_text('file_size_mismatch').format(filename, expected_elements, actual_elements)
                        )
                        self.status_label.setStyleSheet("color: #ea4335;")
                        self.preview_btn.setEnabled(False)
                        return
                        
                except ValueError as e:
                    self.status_label.setText(get_text('file_shape_error').format(filename, str(e)))
                    self.status_label.setStyleSheet("color: #ea4335;")
                    self.preview_btn.setEnabled(False)
                    return
                    
            self.status_label.setText(
                get_text('files_ready').format(len(self.file_list)) + "\n" +
                get_text('tensor_mode').format(axis)
            )
        else:
            # 简单模式
            self.status_label.setText(
                get_text('files_ready').format(len(self.file_list)) + "\n" +
                get_text('simple_mode')
            )
            
        self.status_label.setStyleSheet("color: #34a853;")
        self.preview_btn.setEnabled(True)
            
    def preview_concat(self):
        try:
            dtype = np.dtype(self.dtype_combo.currentText())
            is_tensor_mode = get_text('tensor_concat_mode') in self.mode_combo.currentText()
            
            data_arrays = []
            for file_path in self.file_list:
                data = bin_utils.read_bin_file(file_path, dtype=dtype)
                data_arrays.append(data)
                
            if is_tensor_mode:
                axis = self.axis_spinbox.value()
                tensors = []
                
                for i, (file_path, data) in enumerate(zip(self.file_list, data_arrays)):
                    filename = os.path.basename(file_path)
                    shape_text = self.file_shapes[filename]
                    shape = tuple(map(int, shape_text.split(',')))
                    tensor = data.reshape(shape)
                    tensors.append(tensor)
                    
                self.result_tensor = np.concatenate(tensors, axis=axis)
                
                # 显示结果预览窗口
                result_window = ResultPreviewWindow(self, self.result_tensor, "Tensor Concatenation Result")
                result_window.exec_()
            else:
                self.result_tensor = np.concatenate(data_arrays, axis=0)
                
                # 显示结果预览窗口
                result_window = ResultPreviewWindow(self, self.result_tensor, "Simple Concatenation Result")
                result_window.exec_()
                
            self.save_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, get_text('concat_failed'), f"{get_text('error')}: {str(e)}")
            
    def save_result(self):
        if self.result_tensor is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, get_text('save_concat_result'), "concatenated.bin", "BIN Files (*.bin);;All Files (*)"
        )
        
        if file_path:
            try:
                self.result_tensor.tofile(file_path)
                QMessageBox.information(
                    self, get_text('save_success'), 
                    get_text('result_saved').format(
                        file_path, self.result_tensor.shape, self.result_tensor.nbytes
                    )
                )
            except Exception as e:
                QMessageBox.critical(self, get_text('save_failed'), f"{get_text('error')}: {str(e)}")