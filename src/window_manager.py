# 窗口管理器
from PyQt5.QtWidgets import QApplication

class WindowManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.windows = []
            cls._instance.next_index = 1
        return cls._instance
    
    def register_window(self, window):
        """注册窗口"""
        self.windows.append(window)
        return self.next_index
    
    def unregister_window(self, window):
        """注销窗口"""
        if window in self.windows:
            self.windows.remove(window)
    
    def get_next_index(self):
        """获取下一个窗口索引"""
        # 查找现有PlotWindow的最大索引
        from .plot_window import PlotWindow
        existing_windows = [w for w in QApplication.instance().topLevelWidgets() 
                          if isinstance(w, PlotWindow)]
        
        if existing_windows:
            max_index = max(w.index for w in existing_windows)
            self.next_index = max_index + 1
        
        current_index = self.next_index
        self.next_index += 1
        return current_index
    
    def close_all_windows(self):
        """关闭所有窗口"""
        for window in self.windows[:]:  # 复制列表避免修改时出错
            window.close()
        self.windows.clear()
    
    def get_window_count(self):
        """获取窗口数量"""
        return len(self.windows)