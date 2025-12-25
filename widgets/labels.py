"""自定义标签组件"""

from PyQt6.QtWidgets import QLabel


class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._callback = None
        self._normal_style = ""
        self._hover_style = ""

    def setCallback(self, callback):
        self._callback = callback

    def setHoverStyle(self, normal_style, hover_style):
        self._normal_style = normal_style
        self._hover_style = hover_style
        self.setStyleSheet(normal_style)

    def mousePressEvent(self, ev):
        if self._callback:
            self._callback()
        super().mousePressEvent(ev)

    def enterEvent(self, ev):
        if self._hover_style:
            self.setStyleSheet(self._hover_style)
        super().enterEvent(ev)

    def leaveEvent(self, ev):
        if self._normal_style:
            self.setStyleSheet(self._normal_style)
        super().leaveEvent(ev)
