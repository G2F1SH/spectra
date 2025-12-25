"""UI构建器"""

from PyQt6.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel,
                             QLineEdit, QSlider, QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor

from widgets import JellyButton, CardButton, ClickableLabel, make_transparent
from styles import STYLE_BTN, STYLE_ICON, SLIDER_STYLE
from utils import load_svg_icon, scale_icon_for_display


class UIBuilder:
    def __init__(self, window):
        self.window = window
        self.dpi_scale = getattr(window, 'dpi_scale', 1.0)

    def _scale_size(self, size):
        return int(size * self.dpi_scale)

    def create_nav_btn(self, icon, text, handler, page_index=None,
                       icon_path=None, icon_path_active=None):
        container = QWidget()
        container.setFixedHeight(self._scale_size(40))
        container.setStyleSheet("background:transparent;")
        container.setMouseTracking(True)
        cl = QHBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        btn = JellyButton()
        btn.setFixedHeight(self._scale_size(40))
        btn.setStyleSheet(STYLE_BTN)
        btn.clicked.connect(handler)

        outer = QHBoxLayout(btn)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        indicator = QWidget()
        indicator.setFixedSize(self._scale_size(3), self._scale_size(18))
        indicator.setStyleSheet("background:transparent;border-radius:1px;")
        indicator.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        outer.addWidget(indicator, 0, Qt.AlignmentFlag.AlignVCenter)
        if page_index is not None:
            self.window.nav_indicators.append((page_index, indicator, btn, icon_path, icon_path_active, container))

        inner = make_transparent(QWidget())
        inner.setFixedWidth(self._scale_size(125))
        il = QHBoxLayout(inner)
        il.setContentsMargins(self._scale_size(7), 0, self._scale_size(5), 0)
        il.setSpacing(self._scale_size(12))

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(self._scale_size(20), self._scale_size(20))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background:transparent;")
        icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        icon_lbl.setMouseTracking(True)
        icon_lbl.setObjectName("nav_icon")

        if isinstance(icon, QPixmap):
            icon_lbl.setPixmap(scale_icon_for_display(icon, 20, self.dpi_scale))
        else:
            icon_lbl.setText(icon)
            icon_lbl.setStyleSheet(STYLE_ICON)

        il.addWidget(icon_lbl)

        text_lbl = QLabel(text)
        font_size = int(14 * self.dpi_scale)
        text_lbl.setStyleSheet(f"color:white;background:transparent;font-size:{font_size}px;font-family:'微软雅黑';")
        text_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_lbl.setMouseTracking(True)
        text_lbl.hide()
        il.addWidget(text_lbl)
        il.addStretch()
        self.window.nav_texts.append(text_lbl)

        outer.addWidget(inner)
        outer.addStretch()
        cl.addWidget(btn)
        return container

    def create_title_btn(self, text, handler):
        b = JellyButton(text)
        b.setFixedSize(self._scale_size(32), self._scale_size(32))
        font_size = self._scale_size(16)
        b.setStyleSheet(
            f"QPushButton{{background:transparent;color:white;border:none;border-radius:{self._scale_size(16)}px;font-size:{font_size}px;font-family:'微软雅黑';}}QPushButton:hover{{background:rgba(255,255,255,0.2);}}")
        b.clicked.connect(handler)
        return b

    def create_bg_card(self, title, desc, selected, handler):
        card = CardButton()
        card.setFixedHeight(self._scale_size(70))
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.clicked.connect(handler)

        style = "background:rgba(255,255,255,0.15);" if selected else "background:rgba(255,255,255,0.05);"
        card.setStyleSheet(
            f"QPushButton{{{style}border:none;border-radius:0px;}}QPushButton:hover{{background:rgba(255,255,255,0.1);}}QPushButton:pressed{{background:rgba(255,255,255,0.05);}}")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(self._scale_size(15), self._scale_size(12), self._scale_size(15), self._scale_size(12))
        layout.setSpacing(self._scale_size(12))

        check_label = QLabel()
        check_label.setFixedSize(self._scale_size(20), self._scale_size(20))
        check_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        check_label.setStyleSheet("background:transparent;")
        check_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        if selected:
            check_pixmap = load_svg_icon("svg/check-lg.svg", self.dpi_scale)
            if check_pixmap:
                check_label.setPixmap(scale_icon_for_display(check_pixmap, 20, self.dpi_scale))

        layout.addWidget(check_label, 0, Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(self._scale_size(4))
        text_layout.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color:white;font-size:{self._scale_size(14)}px;font-family:'微软雅黑';background:transparent;")
        title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_layout.addWidget(title_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(
            f"color:rgba(255,255,255,0.6);font-size:{self._scale_size(12)}px;font-family:'微软雅黑';background:transparent;")
        desc_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_layout.addWidget(desc_lbl)

        layout.addLayout(text_layout)
        layout.addStretch()

        card.check_label = check_label
        return card

    def create_expandable_menu(self, title, desc, icon_path=None, icon_path_active=None, toggle_handler=None, content_attr="appearance"):
        container = QWidget()
        container.setStyleSheet("background:rgba(255,255,255,0.08);border-radius:8px;")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = CardButton()
        header.setFixedHeight(self._scale_size(70))
        header.setCursor(Qt.CursorShape.PointingHandCursor)
        if toggle_handler:
            header.clicked.connect(toggle_handler)
        else:
            header.clicked.connect(self.window.toggle_appearance_menu)

        border_radius = self._scale_size(8)
        header.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;border-top-left-radius:{border_radius}px;border-top-right-radius:{border_radius}px;}}QPushButton:hover{{background:rgba(255,255,255,0.05);}}QPushButton:pressed{{background:rgba(255,255,255,0.02);}}")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(self._scale_size(15), self._scale_size(12), self._scale_size(15), self._scale_size(12))
        header_layout.setSpacing(self._scale_size(12))

        icon_label = None
        if icon_path:
            icon_label = QLabel()
            icon_label.setFixedSize(self._scale_size(20), self._scale_size(20))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("background:transparent;")
            icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            icon_label.setObjectName("menu_icon")

            icon_pixmap = load_svg_icon(icon_path, self.dpi_scale)
            if icon_pixmap:
                icon_label.setPixmap(scale_icon_for_display(icon_pixmap, 20, self.dpi_scale))

            header_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(self._scale_size(4))
        text_layout.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color:white;font-size:{self._scale_size(14)}px;font-family:'微软雅黑';background:transparent;")
        title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_layout.addWidget(title_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(
            f"color:rgba(255,255,255,0.6);font-size:{self._scale_size(12)}px;font-family:'微软雅黑';background:transparent;")
        desc_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_layout.addWidget(desc_lbl)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        main_layout.addWidget(header)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setStyleSheet("background:transparent;")

        main_layout.addWidget(content_widget)

        setattr(self.window, f"{content_attr}_content_layout", content_layout)
        setattr(self.window, f"{content_attr}_icon_path", icon_path)
        setattr(self.window, f"{content_attr}_icon_path_active", icon_path_active)
        setattr(self.window, f"{content_attr}_icon_label", icon_label)

        return container

    def create_config_page(self):
        """创建设置页面"""
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        pl = QVBoxLayout(page)
        pl.setContentsMargins(self._scale_size(20), self._scale_size(10), self._scale_size(20), self._scale_size(20))
        pl.setSpacing(self._scale_size(15))

        title = QLabel("设置")
        title.setStyleSheet(f"color:white;font-size:{self._scale_size(20)}px;font-family:'微软雅黑';font-weight:bold;")
        pl.addWidget(title)

        # 外观设置容器
        self.window.appearance_container = self.create_expandable_menu(
            "外观设置", "背景、主题等外观选项", "svg/palette.svg", "svg/palette-fill.svg",
            content_attr="appearance"
        )
        pl.addWidget(self.window.appearance_container)

        self.window.appearance_content = self.window.appearance_container.layout().itemAt(1).widget()

        # 模糊背景卡片
        self.window.blur_card = self.create_bg_card(
            "模糊背景", "使用系统窗口模糊效果",
            self.window.config.get("background_mode") == "blur",
            lambda: self.window.set_background("blur")
        )
        self.window.appearance_content_layout.addWidget(self.window.blur_card)

        # 透明度滑块
        self._create_opacity_slider()
        self.window.appearance_content_layout.addWidget(self.window.opacity_widget)

        # 纯色背景卡片
        self.window.solid_card = self.create_bg_card(
            "纯色背景", "使用纯色作为背景",
            self.window.config.get("background_mode") == "solid",
            lambda: self.window.set_background("solid")
        )
        self.window.appearance_content_layout.addWidget(self.window.solid_card)

        # 颜色选择区域
        self._create_color_picker()
        self.window.appearance_content_layout.addWidget(self.window.color_widget)

        # 图片背景卡片
        self.window.image_card = self.create_bg_card(
            "图像背景", "使用图像作为背景",
            self.window.config.get("background_mode") == "image",
            lambda: self.window.set_background("image")
        )
        self.window.appearance_content_layout.addWidget(self.window.image_card)

        # 路径输入区域
        self._create_path_input()
        self.window.appearance_content_layout.addWidget(self.window.path_widget)

        self.window.appearance_content.setVisible(False)

        # 语言设置容器
        self.window.language_container = self.create_expandable_menu(
            "语言设置", "选择界面显示语言", "svg/translate.svg", "svg/file-earmark-font.svg",
            toggle_handler=self.window.toggle_language_menu,
            content_attr="language"
        )
        pl.addWidget(self.window.language_container)

        self.window.language_content = self.window.language_container.layout().itemAt(1).widget()

        # 语言卡片（创建但不添加到布局，_create_language_card 会自己添加）
        self._create_language_card()

        self.window.language_content.setVisible(False)

        pl.addStretch()
        return page

    def create_instance_page(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        pl = QVBoxLayout(page)
        pl.setContentsMargins(self._scale_size(20), self._scale_size(10), self._scale_size(20), self._scale_size(20))
        pl.setSpacing(self._scale_size(15))

        title = QLabel("实例")
        title.setStyleSheet(f"color:white;font-size:{self._scale_size(20)}px;font-family:'微软雅黑';font-weight:bold;")
        pl.addWidget(title)

        pl.addStretch()
        return page

    def create_download_page(self):
        page = QWidget()
        page.setStyleSheet("background:transparent;")
        pl = QVBoxLayout(page)
        pl.setContentsMargins(self._scale_size(20), self._scale_size(10), self._scale_size(20), self._scale_size(20))
        pl.setSpacing(self._scale_size(15))

        title = QLabel("下载")
        title.setStyleSheet(f"color:white;font-size:{self._scale_size(20)}px;font-family:'微软雅黑';font-weight:bold;")
        pl.addWidget(title)

        pl.addStretch()
        return page

    def _create_opacity_slider(self):
        self.window.opacity_widget = QWidget()
        border_radius = self._scale_size(8)
        self.window.opacity_widget.setStyleSheet(f"background:rgba(255,255,255,0);border-bottom-left-radius:{border_radius}px;border-bottom-right-radius:{border_radius}px;")
        opacity_layout = QVBoxLayout(self.window.opacity_widget)
        opacity_layout.setContentsMargins(self._scale_size(35), self._scale_size(8), self._scale_size(15), self._scale_size(8))
        opacity_layout.setSpacing(self._scale_size(4))

        opacity_header_layout = QHBoxLayout()
        opacity_label = QLabel("模糊透明度")
        opacity_label.setStyleSheet(f"color:rgba(255,255,255,0.8);font-size:{self._scale_size(13)}px;font-family:'微软雅黑';")
        opacity_value = QLabel()
        opacity_value.setText(str(int((self.window.config.get("blur_opacity", 150) - 10) / (255 - 10) * 100)) + "%")
        opacity_value.setStyleSheet(f"color:rgba(255,255,255,0.8);font-size:{self._scale_size(13)}px;font-family:'微软雅黑';")
        self.window.opacity_value_label = opacity_value
        opacity_header_layout.addWidget(opacity_label)
        opacity_header_layout.addStretch()
        opacity_header_layout.addWidget(opacity_value)
        opacity_layout.addLayout(opacity_header_layout)

        self.window.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.window.opacity_slider.setRange(10, 255)
        self.window.opacity_slider.setValue(self.window.config.get("blur_opacity", 150))
        self.window.opacity_slider.setStyleSheet(SLIDER_STYLE)
        self.window.opacity_slider.valueChanged.connect(self.window.on_opacity_changed)
        opacity_layout.addWidget(self.window.opacity_slider)

        self.window.opacity_widget.setVisible(self.window.config.get("background_mode") == "blur")

    def _create_path_input(self):
        self.window.path_widget = QWidget()
        border_radius = self._scale_size(8)
        self.window.path_widget.setStyleSheet(f"background:rgba(255,255,255,0);border-bottom-left-radius:{border_radius}px;border-bottom-right-radius:{border_radius}px;")
        path_layout = QHBoxLayout(self.window.path_widget)
        path_layout.setContentsMargins(self._scale_size(35), self._scale_size(12), self._scale_size(15), self._scale_size(12))
        path_layout.setSpacing(self._scale_size(10))

        path_label = QLabel("背景图片路径")
        path_label.setStyleSheet(f"color:rgba(255,255,255,0.8);font-size:{self._scale_size(13)}px;font-family:'微软雅黑';")
        path_layout.addWidget(path_label)

        self.window.path_input = QLineEdit()
        self.window.path_input.setText(self.window.config.get("background_image_path", ""))
        padding = self._scale_size(6)
        border_radius_input = self._scale_size(4)
        self.window.path_input.setStyleSheet(
            f"QLineEdit{{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:{border_radius_input}px;padding:{padding}px;color:white;font-size:{self._scale_size(13)}px;font-family:'微软雅黑';}}")
        self.window.path_input.editingFinished.connect(self.window.on_path_changed)
        path_layout.addWidget(self.window.path_input, 1)

        # 浏览按钮
        browse_btn = ClickableLabel()
        browse_btn.setFixedSize(self._scale_size(32), self._scale_size(32))
        border_radius_btn = self._scale_size(4)
        browse_btn.setHoverStyle(
            f"background:rgba(255,255,255,0.1);border:none;border-radius:{border_radius_btn}px;",
            f"background:rgba(255,255,255,0.15);border:none;border-radius:{border_radius_btn}px;"
        )
        browse_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.setCallback(self.window.choose_background_image)

        folder_pixmap = load_svg_icon("svg/folder2.svg", self.dpi_scale)
        if folder_pixmap:
            browse_btn.setPixmap(scale_icon_for_display(folder_pixmap, 20, self.dpi_scale))

        path_layout.addWidget(browse_btn)

        self.window.path_widget.setVisible(self.window.config.get("background_mode") == "image")

    def _create_color_picker(self):
        self.window.color_widget = QWidget()
        border_radius = self._scale_size(8)
        self.window.color_widget.setStyleSheet(f"background:rgba(255,255,255,0);border-bottom-left-radius:{border_radius}px;border-bottom-right-radius:{border_radius}px;")
        color_layout = QHBoxLayout(self.window.color_widget)
        color_layout.setContentsMargins(self._scale_size(35), self._scale_size(12), self._scale_size(15), self._scale_size(12))
        color_layout.setSpacing(self._scale_size(10))

        color_label = QLabel("背景颜色 (ARGB)")
        color_label.setStyleSheet(f"color:rgba(255,255,255,0.8);font-size:{self._scale_size(13)}px;font-family:'微软雅黑';")
        color_layout.addWidget(color_label)

        # 颜色预览和输入
        self.window.color_input = QLineEdit()
        self.window.color_input.setText(self.window.config.get("background_color", "#00000000"))
        padding = self._scale_size(6)
        border_radius_input = self._scale_size(4)
        self.window.color_input.setStyleSheet(
            f"QLineEdit{{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:{border_radius_input}px;padding:{padding}px;color:white;font-size:{self._scale_size(13)}px;font-family:'微软雅黑';}}")
        self.window.color_input.editingFinished.connect(self.window.on_color_changed)
        color_layout.addWidget(self.window.color_input, 1)

        color_btn = QPushButton()
        color_btn.setFixedSize(self._scale_size(32), self._scale_size(32))
        border_radius_btn = self._scale_size(4)

        color_str = self.window.config.get("background_color", "#00000000")
        try:
            from PyQt6.QtGui import QColor
            color = self._parse_color(color_str)
            bg_color = color.name(QColor.NameFormat.HexArgb) if color else "#00000000"
        except:
            bg_color = "#00000000"

        color_btn.setStyleSheet(f"QPushButton{{background:{bg_color};border:1px solid rgba(255,255,255,0.3);border-radius:{border_radius_btn}px;}}QPushButton:hover{{background:{bg_color};border:1px solid rgba(255,255,255,0.5);}}")
        color_btn.clicked.connect(self.window.choose_background_color)
        color_layout.addWidget(color_btn)
        self.window.color_btn = color_btn

        self.window.color_widget.setVisible(self.window.config.get("background_mode") == "solid")

    def _parse_color(self, color_str):
        from PyQt6.QtGui import QColor
        color = QColor(color_str)
        if color.isValid():
            return color
        if len(color_str) == 7 and color_str.startswith('#'):
            return QColor(f"#FF{color_str[1:]}")
        return QColor("#00000000")

    def _create_language_card(self):
        language_widget = QWidget()
        language_widget.setStyleSheet(f"background:rgba(255,255,255,0);border-bottom-left-radius:{self._scale_size(8)}px;border-bottom-right-radius:{self._scale_size(8)}px;")
        language_layout = QHBoxLayout(language_widget)
        language_layout.setContentsMargins(self._scale_size(35), self._scale_size(12), self._scale_size(15), self._scale_size(12))
        language_layout.setSpacing(self._scale_size(10))

        language_label = QLabel("界面语言")
        language_label.setStyleSheet(f"color:rgba(255,255,255,0.8);font-size:{self._scale_size(13)}px;font-family:'微软雅黑';")
        language_layout.addWidget(language_label)

        language_layout.addStretch()

        from PyQt6.QtWidgets import QComboBox
        self.window.language_combo = QComboBox()
        self.window.language_combo.setFixedHeight(self._scale_size(32))
        self.window.language_combo.setFixedWidth(self._scale_size(150))
        self.window.language_combo.setMaxVisibleItems(5)
        padding = self._scale_size(6)
        border_radius = self._scale_size(4)
        self.window.language_combo.setStyleSheet(
            f"QComboBox{{"
            f"background:rgba(0,0,0,0.3);"
            f"border:1px solid rgba(255,255,255,0.15);"
            f"border-radius:{border_radius}px;"
            f"padding:{padding}px;"
            f"color:rgba(255,255,255,0.95);"
            f"font-size:{self._scale_size(13)}px;"
            f"font-family:'微软雅黑';"
            f"}}"
            f"QComboBox:hover{{"
            f"background:rgba(0,0,0,0.4);"
            f"border:1px solid rgba(255,255,255,0.25);"
            f"}}"
            f"QComboBox:focus{{"
            f"background:rgba(0,0,0,0.5);"
            f"border:1px solid rgba(100,150,255,0.6);"
            f"}}"
            f"QComboBox:on{{"
            f"padding-top:{padding - 1}px;"
            f"padding-bottom:{padding - 1}px;"
            f"}}"
            f"QComboBox::drop-down{{"
            f"border:none;"
            f"width:28px;"
            f"background:transparent;"
            f"}}"
            f"QComboBox::down-arrow{{"
            f"image:url(svg/x-diamond.svg);"
            f"width:12px;"
            f"height:12px;"
            f"}}"
            f"QComboBox QAbstractItemView{{"
            f"background:rgba(0,0,0,0.9);"
            f"border:1px solid rgba(255,255,255,0.1);"
            f"border-radius:{border_radius}px;"
            f"selection-background-color:rgba(64,128,255,0.8);"
            f"selection-color:white;"
            f"outline:none;"
            f"padding:{self._scale_size(2)}px;"
            f"}}"
            f"QComboBox QAbstractItemView::item{{"
            f"height:{self._scale_size(28)}px;"
            f"padding:{self._scale_size(6)}px {self._scale_size(8)}px;"
            f"color:rgba(255,255,255,0.85);"
            f"border-radius:{border_radius - 1}px;"
            f"}}"
            f"QComboBox QAbstractItemView::item:hover{{"
            f"background:rgba(255,255,255,0.08);"
            f"}}"
            f"QComboBox QAbstractItemView::item:selected{{"
            f"background:rgba(64,128,255,0.9);"
            f"color:white;"
            f"}}"
            f"QComboBox QScrollBar:vertical{{"
            f"background:rgba(255,255,255,0.05);"
            f"width:8px;"
            f"margin:0px;"
            f"border-radius:4px;"
            f"}}"
            f"QComboBox QScrollBar::handle:vertical{{"
            f"background:rgba(255,255,255,0.3);"
            f"min-height:20px;"
            f"border-radius:4px;"
            f"}}"
            f"QComboBox QScrollBar::handle:vertical:hover{{"
            f"background:rgba(255,255,255,0.5);"
            f"}}"
            f"QComboBox QScrollBar::add-line:vertical,"
            f"QComboBox QScrollBar::sub-line:vertical{{"
            f"border:none;"
            f"background:none;"
            f"}}"
            f"QComboBox QScrollBar::add-page:vertical,"
            f"QComboBox QScrollBar::sub-page:vertical{{"
            f"background:none;"
            f"}}"
        )
        self.window.language_combo.addItems([
            "简体中文",
            "English",
            "日本語",
            "한국어",
            "Español",
            "Français",
            "Deutsch",
            "Português",
            "Русский",
            "العربية"
        ])
        self.window.language_combo.setCurrentIndex(0)

        language_layout.addWidget(self.window.language_combo)

        self.window.language_content_layout.addWidget(language_widget)

        return language_widget
