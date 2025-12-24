from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QStylePainter, QStyleOptionButton, QStackedWidget
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QPainter
from BlurWindow.blurWindow import blur
import ctypes, sys, os

STYLE_BTN = "QPushButton{background:transparent;border:none;border-radius:8px;}QPushButton:hover{background:rgba(255,255,255,0.2);}"
STYLE_BTN_ACTIVE = "QPushButton{background:rgba(255,255,255,0.15);border:none;border-radius:8px;}QPushButton:hover{background:rgba(255,255,255,0.1);}"
STYLE_ICON = "color:white;background:transparent;font-size:16px;font-family:'Segoe Fluent Icons';"
STYLE_TEXT = "color:white;background:transparent;font-size:14px;font-family:'微软雅黑';"


class JellyButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._scale = 1.0
        self.setMouseTracking(True)

    def getScale(self):
        return self._scale

    def setScale(self, s):
        self._scale = s
        self.update()

    def paintEvent(self, ev):
        painter = QStylePainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        painter.translate(cx, cy)
        painter.scale(self._scale, self._scale)
        painter.translate(-cx, -cy)
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        painter.drawControl(self.style().ControlElement.CE_PushButton, opt)

    def _animate(self, end, duration, curve):
        self.anim = QPropertyAnimation()
        self.anim.setDuration(duration)
        self.anim.setStartValue(self._scale)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(curve)
        self.anim.valueChanged.connect(self.setScale)
        self.anim.start()

    def mousePressEvent(self, ev):
        self._animate(0.92, 100, QEasingCurve.Type.OutQuad)
        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        self._animate(1.0, 150, QEasingCurve.Type.OutBack)
        super().mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        win = self.window()
        if hasattr(win, 'update_cursor'):
            win.update_cursor(ev.globalPosition().toPoint())
        super().mouseMoveEvent(ev)


def make_transparent(widget):
    widget.setStyleSheet("background:transparent;")
    widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    widget.setMouseTracking(True)
    return widget


class Window(QWidget):
    EDGE = 8

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spectra")
        if os.path.exists("icon.png"):
            self.setWindowIcon(QIcon("icon.png"))
        self.resize(600, 400)
        self.setMinimumSize(400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        blur(self.winId())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(int(self.winId()), 33, ctypes.byref(ctypes.c_int(2)), 4)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 侧边栏
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(50)
        self.sidebar.setStyleSheet("background:rgba(0,0,0,80);")
        self.sidebar.setMouseTracking(True)
        self.sidebar_expanded = False
        self.nav_texts = []
        self.nav_indicators = []

        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(2, 10, 5, 10)
        sb.setSpacing(5)

        # 标题
        title = make_transparent(QWidget())
        title.setFixedSize(133, 30)
        tl = QHBoxLayout(title)
        tl.setContentsMargins(48, 0, 0, 0)
        lbl = QLabel("Spectra")
        lbl.setStyleSheet(STYLE_TEXT)
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lbl.setMouseTracking(True)
        tl.addWidget(lbl)
        tl.addStretch()
        sb.addWidget(title)

        # 导航按钮
        sb.addWidget(self.create_nav_btn("\uE700", "菜单", self.toggle_sidebar))
        sb.addWidget(self.create_nav_btn("\uE80F", "主页", lambda: self.switch_page(0), 0))
        sb.addStretch()
        sb.addWidget(self.create_nav_btn("\uE713", "设置", lambda: self.switch_page(1), 1))

        layout.addWidget(self.sidebar)

        # 右侧区域
        right = QWidget()
        right.setStyleSheet("background:rgba(0,0,0,100);")
        right.setMouseTracking(True)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # 标题栏
        titlebar = QWidget()
        titlebar.setFixedHeight(40)
        titlebar.setStyleSheet("background:transparent;")
        titlebar.setMouseTracking(True)
        tb = QHBoxLayout(titlebar)
        tb.setContentsMargins(0, 0, 8, 0)
        tb.addStretch()
        for t, s in [("−", self.showMinimized), ("×", self.close)]:
            tb.addWidget(self.create_title_btn(t, s))
        rl.addWidget(titlebar)

        # 内容区
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        self.stack.addWidget(QWidget())  # 主页
        self.stack.addWidget(self.create_config_page())
        rl.addWidget(self.stack, 1)

        layout.addWidget(right, 1)

        self.drag_pos = None
        self.resize_edge = None
        self.switch_page(0)

    def create_nav_btn(self, icon, text, handler, page_index=None):
        container = QWidget()
        container.setFixedHeight(40)
        container.setStyleSheet("background:transparent;")
        container.setMouseTracking(True)
        cl = QHBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        btn = JellyButton()
        btn.setFixedHeight(40)
        btn.setStyleSheet(STYLE_BTN)
        btn.clicked.connect(handler)

        outer = QHBoxLayout(btn)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        indicator = QWidget()
        indicator.setFixedSize(3, 18)
        indicator.setStyleSheet("background:transparent;border-radius:1px;")
        indicator.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        outer.addWidget(indicator, 0, Qt.AlignmentFlag.AlignVCenter)
        if page_index is not None:
            self.nav_indicators.append((page_index, indicator, btn))

        inner = make_transparent(QWidget())
        inner.setFixedWidth(125)
        il = QHBoxLayout(inner)
        il.setContentsMargins(7, 0, 5, 0)
        il.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(20, 20)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(STYLE_ICON)
        icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        icon_lbl.setMouseTracking(True)
        il.addWidget(icon_lbl)

        text_lbl = QLabel(text)
        text_lbl.setStyleSheet(STYLE_TEXT)
        text_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_lbl.setMouseTracking(True)
        text_lbl.hide()
        il.addWidget(text_lbl)
        il.addStretch()
        self.nav_texts.append(text_lbl)

        outer.addWidget(inner)
        outer.addStretch()
        cl.addWidget(btn)
        return container

    def create_title_btn(self, text, handler):
        b = JellyButton(text)
        b.setFixedSize(32, 32)
        b.setStyleSheet("QPushButton{background:transparent;color:white;border:none;border-radius:16px;font-size:16px;font-family:'微软雅黑';}QPushButton:hover{background:rgba(255,255,255,0.2);}")
        b.clicked.connect(handler)
        return b

    def create_config_page(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        pl = QVBoxLayout(page)
        pl.setContentsMargins(20, 10, 20, 20)
        lbl = QLabel("设置")
        lbl.setStyleSheet("color:white;font-size:20px;font-family:'微软雅黑';font-weight:bold;")
        pl.addWidget(lbl)
        pl.addStretch()
        return page

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, ind, btn in self.nav_indicators:
            if i == index:
                ind.setStyleSheet("background:#a0a0ff;border-radius:1px;")
                btn.setStyleSheet(STYLE_BTN_ACTIVE)
            else:
                ind.setStyleSheet("background:transparent;border-radius:1px;")
                btn.setStyleSheet(STYLE_BTN)

    def toggle_sidebar(self):
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        for a in (self.anim, self.anim2):
            a.setDuration(200)
            a.setEasingCurve(QEasingCurve.Type.InOutQuad)
            a.setStartValue(140 if self.sidebar_expanded else 50)
            a.setEndValue(50 if self.sidebar_expanded else 140)
        if self.sidebar_expanded:
            self.anim.finished.connect(lambda: [t.hide() for t in self.nav_texts])
        else:
            [t.show() for t in self.nav_texts]
        self.anim.start()
        self.anim2.start()
        self.sidebar_expanded = not self.sidebar_expanded

    def get_edge(self, pos):
        x, y, w, h, e = pos.x(), pos.y(), self.width(), self.height(), self.EDGE
        edge = ""
        if y < e: edge += "t"
        elif y > h - e: edge += "b"
        if x < e: edge += "l"
        elif x > w - e: edge += "r"
        return edge

    def update_cursor(self, global_pos):
        local_pos = self.mapFromGlobal(global_pos)
        edge = self.get_edge(local_pos)
        cursors = {"t": Qt.CursorShape.SizeVerCursor, "b": Qt.CursorShape.SizeVerCursor,
                   "l": Qt.CursorShape.SizeHorCursor, "r": Qt.CursorShape.SizeHorCursor,
                   "tl": Qt.CursorShape.SizeFDiagCursor, "br": Qt.CursorShape.SizeFDiagCursor,
                   "tr": Qt.CursorShape.SizeBDiagCursor, "bl": Qt.CursorShape.SizeBDiagCursor}
        self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            edge = self.get_edge(ev.position().toPoint())
            if edge:
                self.resize_edge = edge
                self.resize_start = ev.globalPosition().toPoint()
                self.resize_geo = self.geometry()
            elif ev.position().y() < 40 and ev.position().x() > self.sidebar.width():
                self.drag_pos = ev.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, ev):
        if self.resize_edge:
            diff = ev.globalPosition().toPoint() - self.resize_start
            geo = QRect(self.resize_geo)
            if 't' in self.resize_edge: geo.setTop(geo.top() + diff.y())
            if 'b' in self.resize_edge: geo.setBottom(geo.bottom() + diff.y())
            if 'l' in self.resize_edge: geo.setLeft(geo.left() + diff.x())
            if 'r' in self.resize_edge: geo.setRight(geo.right() + diff.x())
            if geo.width() >= self.minimumWidth() and geo.height() >= self.minimumHeight():
                self.setGeometry(geo)
        elif self.drag_pos:
            self.move(ev.globalPosition().toPoint() - self.drag_pos)
        else:
            self.update_cursor(ev.globalPosition().toPoint())

    def mouseReleaseEvent(self, ev):
        self.drag_pos = None
        self.resize_edge = None


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
