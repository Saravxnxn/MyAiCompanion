from enum import Enum

class CharacterState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    JUMPING = "jumping"
    CLIMBING = "climbing"
    FALLING = "falling"
    DRAGGING = "dragging"
    SITTING = "sitting"
    SLEEPING = "sleeping"
    TALKING = "talking"