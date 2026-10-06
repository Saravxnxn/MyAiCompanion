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

        # HWND -> persistent Surface
        self.surface_cache = {}

    # ==========================================
    # GET WINDOWS
    # ==========================================

    def get_windows(self):

        windows = []

        EnumWindowsProc = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM
        )

        z_order = 0

        def callback(hwnd, lParam):

            nonlocal z_order

            current_z_order = z_order

            z_order += 1

            # ==================================
            # Ignore companion
            # ==================================

            if hwnd == self.companion_hwnd:
                return True

            # ==================================
            # Ignore invisible windows
            # ==================================

            if not self.user32.IsWindowVisible(hwnd):
                return True

            # ==================================
            # Ignore minimized windows
            # ==================================

            if self.user32.IsIconic(hwnd):
                return True

            # ==================================
            # Get rectangle
            # ==================================

            rect = wintypes.RECT()

            success = self.user32.GetWindowRect(
                hwnd,
                ctypes.byref(rect)
            )

            if not success:
                return True

            width = (
                rect.right
                - rect.left
            )

            height = (
                rect.bottom
                - rect.top
            )

            # ==================================
            # Ignore small windows
            # ==================================

            if width < 200:
                return True

            if height < 100:
                return True

            # ==================================
            # Ignore extremely off-screen windows
            # ==================================

            if rect.left < -5000:
                return True

            if rect.top < -5000:
                return True

            # ==================================
            # Get title
            # ==================================

            title_length = (
                self.user32.GetWindowTextLengthW(
                    hwnd
                )
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

            title_value = title.value.strip()

            # ==================================
            # Ignore known shell/system windows
            # ==================================

            ignored_titles = {
                "Program Manager",
                "Windows Input Experience",
            }

            if title_value in ignored_titles:
                return True

            # ==================================
            # Store window
            # ==================================

            windows.append({

                "hwnd": hwnd,

                "title": title_value,

                "x": rect.left,

                "y": rect.top,

                "width": width,

                "height": height,

                # EnumWindows gives us the
                # Z-order of top-level windows.
                #
                # Smaller number = higher in Z-order.
                "z_order": current_z_order,

            })

            return True

        callback_function = EnumWindowsProc(
            callback
        )

        self.user32.EnumWindows(
            callback_function,
            0
        )

        return windows

    # ==========================================
    # GET SURFACES
    # ==========================================

    def get_surfaces(self):

        windows = self.get_windows()

        active_hwnds = set()

        for window in windows:

            hwnd = window["hwnd"]

            active_hwnds.add(hwnd)

            # ==================================
            # Existing surface
            # ==================================

            if hwnd in self.surface_cache:

                surface = (
                    self.surface_cache[hwnd]
                )

                surface.x = (
                    window["x"]
                )

                surface.y = (
                    window["y"]
                )

                surface.width = (
                    window["width"]
                )

                surface.height = (
                    window["height"]
                )

                surface.source_window = (
                    window
                )

                surface.z_order = (
                    window.get(
                        "z_order",
                        999999
                    )
                )

            # ==================================
            # New surface
            # ==================================

            else:

                surface = Surface(

                    window["x"],

                    window["y"],

                    window["width"],

                    window["height"],

                    window,

                    SurfaceType.WINDOW
                )

                surface.z_order = (
                    window.get(
                        "z_order",
                        999999
                    )
                )

                self.surface_cache[
                    hwnd
                ] = surface

        # ======================================
        # Remove stale windows
        # ======================================

        stale_hwnds = (
            set(
                self.surface_cache.keys()
            )
            - active_hwnds
        )

        for hwnd in stale_hwnds:

            del self.surface_cache[
                hwnd
            ]

        # ======================================
        # Return surfaces ordered by Z-order
        # ======================================

        surfaces = list(
            self.surface_cache.values()
        )

        surfaces.sort(
            key=lambda surface:
                surface.z_order
        )

        return surfaces

    # ==========================================
    # TOPMOST SURFACE AT POINT
    # ==========================================

    def get_top_surface_at(
        self,
        x,
        y
    ):

        surfaces = list(
            self.surface_cache.values()
        )

        # Topmost first.
        surfaces.sort(
            key=lambda surface:
                surface.z_order
        )

        for surface in surfaces:

            if not surface.walkable:
                continue

            if (
                surface.left
                <= x
                <= surface.right
                and
                surface.top
                <= y
                <= surface.bottom
            ):

                return surface

        return None


class Surface:

    def __init__(
        self,
        x,
        y,
        width,
        height,
        source_window=None,
        surface_type=SurfaceType.WINDOW
    ):

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.source_window = (
            source_window
        )

        self.surface_type = (
            surface_type
        )

        self.hwnd = None

        self.z_order = 999999

        if source_window is not None:

            self.hwnd = (
                source_window["hwnd"]
            )

            self.z_order = (
                source_window.get(
                    "z_order",
                    999999
                )
            )

    # ==========================================
    # GEOMETRY
    # ==========================================

    @property
    def left(self):

        return self.x

    @property
    def right(self):

        return (
            self.x
            + self.width
        )

    @property
    def top(self):

        return self.y

    @property
    def bottom(self):

        return (
            self.y
            + self.height
        )

    # ==========================================
    # IDENTITY
    # ==========================================

    @property
    def identity(self):

        return self.hwnd

    # ==========================================
    # CAPABILITIES
    # ==========================================

    @property
    def walkable(self):

        return True

    @property
    def climbable(self):

        return (
            self.surface_type
            == SurfaceType.WINDOW
        )