import ctypes
from ctypes import wintypes
from enum import Enum


class SurfaceType(Enum):

    WINDOW = "window"
    SCREEN = "screen"


class DesktopEnvironment:

    def __init__(self, companion_hwnd=None):

        self.user32 = ctypes.windll.user32
        self.companion_hwnd = companion_hwnd

        self.surface_cache = {}

    def get_windows(self):

        windows = []

        EnumWindowsProc = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM
        )

        def callback(hwnd, lParam):

            # Ignore our own companion
            if self.companion_hwnd == hwnd:
                return True

            # Ignore invisible windows
            if not self.user32.IsWindowVisible(hwnd):
                return True

            # Get rectangle FIRST
            rect = wintypes.RECT()

            if not self.user32.GetWindowRect(
                hwnd,
                ctypes.byref(rect)
            ):
                return True

            width = rect.right - rect.left
            height = rect.bottom - rect.top

            # Ignore small windows
            if width < 200:
                return True

            if height < 100:
                return True

            # Ignore extremely off-screen windows
            if rect.left < -5000:
                return True

            if rect.top < -5000:
                return True

            # Get title
            title_length = (
                self.user32.GetWindowTextLengthW(hwnd)
            )

            if title_length == 0:
                return True

            title = ctypes.create_unicode_buffer(
                title_length + 1
            )

            self.user32.GetWindowTextW(
                hwnd,
                title,
                title_length + 1
            )

            windows.append({
                "hwnd": hwnd,
                "title": title.value,
                "x": rect.left,
                "y": rect.top,
                "width": width,
                "height": height
            })

            return True

        callback_function = EnumWindowsProc(callback)

        self.user32.EnumWindows(
            callback_function,
            0
        )

        return windows

    def get_surfaces(self):

        windows = self.get_windows()

        active_hwnds = set()

        for window in windows:

            hwnd = window["hwnd"]

            active_hwnds.add(hwnd)

            if hwnd in self.surface_cache:

                surface = self.surface_cache[hwnd]

                surface.x = window["x"]
                surface.y = window["y"]
                surface.width = window["width"]
                surface.source_window = window

            else:

                surface = Surface(
                    window["x"],
                    window["y"],
                    window["width"],
                    window,
                    SurfaceType.WINDOW
                )

                self.surface_cache[hwnd] = surface

        stale_hwnds = (
            set(self.surface_cache.keys())
            - active_hwnds
        )

        for hwnd in stale_hwnds:

            del self.surface_cache[hwnd]

        return list(self.surface_cache.values())


class Surface:

    def __init__(
        self,
        x,
        y,
        width,
        source_window=None,
        surface_type=SurfaceType.WINDOW
    ):

        self.x = x
        self.y = y
        self.width = width

        self.source_window = source_window
        self.surface_type = surface_type

        self.hwnd = None

        if source_window is not None:
            self.hwnd = source_window["hwnd"]

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y

    @property
    def identity(self):

        return self.hwnd

    @property
    def walkable(self):
        return True

    @property
    def climbable(self):
        return (
            self.surface_type
            == SurfaceType.WINDOW
        )