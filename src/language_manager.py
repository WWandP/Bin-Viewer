# 语言管理器
import json
import os
import sys

class LanguageManager:
    _instance = None
    _current_language = "zh"
    _config_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance
    
    def _init_config(self):
        """初始化配置文件路径"""
        if hasattr(sys, '_MEIPASS'):
            # 打包后的环境
            config_dir = os.path.expanduser("~/.binviewer")
        else:
            # 开发环境
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        self._config_file = os.path.join(config_dir, "config.json")
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._current_language = config.get('language', 'zh')
        except Exception:
            self._current_language = 'zh'
    
    def _save_config(self):
        """保存配置"""
        try:
            config = {'language': self._current_language}
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def get_language(self):
        """获取当前语言"""
        return self._current_language
    
    def set_language(self, language):
        """设置语言"""
        if language in ['zh', 'en']:
            self._current_language = language
            self._save_config()
    
    def get_text(self, key):
        """获取文本"""
        return TEXTS.get(key, {}).get(self._current_language, key)

# 文本字典
TEXTS = {
    # 主窗口
    'main_title': {'zh': 'BIN文件查看器', 'en': 'BIN File Viewer'},
    'drag_hint': {'zh': '将BIN文件拖放到此处\n或点击下方按钮选择文件\n(文件大小限制：{}MB)', 'en': 'Drag BIN files here\nor click button below to select files\n(File size limit: {}MB)'},
    'open_file': {'zh': '打开BIN文件', 'en': 'Open BIN File'},
    'compare_files': {'zh': '直接对比两个文件', 'en': 'Compare Two Files'},
    'tensor_concat': {'zh': '张量拼接工具', 'en': 'Tensor Concatenation Tool'},
    'theme': {'zh': '主题', 'en': 'Theme'},
    'language': {'zh': '语言', 'en': 'Language'},
    'chinese': {'zh': '中文', 'en': 'Chinese'},
    'english': {'zh': 'English', 'en': 'English'},
    'tips': {'zh': '提示:\n- 按ESC键关闭任何窗口\n- 支持拖放文件（1个打开，2个对比）\n- 右键点击图形可保存图片', 'en': 'Tips:\n- Press ESC to close any window\n- Support drag & drop (1 file to open, 2 files to compare)\n- Right-click on chart to save image'},
    'file_opened': {'zh': '已打开文件: {} (文件 {})', 'en': 'File opened: {} (File {})'},
    'no_files': {'zh': '没有打开的文件', 'en': 'No files opened'},
    'select_first_file': {'zh': '选择第一个BIN文件', 'en': 'Select First BIN File'},
    'select_second_file': {'zh': '选择第二个BIN文件', 'en': 'Select Second BIN File'},
    
    # 张量拼接窗口
    'tensor_concat_title': {'zh': '张量拼接工具', 'en': 'Tensor Concatenation Tool'},
    'drag_bin_files': {'zh': '将 BIN 文件拖放到此处\n(最多支持 4 个文件)', 'en': 'Drag BIN files here\n(Up to 4 files supported)'},
    'add_bin_file': {'zh': '+ 添加 BIN 文件', 'en': '+ Add BIN File'},
    'file_list': {'zh': '文件列表 (最多4个文件)', 'en': 'File List (Max 4 files)'},
    'config_options': {'zh': '配置选项', 'en': 'Configuration'},
    'data_type': {'zh': '数据类型:', 'en': 'Data Type:'},
    'concat_mode': {'zh': '拼接模式:', 'en': 'Concat Mode:'},
    'simple_concat': {'zh': '简单拼接 (第1维)', 'en': 'Simple Concat (1st dim)'},
    'tensor_concat_mode': {'zh': '张量拼接 (指定形状)', 'en': 'Tensor Concat (specify shape)'},
    'concat_axis': {'zh': '拼接轴:', 'en': 'Concat Axis:'},
    'show_preview': {'zh': '显示数据预览', 'en': 'Show Data Preview'},
    'preview_result': {'zh': '预览拼接结果', 'en': 'Preview Result'},
    'save_result': {'zh': '保存结果', 'en': 'Save Result'},
    'add_files': {'zh': '请添加文件', 'en': 'Please add files'},
    'max_files_warning': {'zh': '最多支持 4 个文件', 'en': 'Maximum 4 files supported'},
    'files_ready': {'zh': '✓ {} 个文件就绪', 'en': '✓ {} files ready'},
    'simple_mode': {'zh': '简单拼接模式 (第1维)', 'en': 'Simple concat mode (1st dim)'},
    'tensor_mode': {'zh': '张量模式, 拼接轴: {}', 'en': 'Tensor mode, concat axis: {}'},
    'no_files_empty': {'zh': '暂无文件', 'en': 'No Files'},
    'drag_hint_empty': {'zh': '拖拽或添加 BIN 文件开始', 'en': 'Drag or add BIN files to start'},
    'shape_placeholder': {'zh': '形状: 例如 3,224,224', 'en': 'Shape: e.g. 3,224,224'},
    'file_need_shape': {'zh': '文件 {} 需要输入形状', 'en': 'File {} needs shape input'},
    'axis_out_of_range': {'zh': '拼接轴 {} 超出文件 {} 的维度范围', 'en': 'Concat axis {} exceeds dimensions of file {}'},
    'file_size_mismatch': {'zh': '文件 {} 大小不匹配\n期望: {} 个元素, 实际: {} 个元素', 'en': 'File {} size mismatch\nExpected: {} elements, Actual: {} elements'},
    'file_shape_error': {'zh': '文件 {} 形状格式错误: {}', 'en': 'File {} shape format error: {}'},
    'move_up': {'zh': '上移', 'en': 'Up'},
    'move_down': {'zh': '下移', 'en': 'Down'},
    'delete': {'zh': '删除', 'en': 'Del'},
    'data_preview': {'zh': '数据预览', 'en': 'Data Preview'},
    'concat_failed': {'zh': '拼接失败', 'en': 'Concatenation Failed'},
    'save_success': {'zh': '保存成功', 'en': 'Save Success'},
    'save_failed': {'zh': '保存失败', 'en': 'Save Failed'},
    'error': {'zh': '错误', 'en': 'Error'},
    'hint': {'zh': '提示', 'en': 'Hint'},
    'info': {'zh': '信息', 'en': 'Info'},
    
    # 文件操作
    'file_error': {'zh': '文件错误', 'en': 'File Error'},
    'not_support_3_files': {'zh': '不支持3个及以上文件对比', 'en': 'Not support comparing 3+ files'},
    'select_bin_file': {'zh': '选择BIN文件', 'en': 'Select BIN File'},
    'save_concat_result': {'zh': '保存拼接结果', 'en': 'Save Concatenation Result'},
    'result_saved': {'zh': '拼接结果已保存到:\n{}\n\n形状: {}\n大小: {:,} 字节', 'en': 'Result saved to:\n{}\n\nShape: {}\nSize: {:,} bytes'},
    
    # 单视图窗口
    'file': {'zh': '文件', 'en': 'File'},
    'data_type_label': {'zh': '数据类型:', 'en': 'Data Type:'},
    'select_compare_file': {'zh': '选择文件对比', 'en': 'Select File to Compare'},
    'open_new_file': {'zh': '打开新文件', 'en': 'Open New File'},
    'select_compare_bin': {'zh': '选择要对比的BIN文件', 'en': 'Select BIN File to Compare'},
    
    # 对比窗口
    'bin_comparison': {'zh': 'bin对比', 'en': 'BIN Comparison'},
    'vs': {'zh': 'vs', 'en': 'vs'},
    'type': {'zh': '类型:', 'en': 'Type:'},
    'save_image': {'zh': '保存图片', 'en': 'Save Image'},
    'save_image_title': {'zh': '保存图片', 'en': 'Save Image'},
    'save_image_filter': {'zh': '矢量图 (SVG) (*.svg);;矢量图 (PDF) (*.pdf);;位图 (PNG) (*.png);;位图 (JPEG) (*.jpg);;所有文件 (*)', 'en': 'Vector (SVG) (*.svg);;Vector (PDF) (*.pdf);;Bitmap (PNG) (*.png);;Bitmap (JPEG) (*.jpg);;All Files (*)'},
    'save_success_msg': {'zh': '图片已保存至: {}', 'en': 'Image saved to: {}'},
    'file_length_mismatch': {'zh': 'File length mismatch: {} vs {}', 'en': 'File length mismatch: {} vs {}'},
    'similarity': {'zh': 'Similarity: Cos={:.3f}, MSE={:.3e}, MAE={:.3e}', 'en': 'Similarity: Cos={:.3f}, MSE={:.3e}, MAE={:.3e}'},
    'calc_error': {'zh': '计算指标出错: {}', 'en': 'Calculation error: {}'},
    'index': {'zh': 'Index', 'en': 'Index'},
    'value': {'zh': 'Value', 'en': 'Value'},
    
    # 通用
    'close': {'zh': '关闭', 'en': 'Close'},
    'cancel': {'zh': '取消', 'en': 'Cancel'},
    'ok': {'zh': '确定', 'en': 'OK'},
    'yes': {'zh': '是', 'en': 'Yes'},
    'no': {'zh': '否', 'en': 'No'}
}

# 全局实例
language_manager = LanguageManager()

def get_text(key):
    """获取文本的便捷函数"""
    return language_manager.get_text(key)