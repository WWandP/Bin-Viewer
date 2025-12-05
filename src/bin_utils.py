import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

# 纯numpy实现3个指标函数（增强鲁棒性）
def cosine_similarity(data1, data2):
    """纯numpy实现余弦相似度（兼容不同类型输入，增强鲁棒性）"""
    # 统一转换为numpy数组（支持列表、元组等输入）
    data1 = np.asarray(data1)
    data2 = np.asarray(data2)
    
    # 处理空数组
    if data1.size == 0 or data2.size == 0:
        raise ValueError("输入数组不能为空（解析后长度为0）")
    
    # 统一为2D数组（兼容1D/2D输入）
    if data1.ndim == 1:
        data1 = data1.reshape(1, -1)
    if data2.ndim == 1:
        data2 = data2.reshape(1, -1)
    
    # 检查特征维度是否一致（截断后理论上应一致，此处做双重保障）
    if data1.shape[1] != data2.shape[1]:
        raise ValueError(f"数组特征维度不一致: {data1.shape[1]} vs {data2.shape[1]}（可能截断逻辑有误）")
    
    # 处理全零数组（避免除零）
    if np.allclose(data1, 0) or np.allclose(data2, 0):
        return np.array([[0.0]])
    
    # 计算余弦相似度（添加微小值防止除零）
    norm1 = np.linalg.norm(data1, axis=1, keepdims=True)
    norm2 = np.linalg.norm(data2, axis=1, keepdims=True)
    return np.dot(data1, data2.T) / (np.dot(norm1, norm2.T) + 1e-10)

def mean_squared_error(data1, data2):
    """纯numpy实现均方误差（MSE），支持不同类型数组"""
    data1 = np.asarray(data1)
    data2 = np.asarray(data2)
    
    # 确保长度一致（截断后应满足，此处做校验）
    if data1.size != data2.size:
        raise ValueError(f"数组长度不一致: {data1.size} vs {data2.size}（截断后仍不匹配）")
    
    # 统一转换为float64计算，避免低精度类型溢出
    return np.mean(((data1.astype(np.float64) - data2.astype(np.float64)) **2))

def mean_absolute_error(data1, data2):
    """纯numpy实现平均绝对误差（MAE），支持不同类型数组"""
    data1 = np.asarray(data1)
    data2 = np.asarray(data2)
    
    if data1.size != data2.size:
        raise ValueError(f"数组长度不一致: {data1.size} vs {data2.size}（截断后仍不匹配）")
    
    # 统一转换为float64计算
    return np.mean(np.abs(data1.astype(np.float64) - data2.astype(np.float64)))

def read_bin_file(file_path, dtype=np.float32):
    """读取bin文件，返回完整解析的numpy数组（增强类型校验）"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    if not os.path.isfile(file_path):
        raise IsADirectoryError(f"路径不是文件：{file_path}")
    
    try:
        # 读取完整文件（不做截断，确保解析完整性）
        data = np.fromfile(file_path, dtype=dtype)
        # 检查解析后是否为空
        if data.size == 0:
            raise ValueError(f"文件解析后为空（可能类型不匹配）：{file_path}（指定类型：{dtype}）")
        return data
    except Exception as e:
        raise IOError(f"读取文件失败：{file_path}，错误：{str(e)}")

def handle_invalid_values(data):
    """处理非法值（NaN/inf），替换为0.0"""
    return np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)

def compare_bin_distributions(file1_path, file2_path, ax=None, dtype1=np.float32, dtype2=np.float32):
    """对比两个bin文件（支持不同数据类型），确保完全解析后再比较"""
    # 1. 完全解析两个文件（无论类型，先完整读取）
    data1 = handle_invalid_values(read_bin_file(file1_path, dtype=dtype1))
    data2 = handle_invalid_values(read_bin_file(file2_path, dtype=dtype2))
    
    # 2. 解析后明确打印原始长度（方便调试类型差异导致的长度问题）
    len1, len2 = len(data1), len(data2)
    pass
    
    # 3. 基于解析后的实际长度，取较短的长度进行截断（确保完全解析后再判断）
    min_len = min(len1, len2)
    if min_len == 0:
        raise ValueError("解析后的数组长度为0，无法比较")
    # 只在长度不同时才截断，并提示
    if len1 != len2:
        pass
    data1_truncated = data1[:min_len]
    data2_truncated = data2[:min_len]

    # 4. 计算相似度指标（兼容不同类型数组）
    try:
        # 余弦相似度（支持1D输入）
        cos_sim = cosine_similarity(data1_truncated, data2_truncated)[0][0]
        # MSE和MAE（自动转换为float64避免类型问题）
        mse = mean_squared_error(data1_truncated, data2_truncated)
        mae = mean_absolute_error(data1_truncated, data2_truncated)
    except Exception as e:
        raise RuntimeError(f"计算指标失败：{str(e)}")

    # 5. 格式化输出（保持直观性）
    def format_metric(value):
        if value >= 1e-3:
            return f"{value:.4f}"
        elif value >= 1e-6:
            return f"{value:.6f}"
        else:
            return f"{value:.8f}"
    
    cos_str = f"{cos_sim:.3f}"
    mse_str = format_metric(mse)
    mae_str = format_metric(mae)

    # 6. 绘图（标注数据类型和截断信息）
    # 6. 绘图（修改部分：添加交互工具栏，支持放大）
    if ax is None:
        # 独立绘图时（无外部ax传入），创建窗口并添加工具栏
        fig, ax = plt.subplots(figsize=(10, 6))  # 替换plt.figure为subplots，方便获取ax
        # 绘制曲线（逻辑不变）
        ax.plot(data1_truncated, label=f"{os.path.basename(file1_path)}（{dtype1}，长度={min_len}）")
        ax.plot(data2_truncated, label=f"{os.path.basename(file2_path)}（{dtype2}，长度={min_len}）")
        ax.legend()
        ax.set_title(f"余弦相似度: {cos_str} | MSE: {mse_str} | MAE: {mae_str}")
        ax.set_xlabel("索引（已截断到较短长度）")
        ax.set_ylabel("值")
        
        # 新增：创建窗口并添加交互工具栏
        from PyQt5.QtWidgets import QApplication  # 延迟导入，避免无Qt环境时报错
        app = QApplication.instance() or QApplication([])
        window = plt.get_current_fig_manager().window  # 获取Matplotlib默认窗口
        toolbar = NavigationToolbar(fig.canvas, window)  # 给窗口添加工具栏
        window.addToolBar(toolbar)  # 显示工具栏
        
        plt.show()
    else:
        # 外部传入ax（如对比窗口、单个文件窗口），不处理工具栏（由外部窗口管理）
        ax.plot(data1_truncated, label=f"{os.path.basename(file1_path)}（{dtype1}）")
        ax.plot(data2_truncated, label=f"{os.path.basename(file2_path)}（{dtype2}）")
        ax.legend()
        ax.set_title(f"Cos: {cos_str}, MSE: {mse_str}, MAE: {mae_str}")
        ax.set_xlabel("索引（已截断）")
    
    # （保留原有返回结果逻辑）
    return {
        "cosine_similarity": cos_sim,
        "mse": mse,
        "mae": mae,
        "truncated_length": min_len,
        "original_lengths": (len1, len2)
    }
