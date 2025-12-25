"""图标工具函数"""

import os
from PyQt6.QtGui import QPixmap, QColor, QImage, QIcon
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication


def _get_device_pixel_ratio():
    """获取当前设备像素比"""
    screen = QApplication.primaryScreen()
    if screen:
        return screen.devicePixelRatio()
    return 1.0


def load_svg_icon(path):
    """加载SVG图标为QPixmap，并渲染为白色，支持高DPI显示"""
    svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", path.replace('\\', os.sep))
    svg_path = os.path.abspath(svg_path)
    if os.path.exists(svg_path):
        # 直接使用 QIcon 加载 SVG，它原生支持矢量缩放
        icon = QIcon(svg_path)
        if not icon.isNull():
            # 获取设备像素比
            device_ratio = _get_device_pixel_ratio()
            # 使用较大尺寸渲染（设备像素尺寸），保证高DPI下清晰
            pixmap = icon.pixmap(int(32 * device_ratio), int(32 * device_ratio))
            if not pixmap.isNull():
                # 设置设备像素比，这样Qt会正确处理缩放
                pixmap.setDevicePixelRatio(device_ratio)
                # 将 pixmap 转换为 QImage
                image = pixmap.toImage()
                # 遍历每个像素，将非透明像素设置为白色
                for y in range(image.height()):
                    for x in range(image.width()):
                        color = image.pixelColor(x, y)
                        if color.alpha() > 0:
                            image.setPixelColor(x, y, QColor(255, 255, 255, color.alpha()))
                result = QPixmap.fromImage(image)
                result.setDevicePixelRatio(device_ratio)
                return result
    return None


def scale_icon_for_display(pixmap, size):
    """为显示缩放图标，正确处理高DPI

    Args:
        pixmap: 原始 pixmap
        size: 逻辑像素尺寸（如 20）

    Returns:
        适合显示的 pixmap
    """
    if pixmap.isNull():
        return pixmap
    device_ratio = _get_device_pixel_ratio()
    # 设备像素尺寸 = 逻辑像素尺寸 * 设备像素比
    device_size = int(size * device_ratio)
    return pixmap.scaled(
        device_size, device_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )
