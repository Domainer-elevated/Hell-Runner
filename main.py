import sys, math, json, os
import pygame as pg
from random import choice,randint
from scripts.util import image_load, load_images
from scripts.entities import Player, Obstacle
from scripts.menu import Main, Restart, Mode, Pause, Settings

class Game(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        pg.init()
        pg.display.set_caption("Hell runners")
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((800, 400))
        self.surface = pg.Surface((800, 400), pg.SRCALPHA)
        self.font = pg.font.Font("resources/glitch_inside.otf", 50)
        self.font_2 = pg.font.Font("resources/Melcoinda.otf", 40)
        self.font_3 = pg.font.Font("resources/the_devil_net.ttf", 110)
        self.font_4 = pg.font.Font("resources/the_devil_net.ttf", 10)
        self.start_time = 0
        self.elapsed_time = 0
        self.pause_start_time = 0
        self.time = 0
        self.high_score = 0
        self.easy_high_score = 0
        self.hard_high_score = 0
        self.difficulty_increments = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        self.current_increment = 0  # Track the current difficulty increment
        self.obstacle_speed = 5# Initial speed of obstacles
        self.obstacle_spawn_time = 1800  # Initial spawn time
        self.max_speed = 12  # Maximum speed of obstacles
        self.last_spawn_pos = 800 # Initial spawn position
        self.main_menu = Main(self.screen)
        pg.mixer.set_num_channels(2)  # Ensure there are at least 2 channels
        self.bg_music_channel = pg.mixer.Channel(0)  # Reserve channel 0 for background music
        self.sound_effect_channel = pg.mixer.Channel(1)
        self.hurt = pg.mixer.Sound("resources/music/dog_hurt.mp3")
        self.bg_music = pg.mixer.Sound("resources/music/manic_shadows.wav")
        self.menu_music = pg.mixer.Sound("resources/music/nasty_shadows.wav")
        self.restart = Restart(self.screen)
        self.pause_restart = Restart(self.screen)
        self.mode = Mode(self.screen)
        self.settings = Settings(self)
        self.settings_menu = False
        self.game_pause = False
        self.game_reset = False
        self.pause_return = False
        self.pause_menu = Pause(self)
        self.hard_mode = False
        if self.hard_mode:
            self.lives = 1
        else:
            self.lives = 3
        self.data = {
            "easy" : 0,
            "hard" : 0
        }
        self.load_scores()
        self.scroll = 0
        self.render_offset = [0, 0]
        self.active = False
        self.game_active = False
        self.enemies = set()
        self.assets = {
            "background" : load_images("background"),
            "platform": image_load("platform.png"),
            "bg" : image_load("bg.png"),
            "title" : image_load("title.png"),
            "player/run" : load_images("player/run"),
            "player/jump" : load_images("player/jump"),
            "enemy/ghost" : load_images("enemies/ghost"),
            "enemy/demon" : load_images("enemies/demon"),
        }
        self.backgrounds = []
        for bg in self.assets["background"]:
            lol = pg.transform.rotozoom(bg, 0, 1.4)
            lol = pg.transform.flip(lol, True, False)
            self.backgrounds.append(lol)
        self.bg_width = self.backgrounds[1].get_width()
        self.tiles = math.ceil(800/ self.bg_width) + 1
        heart = image_load("heart.png")
        self.heart = pg.transform.scale2x(heart)
        self.hearts = [(self.heart, (0, 0)), (self.heart, (20, 0)), (self.heart, (40, 0))]
        runner = []
        for img in self.assets["player/run"]:
            lol = pg.transform.scale2x(img)
            lol = pg.transform.flip(lol, True, False)
            runner.append(lol)
        jumper = []
        for img in self.assets["player/jump"]:
            lol = pg.transform.rotozoom(img, 0, 1.8)
            lol = pg.transform.flip(lol, True, False)
            jumper.append(lol)

        self.player = pg.sprite.GroupSingle()
        self.player.add(Player(runner, jumper))
        self.obstacles = pg.sprite.Group()
        #timer
        self.obstacle_timer = pg.USEREVENT + 1
        if not self.game_pause:
            pg.time.set_timer(self.obstacle_timer, self.obstacle_spawn_time)

    def load_scores(self):
        if os.path.exists("game_score.txt"):
            with open("game_score.txt", "r") as score_file:
                try:
                    self.data = json.load(score_file)
                    self.easy_high_score = self.data.get("easy", 0)
                    self.hard_high_score = self.data.get("hard", 0)
                except json.JSONDecodeError:
                    self.data = {"easy": 0, "hard": 0}
                    self.easy_high_score = 0
                    self.hard_high_score = 0
        else:
            self.data = {"easy": 0, "hard": 0}
            self.easy_high_score = 0
            self.hard_high_score = 0
    def spawn_obstacle(self):
        self.min_spacing = 50  # Minimum spacing between obstacles
        self.max_spacing = 100  # Maximum spacing between obstacles

        if self.current_increment <= 3:
            obstacle_type = "ghost"
        elif 3 < self.current_increment <= 6:
            obstacle_type = choice(["demon", "ghost", "ghost"])
        elif 6 < self.current_increment <= 9:
            obstacle_type = choice(["demon", "ghost", "ghost", "ghost"])
        else:
            obstacle_type = choice(["demon", "ghost", "ghost"])

        actual_spacing = randint(self.min_spacing, self.max_spacing)
        spawn_pos = self.last_spawn_pos + actual_spacing

        # Adjust spawn position to ensure enough spacing from previous obstacle
        while abs(spawn_pos - self.last_spawn_pos) < self.min_spacing:
            spawn_pos += self.min_spacing

        # Reset spawn position if it goes off the screen to maintain obstacle density
        if spawn_pos > randint(950, 1100):  # Reset when position is too far
            spawn_pos = randint(900, 1000)
        self.last_spawn_pos = spawn_pos
        obstacle = Obstacle(self, obstacle_type, self.last_spawn_pos)
        self.obstacles.add(obstacle)

    def reset_game(self):
        self.game_pause = False
        if self.game_reset:
            self.game_reset = False
        elif self.pause_return:
            self.pause_return = False
        else:
            if self.hard_mode:
                self.high_score = self.hard_high_score
            else:
                self.high_score = self.easy_high_score
        self.lives = 3
        self.obstacles.empty()
        self.elapsed_time = 0
        self.pause_start_time = 0
        self.settings_menu = False
        self.start_time = int(pg.time.get_ticks())
        if self.hard_mode == False:
            self.hearts = [(self.heart, (0, 0)), (self.heart, (20, 0)), (self.heart, (40, 0))]
        self.current_increment = 0
        self.obstacle_spawn_time = 1800  # Reset to initial spawn time
        self.obstacle_speed = 5 # Reset to initial speed
        self.last_spawn_pos = 800
        self.enemies = set()
        pg.time.set_timer(self.obstacle_timer, self.obstacle_spawn_time)
        # self.game_reset = False
        # self.pause_return = False
    def collisions(self):
        if pg.sprite.spritecollide(self.player.sprite, self.obstacles, False):
            return True
        else: return False

    def update_high_score(self):
        if self.hard_mode:
            if self.time > self.hard_high_score:
                self.hard_high_score = self.time
            self.data['hard'] = self.hard_high_score
        else:
            if self.time > self.easy_high_score:
                self.easy_high_score = self.time
            self.data['easy'] = self.easy_high_score
    def display_score(self):
        if not self.game_pause:
            current_time = pg.time.get_ticks()
            self.time = int((current_time - self.start_time - self.elapsed_time)/100)
        score_surf = self.font_2.render(f"Score: {int(self.time)}", False, "#FFEC5C")
        score_rect = score_surf.get_rect(center= (400, 80))
        self.screen.blit(score_surf, score_rect)
        if self.hard_mode:
            high_score_surf = self.font_2.render(f"High Score: {self.hard_high_score}", False, "#FFEC5C")
        else:
            high_score_surf = self.font_2.render(f"High Score: {self.easy_high_score}", False, "#FFEC5C")
        high_score_rect = high_score_surf.get_rect(center=(360, 50))
        self.screen.blit(high_score_surf, high_score_rect)
        # Game difficulty system ( didn't wanna create a separate function for it)
        if not self.game_pause:
            if self.current_increment < len(self.difficulty_increments) and self.time > self.difficulty_increments[self.current_increment]:
                self.current_increment += 1
                if 1 < self.current_increment <= 3:
                    self.obstacle_speed = min(self.max_speed, self.obstacle_speed + 1)
                    self.obstacle_spawn_time = max(1250, self.obstacle_spawn_time - 200)
                elif 3 < self.current_increment <= 6:
                    self.obstacle_speed = min(self.max_speed, self.obstacle_speed + 1)
                    self.obstacle_spawn_time = max(950, self.obstacle_spawn_time - 200)
                elif 6 < self.current_increment <= 9:
                    self.obstacle_spawn_time = max(600, self.obstacle_spawn_time - 100)
                pg.time.set_timer(self.obstacle_timer, self.obstacle_spawn_time)
            return self.time

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    with open('game_score.txt', 'w') as score_file:
                        json.dump(self.data, score_file)
                    pg.quit()
                    sys.exit()
                if not self.game_pause:
                    if self.game_active or self.active:
                        if event.type == self.obstacle_timer:
                            self.spawn_obstacle()
                    elif not self.game_active:
                        if self.main_menu.run():
                            self.active = self.main_menu.run()
                            self.game_active = True
                            self.start_time = int(pg.time.get_ticks())

            if self.game_active:
                if not self.bg_music_channel.get_busy() and self.active:  # Check if the channel is already playing something
                    self.bg_music_channel.play(self.bg_music, loops=-1)
                if not self.game_pause:
                    if self.time < 200:
                        self.scroll -= 4
                    elif 200 < self.time < 400:
                        self.scroll -= 5
                    elif 400 < self.time < 600:
                        self.scroll -= 7
                    elif 600 < self.time < 800:
                        self.scroll -= 8
                    elif self.time > 800:
                        self.scroll -= 9
                    # reset scroll
                    if abs(self.scroll) > self.bg_width:
                        self.scroll = 0
                    for i in range(0, self.tiles):
                        for bg in self.backgrounds:
                            self.screen.blit(bg, (i * self.bg_width + self.scroll,self.render_offset[1]))
                        self.screen.blit(self.assets["platform"], (i * self.bg_width + self.scroll,self.render_offset[1]))
                if not self.settings_menu:
                    if self.hard_mode:
                        self.screen.blit(self.heart, (0,0))
                    else:
                        self.screen.blits(self.hearts)
                    self.player.draw(self.screen)
                    self.obstacles.draw(self.screen)
                if not self.settings_menu:
                    self.pause_menu.run()
                if not self.game_pause:
                    if self.hard_mode:
                        self.data['easy'] = self.data['easy']
                        self.data['hard'] = max(self.data['hard'], self.time)
                    else:
                        self.data['hard'] = self.data['hard']
                        self.data['easy'] = max(self.data['easy'], self.time)

                    self.display_score()
                    self.player.update()
                    self.obstacles.update()
                if self.collisions():
                    lol = pg.sprite.spritecollide(self.player.sprite, self.obstacles, False, pg.sprite.collide_mask)
                    if self.hard_mode:
                        self.render_offset[1] = 0
                        self.lives -= 1
                    else:
                        for i in lol:
                            if i not in self.enemies:
                                self.sound_effect_channel.play(self.hurt)
                                pg.time.delay(200)
                                self.render_offset[1] = 0
                                self.lives -= 1
                                self.hearts.pop()
                                self.enemies.add(i)
                    if self.lives == 0:
                        self.sound_effect_channel.play(self.hurt)
                        pg.time.delay(250)
                        self.update_high_score()
                        self.reset_game()
                        self.game_active = False
                        # self.active = None
            elif self.active == False:
                self.bg_music_channel.stop()
                # self.menu_music.play()
                self.screen.blit(self.assets["bg"], (0,0))
                self.screen.blit(self.assets["title"], (200, 0))
                text_surf = self.font_4.render('Developed by Rafsan', False, 'white')
                text_surf_rect = text_surf.get_frect(bottomright=(790, 390))
                self.screen.blit(text_surf, text_surf_rect)
                self.main_menu.animate()
                self.main_menu.animate_demon()
                self.main_menu.run()
                self.hard_mode = self.mode.run()
            elif not self.game_active and not self.game_reset:
                self.screen.fill("yellow")
                die_surf = self.font_3.render(f"YOU DIED", False, "#A02334")
                # die_surf = pg.transform.rotozoom(die_surf, 0, 3)
                die_rect = die_surf.get_rect(center=(400, 80))
                self.screen.blit(die_surf, die_rect)
                self.game_active = self.restart.run()
                self.active =not self.restart.return_menu()
            if self.game_pause:
                if self.settings_menu:
                    self.settings.show()
                else:
                    self.screen.fill("black")  # Ensure the screen is cleared for the pause menu
                    self.game_active = not self.pause_restart.run()
                    self.game_reset = self.pause_restart.run()
                    if self.pause_restart.return_menu():
                        self.pause_return = True
                        self.reset_game()
                        self.game_active = False
                        self.active = False
                    self.pause_menu.unpause()
                    self.settings.run()

            if self.game_reset:
                self.reset_game()
                self.game_active = True
            self.clock.tick(60)
            pg.display.update()


Game().run()