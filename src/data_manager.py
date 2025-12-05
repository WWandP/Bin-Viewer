# 数据管理器
import numpy as np
from .bin_utils import read_bin_file, handle_invalid_values
from .config import Config

class DataManager:
    def __init__(self):
        self.raw_data = None
        self.processed_data = None
        self.file_path = None
        self.dtype = None
    
    def load_file(self, file_path, dtype="float32"):
        """加载并处理文件数据"""
        import numpy as np
        
        self.file_path = file_path
        self.dtype = dtype
        
        try:
            # 读取原始数据
            self.raw_data = handle_invalid_values(
                read_bin_file(file_path, dtype=np.dtype(dtype))
            )
            
            if len(self.raw_data) == 0:
                pass
                return None
            
            # 降采样处理
            self.processed_data = self._downsample_data(
                self.raw_data, Config.MAX_DOWNSAMPLE_POINTS
            )
            
            pass
            return self.processed_data
            
        except Exception as e:
            pass
            return None
    
    def change_dtype(self, new_dtype):
        """更改数据类型并重新加载"""
        if self.file_path:
            self.dtype = new_dtype
            return self.load_file(self.file_path, new_dtype)
        return None
    
    def _downsample_data(self, data, max_points):
        """数据降采样"""
        if len(data) <= max_points:
            return data
        step = (len(data) + max_points - 1) // max_points
        return data[::step]
    
    def get_data_info(self):
        """获取数据信息"""
        if self.processed_data is None:
            return {}
        
        return {
            'raw_length': len(self.raw_data) if self.raw_data is not None else 0,
            'processed_length': len(self.processed_data),
            'dtype': self.dtype,
            'file_path': self.file_path
        }