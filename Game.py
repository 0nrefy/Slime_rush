import random
from datetime import datetime

import pygame
import sys
import os


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, group, sheet, columns, rows, x, y):
        super().__init__(group)
        self.frames = []
        self.col, self.row = columns, rows
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                for _ in range(0, 64 // self.col * self.row):
                    self.frames.append(pygame.transform.scale(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)), (150, 150)).convert_alpha())

    def get_frames(self):
        return self.frames

    def set_frames(self, new_frames):
        self.frames = new_frames

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, pos, size):
        super().__init__(all_sprites)
        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color('grey'))
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Level(Sprite):
    def __init__(self):
        super().__init__(level_group)


class Slime(AnimatedSprite):
    def __init__(self, pos, sheet, columns, rows, x, y):
        super().__init__(all_sprites, sheet, columns, rows, x, y)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.jump_value = 20
        self.health = 5
        self.damage = 1
        self.exp = 0
        self.artifact = {
            'weapon': 0,
            'speed': 0,
        }

    def update(self):
        super().update()


class Monster(AnimatedSprite):
    def __init__(self, pos, sheet, columns, rows, x, y, hp):
        super().__init__(all_sprites, sheet, columns, rows, x, y)
        self.add(monster_group)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.hp = hp
        self.last_move = 0
        self.move_x, self.move_y = 0, 0

    def update(self):
        super().update()
        if self.rect.x > player.rect.x:
            self.move_x = -3
        elif self.rect.x < player.rect.x:
            self.move_x = 3
        if self.rect.y > player.rect.y:
            self.move_y = -3
        elif self.rect.y < player.rect.y:
            self.move_y = 3
        if self.last_move != self.move_x:
            for i in range(len(self.frames)):
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
        self.rect.x += self.move_x
        self.rect.y += self.move_y
        self.last_move = self.move_x
        if self.hp < 0:
            self.remove()

    def damage(self, damage):
        if player.rect.collidepoint(self.rect.x, self.rect.y):
            self.hp -= damage


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = [load_image('Slime_rush.png', -1), load_image('button.png', -1)]
    fon = pygame.transform.scale(load_image('start_image.png'), screen_size)
    screen.blit(fon, (0, 0))
    text = Sprite(start_screen_group)
    text.image = intro_text[0]
    text.image = pygame.transform.scale(text.image, (1500, 500)).convert_alpha()
    text.rect = (width // 9, height // 7)
    text2 = Sprite(start_screen_group)
    text2.image = intro_text[1]
    text2.image = pygame.transform.scale(text2.image, (1000, 250)).convert_alpha()
    text2.rect = (width // 4, height // 1.5)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        start_screen_group.draw(screen)
        start_screen_group.update()
        pygame.display.flip()
        clock.tick(FPS)


def check_level(side):
    global cur_loc
    try:
        c_loc = cur_loc
        if side == 'right':
            c_loc += 1
            loc = rooms[c_loc]
        if side == 'left':
            c_loc -= 1
            if c_loc >= 0:
                loc = rooms[c_loc]
            else:
                raise IndexError
        cur_loc = c_loc
        return True
    except IndexError:
        return False


def move(side):
    global right, left
    global right_w, left_w
    if side == 'right':
        if left_w:
            for i in range(len(player.frames)):
                player.frames[i] = pygame.transform.flip(player.frames[i], True, False)
        right_w, left_w = True, False
        right, left = True, False
    elif side == 'left':
        if right_w:
            for i in range(len(player.frames)):
                player.frames[i] = pygame.transform.flip(player.frames[i], True, False)
        right_w, left_w = False, True
        right, left = False, True


pygame.init()
screen_size = width, height = (1920, 1080)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Slime rush')
FPS = 60

images_sprites = {
    'player': load_image('Slime.png', -1),
    'skeleton': load_image('Skeleton.png', -1),
    'zombie': load_image('Zombie.png', -1),
    'ratatuy': load_image('ratatuy.png', -1),
    'button': load_image('button.png', -1)
}

all_sprites = SpriteGroup()
clock = pygame.time.Clock()
doors_group = SpriteGroup()
monster_group = SpriteGroup()
level_group = SpriteGroup()
start_screen_group = SpriteGroup()
right, left = False, False
right_w, left_w = True, False
up, down = False, False
jump_max = 0
cur_loc = 0
rooms = [pygame.transform.scale(load_image('start_screen.png'), screen_size),
         pygame.transform.scale(load_image('level_2.png'), screen_size),
         pygame.transform.scale(load_image('level_3.png'), screen_size)]


start_screen()
player = Slime((1920 // 2, 800), images_sprites['player'], 4, 1, 0, 0)
skeleton = Monster((500, 500), images_sprites['skeleton'], 4, 1, 0, 0, 3)
zombie = Monster((700, 500), images_sprites['zombie'], 4, 1, 0, 0, 3)
ratatuy = Monster((900, 500), images_sprites['ratatuy'], 4, 1, 0, 0, 1)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and not right:
                move('right')
            if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and not left:
                move('left')
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and not down:
                up, down = True, False
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not up:
                down, up = True, False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i in monster_group:
                    if i.rect.collidepoint(player.rect.x, player.rect.y):
                        i.damage(player.damage + player.artifact['weapon'])
        if event.type == pygame.KEYUP:
            if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and not left:
                right = False
            if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and not right:
                left = False
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and not down:
                up = False
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not up:
                down = False
    if right:
        player.rect.x += 7
        if player.rect.x + 150 > width:
            if check_level('right'):
                player.rect.x = 0
            else:
                player.rect.x -= 7
    elif left:
        player.rect.x -= 7
        if player.rect.x < 0:
            if check_level('left'):
                player.rect.x = width - 150
            else:
                player.rect.x += 7
    if up:
        player.rect.y -= 7
        if player.rect.y + 150 // 2 < 0:
            player.rect.y += 7
    elif down:
        player.rect.y += 7
        if player.rect.y + 150 > height:
            player.rect.y = height - 150
    fon = rooms[cur_loc]
    screen.blit(fon, (0, 0))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
