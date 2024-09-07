import pygame as pg
import pygame.transform

from .util import image_load, load_images, get_image, Slider


# font = pg.font.Font("resources/the_devil_net.ttf", 20)
class Main:  # has quit option #has settings options #has start option
    def __init__(self, screen):
        self.screen = screen
        self.start = image_load("menu/play.png")
        self.start = pg.transform.rotozoom(self.start, 0, 1.5)
        self.start_rect = self.start.get_rect(center=(400, 200))
        self.ghosts = load_images("menu/ghost")
        self.demons = load_images("enemies/demon")
        self.index = 0
        self.ghost = self.ghosts[self.index]
        self.ghost_rect = self.ghost.get_rect(center= (80, 320))
        self.demon = self.demons[self.index]
        self.demon_rect = self.demon.get_rect(center= (700, 200))
        self.processed_ghosts = []
        for img in self.ghosts:
            img = pygame.transform.rotozoom(img, 0, 1.25)
            img = pygame.transform.flip(img, True, False)
            self.processed_ghosts.append(img)
    def run(self):
        keys = pg.key.get_pressed()
        # self.screen.fill("blue")
        self.screen.blit(self.start, self.start_rect)
        if self.start_rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0] or keys[pg.K_SPACE]:
            return True
    def animate(self):
        self.index += 0.05
        if self.index >= len(self.processed_ghosts):
            self.index = 0
        self.ghost = self.processed_ghosts[int(self.index)]
        self.screen.blit(self.ghost, self.ghost_rect)
    def animate_demon(self):
        self.index += 0.03
        if self.index >= len(self.demons):
            self.index = 0
        self.demon = self.demons[int(self.index)]
        self.screen.blit(self.demon, self.demon_rect)




class Restart:  # has restart option#ends the game # has settings option
    def __init__(self, screen):
        self.screen = screen
        self.restart = image_load("menu/restart.png")
        self.restart = pg.transform.rotozoom(self.restart, 0, 1.25)
        self.restart_rect = self.restart.get_rect(center=(400,200))
        self.home = image_load("menu/home.png")  # error?
        self.home = pg.transform.rotozoom(self.home, 0 , 1.2)
        self.home_rect = self.home.get_rect(center=(370, 270))

    def run(self):
        self.screen.blit(self.restart, self.restart_rect)
        if self.restart_rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
            return True

    def return_menu(self):
        self.screen.blit(self.home, self.home_rect)
        if pg.mouse.get_pressed()[0] and self.home_rect.collidepoint(pg.mouse.get_pos()):
            return True


class Mode:  # has hard and easy mode
    def __init__(self, screen):
        self.screen = screen
        self.hard_mode = image_load("menu/mode_hard.png")
        self.hard_mode = pg.transform.rotozoom(self.hard_mode, 0, 1.5)
        self.hard_mode_rect = self.hard_mode.get_rect(center=(400, 290))
        self.easy_mode = image_load("menu/mode_easy.png")
        self.easy_mode = pg.transform.rotozoom(self.easy_mode, 0, 1.5)
        self.easy_mode_rect = self.easy_mode.get_rect(center=(400, 290))
        self.hard = False

    def run(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_button = pg.mouse.get_pressed()
        keys = pg.key.get_pressed()
        if self.hard:
            self.screen.blit(self.hard_mode, self.hard_mode_rect)
            if mouse_button[0] and self.hard_mode_rect.collidepoint(mouse_pos) or keys[pg.K_m]:
                self.hard = False
                pg.time.delay(100)
        else:
            self.screen.blit(self.easy_mode, self.easy_mode_rect)
            if mouse_button[0] and self.easy_mode_rect.collidepoint(mouse_pos) or keys[pg.K_m]:
                self.hard = True
                pg.time.delay(100)
        return self.hard


class Settings:  # has audio setting
    def __init__(self, game, volume=0):
        self.game = game
        self.button = image_load("menu/settings.png")
        self.button = pygame.transform.rotozoom(self.button, 0, 1.2)
        self.button_rect = self.button.get_rect(center=(430, 270))
        self.exit = image_load("menu/exit.png")
        self.exit = pygame.transform.rotozoom(self.exit, 0, 1.2)
        self.exit_rect = self.exit.get_rect(center=(780, 30))
        self.audio_on = image_load("music/audio_on.png")
        self.audio_on = pygame.transform.rotozoom(self.audio_on, 0, 0.15)
        self.audio_off = image_load("music/audio_off.png")
        self.audio_off = pygame.transform.rotozoom(self.audio_off, 0, 0.15)
        self.volume = volume
        self.sliders = [
            Slider((400,200), (300,20), 0.5,0, 0.7)
        ]

    def show(self):
        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pressed()
        mouse_pos = pg.mouse.get_pos()
        self.game.screen.fill("black")
        self.game.screen.blit(self.exit, self.exit_rect)
        self.game.screen.blit(self.audio_on, (170, 160))
        for slider in self.sliders:
            if slider.container_rect.collidepoint(mouse_pos) and mouse[0]:
                slider.move_slider(mouse_pos)
                self.game.bg_music.set_volume(slider.get_value())
            if slider.get_value() < 0.01:
                self.game.screen.blit(self.audio_off, (170, 160))
            slider.render(self.game.screen)
        if mouse[0] and self.exit_rect.collidepoint(mouse_pos) or keys[pg.K_ESCAPE]:
            self.game.settings_menu = False
    def run(self):
        self.game.screen.blit(self.button, self.button_rect)
        if pg.mouse.get_pressed()[0] and self.button_rect.collidepoint(pg.mouse.get_pos()):
            self.game.settings_menu = True







class Pause:  # pauses the game # has settings option #has quit
    def __init__(self, game):
        self.game = game
        self.time_paused = 0
        self.pause = image_load("menu/pause.png")
        self.pause_rect = self.pause.get_rect(center=(780, 30))
        self.resume = image_load("menu/RESUME.png")
        self.resume = pg.transform.rotozoom(self.resume, 0, 1.25)
        self.resume_rect = self.resume.get_rect(center=(400, 120))
    def run(self):
        keys = pg.key.get_pressed()
        self.game.screen.blit(self.pause, self.pause_rect)
        if self.pause_rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0] and not self.game.game_pause or keys[pg.K_p] and not self.game.game_pause:
            self.game.game_pause = True
            self.game.pause_start_time = pg.time.get_ticks()

    def unpause(self):
        keys = pg.key.get_pressed()
        self.game.screen.blit(self.resume, self.resume_rect)
        if self.game.game_pause:
            if (((self.resume_rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0])) and not self.game.game_reset
                    or keys[pg.K_ESCAPE]) and not self.game.game_reset:
                self.game.game_pause = False
                self.game.elapsed_time += pg.time.get_ticks() - self.game.pause_start_time

