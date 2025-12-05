# 样式管理器
from .config import Config

class StyleManager:
    @staticmethod
    def generate_main_style(dpi):
        scaled_font_size = Config.get_scaled_font_size(11, dpi)
        scaled_small_font = Config.get_scaled_font_size(10, dpi)
        scaled_btn_padding = Config.get_scaled_value(5, dpi)
        scaled_border_radius = Config.get_scaled_value(2, dpi)
        
        return f"""
QWidget {{
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: {scaled_font_size}px;
    color: #333;
    background-color: #fff;
}}

QPushButton {{
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: {scaled_border_radius}px;
    padding: {scaled_btn_padding}px {Config.get_scaled_value(10, dpi)}px;
    min-height: {Config.get_scaled_value(24, dpi)}px;
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
    padding: {Config.get_scaled_value(3, dpi)}px {Config.get_scaled_value(20, dpi)}px {Config.get_scaled_value(3, dpi)}px {Config.get_scaled_value(6, dpi)}px;
    min-width: {Config.get_scaled_value(100, dpi)}px;
    min-height: {Config.get_scaled_value(24, dpi)}px;
}}

QFrame#ControlBar {{
    background-color: #f9f9f9;
    border-bottom: 1px solid #eee;
    padding: {Config.get_scaled_value(6, dpi)}px;
}}

QLabel#WindowTitle {{
    font-weight: 500;
    padding: 0 {Config.get_scaled_value(12, dpi)}px;
    font-size: {scaled_font_size}px;
}}

QLabel#DropLabel {{
    border: 2px dashed #ccc;
    border-radius: {Config.get_scaled_value(5, dpi)}px;
    padding: {Config.get_scaled_value(25, dpi)}px;
    color: #666;
    margin: {Config.get_scaled_value(12, dpi)}px;
    font-size: {scaled_small_font}px;
}}

QLabel#DropLabel:hover, QLabel#DropLabel#Active {{
    border-color: #4285f4;
    color: #4285f4;
}}


"""
    
    @staticmethod
    def generate_plot_style(dpi):
        scaled_font_size = Config.get_scaled_font_size(11, dpi)
        scaled_small_font = Config.get_scaled_font_size(10, dpi)
        scaled_btn_padding = Config.get_scaled_value(3, dpi)
        scaled_border_radius = Config.get_scaled_value(2, dpi)
        
        return f"""
QWidget {{
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: {scaled_font_size}px;
    color: #333;
    background-color: #fff;
}}

QPushButton {{
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: {scaled_border_radius}px;
    padding: {scaled_btn_padding}px {Config.get_scaled_value(8, dpi)}px;
    min-height: {Config.get_scaled_value(22, dpi)}px;
}}

QPushButton#PrimaryButton {{
    background-color: #4285f4;
    color: white;
    border: none;
}}

QFrame#ControlBar {{
    background-color: #f9f9f9;
    border-bottom: 1px solid #eee;
    padding: {Config.get_scaled_value(5, dpi)}px;
}}

QLabel#WindowTitle {{
    font-weight: 500;
    padding: 0 {Config.get_scaled_value(10, dpi)}px;
}}


"""