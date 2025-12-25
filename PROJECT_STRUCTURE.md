# Spectra 项目结构

```
Spectra/
├── main.py                 # 程序入口
├── config.json             # 配置文件
├── icon.png               # 应用图标
├── styles.py              # 样式定义
├── splash_screen.py       # 启动画面
├── window.py             # 主窗口
├── widgets/              # 自定义组件
│   ├── __init__.py
│   ├── buttons.py        # 按钮（JellyButton, CardButton）
│   └── labels.py        # 标签（ClickableLabel）
├── ui/                  # UI构建
│   ├── __init__.py
│   └── builder.py       # UI构建器
├── managers/            # 管理器
│   ├── __init__.py
│   ├── config.py        # 配置管理
│   └── background.py    # 背景管理
├── utils/               # 工具函数
│   ├── __init__.py
│   └── icons.py        # 图标加载
└── svg/                # SVG图标
```

## 模块说明

### main.py
程序的入口文件，负责初始化应用、显示启动画面和主窗口。

### styles.py
定义所有UI样式常量，包括按钮、滑块等组件的样式。

### splash_screen.py
启动画面类，显示应用图标。

### window.py
主窗口类，包含窗口初始化、事件处理、页面切换等核心逻辑。

### widgets/
- **buttons.py**: 自定义按钮组件
  - `JellyButton`: 带动画效果的按钮
  - `CardButton`: 卡片式按钮
- **labels.py**: 自定义标签组件
  - `ClickableLabel`: 可点击的标签

### ui/
- **builder.py**: UI构建器，负责创建各种UI组件
  - 导航按钮
  - 标题栏按钮
  - 背景选项卡片
  - 可展开菜单
  - 设置页面

### managers/
- **config.py**: 配置管理器
  - 加载/保存配置
  - 提供配置访问接口
- **background.py**: 背景管理器
  - 管理背景图片和视频
  - 处理视频播放
  - 背景切换逻辑

### utils/
- **icons.py**: 图标工具
  - 加载SVG图标
  - 转换图标颜色

## 使用方法

直接运行 `python main.py` 即可启动应用。
