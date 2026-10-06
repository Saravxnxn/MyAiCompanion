from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtGui import QPixmap, QPainter, QRegion, QBitmap


class AnimationController(QObject):

    def __init__(self, parent=None):

        super().__init__(parent)

        # ==========================================
        # Animation storage
        # ==========================================

        self.animations = {}

        # ==========================================
        # Current animation
        # ==========================================

        self.current_animation = None
        self.frames = []
        self.current_frame = 0

        # ==========================================
        # Visual canvas
        # ==========================================

        self.canvas_width = 160
        self.canvas_height = 160

        # ==========================================
        # Playback settings
        # ==========================================

        self.interval = 120

        self.loop = True
        self.ping_pong = False
        self.hold_last = False

        self.direction = 1

        # ==========================================
        # Timer
        # ==========================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.next_frame
        )

        # ==========================================
        # UI callback
        # ==========================================

        self.frame_changed_callback = None

    # ==========================================
    # FIND VISIBLE CONTENT
    # ==========================================

    def get_content_rect(self, pixmap):

        image = pixmap.toImage()

        if image.hasAlphaChannel():

            # Qt returns a QImage from createAlphaMask()
            alpha_image = image.createAlphaMask()

            # Convert QImage -> QBitmap
            bitmap = QBitmap.fromImage(
                alpha_image
            )

            # QRegion accepts QBitmap
            region = QRegion(
                bitmap
            )

            rect = region.boundingRect()

            if not rect.isNull():
                return rect

        return pixmap.rect()

    # ==========================================
    # PREPARE ONE FRAME
    # ==========================================

    def prepare_frame(
        self,
        pixmap,
        content_rect,
        scale
    ):

        # Crop away transparent margins.
        cropped = pixmap.copy(
            content_rect
        )

        # Apply the SAME scale factor to every
        # frame in this animation.
        new_width = max(
            1,
            int(cropped.width() * scale)
        )

        new_height = max(
            1,
            int(cropped.height() * scale)
        )

        scaled = cropped.scaled(
            new_width,
            new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # ======================================
        # Fixed visual canvas
        # ======================================

        canvas = QPixmap(
            self.canvas_width,
            self.canvas_height
        )

        canvas.fill(
            Qt.GlobalColor.transparent
        )

        painter = QPainter(canvas)

        # Center horizontally.
        x = (
            self.canvas_width
            - scaled.width()
        ) // 2

        # Align bottom/feet.
        y = (
            self.canvas_height
            - scaled.height()
        )

        painter.drawPixmap(
            x,
            y,
            scaled
        )

        painter.end()

        return canvas

    # ==========================================
    # ADD ANIMATION
    # ==========================================

    def add_animation(
        self,
        name,
        frame_paths
    ):

        source_frames = []

        # --------------------------------------
        # Load every source image first
        # --------------------------------------

        for path in frame_paths:

            pixmap = QPixmap(
                str(Path(path))
            )

            if pixmap.isNull():

                print(
                    f"Warning: Could not load "
                    f"animation frame: {path}"
                )

                continue

            content_rect = (
                self.get_content_rect(
                    pixmap
                )
            )

            source_frames.append(
                (
                    pixmap,
                    content_rect
                )
            )

        # --------------------------------------
        # No valid frames
        # --------------------------------------

        if not source_frames:

            self.animations[name] = []

            print(
                f"Warning: No valid frames "
                f"for animation '{name}'"
            )

            return

        # --------------------------------------
        # Find largest visible dimensions
        # --------------------------------------

        max_width = 1
        max_height = 1

        for pixmap, rect in source_frames:

            max_width = max(
                max_width,
                rect.width()
            )

            max_height = max(
                max_height,
                rect.height()
            )

        # --------------------------------------
        # Calculate ONE common scale
        # --------------------------------------

        available_width = (
            self.canvas_width - 10
        )

        available_height = (
            self.canvas_height - 10
        )

        scale_x = (
            available_width
            / max_width
        )

        scale_y = (
            available_height
            / max_height
        )

        scale = min(
            scale_x,
            scale_y
        )

        # --------------------------------------
        # Prepare all frames
        # --------------------------------------

        prepared_frames = []

        for pixmap, content_rect in source_frames:

            frame = self.prepare_frame(
                pixmap,
                content_rect,
                scale
            )

            prepared_frames.append(
                frame
            )

        self.animations[name] = (
            prepared_frames
        )

        print(
            f"Loaded animation '{name}' "
            f"with {len(prepared_frames)} frame(s)"
        )

    # ==========================================
    # PLAY
    # ==========================================

    def play(
        self,
        name,
        interval=120,
        loop=True,
        ping_pong=False,
        hold_last=False
    ):

        if name not in self.animations:
            return

        if not self.animations[name]:
            return

        # --------------------------------------
        # Switch to new animation
        # --------------------------------------

        if self.current_animation != name:

            self.current_animation = name

            self.frames = (
                self.animations[name]
            )

            self.current_frame = 0

            self.direction = 1

        # --------------------------------------
        # Playback configuration
        # --------------------------------------

        self.interval = interval
        self.loop = loop
        self.ping_pong = ping_pong
        self.hold_last = hold_last

        # --------------------------------------
        # Start timer
        # --------------------------------------

        self.timer.start(
            self.interval
        )

        # --------------------------------------
        # Draw immediately
        # --------------------------------------

        if self.frame_changed_callback:

            self.frame_changed_callback()

    # ==========================================
    # STOP
    # ==========================================

    def stop(self):

        self.timer.stop()

    # ==========================================
    # NEXT FRAME
    # ==========================================

    def next_frame(self):

        if not self.frames:
            return

        # ======================================
        # Single-frame animation
        # ======================================

        if len(self.frames) == 1:

            self.current_frame = 0

            if not self.loop:

                self.timer.stop()

            if self.frame_changed_callback:

                self.frame_changed_callback()

            return

        # ======================================
        # Ping-pong animation
        # ======================================

        if self.ping_pong:

            self.current_frame += (
                self.direction
            )

            # Hit the last frame.
            if self.current_frame >= len(
                self.frames
            ):

                self.current_frame = (
                    len(self.frames) - 2
                )

                self.direction = -1

            # Hit the first frame.
            elif self.current_frame < 0:

                if self.loop:

                    self.current_frame = 1
                    self.direction = 1

                else:

                    self.current_frame = 0

                    self.timer.stop()

        # ======================================
        # Normal looping animation
        # ======================================

        else:

            self.current_frame += 1

            if self.current_frame >= len(
                self.frames
            ):

                if self.loop:

                    self.current_frame = 0

                else:

                    self.current_frame = (
                        len(self.frames) - 1
                    )

                    self.timer.stop()

        # ======================================
        # Request repaint
        # ======================================

        if self.frame_changed_callback:

            self.frame_changed_callback()

    # ==========================================
    # GET CURRENT FRAME
    # ==========================================

    def get_current_frame(self):

        if not self.frames:
            return None

        return self.frames[
            self.current_frame
        ]