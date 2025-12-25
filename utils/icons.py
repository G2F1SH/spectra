"""图标工具函数"""

import os
from PyQt6.QtGui import QPixmap, QColor, QImage


def load_svg_icon(path):
    """加载SVG图标为QPixmap，并渲染为白色"""
    svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", path.replace('\\', os.sep))
    svg_path = os.path.abspath(svg_path)
    if os.path.exists(svg_path):
        # 加载SVG为QPixmap
        pixmap = QPixmap(svg_path)
        if not pixmap.isNull():
            # 将 pixmap 转换为 QImage
            image = pixmap.toImage()
            # 遍历每个像素，将非透明像素设置为白色
            for y in range(image.height()):
                for x in range(image.width()):
                    color = image.pixelColor(x, y)
                    if color.alpha() > 0:
                        image.setPixelColor(x, y, QColor(255, 255, 255, color.alpha()))
            return QPixmap.fromImage(image)
    return None
