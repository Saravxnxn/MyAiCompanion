from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from desktop.animation import AnimationController
from desktop.character import CharacterState
from desktop.behavior import BehaviorController
from desktop.environment import DesktopEnvironment


class CompanionWindow(QWidget):

    def __init__(self):
        super().__init__()

        # ==========================================
        # WINDOW
        # ==========================================

        self.setup_window()

        # ==========================================
        # ENVIRONMENT
        # ==========================================

        self.environment = DesktopEnvironment(
            int(self.winId())
        )

        self.surfaces = []

        self.current_surface = None

        self.previous_surface_x = None
        self.previous_surface_y = None

        # ==========================================
        # PHYSICS
        # ==========================================

        self.velocity_x = 2
        self.velocity_y = 0

        self.gravity = 0.5

        # ==========================================
        # JUMP PHYSICS
        # ==========================================

        self.jump_velocity_y = -8.5

        self.max_jump_horizontal_speed = 4.0

        self.jump_target = None

        # ==========================================
        # PHYSICS BODY
        # ==========================================

        self.body_width = 110
        self.body_height = 115

        self.body_offset_x = 25
        self.body_offset_y = 45

        # ==========================================
        # MOUSE DRAGGING
        # ==========================================

        self.dragging = False
        self.drag_offset = QPoint()

        # ==========================================
        # ANIMATION
        # ==========================================

        self.animation = AnimationController(self)

        self.setup_animations()

        self.animation.frame_changed_callback = self.update

        # ==========================================
        # CHARACTER STATE
        # ==========================================

        self.state = None

        self.behavior = BehaviorController(self)

        self.set_state(
            CharacterState.WALKING
        )

        # ==========================================
        # PHYSICS TIMER
        # ==========================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_character
        )

        # ~60 FPS
        self.timer.start(16)

        # ==========================================
        # BEHAVIOR TIMER
        # ==========================================

        self.behavior_timer = QTimer(self)

        self.behavior_timer.timeout.connect(
            self.update_behavior
        )

        # Every 500 ms
        self.behavior_timer.start(500)

        # ==========================================
        # ENVIRONMENT TIMER
        # ==========================================

        self.environment_timer = QTimer(self)

        self.environment_timer.timeout.connect(
            self.update_environment
        )

        # Every 200 ms
        self.environment_timer.start(200)

    # ==========================================
    # UPDATE CHARACTER
    # ==========================================

    def update_character(self):

        self.update_position()

    # ==========================================
    # UPDATE BEHAVIOR
    # ==========================================

    def update_behavior(self):

        if self.dragging:
            return

        self.behavior.update()

    # ==========================================
    # ANIMATIONS
    # ==========================================

    def setup_animations(self):

        self.animation.add_animation(
            "idle",
            [
                "assets/characters/default/idle_1.png",
                "assets/characters/default/idle_2.png",
                "assets/characters/default/idle_3.png",
            ]
        )

        self.animation.add_animation(
            "walk",
            [
                "assets/characters/default/walk_1.png",
                "assets/characters/default/walk_2.png",
                "assets/characters/default/walk_3.png",
                "assets/characters/default/walk_4.png",
            ]
        )

        self.animation.add_animation(
            "fall",
            [
                "assets/characters/default/fall.png",
            ]
        )

        self.animation.add_animation(
            "sit",
            [
                "assets/characters/default/sit_1.png",
                "assets/characters/default/sit_2.png",
            ]
        )

        self.animation.add_animation(
            "sleep",
            [
                "assets/characters/default/sleep_1.png",
                "assets/characters/default/sleep_2.png",
                "assets/characters/default/sleep_3.png",
            ]
        )

        self.animation.add_animation(
            "talk",
            [
                "assets/characters/default/talk_1.png",
                "assets/characters/default/talk_2.png",
            ]
        )

    # ==========================================
    # STATE MANAGEMENT
    # ==========================================

    def set_state(self, new_state):

        # Don't restart the same animation.
        if self.state == new_state:
            return

        self.state = new_state

        # ======================================
        # IDLE
        # ======================================

        if new_state == CharacterState.IDLE:

            self.animation.play(
                "idle",
                interval=500,
                loop=True,
                ping_pong=True
            )

        # ======================================
        # WALKING
        # ======================================

        elif new_state == CharacterState.WALKING:

            self.animation.play(
                "walk",
                interval=120,
                loop=True,
                ping_pong=False
            )

        # ======================================
        # FALLING
        # ======================================

        elif new_state == CharacterState.FALLING:

            self.animation.play(
                "fall",
                interval=150,
                loop=False,
                ping_pong=False,
                hold_last=True
            )

        # ======================================
        # SITTING
        # ======================================

        elif new_state == CharacterState.SITTING:

            self.animation.play(
                "sit",
                interval=500,
                loop=False,
                ping_pong=False,
                hold_last=True
            )

        # ======================================
        # SLEEPING
        # ======================================

        elif new_state == CharacterState.SLEEPING:

            self.animation.play(
                "sleep",
                interval=900,
                loop=True,
                ping_pong=True
            )

        # ======================================
        # TALKING
        # ======================================

        elif new_state == CharacterState.TALKING:

            self.animation.play(
                "talk",
                interval=250,
                loop=True,
                ping_pong=True
            )

        # ======================================
        # DRAGGING
        # ======================================

        elif new_state == CharacterState.DRAGGING:

            # Keep the current visual frame while dragging.
            self.animation.stop()

        # ======================================
        # JUMPING
        # ======================================

        elif new_state == CharacterState.JUMPING:

            self.animation.play(
                "walk",
                interval=100,
                loop=True,
                ping_pong=False
            )

    # ==========================================
    # WINDOW SETUP
    # ==========================================

    def setup_window(self):

        self.setWindowTitle(
            "My AI Companion"
        )

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.resize(
            160,
            160
        )

        self.move(
            300,
            300
        )

    # ==========================================
    # PHYSICS BODY
    # ==========================================

    def body_left(self):

        return (
            self.x()
            + self.body_offset_x
        )

    def body_right(self):

        return (
            self.x()
            + self.body_offset_x
            + self.body_width
        )

    def body_top(self):

        return (
            self.y()
            + self.body_offset_y
        )

    def body_bottom(self):

        return (
            self.y()
            + self.body_offset_y
            + self.body_height
        )

    def find_jump_target(self):

        if self.current_surface is None:
            return None

        current_surface = self.current_surface

        # --------------------------------------
        # Starting position
        # --------------------------------------

        start_center = (
            self.body_left()
            + self.body_width / 2
        )

        start_bottom = (
            current_surface.top
        )

        best_target = None
        best_score = None

        jump_speed = abs(
            self.jump_velocity_y
        )

        gravity = self.gravity

        # --------------------------------------
        # Check every detected surface
        # --------------------------------------

        for surface in self.surfaces:

            # Don't jump onto the same surface.
            if (
                surface.identity
                == current_surface.identity
            ):
                continue

            target_center = (
                surface.left
                + surface.width / 2
            )

            dx = (
                target_center
                - start_center
            )

            dy = (
                surface.top
                - start_bottom
            )

            # ----------------------------------
            # Ballistic reachability
            #
            # y = -Vt + 1/2gt²
            #
            # discriminant:
            # V² + 2g*dy
            # ----------------------------------

            discriminant = (
                jump_speed ** 2
                + 2 * gravity * dy
            )

            if discriminant <= 0:
                continue

            sqrt_value = (
                discriminant ** 0.5
            )

            # Falling branch of the trajectory.
            flight_time = (
                jump_speed
                + sqrt_value
            ) / gravity

            if flight_time <= 0:
                continue

            # ----------------------------------
            # Required horizontal velocity
            # ----------------------------------

            required_velocity_x = (
                dx / flight_time
            )

            # ----------------------------------
            # Too far horizontally
            # ----------------------------------

            if abs(required_velocity_x) > (
                self.max_jump_horizontal_speed
            ):
                continue

            # ----------------------------------
            # Prefer nearby surfaces
            # ----------------------------------

            score = (
                abs(dx)
                + abs(dy) * 0.5
            )

            if (
                best_target is None
                or score < best_score
            ):

                best_target = {
                    "surface": surface,
                    "velocity_x": required_velocity_x,
                    "flight_time": flight_time
                }

                best_score = score

        return best_target
    # ==========================================
    # PHYSICS
    # ==========================================

    def jump(self):

        # Must be standing on a surface.
        if self.current_surface is None:
            return False

        # Don't jump while airborne or dragging.
        if self.state in (
            CharacterState.JUMPING,
            CharacterState.FALLING,
            CharacterState.DRAGGING,
        ):
            return False

        # --------------------------------------
        # Find a reachable target.
        # --------------------------------------

        target = self.find_jump_target()

        # No reachable surface.
        if target is None:
            return False

        self.jump_target = target["surface"]

        # --------------------------------------
        # Vertical jump impulse
        # --------------------------------------

        self.velocity_y = (
            self.jump_velocity_y
        )

        # --------------------------------------
        # Horizontal velocity toward target
        # --------------------------------------

        self.velocity_x = (
            target["velocity_x"]
        )

        # --------------------------------------
        # Leave current surface
        # --------------------------------------

        self.current_surface = None

        self.previous_surface_x = None
        self.previous_surface_y = None

        self.set_state(
            CharacterState.JUMPING
        )

        return True

    def update_position(self):

        # --------------------------------------
        # Don't apply physics while dragging
        # --------------------------------------

        if self.dragging:
            return

        # Current window position.
        x = self.x()
        y = self.y()

        # ======================================
        # HORIZONTAL MOVEMENT
        # ======================================

        if self.state in (
            CharacterState.IDLE,
            CharacterState.SITTING,
            CharacterState.SLEEPING,
        ):

            self.velocity_x = 0

        else:

            x += self.velocity_x

        # ======================================
        # GRAVITY
        # ======================================

        previous_bottom = (
            self.body_bottom()
        )

        self.velocity_y += self.gravity

        y += self.velocity_y

        next_bottom = (
            y
            + self.body_offset_y
            + self.body_height
        )

        # ======================================
        # FIND LANDING SURFACE
        # ======================================

        landing_surface = None

        if self.velocity_y >= 0:

            landing_surface = (
                self.find_landing_surface(y)
            )

        # ======================================
        # JUMP → FALL TRANSITION
        # ======================================

        if (
            self.state == CharacterState.JUMPING
            and self.velocity_y >= 0
        ):

            self.set_state(
                CharacterState.FALLING
            )

        # ======================================
        # CURRENT SCREEN
        # ======================================

        screen = (
            self.screen().availableGeometry()
        )

        # Horizontal limit of physics body.
        max_x = (
            screen.width()
            - self.body_offset_x
            - self.body_width
        )

        # ======================================
        # SURFACE / SCREEN HORIZONTAL LOGIC
        # ======================================

        if self.current_surface is not None:

            surface = self.current_surface

            # ----------------------------------
            # Surface body boundaries
            # ----------------------------------

            min_x = (
                surface.left
                - self.body_offset_x
            )

            max_surface_x = (
                surface.right
                - self.body_offset_x
                - self.body_width
            )

            # ==================================
            # LEFT EDGE
            # ==================================

            if x <= min_x:

                # Only fall if actually walking
                # toward the left edge.
                if self.velocity_x < 0:

                    self.current_surface = None

                    self.previous_surface_x = None
                    self.previous_surface_y = None

                    self.velocity_y = 0

                    self.set_state(
                        CharacterState.FALLING
                    )

                else:

                    x = min_x

            # ==================================
            # RIGHT EDGE
            # ==================================

            elif x >= max_surface_x:

                # Only fall if actually walking
                # toward the right edge.
                if self.velocity_x > 0:

                    self.current_surface = None

                    self.previous_surface_x = None
                    self.previous_surface_y = None

                    self.velocity_y = 0

                    self.set_state(
                        CharacterState.FALLING
                    )

                else:

                    x = max_surface_x

        else:

            # ==================================
            # MONITOR BOUNDARIES
            # ==================================

            if x <= 0:

                x = 0

                self.velocity_x = abs(
                    self.velocity_x
                )

            elif x >= max_x:

                x = max_x

                self.velocity_x = -abs(
                    self.velocity_x
                )

        # ======================================
        # SURFACE COLLISION
        # ======================================

        if (
            landing_surface is not None
            and previous_bottom
                <= landing_surface.top
            and next_bottom
                >= landing_surface.top
        ):

            # The physics body's bottom must
            # touch the surface top.

            y = (
                landing_surface.top
                - self.body_offset_y
                - self.body_height
            )

            self.velocity_y = 0

            self.current_surface = (
                landing_surface
            )

            self.jump_target = None

            # Reset surface tracking.
            self.previous_surface_x = (
                landing_surface.x
            )

            self.previous_surface_y = (
                landing_surface.y
            )

            # If falling, begin walking again.
            if self.state == CharacterState.FALLING:

                self.set_state(
                    CharacterState.WALKING
                )

        # ======================================
        # SCREEN FLOOR FALLBACK
        # ======================================

        screen = (
            self.screen().availableGeometry()
        )

        max_y = (
            screen.height()
            - self.height()
        )

        if y >= max_y:

            y = max_y

            self.velocity_y = 0

            self.current_surface = None

            self.previous_surface_x = None
            self.previous_surface_y = None

            if self.state == CharacterState.FALLING:

                self.set_state(
                    CharacterState.WALKING
                )

        # ======================================
        # APPLY POSITION
        # ======================================

        self.move(
            x,
            y
        )

    # ==========================================
    # MOUSE PRESS
    # ==========================================

    def mousePressEvent(self, event):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.dragging = True

            self.current_surface = None

            self.previous_surface_x = None
            self.previous_surface_y = None

            self.set_state(
                CharacterState.DRAGGING
            )

            self.drag_offset = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()

    # ==========================================
    # MOUSE MOVE
    # ==========================================

    def mouseMoveEvent(self, event):

        if self.dragging:

            new_position = (
                event.globalPosition().toPoint()
                - self.drag_offset
            )

            self.move(
                new_position
            )

            event.accept()

    # ==========================================
    # MOUSE RELEASE
    # ==========================================

    def mouseReleaseEvent(self, event):

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.dragging = False

            self.velocity_y = 0

            self.current_surface = None

            self.previous_surface_x = None
            self.previous_surface_y = None

            self.set_state(
                CharacterState.FALLING
            )

            event.accept()

    # ==========================================
    # DRAWING
    # ==========================================

    def paintEvent(self, event):

        painter = QPainter(self)

        pixmap = (
            self.animation.get_current_frame()
        )

        if pixmap is None:
            return

        painter.drawPixmap(
            0,
            0,
            pixmap
        )

        painter.end()

    # ==========================================
    # FIND LANDING SURFACE
    # ==========================================

    def find_landing_surface(self, next_y):

        character_left = self.body_left()
        character_right = self.body_right()

        previous_bottom = self.body_bottom()

        next_bottom = (
            next_y
            + self.body_offset_y
            + self.body_height
        )

        best_surface = None
        best_distance = None

        for surface in self.surfaces:

            # ======================================
            # 1. Horizontal overlap
            # ======================================

            horizontal_overlap = (
                character_right > surface.left
                and character_left < surface.right
            )

            if not horizontal_overlap:
                continue

            # ======================================
            # 2. Surface must be below the feet
            #    and crossed during this physics step
            # ======================================

            crossed_surface = (
                previous_bottom <= surface.top
                and next_bottom >= surface.top
            )

            if not crossed_surface:
                continue

            # ======================================
            # 3. Distance from current feet
            # ======================================

            distance = (
                surface.top
                - previous_bottom
            )

            # Safety check
            if distance < 0:
                continue

            # ======================================
            # 4. Choose nearest surface
            # ======================================

            if (
                best_surface is None
                or distance < best_distance
            ):

                best_surface = surface
                best_distance = distance

        return best_surface

    # ==========================================
    # UPDATE ENVIRONMENT
    # ==========================================

    def update_environment(self):

        self.surfaces = (
            self.environment.get_surfaces()
        )

        if self.current_surface is None:
            return

        current_identity = (
            self.current_surface.identity
        )

        matching_surface = None

        for surface in self.surfaces:

            if surface.identity == current_identity:

                matching_surface = surface

                break

        # ======================================
        # SURFACE DISAPPEARED
        # ======================================

        if matching_surface is None:

            self.current_surface = None
            self.jump_target = None

            self.previous_surface_x = None
            self.previous_surface_y = None

            if self.state not in (
                CharacterState.FALLING,
                CharacterState.DRAGGING,
            ):

                self.set_state(
                    CharacterState.FALLING
                )

            return

        # ======================================
        # FIRST TIME TRACKING SURFACE
        # ======================================

        if self.previous_surface_x is None:

            self.previous_surface_x = (
                matching_surface.x
            )

            self.previous_surface_y = (
                matching_surface.y
            )

        else:

            # ==================================
            # DETECT WINDOW MOVEMENT
            # ==================================

            delta_x = (
                matching_surface.x
                - self.previous_surface_x
            )

            delta_y = (
                matching_surface.y
                - self.previous_surface_y
            )

            # ==================================
            # MOVE CHARACTER WITH WINDOW
            # ==================================

            if self.state not in (
                CharacterState.FALLING,
                CharacterState.DRAGGING,
            ):

                self.move(
                    self.x() + delta_x,
                    self.y() + delta_y
                )

            # ==================================
            # SAVE NEW SURFACE POSITION
            # ==================================

            self.previous_surface_x = (
                matching_surface.x
            )

            self.previous_surface_y = (
                matching_surface.y
            )

        # ======================================
        # UPDATE CURRENT SURFACE
        # ======================================

        self.current_surface = (
            matching_surface
        )