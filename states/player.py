import pygame

from transitions import Machine, State
from pygame.math import Vector2 as vector


class PlayerState:
    def __init__(self, player):
        self.player = player
        self.key_direction_mapping = {
            pygame.K_RIGHT: (1, 0, "right"),
            pygame.K_LEFT: (-1, 0, "left"),
            pygame.K_UP: (0, -1, "up"),
            pygame.K_DOWN: (0, 1, "down"),
        }


class PlayerIdleState(PlayerState):
    def on_enter(self):
        print("Player has entered idle state")

    def on_exit(self):
        self.player.direction = vector(0, 0)
        print("Player is leaving idle state")

    def handle_input(self, keys):
        for key, (x, y, status) in self.key_direction_mapping.items():
            if keys[key]:
                self.player.direction = vector(x, y)
                self.player.status = status
                self.player.state_machine.walk()


class PlayerWalkingState(PlayerState):
    def on_enter(self):
        print("Player has entered walking state")

    def on_exit(self):
        self.player.direction = vector(0, 0)
        print("Player is leaving walking state")

    def handle_input(self, keys):
        if not any(keys):
            if not self.player.state_machine.state == "dead":
                self.player.state_machine.idle()

        for key, (x, y, status) in self.key_direction_mapping.items():
            if keys[key]:
                self.player.direction = vector(x, y)
                self.player.status = status
                if self.player.state_machine.state != "walking":
                    self.player.state_machine.walk()


class PlayerAttackingState(PlayerState):
    def on_enter(self):
        print("Player has entered attack state")

    def on_exit(self):
        print("Player is leaving attack state")

    def handle_input(self, keys):
        pass


class PlayerDamagedState(PlayerState):
    def on_enter(self):
        self.player.status = "damaged"
        if self.player.is_vulnerable:
            self.player.health -= 1
            self.player.is_vulnerable = False
            self.player.hit_time = pygame.time.get_ticks()
            self.player.hit_sound.play()
        print("Player has entered damaged state")

    def on_exit(self):
        print("Player is exiting damaged state")

    def handle_input(self, keys):
        pass


class PlayerDeadState(PlayerState):
    def display_you_died(self, screen):
        font = pygame.font.Font(None, 72)
        text_surface = font.render("YOU DIED!", True, (255, 0, 0))
        screen_rect = screen.get_rect()
        text_rect = text_surface.get_rect(center=screen_rect.center)
        screen.blit(text_surface, text_rect)

    def on_enter(self):
        print("Player has entered dead state")

    def handle_input(self, keys):
        pass


class PlayerStateMachine:
    def __init__(self, player):
        self.state_classes = {
            "idle": PlayerIdleState(player),
            "walking": PlayerWalkingState(player),
            "attacking": PlayerAttackingState(player),
            "damaged": PlayerDamagedState(player),
            "dead": PlayerDeadState(player),
        }

        states = [
            State(
                name="idle",
                on_enter=self.state_classes["idle"].on_enter,
                on_exit=self.state_classes["idle"].on_exit,
            ),
            State(
                name="walking",
                on_enter=self.state_classes["walking"].on_enter,
                on_exit=self.state_classes["walking"].on_exit,
            ),
            State(
                name="attacking",
                on_enter=self.state_classes["attacking"].on_enter,
                on_exit=self.state_classes["attacking"].on_exit,
            ),
            State(
                name="damaged",
                on_enter=self.state_classes["damaged"].on_enter,
                on_exit=self.state_classes["damaged"].on_exit,
            ),
            State(
                name="dead",
                on_enter=self.state_classes["dead"].on_enter,
            ),
        ]

        transitions = [
            ["walk", "*", "walking"],
            ["idle", "*", "idle"],
            ["attack", "*", "attacking"],
            ["take_damage", "*", "damaged"],
            ["die", "*", "dead"],
        ]

        self.machine = Machine(
            model=self, states=states, transitions=transitions, initial="idle"
        )

    def update(self, dt):
        state_instance = self.state_classes[self.state]
        state_instance.update(dt)
