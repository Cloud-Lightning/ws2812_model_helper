from __future__ import annotations

import argparse
from collections import Counter
import re
import sys
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageDraw, ImageFont, ImageSequence

try:
    from PyQt6.QtCore import QByteArray, QPointF, QRectF, Qt, QTimer
    from PyQt6.QtGui import QAction, QColor, QFont, QFontDatabase, QIcon, QImage, QLinearGradient, QPainter, QPainterPath, QPen
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtWidgets import (
        QApplication,
        QColorDialog,
        QComboBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGraphicsDropShadowEffect,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSplitter,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    Qt = None


RGB = tuple[int, int, int]
Coord = tuple[int, int]

LAYOUT_ROW_ZIGZAG = "row_zigzag"
LAYOUT_COL_ZIGZAG = "column_zigzag"
LAYOUT_ROW_MAJOR = "row_major"
LAYOUT_COL_MAJOR = "column_major"

MODE_IMAGE = "image"
MODE_MANUAL = "manual"
MODE_TEXT = "text"
MODE_ANIMATION = "animation"

LAYOUT_LABELS = {
    LAYOUT_ROW_ZIGZAG: "Horizontal zigzag",
    LAYOUT_COL_ZIGZAG: "Vertical zigzag",
    LAYOUT_ROW_MAJOR: "Row major",
    LAYOUT_COL_MAJOR: "Column major",
}

ORIGIN_TOP_LEFT = "top_left"
ORIGIN_TOP_RIGHT = "top_right"
ORIGIN_BOTTOM_LEFT = "bottom_left"
ORIGIN_BOTTOM_RIGHT = "bottom_right"

ORIGIN_LABELS = {
    ORIGIN_TOP_LEFT: "Top left",
    ORIGIN_TOP_RIGHT: "Top right",
    ORIGIN_BOTTOM_LEFT: "Bottom left",
    ORIGIN_BOTTOM_RIGHT: "Bottom right",
}

SVG_BG_TRANSPARENT = "transparent"
SVG_BG_COLOR = "color"
SVG_CUT_ALPHA = "alpha"
SVG_CUT_AUTO = "auto"
SVG_CUT_COLOR = "color"
SVG_COLOR_ORIGINAL = "original"
SVG_COLOR_PALETTE = "palette"
DEFAULT_SVG_BACKGROUND: RGB = (0, 0, 0)
DEFAULT_SVG_CUT_COLOR: RGB = (255, 255, 255)
DEFAULT_SVG_CUT_TOLERANCE = 24
DEFAULT_SVG_COLOR: RGB = (126, 234, 255)
DEFAULT_BRUSH_COLOR: RGB = (255, 0, 0)
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".wmv"}
FONT_CHOICES = {
    "Microsoft YaHei": "C:/Windows/Fonts/msyh.ttc",
    "Microsoft YaHei Bold": "C:/Windows/Fonts/msyhbd.ttc",
    "SimHei": "C:/Windows/Fonts/simhei.ttf",
    "SimSun": "C:/Windows/Fonts/simsun.ttc",
    "KaiTi": "C:/Windows/Fonts/simkai.ttf",
    "FangSong": "C:/Windows/Fonts/simfang.ttf",
    "DengXian": "C:/Windows/Fonts/Deng.ttf",
    "Arial": "C:/Windows/Fonts/arial.ttf",
    "Consolas": "C:/Windows/Fonts/consola.ttf",
    "STXingkai": "C:/Windows/Fonts/STXINGKA.TTF",
    "STCaiyun": "C:/Windows/Fonts/STCAIYUN.TTF",
    "Custom path": "",
}
_SVG_QT_APP = None

UI_TEXT = {
    "zh": {
        "window_title": "WS2812 点阵取模助手",
        "title": "WS2812 MATRIX",
        "subtitle": "图片取模 / Z 字映射 / C 数组导出",
        "language": "语言",
        "theme": "主题",
        "theme_dark": "深色",
        "theme_light": "浅色",
        "panel_settings": "矩阵参数",
        "rows": "行数",
        "cols": "列数",
        "layout": "排列方式",
        "origin": "起点角",
        "first_line": "首行/首列",
        "resize": "缩放算法",
        "array_name": "数组名",
        "svg_caption": "抠图 / 调色",
        "svg_cut_mode": "抠底",
        "svg_cut_color": "抠底色",
        "svg_cut_tolerance": "容差",
        "svg_bg_mode": "输出背景",
        "svg_bg_color_label": "输出背景色",
        "svg_color_mode": "主体颜色",
        "svg_main_color": "主体色",
        "open_image": "导入图片",
        "export_header": "导出 C 头文件",
        "status_ready": "就绪",
        "status_default": "默认 16 x 16 测试图案",
        "status_exported": "已导出",
        "metric_size": "矩阵",
        "metric_leds": "LED 数量",
        "metric_layout": "路径",
        "preview_title": "LED 物理顺序预览",
        "empty_preview": "导入图片或使用默认测试图案",
        "dialog_open": "导入图片",
        "dialog_export": "导出 C 头文件",
        "dialog_images": "图片 (*.png *.jpg *.jpeg *.bmp *.svg);;所有文件 (*.*)",
        "dialog_header": "C 头文件 (*.h);;所有文件 (*.*)",
        "image_error": "图片错误",
        "export_error": "导出错误",
        "layout_row_zigzag": "横向 Z 字",
        "layout_column_zigzag": "竖向 Z 字",
        "layout_row_major": "普通行优先",
        "layout_column_major": "普通列优先",
        "origin_top_left": "左上角",
        "origin_top_right": "右上角",
        "origin_bottom_left": "左下角",
        "origin_bottom_right": "右下角",
        "first_origin": "从起点方向开始",
        "first_reverse": "首行/首列反向",
        "resize_lanczos": "Lanczos 平滑",
        "resize_nearest": "Nearest 像素",
        "svg_bg_transparent": "透明/熄灭",
        "svg_bg_custom": "自定义背景色",
        "svg_cut_alpha": "使用图片 Alpha",
        "svg_cut_auto": "自动识别边缘底色",
        "svg_cut_color_key": "按抠底色移除",
        "svg_color_original": "保留原图颜色",
        "svg_color_palette": "使用主体调色盘",
        "choose_color": "选择颜色",
    },
    "en": {
        "window_title": "WS2812 Model Helper",
        "title": "WS2812 MATRIX",
        "subtitle": "Image sampling / Zigzag mapping / C array export",
        "language": "Language",
        "theme": "Theme",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "panel_settings": "Matrix settings",
        "rows": "Rows",
        "cols": "Columns",
        "layout": "Layout",
        "origin": "Origin",
        "first_line": "First line",
        "resize": "Resize",
        "array_name": "Array name",
        "svg_caption": "Cutout / palette",
        "svg_cut_mode": "Cutout",
        "svg_cut_color": "Key color",
        "svg_cut_tolerance": "Tolerance",
        "svg_bg_mode": "Output bg",
        "svg_bg_color_label": "Output bg color",
        "svg_color_mode": "Main color",
        "svg_main_color": "Main palette",
        "open_image": "Open image",
        "export_header": "Export C header",
        "status_ready": "Ready",
        "status_default": "Default 16 x 16 test pattern",
        "status_exported": "Exported",
        "metric_size": "Size",
        "metric_leds": "LEDs",
        "metric_layout": "Route",
        "preview_title": "LED Physical Order Preview",
        "empty_preview": "Open an image or use the default test pattern",
        "dialog_open": "Open image",
        "dialog_export": "Export C header",
        "dialog_images": "Images (*.png *.jpg *.jpeg *.bmp *.svg);;All files (*.*)",
        "dialog_header": "C header (*.h);;All files (*.*)",
        "image_error": "Image error",
        "export_error": "Export error",
        "layout_row_zigzag": "Horizontal zigzag",
        "layout_column_zigzag": "Vertical zigzag",
        "layout_row_major": "Row major",
        "layout_column_major": "Column major",
        "origin_top_left": "Top left",
        "origin_top_right": "Top right",
        "origin_bottom_left": "Bottom left",
        "origin_bottom_right": "Bottom right",
        "first_origin": "From selected origin",
        "first_reverse": "Reverse first line",
        "resize_lanczos": "Lanczos smooth",
        "resize_nearest": "Nearest pixel",
        "svg_bg_transparent": "Transparent/off",
        "svg_bg_custom": "Custom background",
        "svg_cut_alpha": "Use image alpha",
        "svg_cut_auto": "Auto edge key color",
        "svg_cut_color_key": "Remove key color",
        "svg_color_original": "Keep original colors",
        "svg_color_palette": "Use main palette color",
        "choose_color": "Choose color",
    },
}

UI_LAYOUT_KEYS = {
    LAYOUT_ROW_ZIGZAG: "layout_row_zigzag",
    LAYOUT_COL_ZIGZAG: "layout_column_zigzag",
    LAYOUT_ROW_MAJOR: "layout_row_major",
    LAYOUT_COL_MAJOR: "layout_column_major",
}

UI_ORIGIN_KEYS = {
    ORIGIN_TOP_LEFT: "origin_top_left",
    ORIGIN_TOP_RIGHT: "origin_top_right",
    ORIGIN_BOTTOM_LEFT: "origin_bottom_left",
    ORIGIN_BOTTOM_RIGHT: "origin_bottom_right",
}

UI_MODE_KEYS = {
    MODE_IMAGE: "mode_image",
    MODE_MANUAL: "mode_manual",
    MODE_TEXT: "mode_text",
    MODE_ANIMATION: "mode_animation",
}

UI_ROTATION_KEYS = {
    0: "rotation_0",
    90: "rotation_90",
    180: "rotation_180",
    270: "rotation_270",
}

UI_TEXT["zh"].update({
    "mode": "取模模式",
    "mode_image": "图片取模",
    "mode_manual": "手动点亮",
    "mode_text": "文字取模",
    "mode_animation": "动画取模",
    "open_media": "导入图片 / GIF / 视频",
    "rotation": "图片旋转",
    "animation_caption": "动画 / GIF",
    "frame_index": "预览帧",
    "max_frames": "最大帧数",
    "frame_step": "抽帧间隔",
    "frame_delay": "帧延时(ms)",
    "play_animation": "播放预览",
    "pause_animation": "暂停播放",
    "status_processing": "正在取模",
    "manual_caption": "手动 / 文字",
    "manual_settings": "手动点亮",
    "text_settings": "文字设置",
    "text_background": "文字背景",
    "brush_color": "画笔颜色",
    "fill_all": "全部填充",
    "clear_all": "全部熄灭",
    "text_input": "文字内容",
    "text_font": "字体",
    "custom_font": "自定义字体路径",
    "text_scale": "文字大小",
    "rotation_0": "不旋转",
    "rotation_90": "顺时针 90°",
    "rotation_180": "旋转 180°",
    "rotation_270": "逆时针 90°",
    "font_custom_path": "自定义路径",
    "source_preview_title": "原文件预览",
    "source_preview_empty": "导入图片/GIF/视频后在这里查看原文件",
})

UI_TEXT["en"].update({
    "mode": "Mode",
    "mode_image": "Image sampling",
    "mode_manual": "Manual pixels",
    "mode_text": "Text sampling",
    "mode_animation": "Animation sampling",
    "open_media": "Open image / GIF / video",
    "rotation": "Image rotation",
    "animation_caption": "Animation / GIF",
    "frame_index": "Preview frame",
    "max_frames": "Max frames",
    "frame_step": "Frame step",
    "frame_delay": "Frame delay(ms)",
    "play_animation": "Play preview",
    "pause_animation": "Pause",
    "status_processing": "Sampling",
    "manual_caption": "Manual / text",
    "manual_settings": "Manual pixels",
    "text_settings": "Text settings",
    "text_background": "Text background",
    "brush_color": "Brush color",
    "fill_all": "Fill all",
    "clear_all": "Clear all",
    "text_input": "Text",
    "text_font": "Font",
    "custom_font": "Custom font path",
    "text_scale": "Text size",
    "rotation_0": "No rotation",
    "rotation_90": "90 deg clockwise",
    "rotation_180": "180 deg",
    "rotation_270": "90 deg counterclockwise",
    "font_custom_path": "Custom path",
    "source_preview_title": "Source Preview",
    "source_preview_empty": "Open an image/GIF/video to preview the source here",
})

DARK_STYLE = """
QMainWindow {
  background: #101418;
}
QWidget#Root {
  color: #eef2f6;
}
QFrame#HeaderGlass,
QFrame#ControlsGlass,
QFrame#PreviewGlass {
  background-color: rgba(20, 25, 31, 238);
  border: 1px solid rgba(255, 255, 255, 34);
  border-radius: 8px;
}
QFrame#SectionFrame {
  background: transparent;
  border: 0;
}
QSplitter::handle {
  background: rgba(148, 163, 184, 70);
  border-radius: 3px;
}
QSplitter::handle:hover {
  background: rgba(203, 213, 225, 130);
}
QLabel {
  color: #eef2f6;
  font-family: "Microsoft YaHei UI", "Segoe UI";
  letter-spacing: 0px;
}
QLabel#TitleLabel {
  color: #f8fafc;
  font-family: "Microsoft YaHei UI", "Segoe UI";
  font-size: 22px;
  font-weight: 700;
}
QLabel#SubtitleLabel,
QLabel#PanelCaption,
QLabel#MetricName {
  color: rgba(203, 213, 225, 210);
}
QLabel#PanelCaption {
  font-size: 13px;
  font-weight: 700;
}
QLabel#MetricValue {
  color: #e2e8f0;
  font-family: "Microsoft YaHei UI", "Segoe UI";
  font-size: 16px;
  font-weight: 700;
}
QLabel#StatusLabel {
  color: #dbe5ef;
  background-color: rgba(15, 23, 32, 190);
  border: 1px solid rgba(255, 255, 255, 28);
  border-radius: 6px;
  padding: 8px 10px;
}
QComboBox,
QSpinBox,
QLineEdit {
  color: #f8fafc;
  background-color: rgba(15, 23, 32, 238);
  border: 1px solid rgba(148, 163, 184, 74);
  border-radius: 6px;
  padding: 7px 9px;
  selection-background-color: rgba(96, 165, 250, 150);
}
QComboBox::drop-down {
  border: 0;
  width: 24px;
}
QComboBox QAbstractItemView {
  color: #f8fafc;
  background-color: #111827;
  border: 1px solid rgba(148, 163, 184, 90);
  selection-background-color: rgba(59, 130, 246, 150);
}
QSpinBox::up-button,
QSpinBox::down-button {
  width: 18px;
  border: 0;
  background-color: rgba(148, 163, 184, 26);
}
QPushButton {
  min-height: 34px;
  color: #f8fafc;
  background-color: rgba(30, 41, 59, 238);
  border: 1px solid rgba(148, 163, 184, 72);
  border-radius: 6px;
  padding: 8px 12px;
  font-weight: 700;
}
QPushButton:hover {
  background-color: rgba(51, 65, 85, 238);
  border-color: rgba(203, 213, 225, 120);
}
QPushButton#PrimaryButton {
  color: #0f172a;
  background-color: #f8fafc;
  border-color: rgba(255, 255, 255, 160);
}
QPushButton#PrimaryButton:hover {
  background-color: #e2e8f0;
}
QPushButton#ThemeButton {
  min-height: 28px;
  padding: 6px 12px;
}
QPushButton#ThemeButton:checked {
  color: #0f172a;
  background-color: #f8fafc;
  border-color: rgba(255, 255, 255, 160);
}
QPushButton#ColorButton {
  min-height: 28px;
  padding: 6px 8px;
  font-family: "Consolas", "Microsoft YaHei UI";
}
QScrollArea#ControlsScroll {
  background: transparent;
  border: 0;
}
QScrollArea#ControlsScroll > QWidget > QWidget {
  background: transparent;
}
QColorDialog,
QColorDialog QWidget {
  background-color: #f3f6fa;
  color: #182532;
}
QColorDialog QLabel {
  color: #182532;
}
QColorDialog QLineEdit,
QColorDialog QSpinBox {
  color: #102030;
  background-color: #ffffff;
  border: 1px solid #9aaaba;
  border-radius: 4px;
  padding: 4px 6px;
}
QColorDialog QPushButton {
  color: #ffffff;
  background-color: #4f7486;
  border: 1px solid #7895a4;
  border-radius: 6px;
  padding: 7px 12px;
}
QColorDialog QPushButton:hover {
  background-color: #365b70;
}
"""

LIGHT_STYLE = """
QMainWindow {
  background: #f4f6f8;
}
QWidget#Root {
  color: #1f2937;
}
QFrame#HeaderGlass,
QFrame#ControlsGlass,
QFrame#PreviewGlass {
  background-color: rgba(255, 255, 255, 245);
  border: 1px solid #dfe4ea;
  border-radius: 8px;
}
QFrame#SectionFrame {
  background: transparent;
  border: 0;
}
QSplitter::handle {
  background: #d8dee6;
  border-radius: 3px;
}
QSplitter::handle:hover {
  background: #b9c1ca;
}
QLabel {
  color: #1f2937;
  font-family: "Microsoft YaHei UI", "Segoe UI";
  letter-spacing: 0px;
}
QLabel#TitleLabel {
  color: #111827;
  font-family: "Microsoft YaHei UI", "Segoe UI";
  font-size: 22px;
  font-weight: 700;
}
QLabel#SubtitleLabel,
QLabel#PanelCaption,
QLabel#MetricName {
  color: #6b7280;
}
QLabel#PanelCaption {
  font-size: 13px;
  font-weight: 700;
}
QLabel#MetricValue {
  color: #111827;
  font-family: "Microsoft YaHei UI", "Segoe UI";
  font-size: 16px;
  font-weight: 700;
}
QLabel#StatusLabel {
  color: #4b5563;
  background-color: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 8px 10px;
}
QComboBox,
QSpinBox,
QLineEdit {
  color: #111827;
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 7px 9px;
  selection-background-color: rgba(147, 197, 253, 160);
}
QComboBox::drop-down {
  border: 0;
  width: 24px;
}
QComboBox QAbstractItemView {
  color: #111827;
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  selection-background-color: rgba(219, 234, 254, 220);
}
QSpinBox::up-button,
QSpinBox::down-button {
  width: 18px;
  border: 0;
  background-color: #f3f4f6;
}
QPushButton {
  min-height: 34px;
  color: #111827;
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 8px 12px;
  font-weight: 700;
}
QPushButton:hover {
  background-color: #f3f4f6;
  border-color: #b9c1ca;
}
QPushButton#PrimaryButton {
  color: #ffffff;
  background-color: #111827;
  border-color: #111827;
}
QPushButton#PrimaryButton:hover {
  background-color: #374151;
  border-color: #374151;
}
QPushButton#ThemeButton {
  min-height: 28px;
  padding: 6px 12px;
}
QPushButton#ThemeButton:checked {
  color: #ffffff;
  background-color: #111827;
  border-color: #111827;
}
QPushButton#ColorButton {
  min-height: 28px;
  padding: 6px 8px;
  font-family: "Consolas", "Microsoft YaHei UI";
}
QScrollArea#ControlsScroll {
  background: transparent;
  border: 0;
}
QScrollArea#ControlsScroll > QWidget > QWidget {
  background: transparent;
}
QColorDialog,
QColorDialog QWidget {
  background-color: #f3f6fa;
  color: #182532;
}
QColorDialog QLabel {
  color: #182532;
}
QColorDialog QLineEdit,
QColorDialog QSpinBox {
  color: #102030;
  background-color: #ffffff;
  border: 1px solid #9aaaba;
  border-radius: 4px;
  padding: 4px 6px;
}
QColorDialog QPushButton {
  color: #ffffff;
  background-color: #4f7486;
  border: 1px solid #7895a4;
  border-radius: 6px;
  padding: 7px 12px;
}
QColorDialog QPushButton:hover {
  background-color: #365b70;
}
"""

APP_STYLE = LIGHT_STYLE


def resample_filter(name: str):
    if name == "nearest":
        return Image.Resampling.NEAREST
    return Image.Resampling.LANCZOS


def is_svg_path(path: Path) -> bool:
    return path.suffix.lower() in (".svg", ".svgz")


def is_gif_path(path: Path) -> bool:
    return path.suffix.lower() == ".gif"


def is_video_path(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def path_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def resolve_existing_path(path: Path) -> Path:
    if path_exists(path):
        return path

    name = path.name
    if not name or "?" in name:
        return path

    roots: list[Path] = []
    try:
        roots.append(path.parent.parent)
    except RuntimeError:
        pass
    if path.drive:
        roots.append(Path(f"{path.drive}\\"))
    roots.extend([Path.home(), Path.home() / "Downloads", Path.home() / "Desktop"])

    seen: set[str] = set()
    for root in roots:
        try:
            resolved_root = root.resolve()
        except OSError:
            continue
        root_key = str(resolved_root).lower()
        if root_key in seen or not resolved_root.exists() or not resolved_root.is_dir():
            continue
        seen.add(root_key)

        direct = resolved_root / name
        if path_exists(direct):
            return direct

        try:
            children = list(resolved_root.iterdir())
        except OSError:
            continue
        for child in children:
            if not child.is_dir():
                continue
            candidate = child / name
            if path_exists(candidate):
                return candidate

    return path


def clamp_u8(value: int) -> int:
    return max(0, min(255, int(value)))


def normalize_rgb(color: RGB) -> RGB:
    return tuple(clamp_u8(value) for value in color)  # type: ignore[return-value]


def rgb_to_hex(color: RGB) -> str:
    r, g, b = normalize_rgb(color)
    return f"#{r:02X}{g:02X}{b:02X}"


def parse_hex_rgb(text: str) -> RGB:
    value = text.strip()
    if value.startswith("#"):
        value = value[1:]
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", value):
        raise ValueError("Color must use #RRGGBB format")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def blend_over_background(fg: RGB, alpha: int, bg: RGB) -> RGB:
    if alpha <= 0:
        return bg
    if alpha >= 255:
        return fg
    r = (fg[0] * alpha + bg[0] * (255 - alpha) + 127) // 255
    g = (fg[1] * alpha + bg[1] * (255 - alpha) + 127) // 255
    b = (fg[2] * alpha + bg[2] * (255 - alpha) + 127) // 255
    return clamp_u8(r), clamp_u8(g), clamp_u8(b)


def color_distance(a: RGB, b: RGB) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def detect_edge_background(image: Image.Image) -> RGB | None:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    if width == 0 or height == 0:
        return None

    samples: list[RGB] = []
    pixels = rgba.load()
    for x in range(width):
        for y in (0, height - 1):
            r, g, b, a = pixels[x, y]
            if a > 16:
                samples.append((r, g, b))
    for y in range(height):
        for x in (0, width - 1):
            r, g, b, a = pixels[x, y]
            if a > 16:
                samples.append((r, g, b))

    if not samples:
        return None

    bucket_counts: Counter[RGB] = Counter((r // 8 * 8, g // 8 * 8, b // 8 * 8) for r, g, b in samples)
    bucket, _ = bucket_counts.most_common(1)[0]
    close = [color for color in samples if color_distance(color, bucket) <= 12]
    if not close:
        return bucket

    count = len(close)
    return (
        sum(color[0] for color in close) // count,
        sum(color[1] for color in close) // count,
        sum(color[2] for color in close) // count,
    )


def apply_svg_cutout(
    image: Image.Image,
    cut_mode: str,
    cut_color: RGB,
    tolerance: int,
) -> Image.Image:
    rgba = image.convert("RGBA")
    if cut_mode == SVG_CUT_ALPHA:
        return rgba

    key = detect_edge_background(rgba) if cut_mode == SVG_CUT_AUTO else normalize_rgb(cut_color)
    if key is None:
        return rgba

    threshold = max(0, min(255, int(tolerance)))
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            distance = color_distance((r, g, b), key)
            if distance <= threshold:
                pixels[x, y] = (r, g, b, 0)
            elif distance <= threshold * 2 and threshold > 0:
                soft = int(a * (distance - threshold) / threshold)
                pixels[x, y] = (r, g, b, max(0, min(255, soft)))
    return rgba


def has_alpha_channel(image: Image.Image) -> bool:
    rgba = image.convert("RGBA")
    extrema = rgba.getchannel("A").getextrema()
    return extrema[0] < 255


def rgba_to_matrix(
    image: Image.Image,
    rows: int,
    cols: int,
    background_mode: str,
    background_color: RGB,
    color_mode: str,
    main_color: RGB,
) -> list[list[RGB]]:
    rgba = image.convert("RGBA")
    if rgba.size != (cols, rows):
        rgba = rgba.resize((cols, rows), Image.Resampling.LANCZOS)

    bg = normalize_rgb(background_color) if background_mode == SVG_BG_COLOR else DEFAULT_SVG_BACKGROUND
    fg = normalize_rgb(main_color)
    use_palette = color_mode == SVG_COLOR_PALETTE

    matrix: list[list[RGB]] = []
    pixels = rgba.load()
    for y in range(rows):
        row: list[RGB] = []
        for x in range(cols):
            r, g, b, alpha = pixels[x, y]
            pixel_color = fg if use_palette and alpha > 0 else (r, g, b)
            row.append(blend_over_background(pixel_color, alpha, bg))
        matrix.append(row)
    return matrix


def ensure_qt_app() -> None:
    global _SVG_QT_APP
    if Qt is None:
        raise RuntimeError("SVG import requires PyQt6 with QtSvg")
    if QApplication.instance() is None:
        _SVG_QT_APP = QApplication(["ws2812_model_helper_svg"])


def origin_axes(origin: str) -> tuple[bool, bool]:
    top_first = origin.startswith("top")
    left_first = origin.endswith("left")
    return top_first, left_first


def ordered_range(count: int, forward: bool) -> list[int]:
    values = list(range(count))
    if not forward:
        values.reverse()
    return values


def physical_order(rows: int, cols: int, layout: str, origin: str, reverse_first_line: bool) -> list[Coord]:
    top_first, left_first = origin_axes(origin)
    order: list[Coord] = []

    if layout in (LAYOUT_ROW_ZIGZAG, LAYOUT_ROW_MAJOR):
        y_values = ordered_range(rows, top_first)
        first_x_values = ordered_range(cols, left_first)
        if reverse_first_line:
            first_x_values = list(reversed(first_x_values))

        for line_index, y in enumerate(y_values):
            x_values = list(first_x_values)
            if layout == LAYOUT_ROW_ZIGZAG and (line_index % 2) == 1:
                x_values.reverse()
            for x in x_values:
                order.append((x, y))
    else:
        x_values = ordered_range(cols, left_first)
        first_y_values = ordered_range(rows, top_first)
        if reverse_first_line:
            first_y_values = list(reversed(first_y_values))

        for line_index, x in enumerate(x_values):
            y_values = list(first_y_values)
            if layout == LAYOUT_COL_ZIGZAG and (line_index % 2) == 1:
                y_values.reverse()
            for y in y_values:
                order.append((x, y))

    return order


def rotate_source_image(source: Image.Image, rotation: int) -> Image.Image:
    normalized = rotation % 360
    if normalized == 90:
        return source.transpose(Image.Transpose.ROTATE_270)
    if normalized == 180:
        return source.transpose(Image.Transpose.ROTATE_180)
    if normalized == 270:
        return source.transpose(Image.Transpose.ROTATE_90)
    return source


def blank_matrix(rows: int, cols: int, color: RGB = (0, 0, 0)) -> list[list[RGB]]:
    fill = normalize_rgb(color)
    return [[fill for _ in range(cols)] for _ in range(rows)]


def resize_matrix(matrix: list[list[RGB]], rows: int, cols: int, fill: RGB = (0, 0, 0)) -> list[list[RGB]]:
    result = blank_matrix(rows, cols, fill)
    copy_rows = min(rows, len(matrix))
    copy_cols = min(cols, len(matrix[0]) if matrix else 0)
    for y in range(copy_rows):
        for x in range(copy_cols):
            result[y][x] = normalize_rgb(matrix[y][x])
    return result


def find_text_font(font_hint: str, pixel_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates: list[str] = []
    hint = font_hint.strip()
    if hint:
        candidates.append(hint)
    candidates.extend([
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ])
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, pixel_size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_text_matrix(
    text: str,
    rows: int,
    cols: int,
    font_hint: str,
    rotation: int,
    scale_percent: int,
    foreground: RGB,
    background_mode: str,
    background_color: RGB,
) -> list[list[RGB]]:
    bg = normalize_rgb(background_color) if background_mode == SVG_BG_COLOR else (0, 0, 0)
    if not text:
        return blank_matrix(rows, cols, bg)

    scale = max(20, min(400, scale_percent)) / 100.0
    canvas_scale = 8 if max(rows, cols) <= 64 else 4
    render_w = max(cols * canvas_scale, 1)
    render_h = max(rows * canvas_scale, 1)
    font_size = max(6, int(render_h * 0.78 * scale))
    font = find_text_font(font_hint, font_size)
    image = Image.new("RGBA", (render_w, render_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (render_w - text_w) // 2 - bbox[0]
    y = (render_h - text_h) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(*normalize_rgb(foreground), 255))
    image = rotate_source_image(image, rotation)
    image = image.resize((cols, rows), Image.Resampling.LANCZOS)
    return rgba_to_matrix(image, rows, cols, background_mode, bg, SVG_COLOR_ORIGINAL, foreground)


def render_svg_matrix(
    path: Path,
    rows: int,
    cols: int,
    rotation: int,
    cut_mode: str,
    cut_color: RGB,
    cut_tolerance: int,
    background_mode: str,
    background_color: RGB,
    color_mode: str,
    main_color: RGB,
) -> list[list[RGB]]:
    ensure_qt_app()
    path = resolve_existing_path(path)

    renderer = QSvgRenderer()
    try:
        svg_bytes = QByteArray(path.read_bytes())
    except OSError as exc:
        raise FileNotFoundError(f"Input SVG not found or unreadable: {path}") from exc
    if not renderer.load(svg_bytes):
        raise ValueError(f"Invalid SVG file: {path}")

    render_scale = 8 if max(rows, cols) <= 64 else 4
    render_w = max(cols, 1) * render_scale
    render_h = max(rows, 1) * render_scale
    image = QImage(render_w, render_h, QImage.Format.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter, QRectF(0, 0, render_w, render_h))
    painter.end()

    source = Image.new("RGBA", (render_w, render_h))
    source_pixels = source.load()
    for y in range(render_h):
        for x in range(render_w):
            pixel = image.pixelColor(x, y)
            source_pixels[x, y] = (pixel.red(), pixel.green(), pixel.blue(), pixel.alpha())

    source = apply_svg_cutout(source, cut_mode, cut_color, cut_tolerance)
    source = rotate_source_image(source, rotation)
    resize_method = Image.Resampling.LANCZOS if render_scale > 1 else Image.Resampling.NEAREST
    source = source.resize((cols, rows), resize_method)

    return rgba_to_matrix(source, rows, cols, background_mode, background_color, color_mode, main_color)


def render_raster_matrix(
    path: Path,
    rows: int,
    cols: int,
    resample_name: str,
    rotation: int,
    cut_mode: str,
    cut_color: RGB,
    cut_tolerance: int,
    background_mode: str,
    background_color: RGB,
    color_mode: str,
    main_color: RGB,
) -> list[list[RGB]]:
    path = resolve_existing_path(path)
    source = Image.open(path).convert("RGBA")
    effective_cut_mode = SVG_CUT_ALPHA if cut_mode == SVG_CUT_AUTO and has_alpha_channel(source) else cut_mode
    source = apply_svg_cutout(source, effective_cut_mode, cut_color, cut_tolerance)
    source = rotate_source_image(source, rotation)
    source = source.resize((cols, rows), resample_filter(resample_name))
    return rgba_to_matrix(source, rows, cols, background_mode, background_color, color_mode, main_color)


def load_image_matrix(
    path: Path,
    rows: int,
    cols: int,
    resample_name: str,
    rotation: int = 0,
    svg_cut_mode: str = SVG_CUT_AUTO,
    svg_cut_color: RGB = DEFAULT_SVG_CUT_COLOR,
    svg_cut_tolerance: int = DEFAULT_SVG_CUT_TOLERANCE,
    svg_background_mode: str = SVG_BG_TRANSPARENT,
    svg_background_color: RGB = DEFAULT_SVG_BACKGROUND,
    svg_color_mode: str = SVG_COLOR_ORIGINAL,
    svg_main_color: RGB = DEFAULT_SVG_COLOR,
) -> list[list[RGB]]:
    path = resolve_existing_path(path)
    if is_svg_path(path):
        return render_svg_matrix(
            path,
            rows,
            cols,
            rotation,
            svg_cut_mode,
            svg_cut_color,
            svg_cut_tolerance,
            svg_background_mode,
            svg_background_color,
            svg_color_mode,
            svg_main_color,
        )

    return render_raster_matrix(
        path,
        rows,
        cols,
        resample_name,
        rotation,
        svg_cut_mode,
        svg_cut_color,
        svg_cut_tolerance,
        svg_background_mode,
        svg_background_color,
        svg_color_mode,
        svg_main_color,
    )


def image_to_matrix(
    source: Image.Image,
    rows: int,
    cols: int,
    resample_name: str,
    rotation: int,
    cut_mode: str,
    cut_color: RGB,
    cut_tolerance: int,
    background_mode: str,
    background_color: RGB,
    color_mode: str,
    main_color: RGB,
) -> list[list[RGB]]:
    image = source.convert("RGBA")
    effective_cut_mode = SVG_CUT_ALPHA if cut_mode == SVG_CUT_AUTO and has_alpha_channel(image) else cut_mode
    image = apply_svg_cutout(image, effective_cut_mode, cut_color, cut_tolerance)
    image = rotate_source_image(image, rotation)
    image = image.resize((cols, rows), resample_filter(resample_name))
    return rgba_to_matrix(image, rows, cols, background_mode, background_color, color_mode, main_color)


def load_gif_frames(
    path: Path,
    rows: int,
    cols: int,
    resample_name: str,
    rotation: int,
    cut_mode: str,
    cut_color: RGB,
    cut_tolerance: int,
    background_mode: str,
    background_color: RGB,
    color_mode: str,
    main_color: RGB,
    max_frames: int,
    frame_step: int,
) -> list[list[list[RGB]]]:
    path = resolve_existing_path(path)
    frames: list[list[list[RGB]]] = []
    step = max(1, frame_step)
    limit = max(1, max_frames)
    with Image.open(path) as image:
        for index, frame in enumerate(ImageSequence.Iterator(image)):
            if index % step != 0:
                continue
            frames.append(image_to_matrix(
                frame,
                rows,
                cols,
                resample_name,
                rotation,
                cut_mode,
                cut_color,
                cut_tolerance,
                background_mode,
                background_color,
                color_mode,
                main_color,
            ))
            if len(frames) >= limit:
                break
    if not frames:
        raise ValueError(f"No GIF frames decoded: {path}")
    return frames


def load_video_frames(
    path: Path,
    rows: int,
    cols: int,
    resample_name: str,
    rotation: int,
    cut_mode: str,
    cut_color: RGB,
    cut_tolerance: int,
    background_mode: str,
    background_color: RGB,
    color_mode: str,
    main_color: RGB,
    max_frames: int,
    frame_step: int,
) -> list[list[list[RGB]]]:
    path = resolve_existing_path(path)
    try:
        import cv2  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("Video import requires OpenCV (cv2)") from exc

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {path}")

    frames: list[list[list[RGB]]] = []
    step = max(1, frame_step)
    limit = max(1, max_frames)
    index = 0
    try:
        while len(frames) < limit:
            ok, frame = capture.read()
            if not ok:
                break
            if index % step == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                source = Image.fromarray(rgb).convert("RGBA")
                frames.append(image_to_matrix(
                    source,
                    rows,
                    cols,
                    resample_name,
                    rotation,
                    cut_mode,
                    cut_color,
                    cut_tolerance,
                    background_mode,
                    background_color,
                    color_mode,
                    main_color,
                ))
            index += 1
    finally:
        capture.release()

    if not frames:
        raise ValueError(f"No video frames decoded: {path}")
    return frames


def load_animation_frames(
    path: Path,
    rows: int,
    cols: int,
    resample_name: str,
    rotation: int,
    cut_mode: str,
    cut_color: RGB,
    cut_tolerance: int,
    background_mode: str,
    background_color: RGB,
    color_mode: str,
    main_color: RGB,
    max_frames: int,
    frame_step: int,
) -> list[list[list[RGB]]]:
    path = resolve_existing_path(path)
    if is_gif_path(path):
        return load_gif_frames(
            path,
            rows,
            cols,
            resample_name,
            rotation,
            cut_mode,
            cut_color,
            cut_tolerance,
            background_mode,
            background_color,
            color_mode,
            main_color,
            max_frames,
            frame_step,
        )
    if is_video_path(path):
        return load_video_frames(
            path,
            rows,
            cols,
            resample_name,
            rotation,
            cut_mode,
            cut_color,
            cut_tolerance,
            background_mode,
            background_color,
            color_mode,
            main_color,
            max_frames,
            frame_step,
        )
    return [load_image_matrix(
        path,
        rows,
        cols,
        resample_name,
        rotation,
        cut_mode,
        cut_color,
        cut_tolerance,
        background_mode,
        background_color,
        color_mode,
        main_color,
    )]


def render_svg_source_preview(path: Path, rotation: int) -> Image.Image:
    ensure_qt_app()
    path = resolve_existing_path(path)
    renderer = QSvgRenderer()
    if not renderer.load(QByteArray(path.read_bytes())):
        raise ValueError(f"Invalid SVG file: {path}")
    default_size = renderer.defaultSize()
    render_w = default_size.width() if not default_size.isEmpty() else 512
    render_h = default_size.height() if not default_size.isEmpty() else 512
    render_w = max(1, min(1024, render_w))
    render_h = max(1, min(1024, render_h))
    image = QImage(render_w, render_h, QImage.Format.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter, QRectF(0, 0, render_w, render_h))
    painter.end()

    source = Image.new("RGBA", (render_w, render_h))
    pixels = source.load()
    for y in range(render_h):
        for x in range(render_w):
            pixel = image.pixelColor(x, y)
            pixels[x, y] = (pixel.red(), pixel.green(), pixel.blue(), pixel.alpha())
    return rotate_source_image(source, rotation)


def load_source_preview_image(path: Path, rotation: int, frame_index: int = 0, frame_step: int = 1) -> Image.Image:
    path = resolve_existing_path(path)
    target_frame = max(0, frame_index) * max(1, frame_step)
    if is_svg_path(path):
        return render_svg_source_preview(path, rotation)
    if is_gif_path(path):
        with Image.open(path) as image:
            selected = None
            for index, frame in enumerate(ImageSequence.Iterator(image)):
                if index == target_frame:
                    selected = frame.convert("RGBA")
                    break
            if selected is None:
                image.seek(0)
                selected = image.convert("RGBA")
            return rotate_source_image(selected, rotation)
    if is_video_path(path):
        try:
            import cv2  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("Video preview requires OpenCV (cv2)") from exc
        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            raise ValueError(f"Could not open video: {path}")
        try:
            capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ok, frame = capture.read()
            if not ok:
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = capture.read()
            if not ok:
                raise ValueError(f"No video frame decoded: {path}")
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return rotate_source_image(Image.fromarray(rgb).convert("RGBA"), rotation)
        finally:
            capture.release()
    return rotate_source_image(Image.open(path).convert("RGBA"), rotation)


def default_matrix(rows: int, cols: int) -> list[list[RGB]]:
    matrix: list[list[RGB]] = []
    for y in range(rows):
        row: list[RGB] = []
        for x in range(cols):
            row.append((clamp_u8(24 + x * 10), clamp_u8(16 + y * 8), clamp_u8(20 + (x + y) * 4)))
        matrix.append(row)
    return matrix


def validate_array_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError("Array name must be a valid C identifier")
    return name


def header_guard_for(array_name: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", array_name).upper()
    return f"{text}_H"


def export_header(
    matrix: list[list[RGB]],
    order: Iterable[Coord],
    array_name: str,
    layout: str,
    origin: str,
    reverse_first_line: bool,
) -> str:
    validate_array_name(array_name)
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    coords = list(order)
    guard = header_guard_for(array_name)
    reverse_text = "reverse" if reverse_first_line else "normal"

    lines = [
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        '#include "ws2812_pwm.h"',
        "",
        f"/* Generated by ws2812_model_helper.py.",
        f" * Size: {cols} x {rows}",
        f" * Layout: {LAYOUT_LABELS.get(layout, layout)}",
        f" * Origin: {ORIGIN_LABELS.get(origin, origin)}",
        f" * First line: {reverse_text}",
        " */",
        f"static const ws2812_rgb_t {array_name}[{len(coords)}] = {{",
    ]

    for x, y in coords:
        r, g, b = matrix[y][x]
        lines.append(f"  {{ {r:3d}U, {g:3d}U, {b:3d}U }},")

    lines.extend([
        "};",
        "",
        f"#endif /* {guard} */",
        "",
    ])
    return "\n".join(lines)


def export_animation_header(
    frames: list[list[list[RGB]]],
    order: Iterable[Coord],
    array_name: str,
    layout: str,
    origin: str,
    reverse_first_line: bool,
    frame_delay_ms: int,
) -> str:
    validate_array_name(array_name)
    if not frames:
        raise ValueError("Animation has no frames")
    rows = len(frames[0])
    cols = len(frames[0][0]) if rows else 0
    coords = list(order)
    guard = header_guard_for(array_name)
    reverse_text = "reverse" if reverse_first_line else "normal"

    lines = [
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        '#include "ws2812_pwm.h"',
        "",
        f"#define {array_name.upper()}_FRAME_COUNT {len(frames)}U",
        f"#define {array_name.upper()}_LED_COUNT {len(coords)}U",
        f"#define {array_name.upper()}_FRAME_DELAY_MS {max(1, frame_delay_ms)}U",
        "",
        f"/* Generated by ws2812_model_helper.py.",
        f" * Size: {cols} x {rows}",
        f" * Frames: {len(frames)}",
        f" * Layout: {LAYOUT_LABELS.get(layout, layout)}",
        f" * Origin: {ORIGIN_LABELS.get(origin, origin)}",
        f" * First line: {reverse_text}",
        " */",
        f"static const ws2812_rgb_t {array_name}[{len(frames)}][{len(coords)}] = {{",
    ]

    for frame_index, frame in enumerate(frames):
        lines.append(f"  /* frame {frame_index} */")
        lines.append("  {")
        for x, y in coords:
            r, g, b = frame[y][x]
            lines.append(f"    {{ {r:3d}U, {g:3d}U, {b:3d}U }},")
        lines.append("  },")

    lines.extend([
        "};",
        "",
        f"#endif /* {guard} */",
        "",
    ])
    return "\n".join(lines)


if Qt is not None:

    def add_glass_shadow(widget: QWidget) -> None:
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(18)
        effect.setOffset(0, 8)
        effect.setColor(QColor(15, 23, 42, 34))
        widget.setGraphicsEffect(effect)


    class TechBackground(QWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.setObjectName("Root")
            self.theme = "light"

        def set_theme(self, theme: str) -> None:
            self.theme = theme
            self.update()

        def paintEvent(self, event) -> None:  # noqa: N802
            del event
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            if self.theme == "light":
                painter.fillRect(self.rect(), QColor(244, 246, 248))
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
                painter.setPen(QPen(QColor(232, 237, 243), 1))
                grid = 48
                for x in range(0, self.width(), grid):
                    painter.drawLine(x, 0, x, self.height())
                return

            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0.0, QColor(16, 20, 24))
            gradient.setColorAt(0.48, QColor(20, 25, 31))
            gradient.setColorAt(1.0, QColor(10, 14, 18))
            grid_color = QColor(148, 163, 184, 18)
            beam_color = QColor(148, 163, 184, 18)
            accent_color = QColor(148, 163, 184, 44)
            short_line = QColor(148, 163, 184, 40)
            painter.fillRect(self.rect(), gradient)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setPen(QPen(grid_color, 1))
            grid = 34
            for x in range(0, self.width(), grid):
                painter.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), grid):
                painter.drawLine(0, y, self.width(), y)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            for offset, alpha in ((-120, 34), (180, 22), (500, 18)):
                path = QPainterPath()
                path.moveTo(offset, self.height())
                path.lineTo(offset + 260, self.height())
                path.lineTo(offset + 760, 0)
                path.lineTo(offset + 500, 0)
                path.closeSubpath()
                color = QColor(beam_color)
                color.setAlpha(alpha)
                painter.fillPath(path, color)

            painter.setPen(QPen(accent_color, 2))
            painter.drawLine(24, 76, min(self.width() - 24, 520), 76)
            painter.setPen(QPen(short_line, 1))
            painter.drawLine(self.width() - 360, 30, self.width() - 24, 30)


    class MatrixPreview(QWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.matrix: list[list[RGB]] = []
            self.order: list[Coord] = []
            self.empty_text = UI_TEXT["zh"]["empty_preview"]
            self.preview_title = UI_TEXT["zh"]["preview_title"]
            self.theme = "light"
            self.editable = False
            self.brush_color: RGB = DEFAULT_BRUSH_COLOR
            self.edit_callback: Callable[[int, int, RGB], None] | None = None
            self._grid_origin = QPointF(0, 0)
            self._cell_size = 0.0
            self._paint_button: Qt.MouseButton | None = None
            self.setMinimumSize(360, 320)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        def set_language(self, empty_text: str, preview_title: str) -> None:
            self.empty_text = empty_text
            self.preview_title = preview_title
            self.update()

        def set_theme(self, theme: str) -> None:
            self.theme = theme
            self.update()

        def set_data(self, matrix: list[list[RGB]], order: list[Coord]) -> None:
            self.matrix = matrix
            self.order = order
            self.update()

        def set_editable(self, editable: bool) -> None:
            self.editable = editable
            self.setCursor(Qt.CursorShape.CrossCursor if editable else Qt.CursorShape.ArrowCursor)
            self.update()

        def set_brush_color(self, color: RGB) -> None:
            self.brush_color = normalize_rgb(color)

        def set_edit_callback(self, callback: Callable[[int, int, RGB], None]) -> None:
            self.edit_callback = callback

        def cell_at(self, position: QPointF) -> Coord | None:
            if not self.matrix or self._cell_size <= 0:
                return None
            x = int((position.x() - self._grid_origin.x()) / self._cell_size)
            y = int((position.y() - self._grid_origin.y()) / self._cell_size)
            rows = len(self.matrix)
            cols = len(self.matrix[0])
            if 0 <= x < cols and 0 <= y < rows:
                return x, y
            return None

        def paint_cell_from_event(self, event) -> None:
            if not self.editable or self.edit_callback is None:
                return
            coord = self.cell_at(event.position())
            if coord is None:
                return
            color = (0, 0, 0) if self._paint_button == Qt.MouseButton.RightButton else self.brush_color
            self.edit_callback(coord[0], coord[1], color)

        def mousePressEvent(self, event) -> None:  # noqa: N802
            if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
                self._paint_button = event.button()
                self.paint_cell_from_event(event)
                event.accept()
                return
            super().mousePressEvent(event)

        def mouseMoveEvent(self, event) -> None:  # noqa: N802
            if self._paint_button is not None:
                self.paint_cell_from_event(event)
                event.accept()
                return
            super().mouseMoveEvent(event)

        def mouseReleaseEvent(self, event) -> None:  # noqa: N802
            if event.button() == self._paint_button:
                self._paint_button = None
                event.accept()
                return
            super().mouseReleaseEvent(event)

        def paintEvent(self, event) -> None:  # noqa: N802
            del event
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            if self.theme == "light":
                bg_color = QColor(255, 255, 255, 245)
                border_color = QColor(223, 228, 234)
                title_color = QColor(17, 24, 39)
                subtitle_color = QColor(107, 114, 128)
                divider_color = QColor(229, 231, 235)
                empty_color = QColor(107, 114, 128)
                panel_bg = QColor(248, 250, 252)
                panel_border = QColor(229, 231, 235)
                cell_border = QColor(209, 213, 219)
                footer_color = QColor(75, 85, 99)
            else:
                bg_color = QColor(20, 25, 31, 238)
                border_color = QColor(255, 255, 255, 34)
                title_color = QColor(248, 250, 252)
                subtitle_color = QColor(203, 213, 225)
                divider_color = QColor(51, 65, 85)
                empty_color = QColor(210, 231, 238)
                panel_bg = QColor(15, 23, 32, 238)
                panel_border = QColor(255, 255, 255, 28)
                cell_border = QColor(7, 16, 26, 190)
                footer_color = QColor(203, 213, 225)

            outer = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
            painter.fillRect(outer, bg_color)
            painter.setPen(QPen(border_color, 1))
            painter.drawRoundedRect(outer, 8, 8)

            compact = self.height() < 430 or self.width() < 520
            margin = 14 if compact else 22
            header_h = 62 if compact else 86
            title_size = 16 if compact else 20
            painter.setFont(QFont("Microsoft YaHei UI", title_size, QFont.Weight.Bold))
            painter.setPen(title_color)
            painter.drawText(QRectF(margin, 14, self.width() - margin * 2, 28), Qt.AlignmentFlag.AlignLeft, "LED MAP")
            painter.setFont(QFont("Microsoft YaHei UI", 9 if compact else 10))
            painter.setPen(subtitle_color)
            painter.drawText(QRectF(margin, 39, self.width() - margin * 2, 22), Qt.AlignmentFlag.AlignLeft, self.preview_title)
            divider_y = header_h - 12
            painter.setPen(QPen(divider_color, 2))
            painter.drawLine(margin, divider_y, self.width() - margin, divider_y)

            if not self.matrix:
                painter.setPen(empty_color)
                painter.setFont(QFont("Microsoft YaHei UI", 12))
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.empty_text)
                return

            rows = len(self.matrix)
            cols = len(self.matrix[0])
            footer_h = 30
            board_top = header_h + 12
            board = QRectF(margin, board_top, self.width() - margin * 2, self.height() - board_top - footer_h - 12)
            usable_w = max(1.0, board.width())
            usable_h = max(1.0, board.height())
            cell = min(usable_w / cols, usable_h / rows)
            origin_x = board.x() + (usable_w - cell * cols) / 2
            origin_y = board.y() + (usable_h - cell * rows) / 2
            self._grid_origin = QPointF(origin_x, origin_y)
            self._cell_size = cell

            panel_rect = QRectF(origin_x - 8, origin_y - 8, cell * cols + 16, cell * rows + 16)
            painter.fillRect(panel_rect, panel_bg)
            painter.setPen(QPen(panel_border, 1))
            painter.drawRect(panel_rect)

            order_index = {coord: index for index, coord in enumerate(self.order)}
            centers: list[QPointF] = []
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

            for y in range(rows):
                for x in range(cols):
                    r, g, b = self.matrix[y][x]
                    rect = QRectF(origin_x + x * cell, origin_y + y * cell, cell, cell)
                    painter.fillRect(rect, QColor(r, g, b))
                    painter.setPen(QPen(cell_border, 1))
                    painter.drawRect(rect)

            if cell >= 10 and len(self.order) > 1:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                for x, y in self.order:
                    centers.append(QPointF(origin_x + (x + 0.5) * cell, origin_y + (y + 0.5) * cell))
                painter.setPen(QPen(QColor(148, 163, 184, 90), max(1, int(cell * 0.05))))
                for index in range(1, len(centers)):
                    painter.drawLine(centers[index - 1], centers[index])

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            font = QFont("Consolas", max(6, int(cell * 0.26)), QFont.Weight.Bold)
            painter.setFont(font)
            if cell >= 14:
                for y in range(rows):
                    for x in range(cols):
                        r, g, b = self.matrix[y][x]
                        rect = QRectF(origin_x + x * cell, origin_y + y * cell, cell, cell)
                        brightness = (r * 299 + g * 587 + b * 114) / 1000
                        painter.setPen(QColor(5, 10, 14) if brightness > 135 else QColor(245, 250, 255))
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(order_index.get((x, y), "")))

            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setFont(QFont("Microsoft YaHei UI", 11))
            painter.setPen(footer_color)
            footer = f"{cols} x {rows}    {cols * rows} LEDS"
            painter.drawText(QRectF(margin, self.height() - 30, self.width() - margin * 2, 20), Qt.AlignmentFlag.AlignRight, footer)


    class SourcePreview(QWidget):
        def __init__(self, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.image: Image.Image | None = None
            self.title = UI_TEXT["zh"]["source_preview_title"]
            self.empty_text = UI_TEXT["zh"]["source_preview_empty"]
            self.theme = "light"
            self.setMinimumSize(320, 320)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        def set_language(self, title: str, empty_text: str) -> None:
            self.title = title
            self.empty_text = empty_text
            self.update()

        def set_theme(self, theme: str) -> None:
            self.theme = theme
            self.update()

        def set_image(self, image: Image.Image | None) -> None:
            self.image = image.copy() if image is not None else None
            self.update()

        @staticmethod
        def pil_to_qimage(image: Image.Image) -> QImage:
            rgba = image.convert("RGBA")
            data = rgba.tobytes("raw", "RGBA")
            qimage = QImage(data, rgba.width, rgba.height, rgba.width * 4, QImage.Format.Format_RGBA8888)
            return qimage.copy()

        def paintEvent(self, event) -> None:  # noqa: N802
            del event
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            if self.theme == "light":
                bg_color = QColor(255, 255, 255, 245)
                border_color = QColor(223, 228, 234)
                title_color = QColor(17, 24, 39)
                empty_color = QColor(107, 114, 128)
                panel_bg = QColor(248, 250, 252)
            else:
                bg_color = QColor(20, 25, 31, 238)
                border_color = QColor(255, 255, 255, 34)
                title_color = QColor(248, 250, 252)
                empty_color = QColor(203, 213, 225)
                panel_bg = QColor(15, 23, 32, 238)

            outer = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
            painter.fillRect(outer, bg_color)
            painter.setPen(QPen(border_color, 1))
            painter.drawRoundedRect(outer, 8, 8)
            margin = 18
            painter.setFont(QFont("Microsoft YaHei UI", 16, QFont.Weight.Bold))
            painter.setPen(title_color)
            painter.drawText(QRectF(margin, 14, self.width() - margin * 2, 30), Qt.AlignmentFlag.AlignLeft, self.title)

            panel = QRectF(margin, 58, self.width() - margin * 2, self.height() - 76)
            painter.fillRect(panel, panel_bg)
            painter.setPen(QPen(border_color, 1))
            painter.drawRect(panel)

            if self.image is None:
                painter.setFont(QFont("Microsoft YaHei UI", 11))
                painter.setPen(empty_color)
                painter.drawText(panel, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.empty_text)
                return

            qimage = self.pil_to_qimage(self.image)
            scale = min(panel.width() / max(1, qimage.width()), panel.height() / max(1, qimage.height()))
            target_w = qimage.width() * scale
            target_h = qimage.height() * scale
            target = QRectF(panel.x() + (panel.width() - target_w) / 2, panel.y() + (panel.height() - target_h) / 2, target_w, target_h)
            painter.drawImage(target, qimage)


    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.language = "zh"
            self.theme = "light"
            self.image_path: Path | None = None
            self.matrix: list[list[RGB]] = []
            self.manual_matrix: list[list[RGB]] = blank_matrix(16, 16)
            self.animation_frames: list[list[list[RGB]]] = []
            self.animation_cache_key: tuple[object, ...] | None = None
            self.brush_color = DEFAULT_BRUSH_COLOR
            self.setMinimumSize(1040, 620)
            self.setStyleSheet(LIGHT_STYLE)

            self.refresh_timer = QTimer(self)
            self.refresh_timer.setSingleShot(True)
            self.refresh_timer.timeout.connect(self.refresh_matrix)
            self.play_timer = QTimer(self)
            self.play_timer.timeout.connect(self.advance_animation_frame)

            self.preview = MatrixPreview()
            self.source_preview = SourcePreview()
            self.preview.set_edit_callback(self.paint_manual_pixel)
            self.rows_spin = QSpinBox()
            self.rows_spin.setRange(1, 128)
            self.rows_spin.setValue(16)
            self.cols_spin = QSpinBox()
            self.cols_spin.setRange(1, 128)
            self.cols_spin.setValue(16)

            self.layout_combo = QComboBox()
            for key in UI_LAYOUT_KEYS:
                self.layout_combo.addItem("", key)

            self.origin_combo = QComboBox()
            for key in UI_ORIGIN_KEYS:
                self.origin_combo.addItem("", key)

            self.first_line_combo = QComboBox()
            self.first_line_combo.addItem("", False)
            self.first_line_combo.addItem("", True)

            self.resample_combo = QComboBox()
            self.resample_combo.addItem("", "lanczos")
            self.resample_combo.addItem("", "nearest")
            self.mode_combo = QComboBox()
            for key in UI_MODE_KEYS:
                self.mode_combo.addItem("", key)
            self.rotation_combo = QComboBox()
            for degrees in UI_ROTATION_KEYS:
                self.rotation_combo.addItem("", degrees)

            self.svg_background_color = DEFAULT_SVG_BACKGROUND
            self.svg_cut_color = DEFAULT_SVG_CUT_COLOR
            self.svg_main_color = DEFAULT_SVG_COLOR
            self.svg_cut_combo = QComboBox()
            self.svg_cut_combo.addItem("", SVG_CUT_AUTO)
            self.svg_cut_combo.addItem("", SVG_CUT_COLOR)
            self.svg_cut_combo.addItem("", SVG_CUT_ALPHA)
            self.svg_cut_button = QPushButton()
            self.svg_cut_button.setObjectName("ColorButton")
            self.svg_cut_tolerance_spin = QSpinBox()
            self.svg_cut_tolerance_spin.setRange(0, 255)
            self.svg_cut_tolerance_spin.setValue(DEFAULT_SVG_CUT_TOLERANCE)
            self.svg_background_combo = QComboBox()
            self.svg_background_combo.addItem("", SVG_BG_TRANSPARENT)
            self.svg_background_combo.addItem("", SVG_BG_COLOR)
            self.svg_color_combo = QComboBox()
            self.svg_color_combo.addItem("", SVG_COLOR_ORIGINAL)
            self.svg_color_combo.addItem("", SVG_COLOR_PALETTE)
            self.svg_color_combo.setCurrentIndex(1)
            self.svg_background_button = QPushButton()
            self.svg_background_button.setObjectName("ColorButton")
            self.svg_main_color_button = QPushButton()
            self.svg_main_color_button.setObjectName("ColorButton")
            self.brush_color_button = QPushButton()
            self.brush_color_button.setObjectName("ColorButton")
            self.fill_button = QPushButton()
            self.clear_button = QPushButton()
            self.text_edit = QLineEdit("文本")
            self.font_combo = QComboBox()
            for name, path in FONT_CHOICES.items():
                self.font_combo.addItem(name, path)
            self.font_edit = QLineEdit(FONT_CHOICES["Microsoft YaHei"])
            self.text_scale_spin = QSpinBox()
            self.text_scale_spin.setRange(20, 400)
            self.text_scale_spin.setValue(100)
            self.frame_index_spin = QSpinBox()
            self.frame_index_spin.setRange(0, 0)
            self.frame_index_spin.setValue(0)
            self.max_frames_spin = QSpinBox()
            self.max_frames_spin.setRange(1, 512)
            self.max_frames_spin.setValue(16)
            self.frame_step_spin = QSpinBox()
            self.frame_step_spin.setRange(1, 240)
            self.frame_step_spin.setValue(1)
            self.frame_delay_spin = QSpinBox()
            self.frame_delay_spin.setRange(1, 10000)
            self.frame_delay_spin.setValue(100)
            self.play_button = QPushButton()
            self.play_button.setCheckable(True)

            self.array_name_edit = QLineEdit("ws2812_image_16x16")
            self.language_combo = QComboBox()
            self.language_combo.addItem("中文", "zh")
            self.language_combo.addItem("English", "en")
            self.dark_theme_button = QPushButton()
            self.dark_theme_button.setObjectName("ThemeButton")
            self.dark_theme_button.setCheckable(True)
            self.light_theme_button = QPushButton()
            self.light_theme_button.setObjectName("ThemeButton")
            self.light_theme_button.setCheckable(True)

            self.title_label = QLabel()
            self.title_label.setObjectName("TitleLabel")
            self.subtitle_label = QLabel()
            self.subtitle_label.setObjectName("SubtitleLabel")
            self.language_label = QLabel()
            self.language_label.setObjectName("PanelCaption")
            self.theme_label = QLabel()
            self.theme_label.setObjectName("PanelCaption")
            self.panel_caption = QLabel()
            self.panel_caption.setObjectName("PanelCaption")
            self.status_label = QLabel()
            self.status_label.setObjectName("StatusLabel")
            self.status_label.setWordWrap(True)

            self.size_name_label = QLabel()
            self.size_value_label = QLabel()
            self.led_name_label = QLabel()
            self.led_value_label = QLabel()
            self.layout_name_label = QLabel()
            self.layout_value_label = QLabel()
            for label in (self.size_name_label, self.led_name_label, self.layout_name_label):
                label.setObjectName("MetricName")
            for label in (self.size_value_label, self.led_value_label, self.layout_value_label):
                label.setObjectName("MetricValue")

            self.rows_label = QLabel()
            self.cols_label = QLabel()
            self.mode_label = QLabel()
            self.layout_label = QLabel()
            self.origin_label = QLabel()
            self.first_line_label = QLabel()
            self.resize_label = QLabel()
            self.rotation_label = QLabel()
            self.array_name_label = QLabel()
            self.manual_caption_label = QLabel()
            self.manual_caption_label.setObjectName("PanelCaption")
            self.animation_caption_label = QLabel()
            self.animation_caption_label.setObjectName("PanelCaption")
            self.brush_color_label = QLabel()
            self.text_input_label = QLabel()
            self.text_font_label = QLabel()
            self.custom_font_label = QLabel()
            self.text_scale_label = QLabel()
            self.frame_index_label = QLabel()
            self.max_frames_label = QLabel()
            self.frame_step_label = QLabel()
            self.frame_delay_label = QLabel()
            self.svg_caption_label = QLabel()
            self.svg_caption_label.setObjectName("PanelCaption")
            self.svg_cut_mode_label = QLabel()
            self.svg_cut_color_label = QLabel()
            self.svg_cut_tolerance_label = QLabel()
            self.svg_background_mode_label = QLabel()
            self.svg_background_color_label = QLabel()
            self.svg_color_mode_label = QLabel()
            self.svg_main_color_label = QLabel()
            self.open_button = QPushButton()
            self.export_button = QPushButton()
            self.export_button.setObjectName("PrimaryButton")

            self.open_button.clicked.connect(self.open_image)
            self.export_button.clicked.connect(self.export_file)
            self.language_combo.currentIndexChanged.connect(self.change_language)
            self.dark_theme_button.clicked.connect(lambda: self.change_theme("dark"))
            self.light_theme_button.clicked.connect(lambda: self.change_theme("light"))
            self.svg_cut_button.clicked.connect(self.choose_cut_color)
            self.svg_background_button.clicked.connect(self.choose_background_color)
            self.svg_main_color_button.clicked.connect(self.choose_main_color)
            self.brush_color_button.clicked.connect(self.choose_brush_color)
            self.fill_button.clicked.connect(self.fill_manual_matrix)
            self.clear_button.clicked.connect(self.clear_manual_matrix)
            self.play_button.clicked.connect(self.toggle_animation_playback)

            self.root = TechBackground()
            root_layout = QVBoxLayout(self.root)
            root_layout.setContentsMargins(16, 16, 16, 16)
            root_layout.setSpacing(12)
            self.mode_sections: dict[str, list[QWidget]] = {}

            header = QFrame()
            header.setObjectName("HeaderGlass")
            add_glass_shadow(header)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(20, 14, 20, 14)
            header_layout.setSpacing(18)

            title_box = QVBoxLayout()
            title_box.setSpacing(2)
            title_box.addWidget(self.title_label)
            title_box.addWidget(self.subtitle_label)
            header_layout.addLayout(title_box, 1)

            language_box = QHBoxLayout()
            language_box.setSpacing(8)
            language_box.addWidget(self.theme_label)
            language_box.addWidget(self.dark_theme_button)
            language_box.addWidget(self.light_theme_button)
            language_box.addWidget(self.language_label)
            language_box.addWidget(self.language_combo)
            header_layout.addLayout(language_box)
            root_layout.addWidget(header)

            body_splitter = QSplitter(Qt.Orientation.Horizontal)
            body_splitter.setChildrenCollapsible(False)
            body_splitter.setHandleWidth(8)
            root_layout.addWidget(body_splitter, 1)

            controls = QFrame()
            controls.setObjectName("ControlsGlass")
            add_glass_shadow(controls)
            controls.setMinimumWidth(300)
            controls_layout = QVBoxLayout(controls)
            controls_layout.setContentsMargins(16, 16, 16, 16)
            controls_layout.setSpacing(12)
            controls_layout.addWidget(self.panel_caption)

            form = QFormLayout()
            form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
            form.setVerticalSpacing(10)
            form.setHorizontalSpacing(12)
            form.addRow(self.mode_label, self.mode_combo)
            form.addRow(self.rows_label, self.rows_spin)
            form.addRow(self.cols_label, self.cols_spin)
            form.addRow(self.array_name_label, self.array_name_edit)
            controls_layout.addLayout(form)

            mapping_box = QFrame()
            mapping_box.setObjectName("SectionFrame")
            mapping_layout = QFormLayout(mapping_box)
            mapping_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            mapping_layout.setVerticalSpacing(10)
            mapping_layout.setHorizontalSpacing(12)
            mapping_layout.addRow(self.layout_label, self.layout_combo)
            mapping_layout.addRow(self.origin_label, self.origin_combo)
            mapping_layout.addRow(self.first_line_label, self.first_line_combo)
            controls_layout.addWidget(mapping_box)

            image_box = QFrame()
            image_box.setObjectName("SectionFrame")
            image_layout = QFormLayout(image_box)
            image_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            image_layout.setVerticalSpacing(10)
            image_layout.setHorizontalSpacing(12)
            image_layout.addRow(self.resize_label, self.resample_combo)
            image_layout.addRow(self.rotation_label, self.rotation_combo)
            controls_layout.addWidget(image_box)

            manual_box = QFrame()
            manual_box.setObjectName("SectionFrame")
            manual_box_layout = QVBoxLayout(manual_box)
            manual_box_layout.setContentsMargins(0, 0, 0, 0)
            manual_box_layout.setSpacing(10)
            manual_form = QFormLayout()
            manual_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            manual_form.setVerticalSpacing(10)
            manual_form.setHorizontalSpacing(12)
            manual_form.addRow(self.brush_color_label, self.brush_color_button)
            manual_form.addRow(self.text_input_label, self.text_edit)
            manual_form.addRow(self.text_font_label, self.font_combo)
            manual_form.addRow(self.custom_font_label, self.font_edit)
            manual_form.addRow(self.text_scale_label, self.text_scale_spin)
            button_row = QHBoxLayout()
            button_row.addWidget(self.fill_button)
            button_row.addWidget(self.clear_button)
            manual_box_layout.addWidget(self.manual_caption_label)
            manual_box_layout.addLayout(manual_form)
            manual_box_layout.addLayout(button_row)
            controls_layout.addWidget(manual_box)

            animation_box = QFrame()
            animation_box.setObjectName("SectionFrame")
            animation_box_layout = QVBoxLayout(animation_box)
            animation_box_layout.setContentsMargins(0, 0, 0, 0)
            animation_box_layout.setSpacing(10)
            animation_form = QFormLayout()
            animation_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            animation_form.setVerticalSpacing(10)
            animation_form.setHorizontalSpacing(12)
            animation_form.addRow(self.frame_index_label, self.frame_index_spin)
            animation_form.addRow(self.max_frames_label, self.max_frames_spin)
            animation_form.addRow(self.frame_step_label, self.frame_step_spin)
            animation_form.addRow(self.frame_delay_label, self.frame_delay_spin)
            animation_box_layout.addWidget(self.animation_caption_label)
            animation_box_layout.addLayout(animation_form)
            animation_box_layout.addWidget(self.play_button)
            controls_layout.addWidget(animation_box)

            svg_box = QFrame()
            svg_box.setObjectName("SectionFrame")
            svg_box_layout = QVBoxLayout(svg_box)
            svg_box_layout.setContentsMargins(0, 0, 0, 0)
            svg_box_layout.setSpacing(10)
            svg_form = QFormLayout()
            svg_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
            svg_form.setVerticalSpacing(10)
            svg_form.setHorizontalSpacing(12)
            svg_form.addRow(self.svg_cut_mode_label, self.svg_cut_combo)
            svg_form.addRow(self.svg_cut_color_label, self.svg_cut_button)
            svg_form.addRow(self.svg_cut_tolerance_label, self.svg_cut_tolerance_spin)
            svg_form.addRow(self.svg_background_mode_label, self.svg_background_combo)
            svg_form.addRow(self.svg_background_color_label, self.svg_background_button)
            svg_form.addRow(self.svg_color_mode_label, self.svg_color_combo)
            svg_form.addRow(self.svg_main_color_label, self.svg_main_color_button)
            svg_box_layout.addWidget(self.svg_caption_label)
            svg_box_layout.addLayout(svg_form)
            controls_layout.addWidget(svg_box)

            self.mode_sections = {
                MODE_IMAGE: [mapping_box, image_box, svg_box, self.open_button],
                MODE_ANIMATION: [mapping_box, image_box, svg_box, animation_box, self.open_button],
                MODE_TEXT: [mapping_box, image_box, svg_box, manual_box],
                MODE_MANUAL: [mapping_box, manual_box],
            }
            self.resize_widgets = [self.resize_label, self.resample_combo]
            self.text_widgets = [
                self.text_input_label,
                self.text_edit,
                self.text_font_label,
                self.font_combo,
                self.custom_font_label,
                self.font_edit,
                self.text_scale_label,
                self.text_scale_spin,
            ]
            self.manual_widgets = [self.fill_button, self.clear_button]
            self.cutout_widgets = [
                self.svg_cut_mode_label,
                self.svg_cut_combo,
                self.svg_cut_color_label,
                self.svg_cut_button,
                self.svg_cut_tolerance_label,
                self.svg_cut_tolerance_spin,
                self.svg_color_mode_label,
                self.svg_color_combo,
                self.svg_main_color_label,
                self.svg_main_color_button,
            ]

            controls_layout.addWidget(self.open_button)
            controls_layout.addWidget(self.export_button)
            controls_layout.addSpacing(4)
            controls_layout.addWidget(self.status_label)

            controls_scroll = QScrollArea()
            controls_scroll.setObjectName("ControlsScroll")
            controls_scroll.setWidgetResizable(True)
            controls_scroll.setFrameShape(QFrame.Shape.NoFrame)
            controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            controls_scroll.setMinimumWidth(220)
            controls_scroll.setWidget(controls)
            body_splitter.addWidget(controls_scroll)

            self.source_panel = QFrame()
            self.source_panel.setObjectName("PreviewGlass")
            self.source_panel.setMinimumWidth(240)
            add_glass_shadow(self.source_panel)
            source_layout = QVBoxLayout(self.source_panel)
            source_layout.setContentsMargins(14, 14, 14, 14)
            source_layout.addWidget(self.source_preview, 1)
            body_splitter.addWidget(self.source_panel)

            preview_panel = QFrame()
            preview_panel.setObjectName("PreviewGlass")
            preview_panel.setMinimumWidth(280)
            add_glass_shadow(preview_panel)
            preview_layout = QVBoxLayout(preview_panel)
            preview_layout.setContentsMargins(14, 14, 14, 14)
            preview_layout.setSpacing(12)

            metrics = QHBoxLayout()
            metrics.setSpacing(28)
            metrics.addLayout(self.metric_block(self.size_name_label, self.size_value_label))
            metrics.addLayout(self.metric_block(self.led_name_label, self.led_value_label))
            metrics.addLayout(self.metric_block(self.layout_name_label, self.layout_value_label))
            metrics.addStretch(1)
            preview_layout.addLayout(metrics)
            preview_layout.addWidget(self.preview, 1)
            body_splitter.addWidget(preview_panel)
            body_splitter.setStretchFactor(0, 0)
            body_splitter.setStretchFactor(1, 1)
            body_splitter.setStretchFactor(2, 1)
            body_splitter.setSizes([320, 430, 530])

            self.setCentralWidget(self.root)

            reload_action = QAction("Reload", self)
            reload_action.triggered.connect(self.refresh_matrix)
            self.addAction(reload_action)

            for widget in (
                self.mode_combo,
                self.rows_spin,
                self.cols_spin,
                self.layout_combo,
                self.origin_combo,
                self.first_line_combo,
                self.resample_combo,
                self.rotation_combo,
                self.svg_cut_combo,
                self.svg_cut_tolerance_spin,
                self.svg_background_combo,
                self.svg_color_combo,
                self.text_scale_spin,
                self.max_frames_spin,
                self.frame_step_spin,
            ):
                if isinstance(widget, QSpinBox):
                    widget.valueChanged.connect(self.schedule_refresh)
                else:
                    widget.currentIndexChanged.connect(self.schedule_refresh)
            self.frame_index_spin.valueChanged.connect(self.handle_frame_index_changed)
            self.frame_delay_spin.valueChanged.connect(self.update_play_timer_delay)
            self.text_edit.textChanged.connect(self.schedule_refresh)
            self.font_combo.currentIndexChanged.connect(self.change_font_choice)
            self.font_edit.textChanged.connect(self.schedule_refresh)

            self.apply_language()
            self.apply_theme()
            self.refresh_matrix()

        @staticmethod
        def metric_block(name_label: QLabel, value_label: QLabel) -> QVBoxLayout:
            layout = QVBoxLayout()
            layout.setSpacing(2)
            layout.addWidget(name_label)
            layout.addWidget(value_label)
            return layout

        @staticmethod
        def set_widgets_visible(widgets: Iterable[QWidget], visible: bool) -> None:
            for widget in widgets:
                widget.setVisible(visible)

        def update_mode_sections(self) -> None:
            mode = self.mode_combo.currentData()
            section_set = {section for sections in self.mode_sections.values() for section in sections}
            for section in section_set:
                section.setVisible(False)
            for section in self.mode_sections.get(mode, []):
                section.setVisible(True)

            image_mode = mode in (MODE_IMAGE, MODE_ANIMATION)
            text_mode = mode == MODE_TEXT
            manual_mode = mode == MODE_MANUAL

            self.set_widgets_visible(self.resize_widgets, image_mode)
            self.set_widgets_visible(self.text_widgets, text_mode)
            self.set_widgets_visible(self.manual_widgets, manual_mode)
            self.set_widgets_visible(self.cutout_widgets, image_mode)
            self.source_preview.setVisible(image_mode)
            self.source_panel.setVisible(image_mode)
            self.play_button.setVisible(mode == MODE_ANIMATION)

            if mode == MODE_ANIMATION:
                self.open_button.setText(self.text("open_media"))
            else:
                self.open_button.setText(self.text("open_image"))
            if text_mode:
                self.manual_caption_label.setText(self.text("text_settings"))
                self.svg_caption_label.setText(self.text("text_background"))
            elif manual_mode:
                self.manual_caption_label.setText(self.text("manual_settings"))
            else:
                self.manual_caption_label.setText(self.text("manual_caption"))
                self.svg_caption_label.setText(self.text("svg_caption"))
            if mode != MODE_ANIMATION and self.play_timer.isActive():
                self.stop_animation_playback()

        def update_source_preview(self) -> None:
            mode = self.mode_combo.currentData()
            if mode not in (MODE_IMAGE, MODE_ANIMATION) or self.image_path is None:
                self.source_preview.set_image(None)
                return
            try:
                image = load_source_preview_image(
                    self.image_path,
                    self.rotation_combo.currentData(),
                    self.frame_index_spin.value(),
                    self.frame_step_spin.value(),
                )
                self.source_preview.set_image(image)
            except Exception:
                self.source_preview.set_image(None)

        def text(self, key: str) -> str:
            return UI_TEXT[self.language][key]

        def set_combo_texts(self, combo: QComboBox, labels: dict[object, str]) -> None:
            current = combo.currentData()
            combo.blockSignals(True)
            for index in range(combo.count()):
                data = combo.itemData(index)
                combo.setItemText(index, labels[data])
            if current is not None:
                for index in range(combo.count()):
                    if combo.itemData(index) == current:
                        combo.setCurrentIndex(index)
                        break
            combo.blockSignals(False)

        def apply_language(self) -> None:
            self.setWindowTitle(self.text("window_title"))
            self.title_label.setText(self.text("title"))
            self.subtitle_label.setText(self.text("subtitle"))
            self.language_label.setText(self.text("language"))
            self.theme_label.setText(self.text("theme"))
            self.dark_theme_button.setText(self.text("theme_dark"))
            self.light_theme_button.setText(self.text("theme_light"))
            self.panel_caption.setText(self.text("panel_settings"))
            self.mode_label.setText(self.text("mode"))
            self.rows_label.setText(self.text("rows"))
            self.cols_label.setText(self.text("cols"))
            self.layout_label.setText(self.text("layout"))
            self.origin_label.setText(self.text("origin"))
            self.first_line_label.setText(self.text("first_line"))
            self.resize_label.setText(self.text("resize"))
            self.rotation_label.setText(self.text("rotation"))
            self.array_name_label.setText(self.text("array_name"))
            self.manual_caption_label.setText(self.text("manual_caption"))
            self.animation_caption_label.setText(self.text("animation_caption"))
            self.brush_color_label.setText(self.text("brush_color"))
            self.fill_button.setText(self.text("fill_all"))
            self.clear_button.setText(self.text("clear_all"))
            self.text_input_label.setText(self.text("text_input"))
            self.text_font_label.setText(self.text("text_font"))
            self.custom_font_label.setText(self.text("custom_font"))
            self.text_scale_label.setText(self.text("text_scale"))
            self.frame_index_label.setText(self.text("frame_index"))
            self.max_frames_label.setText(self.text("max_frames"))
            self.frame_step_label.setText(self.text("frame_step"))
            self.frame_delay_label.setText(self.text("frame_delay"))
            self.svg_caption_label.setText(self.text("svg_caption"))
            self.svg_cut_mode_label.setText(self.text("svg_cut_mode"))
            self.svg_cut_color_label.setText(self.text("svg_cut_color"))
            self.svg_cut_tolerance_label.setText(self.text("svg_cut_tolerance"))
            self.svg_background_mode_label.setText(self.text("svg_bg_mode"))
            self.svg_background_color_label.setText(self.text("svg_bg_color_label"))
            self.svg_color_mode_label.setText(self.text("svg_color_mode"))
            self.svg_main_color_label.setText(self.text("svg_main_color"))
            self.open_button.setText(self.text("open_image"))
            self.export_button.setText(self.text("export_header"))
            self.play_button.setText(self.text("pause_animation") if self.play_button.isChecked() else self.text("play_animation"))
            self.size_name_label.setText(self.text("metric_size"))
            self.led_name_label.setText(self.text("metric_leds"))
            self.layout_name_label.setText(self.text("metric_layout"))
            self.preview.set_language(self.text("empty_preview"), self.text("preview_title"))
            self.source_preview.set_language(self.text("source_preview_title"), self.text("source_preview_empty"))

            self.set_combo_texts(
                self.mode_combo,
                {key: self.text(text_key) for key, text_key in UI_MODE_KEYS.items()},
            )
            self.set_combo_texts(
                self.layout_combo,
                {key: self.text(text_key) for key, text_key in UI_LAYOUT_KEYS.items()},
            )
            self.set_combo_texts(
                self.origin_combo,
                {key: self.text(text_key) for key, text_key in UI_ORIGIN_KEYS.items()},
            )
            self.set_combo_texts(
                self.first_line_combo,
                {
                    False: self.text("first_origin"),
                    True: self.text("first_reverse"),
                },
            )
            self.set_combo_texts(
                self.resample_combo,
                {
                    "lanczos": self.text("resize_lanczos"),
                    "nearest": self.text("resize_nearest"),
                },
            )
            self.set_combo_texts(
                self.rotation_combo,
                {key: self.text(text_key) for key, text_key in UI_ROTATION_KEYS.items()},
            )
            self.set_combo_texts(
                self.svg_cut_combo,
                {
                    SVG_CUT_ALPHA: self.text("svg_cut_alpha"),
                    SVG_CUT_AUTO: self.text("svg_cut_auto"),
                    SVG_CUT_COLOR: self.text("svg_cut_color_key"),
                },
            )
            self.set_combo_texts(
                self.svg_background_combo,
                {
                    SVG_BG_TRANSPARENT: self.text("svg_bg_transparent"),
                    SVG_BG_COLOR: self.text("svg_bg_custom"),
                },
            )
            self.set_combo_texts(
                self.svg_color_combo,
                {
                    SVG_COLOR_ORIGINAL: self.text("svg_color_original"),
                    SVG_COLOR_PALETTE: self.text("svg_color_palette"),
                },
            )
            self.update_color_buttons()
            self.update_mode_sections()
            self.update_status()

        def change_language(self) -> None:
            selected = self.language_combo.currentData()
            if selected in UI_TEXT:
                self.language = selected
                self.apply_language()

        def apply_theme(self) -> None:
            self.setStyleSheet(DARK_STYLE if self.theme == "dark" else LIGHT_STYLE)
            self.root.set_theme(self.theme)
            self.preview.set_theme(self.theme)
            self.source_preview.set_theme(self.theme)
            self.dark_theme_button.setChecked(self.theme == "dark")
            self.light_theme_button.setChecked(self.theme == "light")
            self.update_color_buttons()

        def change_theme(self, selected: str) -> None:
            if selected in ("dark", "light"):
                self.theme = selected
                self.apply_theme()

        def update_color_buttons(self) -> None:
            self.apply_color_button(self.svg_cut_button, self.svg_cut_color)
            self.apply_color_button(self.svg_background_button, self.svg_background_color)
            self.apply_color_button(self.svg_main_color_button, self.svg_main_color)
            self.apply_color_button(self.brush_color_button, self.brush_color)
            self.preview.set_brush_color(self.brush_color)

        def schedule_refresh(self) -> None:
            self.animation_cache_key = None
            self.stop_animation_playback()
            self.status_label.setText(self.text("status_processing"))
            self.refresh_timer.start(120)

        def animation_settings_key(self) -> tuple[object, ...]:
            image_stat = None
            if self.image_path is not None:
                try:
                    resolved = resolve_existing_path(self.image_path)
                    stat = resolved.stat()
                    image_stat = (str(resolved), stat.st_size, int(stat.st_mtime))
                except OSError:
                    image_stat = str(self.image_path)
            return (
                image_stat,
                self.rows_spin.value(),
                self.cols_spin.value(),
                self.resample_combo.currentData(),
                self.rotation_combo.currentData(),
                self.svg_cut_combo.currentData(),
                self.svg_cut_color,
                self.svg_cut_tolerance_spin.value(),
                self.svg_background_combo.currentData(),
                self.svg_background_color,
                self.svg_color_combo.currentData(),
                self.svg_main_color,
                self.max_frames_spin.value(),
                self.frame_step_spin.value(),
            )

        def set_current_animation_frame(self) -> None:
            if not self.animation_frames:
                return
            index = min(self.frame_index_spin.value(), len(self.animation_frames) - 1)
            self.matrix = self.animation_frames[index]
            self.preview.set_editable(False)
            self.preview.set_data(self.matrix, self.current_order())
            self.update_source_preview()
            self.update_status()

        def handle_frame_index_changed(self) -> None:
            if self.mode_combo.currentData() == MODE_ANIMATION and self.animation_frames:
                self.set_current_animation_frame()
            else:
                self.schedule_refresh()

        def update_play_timer_delay(self) -> None:
            if self.play_timer.isActive():
                self.play_timer.setInterval(self.frame_delay_spin.value())

        def stop_animation_playback(self) -> None:
            if self.play_timer.isActive():
                self.play_timer.stop()
            if self.play_button.isChecked():
                self.play_button.blockSignals(True)
                self.play_button.setChecked(False)
                self.play_button.blockSignals(False)
            self.play_button.setText(self.text("play_animation"))

        def toggle_animation_playback(self) -> None:
            if self.play_button.isChecked():
                if self.mode_combo.currentData() != MODE_ANIMATION:
                    self.stop_animation_playback()
                    return
                if not self.animation_frames:
                    self.refresh_matrix()
                if len(self.animation_frames) <= 1:
                    self.stop_animation_playback()
                    return
                self.play_button.setText(self.text("pause_animation"))
                self.play_timer.start(self.frame_delay_spin.value())
            else:
                self.stop_animation_playback()

        def advance_animation_frame(self) -> None:
            if self.mode_combo.currentData() != MODE_ANIMATION or not self.animation_frames:
                self.stop_animation_playback()
                return
            next_index = (self.frame_index_spin.value() + 1) % len(self.animation_frames)
            self.frame_index_spin.setValue(next_index)

        @staticmethod
        def apply_color_button(button: QPushButton, color: RGB) -> None:
            text_color = "#03131E" if (color[0] * 299 + color[1] * 587 + color[2] * 114) > 150000 else "#F4FBFF"
            button.setText(rgb_to_hex(color))
            button.setStyleSheet(
                "QPushButton#ColorButton {"
                f"background-color: {rgb_to_hex(color)};"
                f"color: {text_color};"
                "border: 1px solid rgba(17, 24, 39, 70);"
                "border-radius: 6px;"
                "padding: 6px 8px;"
                "font-family: Consolas, Microsoft YaHei UI;"
                "}"
            )

        def choose_color(self, current: RGB) -> RGB | None:
            dialog = QColorDialog(QColor(*current), self)
            dialog.setWindowTitle(self.text("choose_color"))
            dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
            dialog.setStyleSheet(DARK_STYLE if self.theme == "dark" else LIGHT_STYLE)
            if dialog.exec():
                selected = dialog.currentColor()
                if selected.isValid():
                    return selected.red(), selected.green(), selected.blue()
            return None

        def choose_background_color(self) -> None:
            selected = self.choose_color(self.svg_background_color)
            if selected is not None:
                self.svg_background_color = selected
                self.update_color_buttons()
                self.refresh_matrix()

        def choose_cut_color(self) -> None:
            selected = self.choose_color(self.svg_cut_color)
            if selected is not None:
                self.svg_cut_color = selected
                self.update_color_buttons()
                self.refresh_matrix()

        def choose_main_color(self) -> None:
            selected = self.choose_color(self.svg_main_color)
            if selected is not None:
                self.svg_main_color = selected
                self.update_color_buttons()
                self.refresh_matrix()

        def choose_brush_color(self) -> None:
            selected = self.choose_color(self.brush_color)
            if selected is not None:
                self.brush_color = selected
                self.update_color_buttons()

        def change_font_choice(self) -> None:
            path = self.font_combo.currentData()
            if path:
                self.font_edit.blockSignals(True)
                self.font_edit.setText(path)
                self.font_edit.blockSignals(False)
            self.schedule_refresh()

        def ensure_manual_matrix_size(self) -> None:
            rows = self.rows_spin.value()
            cols = self.cols_spin.value()
            self.manual_matrix = resize_matrix(self.manual_matrix, rows, cols)

        def paint_manual_pixel(self, x: int, y: int, color: RGB) -> None:
            if self.mode_combo.currentData() != MODE_MANUAL:
                return
            self.ensure_manual_matrix_size()
            self.manual_matrix[y][x] = normalize_rgb(color)
            self.matrix = self.manual_matrix
            self.preview.set_data(self.matrix, self.current_order())
            self.update_status()

        def fill_manual_matrix(self) -> None:
            self.manual_matrix = blank_matrix(self.rows_spin.value(), self.cols_spin.value(), self.brush_color)
            if self.mode_combo.currentData() == MODE_MANUAL:
                self.refresh_matrix()

        def clear_manual_matrix(self) -> None:
            self.manual_matrix = blank_matrix(self.rows_spin.value(), self.cols_spin.value(), (0, 0, 0))
            if self.mode_combo.currentData() == MODE_MANUAL:
                self.refresh_matrix()

        def current_order(self) -> list[Coord]:
            return physical_order(
                self.rows_spin.value(),
                self.cols_spin.value(),
                self.layout_combo.currentData(),
                self.origin_combo.currentData(),
                bool(self.first_line_combo.currentData()),
            )

        def update_status(self, exported_name: str | None = None) -> None:
            rows = self.rows_spin.value()
            cols = self.cols_spin.value()
            size = f"{cols} x {rows}"
            leds = f"{cols * rows}"
            layout_text = self.layout_combo.currentText()
            image_text = self.text("status_default") if self.image_path is None else self.image_path.name
            if self.mode_combo.currentData() == MODE_ANIMATION and self.animation_frames:
                image_text = f"{image_text}  |  {len(self.animation_frames)} frames"

            self.size_value_label.setText(size)
            self.led_value_label.setText(leds)
            self.layout_value_label.setText(layout_text)

            if exported_name:
                self.status_label.setText(f"{self.text('status_exported')}: {exported_name}")
            else:
                self.status_label.setText(f"{self.text('status_ready')}  |  {size}  |  {leds} LEDs  |  {image_text}")

        def refresh_matrix(self) -> None:
            self.refresh_timer.stop()
            rows = self.rows_spin.value()
            cols = self.cols_spin.value()
            mode = self.mode_combo.currentData()
            self.update_mode_sections()
            try:
                self.ensure_manual_matrix_size()
                if mode == MODE_MANUAL:
                    self.matrix = self.manual_matrix
                elif mode == MODE_TEXT:
                    self.matrix = render_text_matrix(
                        self.text_edit.text(),
                        rows,
                        cols,
                        self.font_edit.text(),
                        self.rotation_combo.currentData(),
                        self.text_scale_spin.value(),
                        self.brush_color,
                        self.svg_background_combo.currentData(),
                        self.svg_background_color,
                    )
                elif mode == MODE_ANIMATION:
                    cache_key = self.animation_settings_key()
                    if self.animation_frames and self.animation_cache_key == cache_key:
                        pass
                    elif self.image_path is None:
                        self.animation_frames = [default_matrix(rows, cols)]
                        self.animation_cache_key = cache_key
                    else:
                        self.animation_frames = load_animation_frames(
                            self.image_path,
                            rows,
                            cols,
                            self.resample_combo.currentData(),
                            self.rotation_combo.currentData(),
                            self.svg_cut_combo.currentData(),
                            self.svg_cut_color,
                            self.svg_cut_tolerance_spin.value(),
                            self.svg_background_combo.currentData(),
                            self.svg_background_color,
                            self.svg_color_combo.currentData(),
                            self.svg_main_color,
                            self.max_frames_spin.value(),
                            self.frame_step_spin.value(),
                        )
                        self.animation_cache_key = cache_key
                    max_index = max(0, len(self.animation_frames) - 1)
                    self.frame_index_spin.blockSignals(True)
                    self.frame_index_spin.setRange(0, max_index)
                    self.frame_index_spin.setValue(min(self.frame_index_spin.value(), max_index))
                    self.frame_index_spin.blockSignals(False)
                    self.matrix = self.animation_frames[self.frame_index_spin.value()]
                elif self.image_path is None:
                    self.matrix = default_matrix(rows, cols)
                else:
                    self.matrix = load_image_matrix(
                        self.image_path,
                        rows,
                        cols,
                        self.resample_combo.currentData(),
                        self.rotation_combo.currentData(),
                        self.svg_cut_combo.currentData(),
                        self.svg_cut_color,
                        self.svg_cut_tolerance_spin.value(),
                        self.svg_background_combo.currentData(),
                        self.svg_background_color,
                        self.svg_color_combo.currentData(),
                        self.svg_main_color,
                    )
                self.preview.set_editable(mode == MODE_MANUAL)
                self.preview.set_data(self.matrix, self.current_order())
                self.update_source_preview()
                self.update_status()
            except Exception as exc:  # pragma: no cover - UI error path
                QMessageBox.critical(self, self.text("image_error"), str(exc))

        def open_image(self) -> None:
            mode = self.mode_combo.currentData()
            file_filter = (
                self.text("dialog_images") + ";;GIF/Video (*.gif *.mp4 *.avi *.mov *.mkv *.webm *.wmv)"
                if mode == MODE_ANIMATION
                else self.text("dialog_images")
            )
            selected, _ = QFileDialog.getOpenFileName(
                self,
                self.text("dialog_open"),
                "",
                file_filter,
            )
            if selected:
                self.image_path = Path(selected)
                self.animation_cache_key = None
                self.stop_animation_playback()
                self.refresh_matrix()

        def default_export_path(self) -> str:
            desktop = Path.home() / "Desktop"
            f072_header = desktop / "F072" / "Core" / "Inc" / "ws2812_image_16x16.h"
            if f072_header.parent.exists():
                return str(f072_header)
            return str(Path.cwd() / "ws2812_image_16x16.h")

        def current_animation_frames(self) -> list[list[list[RGB]]]:
            if self.mode_combo.currentData() == MODE_ANIMATION:
                if not self.animation_frames:
                    self.refresh_matrix()
                return self.animation_frames
            return []

        def export_file(self) -> None:
            selected, _ = QFileDialog.getSaveFileName(
                self,
                self.text("dialog_export"),
                self.default_export_path(),
                self.text("dialog_header"),
            )
            if not selected:
                return

            try:
                if self.mode_combo.currentData() == MODE_ANIMATION:
                    text = export_animation_header(
                        self.current_animation_frames(),
                        self.current_order(),
                        self.array_name_edit.text().strip(),
                        self.layout_combo.currentData(),
                        self.origin_combo.currentData(),
                        bool(self.first_line_combo.currentData()),
                        self.frame_delay_spin.value(),
                    )
                else:
                    text = export_header(
                        self.matrix,
                        self.current_order(),
                        self.array_name_edit.text().strip(),
                        self.layout_combo.currentData(),
                        self.origin_combo.currentData(),
                        bool(self.first_line_combo.currentData()),
                    )
                output_path = Path(selected)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(text, encoding="utf-8")
                self.update_status(output_path.name)
            except Exception as exc:  # pragma: no cover - UI error path
                QMessageBox.critical(self, self.text("export_error"), str(exc))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert images to WS2812 C arrays")
    parser.add_argument("--export", type=Path, help="Export header path without opening the GUI")
    parser.add_argument("--image", type=Path, help="Input image path for CLI export")
    parser.add_argument("--animation", action="store_true", help="Export GIF/video as a multi-frame C array")
    parser.add_argument("--rows", type=int, default=16)
    parser.add_argument("--cols", type=int, default=16)
    parser.add_argument("--layout", choices=sorted(LAYOUT_LABELS), default=LAYOUT_ROW_ZIGZAG)
    parser.add_argument("--origin", choices=sorted(ORIGIN_LABELS), default=ORIGIN_TOP_LEFT)
    parser.add_argument("--reverse-first-line", action="store_true")
    parser.add_argument("--array-name", default="ws2812_image_16x16")
    parser.add_argument("--resize", choices=("lanczos", "nearest"), default="lanczos")
    parser.add_argument("--rotation", type=int, choices=(0, 90, 180, 270), default=0)
    parser.add_argument("--cut-mode", "--svg-cut-mode", dest="cut_mode", choices=(SVG_CUT_ALPHA, SVG_CUT_AUTO, SVG_CUT_COLOR), default=SVG_CUT_AUTO)
    parser.add_argument("--cut-color", "--svg-cut-color", dest="cut_color", default=rgb_to_hex(DEFAULT_SVG_CUT_COLOR), help="Key color in #RRGGBB")
    parser.add_argument("--cut-tolerance", "--svg-cut-tolerance", dest="cut_tolerance", type=int, default=DEFAULT_SVG_CUT_TOLERANCE)
    parser.add_argument("--bg-mode", "--svg-bg-mode", dest="bg_mode", choices=(SVG_BG_TRANSPARENT, SVG_BG_COLOR), default=SVG_BG_TRANSPARENT)
    parser.add_argument("--bg-color", "--svg-bg-color", dest="bg_color", default=rgb_to_hex(DEFAULT_SVG_BACKGROUND), help="Output background color in #RRGGBB")
    parser.add_argument("--color-mode", "--svg-color-mode", dest="color_mode", choices=(SVG_COLOR_ORIGINAL, SVG_COLOR_PALETTE), default=SVG_COLOR_ORIGINAL)
    parser.add_argument("--main-color", "--svg-main-color", dest="main_color", default=rgb_to_hex(DEFAULT_SVG_COLOR), help="Main palette color in #RRGGBB")
    parser.add_argument("--max-frames", type=int, default=16)
    parser.add_argument("--frame-step", type=int, default=1)
    parser.add_argument("--frame-delay", type=int, default=100)
    return parser.parse_args(argv)


def run_cli(args: argparse.Namespace) -> int:
    if args.rows <= 0 or args.cols <= 0:
        raise ValueError("Rows and columns must be positive")

    image_path = resolve_existing_path(args.image) if args.image else None
    order = physical_order(args.rows, args.cols, args.layout, args.origin, args.reverse_first_line)
    if args.animation:
        frames = (
            load_animation_frames(
                image_path,
                args.rows,
                args.cols,
                args.resize,
                args.rotation,
                args.cut_mode,
                parse_hex_rgb(args.cut_color),
                args.cut_tolerance,
                args.bg_mode,
                parse_hex_rgb(args.bg_color),
                args.color_mode,
                parse_hex_rgb(args.main_color),
                args.max_frames,
                args.frame_step,
            )
            if image_path
            else [default_matrix(args.rows, args.cols)]
        )
        text = export_animation_header(
            frames,
            order,
            args.array_name,
            args.layout,
            args.origin,
            args.reverse_first_line,
            args.frame_delay,
        )
    else:
        matrix = (
            load_image_matrix(
                image_path,
                args.rows,
                args.cols,
                args.resize,
                args.rotation,
                args.cut_mode,
                parse_hex_rgb(args.cut_color),
                args.cut_tolerance,
                args.bg_mode,
                parse_hex_rgb(args.bg_color),
                args.color_mode,
                parse_hex_rgb(args.main_color),
            )
            if image_path
            else default_matrix(args.rows, args.cols)
        )
        text = export_header(matrix, order, args.array_name, args.layout, args.origin, args.reverse_first_line)
    args.export.parent.mkdir(parents=True, exist_ok=True)
    args.export.write_text(text, encoding="utf-8")
    return 0


def run_gui(argv: list[str]) -> int:
    if Qt is None:
        raise RuntimeError("PyQt6 is not installed. Run: py -3.12 -m pip install PyQt6 Pillow")
    app = QApplication(argv)
    for font_path in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        if Path(font_path).exists():
            QFontDatabase.addApplicationFont(font_path)
    app.setFont(QFont("Microsoft YaHei UI", 9))
    icon_path = Path(__file__).resolve().parent / "assets" / "ws2812_logo.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.resize(1280, 760)
    window.show()
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    if args.export:
        return run_cli(args)
    return run_gui(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
