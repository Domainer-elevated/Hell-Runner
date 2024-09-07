import pygame as pg
from random import randint
from .util import load_images


class Player(pg.sprite.Sprite):
    def __init__(self, images, jumps):
        super().__init__()
        self.images = list(images)
        self.masks = [pg.mask.from_surface(img) for img in self.images]
        self.jumps = list(jumps)
        self.jump_masks = [pg.mask.from_surface(jump) for jump in self.jumps]
        self.jump_index = 0
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=(30, 370))
        self.gravity = 0
        self.jump_sound = pg.mixer.Sound("resources/music/jump.mp3")

    def player_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and self.rect.bottom >= 370 or self.rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0] and self.rect.bottom >= 370:
            self.jump_sound.play()
            self.gravity -= 18
    def apply_grav(self):
        self.gravity += 0.9
        self.rect.y += self.gravity
        if self.rect.bottom >= 370:
            self.rect.bottom = 370
            self.gravity = 0

    def animation(self):
        if self.rect.bottom < 370:
            self.jump_index += 0.04
            if self.jump_index >= len(self.jumps):
                self.jump_index = 0
            self.image = self.jumps[int(self.jump_index)]
            self.mask = self.masks[int(self.jump_index)]
        else:
            self.index += 0.2
            if self.index >= len(self.images):
                self.index = 0
            self.image = self.images[int(self.index)]
            self.mask = self.masks[int(self.index)]

    def update(self, *args, **kwargs):
        self.player_input()
        self.apply_grav()
        self.animation()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, type, pos):
        super().__init__()
        self.game = game
        self.type = type
        if type == "demon":
            self.images = []
            self.masks = []
            for img in load_images("enemies/demon"):
                demonic = pg.transform.rotozoom(img, 0, 0.85)
                self.images.append(demonic)
                self.masks.append(pg.mask.from_surface(demonic))
            self.y_pos = 230
        elif type == "ghost":
            self.images = []
            self.masks = []
            for img in load_images("enemies/ghost"):
                self.images.append(img)
                self.masks.append(pg.mask.from_surface(img))
            self.y_pos = 370
        self.index = 0
        self.image = self.images[self.index]
        self.mask = self.masks[self.index]
        self.rect = self.image.get_rect(midbottom=(pos, self.y_pos))

    def animation(self):
        self.index += 0.1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[int(self.index)]
        self.mask = self.masks[int(self.index)]

    def update(self, *args, **kwargs):
        self.animation()
        self.rect.x -= self.game.obstacle_speed
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()
