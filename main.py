import pygame, sys
from pygame.math import Vector2 as vector
from settings import *
from player import Player
from pytmx.util_pygame import load_pygame
from sprite import Sprite, Bullet
from monster import Coffin, Cactus


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.display_surface = pygame.display.get_surface()
        self.bg = pygame.image.load("../graphics/other/bg.png").convert()

    def center_around(self, sprite, window_width, window_height):
        self.offset.x = sprite.rect.centerx - window_width / 2
        self.offset.y = sprite.rect.centery - window_height / 2

    def customize_draw(self, player, window_width, window_height):
        self.center_around(player, window_width, window_height)
        self.blit_surfaces(player)

    def blit_surfaces(self, player):
        self.display_surface.blit(self.bg, -self.offset)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.image.get_rect(center=sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)


class Game:
    def __init__(self):
        pygame.init()

        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720

        self.display_surface = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("Western shooter")
        self.clock = pygame.time.Clock()
        self.bullet_surf = pygame.image.load(
            "../graphics/other/particle.png"
        ).convert_alpha()

        self.all_sprites = AllSprites()
        self.obstacles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()

        self.setup()
        self.music = pygame.mixer.Sound("../sound/music.mp3")
        # self.music.play(loops = -1)

    def create_bullet(self, pos, direction):
        Bullet(pos, direction, self.bullet_surf, [self.all_sprites, self.bullets])

    def bullet_collision(self):
        # bullet obstacle collision
        for obstacle in self.obstacles.sprites():
            pygame.sprite.spritecollide(
                obstacle, self.bullets, True, pygame.sprite.collide_mask
            )

        # bullet monster collision
        for bullet in self.bullets.sprites():
            sprites = pygame.sprite.spritecollide(
                bullet, self.monsters, False, pygame.sprite.collide_mask
            )

            if sprites:
                bullet.kill()
                for sprite in sprites:
                    sprite.damage()

        # player bullet collision
        # if pygame.sprite.spritecollide(
        #     self.player, self.bullets, True, pygame.sprite.collide_mask
        # ):
        #     self.player.damage()

    def setup(self):
        tmx_map = load_pygame("../data/map.tmx")

        for x, y, surf in tmx_map.get_layer_by_name("Fence").tiles():
            Sprite((x * 64, y * 64), surf, [self.all_sprites, self.obstacles])

        for obj in tmx_map.get_layer_by_name("Objects"):
            Sprite((obj.x, obj.y), obj.image, [self.all_sprites, self.obstacles])

        for obj in tmx_map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                self.player = Player(
                    game=self,
                    pos=(obj.x, obj.y),
                    groups=self.all_sprites,
                    path=PATHS["player"],
                    collision_sprites=self.obstacles,
                    create_bullet=self.create_bullet,
                )

            if obj.name == "Coffin":
                Coffin(
                    pos=(obj.x, obj.y),
                    groups=[self.all_sprites, self.monsters],
                    path=PATHS["coffin"],
                    collision_sprites=self.obstacles,
                    player=self.player,
                )

            # if obj.name == "Cactus":
            #     Cactus(
            #         pos=(obj.x, obj.y),
            #         groups=[self.all_sprites, self.monsters],
            #         path=PATHS["cactus"],
            #         collision_sprites=self.obstacles,
            #         player=self.player,
            #         create_bullet=self.create_bullet,
            #     )

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.VIDEORESIZE:
            self.WINDOW_WIDTH = event.w
            self.WINDOW_HEIGHT = event.h

            screen = pygame.display.set_mode(
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE
            )
            self.all_sprites.center_around(
                self.player, self.WINDOW_WIDTH, self.WINDOW_HEIGHT
            )
            self.all_sprites.customize_draw(
                self.player, self.WINDOW_WIDTH, self.WINDOW_HEIGHT
            )

    def draw_groups(self):
        self.display_surface.fill("black")
        self.all_sprites.customize_draw(
            self.player, self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        )

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_events(event)

            dt = self.clock.tick(60) / 1000

            self.all_sprites.update(dt)
            self.bullet_collision()
            self.draw_groups()

            if self.player.state_machine.state == "dead":
                self.player.state_machine.state_classes["dead"].display_you_died(
                    self.display_surface
                )

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
