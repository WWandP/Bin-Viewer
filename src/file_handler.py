# 文件处理器
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from .config import Config

class FileHandler:
    @staticmethod
    def validate_file_size(file_path):
        """验证文件大小"""
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        file_size = os.path.getsize(file_path)
        if file_size > Config.MAX_FILE_SIZE_BYTES:
            file_size_mb = file_size / (1024 * 1024)
            return False, f"文件大小为 {file_size_mb:.2f}MB，超过限制的 {Config.MAX_FILE_SIZE_MB}MB"
        
        return True, ""
    
    @staticmethod
    def validate_bin_file(file_path):
        """验证是否为bin文件"""
        if not file_path:
            return False, "文件路径为空"
        
        if not os.path.splitext(file_path)[1].lower() == '.bin':
            return False, "不是.bin文件"
        
        return FileHandler.validate_file_size(file_path)
    
    @staticmethod
    def select_bin_file(parent, title="选择BIN文件"):
        """选择bin文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent, title, "", "BIN files (*.bin);;All files (*)"
        )
        
        if not file_path:
            return None, ""
        
        is_valid, error_msg = FileHandler.validate_bin_file(file_path)
        if not is_valid:
            QMessageBox.warning(parent, "文件错误", error_msg)
            return None, error_msg
        
        return file_path, ""
    
    @staticmethod
    def process_dropped_files(urls):
        """处理拖拽的文件"""
        files = [url.toLocalFile() for url in urls if url.isLocalFile()]
        bin_files = []
        errors = []
        
        for file in files:
            if os.path.splitext(file)[1].lower() == '.bin':
                is_valid, error_msg = FileHandler.validate_file_size(file)
                if is_valid:
                    bin_files.append(file)
                else:
                    errors.append(f"{os.path.basename(file)}: {error_msg}")
        
        return bin_files, errors