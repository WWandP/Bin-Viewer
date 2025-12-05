# 绘图管理器
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QFont
from .config import Config

class PlotManager:
    def __init__(self, parent, dpi):
        self.parent = parent
        self.dpi = dpi
        self.data = None
        self.figure = None
        self.canvas = None
        self.ax = None
        
        # 交互状态
        self.tooltip = None
        self.point_artist = None
        self.last_annotated_index = -1
        self.is_panning = False
        self.last_x = None
        self.zoom_factor = 1.2
        
        self._init_plot()
    
    def _init_plot(self):
        """初始化绘图区域"""
        scaled_figure_size = (
            Config.get_scaled_value(8, self.dpi) / 100,
            Config.get_scaled_value(5, self.dpi) / 100
        )
        
        self.figure = Figure(
            figsize=scaled_figure_size,
            dpi=self.dpi,
            facecolor='white'
        )
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # 调整边距
        self.figure.subplots_adjust(
            left=0.08, right=0.95, top=0.92, bottom=0.12
        )
        
        # 绑定事件
        self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_move)
        self.canvas.mpl_connect('button_release_event', self._on_release)
        
        # 右键菜单
        self.canvas.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas.customContextMenuRequested.connect(self._show_context_menu)
        
        # 设置最小尺寸
        self.canvas.setMinimumSize(
            Config.get_scaled_value(600, self.dpi),
            Config.get_scaled_value(400, self.dpi)
        )
    
    def set_data(self, data):
        """设置数据"""
        if data is not None and len(data) > 0:
            self.data = data
        else:
            self.data = None
    
    def plot_data(self, title="", xlabel="Index", ylabel="Value"):
        """绘制数据（修复Y轴范围缓存问题）"""
        if self.data is None or len(self.data) == 0:
            pass
            return
        
        # 保存当前视图：只保留X轴范围，放弃Y轴范围（核心修改）
        if self.ax.has_data():
            current_xlim = self.ax.get_xlim()
            # 注释掉Y轴缓存，强制重新计算Y轴
            # current_ylim = self.ax.get_ylim()
        else:
            current_xlim = (0, len(self.data)-1)
        
        # 清除并重绘
        self.ax.clear()
        
        # 只恢复X轴范围，不恢复Y轴（核心修改）
        self.ax.set_xlim(current_xlim)
        
        # 绘制主线
        self.ax.plot(
            self.data,
            color="#4285f4",
            linewidth=Config.get_scaled_value(1.2, self.dpi),
            zorder=1
        )
        
        # 绘制散点（如果需要）
        if self._should_show_points():
            self._draw_data_points()
        
        # 设置标题和标签
        self.ax.set_title(title, fontsize=Config.get_scaled_font_size(10, self.dpi))
        self.ax.set_xlabel(xlabel, fontsize=Config.get_scaled_font_size(9, self.dpi))
        self.ax.set_ylabel(ylabel, fontsize=Config.get_scaled_font_size(9, self.dpi))
        self.ax.grid(True, alpha=0.3, linewidth=Config.get_scaled_value(0.8, self.dpi))
        self.ax.tick_params(axis='both', labelsize=Config.get_scaled_font_size(8, self.dpi))
        
        # 强制重新计算Y轴范围（核心修改：确保适配新数据）
        self.ax.relim()  # 重新计算数据边界
        self.ax.autoscale_view(scaley=True, scalex=False)  # Y轴自动缩放，X轴保持用户视图
        
        self.canvas.draw()
    def _should_show_points(self):
        """判断是否显示数据点"""
        if not hasattr(self, 'data') or self.data is None:
            return False
        
        x_start, x_end = self.ax.get_xlim()
        visible_points = int(x_end - x_start) + 1
        return visible_points <= Config.SHOW_DATA_THRESHOLD
    
    def _draw_data_points(self):
        """绘制数据点"""
        x_start, x_end = self.ax.get_xlim()
        start_idx = max(0, int(round(x_start)))
        end_idx = min(len(self.data) - 1, int(round(x_end)))
        
        visible_indices = np.arange(start_idx, end_idx + 1)
        visible_data = self.data[start_idx:end_idx + 1]
        
        self.point_artist = self.ax.scatter(
            visible_indices,
            visible_data,
            color="#4285f4",
            s=30,
            edgecolor="black",
            linewidth=1.5,
            zorder=10
        )
    
    def _on_scroll(self, event):
        """滚轮缩放"""
        if not hasattr(self, 'data') or self.data is None or event.inaxes != self.ax:
            return
        
        current_xlim = self.ax.get_xlim()
        x_start, x_end = current_xlim
        mouse_x = event.xdata
        
        if event.button == 'up':
            new_x_start = mouse_x - (mouse_x - x_start) / self.zoom_factor
            new_x_end = mouse_x + (x_end - mouse_x) / self.zoom_factor
        else:
            new_x_start = mouse_x - (mouse_x - x_start) * self.zoom_factor
            new_x_end = mouse_x + (x_end - mouse_x) * self.zoom_factor
        
        data_len = len(self.data)
        new_x_start = max(0, new_x_start)
        new_x_end = min(data_len - 1, new_x_end)
        
        self.ax.set_xlim(new_x_start, new_x_end)
        self.canvas.draw()
    
    def _on_press(self, event):
        """鼠标按下"""
        if event.button != 1 or event.inaxes != self.ax:
            return
        self.is_panning = True
        self.last_x = event.xdata
    
    def _on_move(self, event):
        """鼠标移动"""
        if not self.is_panning or self.last_x is None:
            if event.inaxes == self.ax and hasattr(self, 'data') and self.data is not None:
                self._show_tooltip(event)
            return
        
        if event.inaxes != self.ax:
            self.is_panning = False
            self.last_x = None
            return
        
        current_x = event.xdata
        x_offset = current_x - self.last_x
        self.last_x = current_x
        
        current_xlim = self.ax.get_xlim()
        new_x_start = current_xlim[0] - x_offset
        new_x_end = current_xlim[1] - x_offset
        
        data_len = len(self.data)
        new_x_start = max(0, new_x_start)
        new_x_end = min(data_len - 1, new_x_end)
        
        self.ax.set_xlim(new_x_start, new_x_end)
        self.canvas.draw()
    
    def _on_release(self, event):
        """鼠标释放"""
        if event.button == 1:
            self.is_panning = False
            self.last_x = None
    
    def _show_tooltip(self, event):
        """显示数据点提示"""
        if not self._should_show_points():
            if self.tooltip:
                self.tooltip.remove()
                self.tooltip = None
                self.last_annotated_index = -1
            return
        
        x_idx = int(round(event.xdata))
        
        if 0 <= x_idx < len(self.data) and x_idx != self.last_annotated_index:
            if self.tooltip:
                self.tooltip.remove()
            
            value = self.data[x_idx]
            self.tooltip = self.ax.annotate(
                f"Index: {x_idx}\nValue: {value:.6f}",
                xy=(x_idx, value),
                xytext=(10, 10),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                fontsize=Config.get_scaled_font_size(8, self.dpi),
                zorder=100
            )
            
            self.last_annotated_index = x_idx
            self.canvas.draw()
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()
        
        save_action = QAction("保存图片", self.parent)
        save_action.triggered.connect(self.save_image)
        menu.addAction(save_action)
        
        menu.exec_(self.canvas.mapToGlobal(position))
    
    def save_image(self):
        """保存图片"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "保存图片", "plot.png",
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;所有文件 (*)"
        )
        
        if file_path:
            self.figure.savefig(
                file_path,
                dpi=self.dpi * 2,
                bbox_inches='tight',
                facecolor='white'
            )
            QMessageBox.information(
                self.parent, "保存成功",
                f"图片已保存至: {os.path.basename(file_path)}"
            )