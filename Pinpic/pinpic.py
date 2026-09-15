#!/usr/bin/env python3
"""Pinpic - a tiny cross-platform always-on-top image pin.

Usage::

    python pinpic.py /path/to/image.png

The short-lived launcher detaches the actual Qt process, so closing the
terminal that started Pinpic does not close the pinned image.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

try:
    from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
    from PySide6.QtGui import QColor, QCursor, QImage, QPainter, QPixmap, QIcon, QPolygon
    from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon, QWidget
except ModuleNotFoundError as exc:  # pragma: no cover - depends on the host
    if exc.name != "PySide6":
        raise
    print(
        "Pinpic 缺少 PySide6 依赖。请先运行：\n"
        "  ./install.sh\n"
        "之后使用：\n"
        "  ./.venv/bin/python pinpic.py 图片路径",
        file=sys.stderr,
    )
    raise SystemExit(2)

try:
    from pynput import mouse as pynput_mouse
except Exception:  # pragma: no cover - depends on the desktop session
    pynput_mouse = None


class PinWindow(QWidget):
    """Borderless image window with mouse-only controls."""

    closed = Signal()

    MIN_ZOOM = 0.10
    ZOOM_STEP = 1.15
    OPACITY_STEP = 0.05
    # Only a defensive Qt integer-size guard; there is no normal zoom cap.
    MAX_WIDGET_SIDE = 16_000_000

    def __init__(self, image: QImage) -> None:
        super().__init__()
        self.source = QPixmap.fromImage(image)
        self.zoom = 1.0
        self.base_zoom = 1.0
        self.opacity = 1.0
        self.drag_origin = QPoint()
        self.window_origin = QPoint()
        self.dragging = False
        self.home_size = QSize()
        self.home_position = QPoint()

        self.setWindowTitle("Pinpic")
        self.setWindowIcon(make_tray_icon())
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMouseTracking(True)
        self.setMinimumSize(32, 32)
        self.setWindowOpacity(self.opacity)

        screen = QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else QRect(0, 0, 1280, 720)
        max_w = max(160, int(available.width() * 0.72))
        max_h = max(120, int(available.height() * 0.72))
        scale = min(1.0, max_w / self.source.width(), max_h / self.source.height())
        self.zoom = scale
        self.base_zoom = scale
        self.home_size = self.scaled_size()
        self.resize(self.home_size)
        self.home_position = QPoint(
            available.x() + (available.width() - self.width()) // 2,
            available.y() + (available.height() - self.height()) // 2,
        )
        self.move(self.home_position)

    def scaled_size(self) -> QSize:
        width = max(1, round(self.source.width() * self.zoom))
        height = max(1, round(self.source.height() * self.zoom))
        scale = min(1.0, self.MAX_WIDGET_SIDE / width, self.MAX_WIDGET_SIDE / height)
        return QSize(max(1, round(width * scale)), max(1, round(height * scale)))

    def paintEvent(self, _event) -> None:  # noqa: N802 (Qt API)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), QColor(20, 20, 20))
        painter.drawPixmap(self.rect(), self.source)

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt API)
        if event.button() == Qt.MouseButton.RightButton:
            self.hide()
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self.set_zoom(self.base_zoom, event.globalPosition().toPoint())
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_origin = event.globalPosition().toPoint()
            self.window_origin = self.pos()
            self.grabMouse()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 (Qt API)
        if self.dragging:
            delta = event.globalPosition().toPoint() - self.drag_origin
            self.move(self.window_origin + delta)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 (Qt API)
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.releaseMouse()

    def wheelEvent(self, event) -> None:  # noqa: N802 (Qt API)
        if not event.angleDelta().y():
            return
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            steps = event.angleDelta().y() / 120.0
            self.opacity = max(
                0.15,
                min(1.0, self.opacity + self.OPACITY_STEP * steps),
            )
            self.setWindowOpacity(self.opacity)
            event.accept()
            return
        # Qt's convention is positive = wheel up (zoom in), negative =
        # wheel down (zoom out). Use the actual number of wheel steps.
        steps = event.angleDelta().y() / 120.0
        self.set_zoom(
            self.zoom * (self.ZOOM_STEP ** steps),
            event.globalPosition().toPoint(),
        )

    def set_zoom(self, new_zoom: float, anchor_global: QPoint | None = None) -> None:
        """Resize around an exact global anchor without cumulative drift."""
        old_zoom = self.zoom
        new_zoom = max(self.MIN_ZOOM, float(new_zoom))
        if abs(new_zoom - old_zoom) < 1e-7:
            return

        old_rect = self.geometry()
        anchor = anchor_global or old_rect.center()
        rel_x = (anchor.x() - old_rect.left()) / max(1, old_rect.width())
        rel_y = (anchor.y() - old_rect.top()) / max(1, old_rect.height())
        self.zoom = new_zoom
        new_size = self.scaled_size()
        new_left = round(anchor.x() - rel_x * new_size.width())
        new_top = round(anchor.y() - rel_y * new_size.height())
        self.setGeometry(new_left, new_top, new_size.width(), new_size.height())
        self.update()

    def keyPressEvent(self, event) -> None:  # noqa: N802 (Qt API)
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt API)
        self.closed.emit()
        super().closeEvent(event)


class TrayScrollBridge(QWidget):
    """Forward global scroll events to Qt, limited to the tray icon area."""

    scrolled = Signal(int, int, int)

    def __init__(self, tray: QSystemTrayIcon) -> None:
        super().__init__()
        self.tray = tray
        self.listener = None
        if pynput_mouse is not None:
            try:
                self.listener = pynput_mouse.Listener(on_scroll=self._on_scroll)
                self.listener.start()
            except Exception:
                self.listener = None

    def _on_scroll(self, _x, _y, _dx, dy) -> None:
        # The callback runs outside Qt's GUI thread; only emit a value here.
        self.scrolled.emit(int(_x), int(_y), 1 if dy > 0 else -1 if dy < 0 else 0)

    def stop(self) -> None:
        if self.listener is not None:
            self.listener.stop()
            self.listener = None


def launch_detached(image_path: Path) -> int:
    """Start the Qt child in a new session/process group and return."""
    command = [sys.executable, str(Path(__file__).resolve()), "--serve", str(image_path)]
    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if os.name == "nt":
        flags = getattr(subprocess, "DETACHED_PROCESS", 0x00000008) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200
        )
        kwargs["creationflags"] = flags
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(command, **kwargs)
    return 0


def serve(image_path: Path) -> int:
    image = QImage(str(image_path))
    if image.isNull():
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Pinpic", f"无法打开图片：\n{image_path}")
        return 2
    app = QApplication(sys.argv)
    app.setApplicationName("Pinpic")
    app.setQuitOnLastWindowClosed(False)
    window = PinWindow(image)

    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = QSystemTrayIcon(make_tray_icon(), app)
        tray.setToolTip("Pinpic - 图片贴图")
        menu = QMenu()
        taskbar_action = menu.addAction("任务管理器")
        taskbar_action.setCheckable(True)
        taskbar_action.setChecked(True)
        top_action = menu.addAction("置顶")
        top_action.setCheckable(True)
        top_action.setChecked(True)
        menu.addSeparator()
        exit_action = menu.addAction("退出 Pinpic")
        tray.setContextMenu(menu)

        def show_window() -> None:
            # A left click on the tray icon is a wake-up action only; it must
            # never hide or minimize an already visible pin.
            window.show()
            window.showNormal()
            window.raise_()
            window.activateWindow()

        taskbar_action.toggled.connect(
            lambda enabled: set_taskbar_visibility(window, enabled, top_action.isChecked())
        )
        top_action.toggled.connect(lambda enabled: set_always_on_top(window, enabled))
        tray.activated.connect(
            lambda reason: show_window()
            if reason == QSystemTrayIcon.ActivationReason.Trigger
            else None
        )
        exit_action.triggered.connect(app.quit)
        window.closed.connect(app.quit)
        tray.show()
        scroll_bridge = TrayScrollBridge(tray)

        def tray_scroll(x: int, y: int, steps: int) -> None:
            if steps and is_tray_pointer(tray, x, y):
                set_opacity(window, window.opacity + window.OPACITY_STEP * steps)

        scroll_bridge.scrolled.connect(tray_scroll)
        app.aboutToQuit.connect(scroll_bridge.stop)
        # Keep a Python reference for bindings that do not retain it through
        # the QObject parent alone.
        app._pinpic_tray = tray
        app._pinpic_scroll_bridge = scroll_bridge
    else:
        app.setQuitOnLastWindowClosed(True)

    window.show()
    window.raise_()
    window.activateWindow()
    return app.exec()


def make_tray_icon() -> QIcon:
    """Create a dependency-free pin-shaped tray icon."""
    icon = QIcon()
    for size in (16, 24, 32, 48, 64):
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(35, 35, 35))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(75, 180, 255))
        margin = max(2, size // 5)
        painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
        painter.setBrush(QColor(255, 210, 70))
        painter.drawPolygon(
            QPolygon(
                [
                    QPoint(size // 4, size // 2),
                    QPoint(size * 3 // 4, size // 2),
                    QPoint(size // 2, size - margin),
                ]
            )
        )
        painter.end()
        icon.addPixmap(pixmap)
    return icon


def set_opacity(window: PinWindow, value: float) -> None:
    window.opacity = max(0.15, min(1.0, float(value)))
    window.setWindowOpacity(window.opacity)


def is_tray_pointer(tray: QSystemTrayIcon, x: int, y: int) -> bool:
    """Check the tray icon; KDE SNI may not expose its geometry to Qt."""
    geometry = tray.geometry()
    if not geometry.isNull() and geometry.isValid():
        return geometry.contains(x, y)
    screen = QApplication.screenAt(QPoint(x, y)) or QApplication.primaryScreen()
    if screen is None:
        return False
    area = screen.geometry()
    # Plasma's panel is normally at an edge. This fallback is used only when
    # the SNI host reports 0x0 geometry, and keeps scrolling off the image.
    edge_size = 80
    return (
        area.left() <= x <= area.right()
        and area.top() <= y <= area.bottom()
        and (
            y >= area.bottom() - edge_size
            or y <= area.top() + edge_size
            or x <= area.left() + edge_size
            or x >= area.right() - edge_size
        )
    )


def set_always_on_top(window: PinWindow, enabled: bool) -> None:
    """Toggle the top-most flag; re-show is required by some Qt platforms."""
    was_visible = window.isVisible()
    geometry = window.geometry()
    window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, enabled)
    window.setGeometry(geometry)
    if was_visible:
        window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized)
        window.show()
        window.showNormal()
        if enabled:
            window.raise_()


def set_taskbar_visibility(window: PinWindow, enabled: bool, always_on_top: bool) -> None:
    """Switch between a task-manager window and a tool window."""
    was_visible = window.isVisible()
    geometry = window.geometry()
    flags = Qt.WindowType.FramelessWindowHint
    flags |= Qt.WindowType.WindowStaysOnTopHint if always_on_top else Qt.WindowType.Widget
    flags |= Qt.WindowType.Window if enabled else Qt.WindowType.Tool
    window.setWindowFlags(flags)
    window.setGeometry(geometry)
    if was_visible:
        window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized)
        window.show()
        window.showNormal()


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--serve":
        if len(args) != 2:
            return 2
        return serve(Path(args[1]).expanduser().resolve())
    if len(args) != 1 or args[0] in {"-h", "--help"}:
        print("用法: python pinpic.py 图片路径")
        print("左键拖动，滚动放大/缩小，中键还原，右键隐藏")
        return 0 if args and args[0] in {"-h", "--help"} else 2
    image_path = Path(args[0]).expanduser().resolve()
    if not image_path.is_file():
        print(f"图片不存在: {image_path}", file=sys.stderr)
        return 2
    return launch_detached(image_path)


if __name__ == "__main__":
    raise SystemExit(main())
