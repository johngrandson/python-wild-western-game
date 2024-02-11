import pygame
from entity import Entity
from pygame.math import Vector2 as vector
from states.monster import MonsterStateMachine


class Monster(Entity):
    instance_counter = 0

    def __init__(self, pos, groups, path, collision_sprites, player):
        super().__init__(pos, groups, path, collision_sprites)
        self.state_machine = MonsterStateMachine(self, player)
        self.player = player
        self.name = type(self).__name__

        Monster.instance_counter += 1
        self.id = Monster.instance_counter

    def get_player_distance_direction(self):
        enemy_pos = vector(self.rect.center)
        player_pos = vector(self.player.rect.center)
        distance = (player_pos - enemy_pos).magnitude()

        if distance != 0:
            direction = (player_pos - enemy_pos).normalize()
        else:
            direction = vector()

        return (distance, direction)

    def face_player(self):
        distance, direction = self.get_player_distance_direction()

        if distance < self.notice_radius:
            if -0.5 < direction.y < 0.5:
                if direction.x < 0:
                    self.status = "left_idle"
                elif direction.x > 0:
                    self.status = "right_idle"
            else:
                if direction.y < 0:
                    self.status = "up_idle"
                elif direction.y > 0:
                    self.status = "down_idle"

    def walk_to_player(self):
        distance, direction = self.get_player_distance_direction()
        if self.attack_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split("_")[0]

            if not self.state_machine.state == "chasing":
                self.state_machine.chase()

        else:
            self.direction = vector(0, 0)

    def damage(self):
        if self.is_vulnerable:
            self.health -= 1
            self.is_vulnerable = False
            self.hit_time = pygame.time.get_ticks()
            self.hit_sound.play()


class Coffin(Monster):
    def __init__(self, pos, groups, path, collision_sprites, player):
        super().__init__(pos, groups, path, collision_sprites, player)
        self.speed = 150
        self.notice_radius = 550
        self.walk_radius = 400
        self.attack_radius = 50

    def attack(self):
        distance, _ = self.get_player_distance_direction()
        if distance < self.attack_radius and not self.player.state_machine.state == "attacking":
            self.player.state_machine.attack()
            self.frame_index = 0

        self.status = f"{self.status.split('_')[0]}_attacking"
        self.player.state_machine.take_damage()

    def animate(self, dt):
        current_animation = self.animations[self.status]
        self.frame_index += 7 * dt

        if int(self.frame_index) == 4 and self.player.state_machine.state == "attacking":
            distance, _ = self.get_player_distance_direction()
            if distance < self.attack_radius and not self.state_machine.state == "attacking":
                self.attack()

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            # if self.attacking:
            #     self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.face_player()
        self.walk_to_player()

        if not self.player.state_machine.state == "dead":
            self.attack()

        if self.player.state_machine.state in ["dead", "attacking"]:
            self.state_machine.idle()

        self.move(dt)
        self.animate(dt)
        self.blink()

        self.check_death()
        self.vulnerability_timer()


class Cactus(Monster):
    def __init__(self, pos, groups, path, collision_sprites, player, create_bullet):
        super().__init__(pos, groups, path, collision_sprites, player)
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.notice_radius = 600
        self.walk_radius = 500
        self.attack_radius = 350
        self.speed = 90

    def attack(self):
        distance, _ = self.get_player_distance_direction()
        if distance < self.attack_radius and not self.state_machine.state == "attacking":
            self.state_machine.attack()
            self.frame_index = 0
            self.bullet_shot = False
            self.shoot_sound.play()

        if self.attacking:
            self.status = self.status.split("_")[0] + "_attacking"
            if not self.state_machine.state == "attacking":
                self.state_machine.attack()
        else:
            if not self.state_machine.state == "idle":
                self.state_machine.idle()

    def animate(self, dt):
        current_animation = self.animations[self.status]

        if int(self.frame_index) == 6 and self.state_machine.state == "attacking" and not self.bullet_shot:
            _, direction = self.get_player_distance_direction()
            pos = self.rect.center + direction * 150
            self.create_bullet(pos, direction)
            self.bullet_shot = True

        self.frame_index += 7 * dt

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            # if self.attacking:
            #     self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.face_player()
        self.walk_to_player()

        if not self.player.state_machine.state == "dead":
            self.attack()

        self.move(dt)

        self.animate(dt)
        self.blink()

        self.check_death()
        self.vulnerability_timer()
