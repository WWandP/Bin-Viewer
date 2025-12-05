import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.config import Config
from src.bin_viewer import BinViewer
from src.plot_window import PlotWindow
from src.file_handler import FileHandler

# 设置高DPI支持
Config.setup_high_dpi()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 获取屏幕DPI并设置
    screen_dpi = app.desktop().logicalDpiX()
    Config.setup_matplotlib(screen_dpi)
    
    # 处理命令行参数
    bin_file_from_cmd = None
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        if os.path.isfile(target_file) and os.path.splitext(target_file)[1].lower() == '.bin':
            is_valid, error_msg = FileHandler.validate_file_size(target_file)
            if not is_valid:
                QMessageBox.warning(None, "文件错误", error_msg)
            else:
                bin_file_from_cmd = target_file
    
    if bin_file_from_cmd:
        plot_window = PlotWindow(bin_file_from_cmd, index=1, parent=None, screen_dpi=screen_dpi)
        plot_window.show()
    else:
        viewer = BinViewer(screen_dpi=screen_dpi)
        viewer.show()
    
    sys.exit(app.exec_())
    