import pygame, sys

from pygame.math import Vector2 as vector
from entity import Entity
from states.player import PlayerStateMachine


class Player(Entity):
    def __init__(self, pos, groups, path, collision_sprites, create_bullet, game):
        super().__init__(pos, groups, path, collision_sprites)
        self.game = game
        self.state_machine = PlayerStateMachine(self)
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.speed = 250

    def get_status(self):
        if not self.state_machine.state == "damaged":
            status_mapping = {
                "attacking": f"{self.status.split('_')[0]}_attacking",
                "dead": "dead",
            }
            self.status = status_mapping.get(self.state_machine.state, f"{self.status.split('_')[0]}_{self.state_machine.state}")

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.state_machine.state == "attacking":
            self.state_machine.state_classes[self.state_machine.state].handle_input(
                keys
            )

            if keys[pygame.K_SPACE]:
                self.direction = vector()
                self.frame_index = 0
                self.bullet_shot = False
                if not self.state_machine.state == "attacking":
                    self.state_machine.attack()

                match self.status.split("_")[0]:
                    case "left":
                        self.bullet_direction = vector(-1, 0)
                    case "right":
                        self.bullet_direction = vector(1, 0)
                    case "up":
                        self.bullet_direction = vector(0, -1)
                    case "down":
                        self.bullet_direction = vector(0, 1)

    def update_frame_index(self, dt):
        self.frame_index += 7 * dt

    def handle_attack(self):
        if (
            int(self.frame_index) == 2
            and self.state_machine.state == "attacking"
            and not self.bullet_shot
        ):
            bullet_start_pos = self.rect.center + self.bullet_direction * 80
            self.create_bullet(bullet_start_pos, self.bullet_direction)
            self.bullet_shot = True
            self.shoot_sound.play()

    def reset_frame_index(self, current_animation):
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.state_machine.state == "attacking":
                self.state_machine.idle()

        if (
            self.state_machine.state == "dead"
            and self.frame_index >= len(current_animation) - 1
        ):
            self.frame_index = len(current_animation) - 1

    def update_image(self, current_animation):
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)

        print(self.status)

        current_animation = self.animations[self.status]
        self.update_frame_index(dt)
        self.handle_attack()
        self.reset_frame_index(current_animation)
        self.update_image(current_animation)

        self.blink()
        self.check_death()
        self.vulnerability_timer()
