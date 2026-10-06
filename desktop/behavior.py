import random

from desktop.character import CharacterState


class BehaviorController:

    def __init__(self, character):

        self.character = character

        self.state_timer = 0
        self.state_duration = 0

        self.choose_next_action()

    # -----------------------------------------
    # Main update
    # -----------------------------------------

    def update(self):

        self.state_timer += 1

        state = self.character.state

        if state in (
            CharacterState.FALLING,
            CharacterState.JUMPING,
            CharacterState.DRAGGING,
            CharacterState.TALKING,
        ):
            return

        if self.state_timer < self.state_duration:
            return

        self.choose_next_action()

    # -----------------------------------------
    # Choose next action
    # -----------------------------------------

    def choose_next_action(self):

        self.state_timer = 0

        choice = random.random()

        if choice < 0.50:

            self.start_walking()

        elif choice < 0.70:

            self.start_idle()

        elif choice < 0.85:

            self.start_sitting()

        elif choice < 0.95:

            self.start_jumping()

        else:

            self.start_sleeping()

    def start_jumping(self):

        # Jump only when standing on a surface.
        if self.character.current_surface is None:

            self.start_walking()

            return

        self.character.jump()

        self.state_duration = random.randint(
            3,
            6
        )
    # -----------------------------------------
    # Walking
    # -----------------------------------------

    def start_walking(self):

        self.character.velocity_x = random.choice(
            [-2, 2]
        )

        self.character.set_state(
            CharacterState.WALKING
        )

        self.state_duration = random.randint(
            8,
            20
        )

    # -----------------------------------------
    # Idle
    # -----------------------------------------

    def start_idle(self):

        self.character.velocity_x = 0

        self.character.set_state(
            CharacterState.IDLE
        )

        self.state_duration = random.randint(
            4,
            10
        )

    # -----------------------------------------
    # Sitting
    # -----------------------------------------

    def start_sitting(self):

        self.character.velocity_x = 0

        self.character.set_state(
            CharacterState.SITTING
        )

        self.state_duration = random.randint(
            6,
            15
        )

    # -----------------------------------------
    # Sleeping
    # -----------------------------------------

    def start_sleeping(self):

        self.character.velocity_x = 0

        self.character.set_state(
            CharacterState.SLEEPING
        )

        self.state_duration = random.randint(
            15,
            30
        )