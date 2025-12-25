"""主窗口"""

import os
import ctypes
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QFileDialog, QStackedWidget, QApplication)
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QCursor, QPixmap, QIcon
from BlurWindow.blurWindow import blur

from widgets import JellyButton
from styles import STYLE_BTN, STYLE_BTN_ACTIVE
from utils import load_svg_icon
from managers import ConfigManager, BackgroundManager
from ui import UIBuilder


class Window(QWidget):
    EDGE = 8

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.bg_manager = BackgroundManager(self)
        self.ui_builder = UIBuilder(self)

        self.setWindowTitle("Spectra")
        if os.path.exists("icon.png"):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon("icon.png"))

        self.resize(self.config.get("window_width", 900), self.config.get("window_height", 600))
        self.setMinimumSize(400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self._init_ui()
        self._init_nav()
        self._init_content()

        self.drag_pos = None
        self.resize_edge = None
        self.current_bg_path = None
        self.switch_page(0)

        # 定时器轮询光标位置
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(lambda: self.update_cursor(QCursor.pos()))
        self.cursor_timer.start(50)

        # 应用保存的配置
        if self.config.get("background_mode") == "image" and self.config.get("background_image_path"):
            if os.path.exists(self.config.get("background_image_path")):
                self.set_background_image(self.config.get("background_image_path"))

    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def _init_nav(self):
        """初始化导航栏"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(50)
        opacity_value = self.config.get("blur_opacity", 150)
        self.sidebar.setStyleSheet(f"background:rgba(0,0,0,{opacity_value});")
        self.sidebar.setMouseTracking(True)
        self.sidebar_expanded = False
        self.nav_texts = []
        self.nav_indicators = []

        self.menu_icon_path = "svg/chevron-bar-right.svg"
        self.menu_icon_path_active = "svg/chevron-bar-left.svg"
        self.menu_icon_label = None

        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(2, 10, 5, 10)
        sb.setSpacing(5)

        # 标题
        from widgets import make_transparent
        title = make_transparent(QWidget())
        title.setFixedSize(133, 30)
        tl = QHBoxLayout(title)
        tl.setContentsMargins(48, 0, 0, 0)
        lbl = QLabel("Spectra")
        from styles import STYLE_TEXT
        lbl.setStyleSheet(STYLE_TEXT)
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lbl.setMouseTracking(True)
        tl.addWidget(lbl)
        tl.addStretch()
        sb.addWidget(title)

        # 导航按钮
        menu_icon = load_svg_icon("svg/chevron-bar-right.svg")
        menu_icon_active = load_svg_icon("svg/chevron-bar-left.svg")
        menu_btn_container = self.ui_builder.create_nav_btn(
            menu_icon if menu_icon else "\uE700", "菜单", self.toggle_sidebar,
            None, "svg/chevron-bar-right.svg", "svg/chevron-bar-left.svg"
        )
        self.menu_icon_label = menu_btn_container.findChild(QLabel, "nav_icon")
        sb.addWidget(menu_btn_container)

        home_icon = load_svg_icon("svg/houses.svg")
        home_icon_active = load_svg_icon("svg/houses-fill.svg")
        sb.addWidget(self.ui_builder.create_nav_btn(
            home_icon if home_icon else "\uE80F", "主页",
            lambda: self.switch_page(0), 0, "svg/houses.svg", "svg/houses-fill.svg"
        ))
        sb.addStretch()

        settings_icon = load_svg_icon("svg/gear.svg")
        settings_icon_active = load_svg_icon("svg/gear-fill.svg")
        sb.addWidget(self.ui_builder.create_nav_btn(
            settings_icon if settings_icon else "\uE713", "设置",
            lambda: self.switch_page(1), 1, "svg/gear.svg", "svg/gear-fill.svg"
        ))

        self.layout().addWidget(self.sidebar)

    def _init_content(self):
        """初始化右侧内容区"""
        self.right_panel = QWidget()
        opacity_value = self.config.get("blur_opacity", 150)
        self.right_panel.setStyleSheet(f"background:rgba(0,0,0,{opacity_value});")
        self.right_panel.setMouseTracking(True)
        rl = QVBoxLayout(self.right_panel)
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
            tb.addWidget(self.ui_builder.create_title_btn(t, s))
        rl.addWidget(titlebar)

        # 内容区
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        self.stack.addWidget(QWidget())
        self.stack.addWidget(self.ui_builder.create_config_page())
        rl.addWidget(self.stack, 1)

        self.layout().addWidget(self.right_panel, 1)

    def showEvent(self, event):
        super().showEvent(event)
        blur(self.winId())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(int(self.winId()), 33, ctypes.byref(ctypes.c_int(2)), 4)
        self.apply_opacity()

    def switch_page(self, index):
        """切换页面"""
        self.stack.setCurrentIndex(index)
        for item in self.nav_indicators:
            if len(item) == 3:
                i, ind, btn = item
                icon_path, icon_path_active = None, None
                container = None
            else:
                i, ind, btn, icon_path, icon_path_active, container = item

            if i == index:
                ind.setStyleSheet("background:#a0a0ff;border-radius:1px;")
                btn.setStyleSheet(STYLE_BTN_ACTIVE)
                if icon_path_active and container:
                    icon_pixmap = load_svg_icon(icon_path_active)
                    if icon_pixmap:
                        icon_lbl = container.findChild(QLabel, "nav_icon")
                        if icon_lbl:
                            icon_lbl.setPixmap(icon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                ind.setStyleSheet("background:transparent;border-radius:1px;")
                btn.setStyleSheet(STYLE_BTN)
                if icon_path and container:
                    icon_pixmap = load_svg_icon(icon_path)
                    if icon_pixmap:
                        icon_lbl = container.findChild(QLabel, "nav_icon")
                        if icon_lbl:
                            icon_lbl.setPixmap(icon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def toggle_sidebar(self):
        """切换侧边栏"""
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        for a in (self.anim, self.anim2):
            a.setDuration(200)
            a.setEasingCurve(QEasingCurve.Type.InOutQuad)
            a.setStartValue(140 if self.sidebar_expanded else 50)
            a.setEndValue(50 if self.sidebar_expanded else 140)
        if self.sidebar_expanded:
            self.anim.finished.connect(lambda: [t.hide() for t in self.nav_texts])
            if self.menu_icon_label and self.menu_icon_path:
                icon_pixmap = load_svg_icon(self.menu_icon_path)
                if icon_pixmap:
                    self.menu_icon_label.setPixmap(icon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            [t.show() for t in self.nav_texts]
            if self.menu_icon_label and self.menu_icon_path_active:
                icon_pixmap = load_svg_icon(self.menu_icon_path_active)
                if icon_pixmap:
                    self.menu_icon_label.setPixmap(icon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.anim.start()
        self.anim2.start()
        self.sidebar_expanded = not self.sidebar_expanded

    def toggle_appearance_menu(self):
        """切换外观设置菜单"""
        content = self.appearance_container.layout().itemAt(1).widget()
        is_visible = content.isVisible()

        if is_visible:
            content.setVisible(False)
            if self.appearance_icon_label and self.appearance_icon_path:
                icon_pixmap = load_svg_icon(self.appearance_icon_path)
                if icon_pixmap:
                    self.appearance_icon_label.setPixmap(icon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            content.setVisible(True)
            if self.appearance_icon_label and self.appearance_icon_path_active:
                icon_pixmap = load_svg_icon(self.appearance_icon_path_active)
                if icon_pixmap:
                    self.appearance_icon_label.setPixmap(icon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def set_background(self, mode):
        """设置背景模式"""
        self.config["background_mode"] = mode
        self.config_manager.save_config()

        if mode == "blur":
            self.blur_card.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.15);border:none;border-radius:0px;}QPushButton:hover{background:rgba(255,255,255,0.1);}QPushButton:pressed{background:rgba(255,255,255,0.05);}")
            check_pixmap = load_svg_icon("svg/check-lg.svg")
            if check_pixmap:
                self.blur_card.check_label.setPixmap(check_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            self.image_card.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.05);border:none;border-radius:0px;}QPushButton:hover{background:rgba(255,255,255,0.1);}QPushButton:pressed{background:rgba(255,255,255,0.03);}")
            self.image_card.check_label.clear()

            self.path_widget.setVisible(False)
            self.opacity_widget.setVisible(True)
            self.apply_opacity()

            blur(self.winId())
            self.bg_manager.hide()

        elif mode == "image":
            self.blur_card.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.05);border:none;border-radius:0px;}QPushButton:hover{background:rgba(255,255,255,0.1);}QPushButton:pressed{background:rgba(255,255,255,0.03);}")
            self.blur_card.check_label.clear()

            self.image_card.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.15);border:none;border-radius:0px;}QPushButton:hover{background:rgba(255,255,255,0.1);}QPushButton:pressed{background:rgba(255,255,255,0.05);}")
            check_pixmap = load_svg_icon("svg/check-lg.svg")
            if check_pixmap:
                self.image_card.check_label.setPixmap(check_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            self.path_widget.setVisible(True)
            self.opacity_widget.setVisible(False)

            if self.config.get("background_image_path") and os.path.exists(self.config.get("background_image_path")):
                self.set_background_image(self.config.get("background_image_path"))

    def set_background_image(self, path):
        """设置背景图像"""
        self.bg_manager.set_background_image(path)
        self.current_bg_path = path

    def on_path_changed(self):
        """路径改变"""
        path = self.path_input.text().strip()
        if path and os.path.exists(path):
            self.config["background_image_path"] = path
            self.config_manager.save_config()
            self.set_background_image(path)
        elif not path:
            self.config["background_image_path"] = ""
            self.config_manager.save_config()

    def on_opacity_changed(self, value):
        """透明度改变"""
        self.config["blur_opacity"] = value
        self.config_manager.save_config()
        # 将10-255转换为0-100%显示
        opacity_percent = int((value - 10) / (255 - 10) * 100)
        self.opacity_value_label.setText(str(opacity_percent) + "%")
        self.apply_opacity()

    def apply_opacity(self):
        """应用透明度"""
        opacity_value = self.config.get("blur_opacity", 150)
        self.right_panel.setStyleSheet(f"background:rgba(0,0,0,{opacity_value});")
        self.sidebar.setStyleSheet(f"background:rgba(0,0,0,{opacity_value});")

    def choose_background_image(self):
        """选择背景图像"""
        file, _ = QFileDialog.getOpenFileName(
            self, "选择背景", "",
            "媒体文件 (*.png *.jpg *.jpeg *.bmp *.mp4 *.avi *.mov *.mkv *.webm);;所有文件 (*.*)"
        )
        if file:
            self.config["background_image_path"] = file
            self.config_manager.save_config()
            self.path_input.setText(file)
            self.set_background_image(file)

    def get_edge(self, pos):
        """获取边缘"""
        x, y, w, h, e = pos.x(), pos.y(), self.width(), self.height(), self.EDGE
        edge = ""
        if y < e:
            edge += "t"
        elif y > h - e:
            edge += "b"
        if x < e:
            edge += "l"
        elif x > w - e:
            edge += "r"
        return edge

    def update_cursor(self, global_pos):
        """更新光标"""
        local_pos = self.mapFromGlobal(global_pos)
        edge = self.get_edge(local_pos)
        cursors = {
            "t": Qt.CursorShape.SizeVerCursor,
            "b": Qt.CursorShape.SizeVerCursor,
            "l": Qt.CursorShape.SizeHorCursor,
            "r": Qt.CursorShape.SizeHorCursor,
            "tl": Qt.CursorShape.SizeFDiagCursor,
            "br": Qt.CursorShape.SizeFDiagCursor,
            "tr": Qt.CursorShape.SizeBDiagCursor,
            "bl": Qt.CursorShape.SizeBDiagCursor
        }
        self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, ev):
        """鼠标按下事件"""
        if ev.button() == Qt.MouseButton.LeftButton:
            edge = self.get_edge(ev.position().toPoint())
            if edge:
                self.resize_edge = edge
                self.resize_start = ev.globalPosition().toPoint()
                self.resize_geo = self.geometry()
            elif ev.position().y() < 40 and ev.position().x() > self.sidebar.width():
                self.drag_pos = ev.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, ev):
        """鼠标移动事件"""
        if self.resize_edge:
            diff = ev.globalPosition().toPoint() - self.resize_start
            geo = QRect(self.resize_geo)
            if 't' in self.resize_edge:
                geo.setTop(geo.top() + diff.y())
            if 'b' in self.resize_edge:
                geo.setBottom(geo.bottom() + diff.y())
            if 'l' in self.resize_edge:
                geo.setLeft(geo.left() + diff.x())
            if 'r' in self.resize_edge:
                geo.setRight(geo.right() + diff.x())
            if geo.width() >= self.minimumWidth() and geo.height() >= self.minimumHeight():
                self.setGeometry(geo)
        elif self.drag_pos:
            self.move(ev.globalPosition().toPoint() - self.drag_pos)
        else:
            self.update_cursor(ev.globalPosition().toPoint())

    def mouseReleaseEvent(self, ev):
        """鼠标释放事件"""
        self.drag_pos = None
        self.resize_edge = None

    def resizeEvent(self, ev):
        """调整大小事件"""
        super().resizeEvent(ev)
        if hasattr(self, 'current_bg_path') and self.current_bg_path:
            self.set_background_image(self.current_bg_path)

        self.config["window_width"] = self.width()
        self.config["window_height"] = self.height()
        self.config_manager.save_config()
