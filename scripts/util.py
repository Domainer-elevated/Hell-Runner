import pygame

import os

BASE_IMG_PATH = "resources/"

def main():
    ...
def image_load(path):
    img = pygame.image.load(BASE_IMG_PATH+path).convert_alpha()

    return img

def load_images(path):
    images = []

    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(image_load(path + "/" + img_name).convert_alpha())
    return images
def get_image(sheet, frame, width, height, scale, colour, flip= False):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), ((frame * width), 0, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    if flip:
        image = pygame.transform.flip(image, True, False)
    image.set_colorkey(colour)
    return image
class Slider:
    def __init__(self, pos: tuple, size: tuple, initial_val: float, min: float, max: float) -> None:
        self.pos = pos
        self.size = size
        self.hovered = False
        self.grabbed = False

        self.slider_left_pos = self.pos[0] - (size[0]//2)
        self.slider_right_pos = self.pos[0] + (size[0]//2)
        self.slider_top_pos = self.pos[1] - (size[1]//2)

        self.min = min
        self.max = max
        self.initial_val = (self.slider_right_pos-self.slider_left_pos)*initial_val # <- percentage

        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10, self.size[1])

    def render(self, screen):
        pygame.draw.rect(screen, "darkgray", self.container_rect)
        pygame.draw.rect(screen, "blue", self.button_rect)
    def move_slider(self, mouse_pos):
        pos = mouse_pos[0]
        if pos < self.slider_left_pos:
            pos = self.slider_left_pos
        if pos > self.slider_right_pos:
            pos = self.slider_right_pos
        self.button_rect.centerx = pos

    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos - 1
        button_val = self.button_rect.centerx - self.slider_left_pos
        return (button_val / val_range) * (self.max - self.min) + self.min

if __name__ == '__main__':
    main()