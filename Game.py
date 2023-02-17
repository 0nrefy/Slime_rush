import random

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
                for _ in range(0, 60 // self.col * self.row):
                    self.frames.append(pygame.transform.scale(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)), (150, 150)).convert_alpha())

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None


class Heart(Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.image = images_sprites['heart']
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self):
        super().update()


class Button(Sprite):
    def __init__(self, group, pos, image):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.width = int(self.rect.w)
        self.height = int(self.rect.h)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.pressed = False

    def update(self):
        super().update()
        x, y = pygame.mouse.get_pos()
        if self.rect.x <= x <= self.rect.x + self.width and self.rect.y <= y <= self.rect.y + self.height:
            self.image = images_sprites['pressed_button']
            self.pressed = True
        else:
            self.image = images_sprites['not_pressed_button']
            self.pressed = False


class Slime(AnimatedSprite):
    def __init__(self, pos, sheet, columns, rows, x, y):
        super().__init__(all_sprites, sheet, columns, rows, x, y)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.health = 5
        self.damage = 1
        self.speed = 7
        self.max_hp = 5

    def update(self):
        super().update()


class Monster(AnimatedSprite):
    def __init__(self, pos, sheet, columns, rows, x, y, hp, attack_sheet, co_attack, r_attack):
        super().__init__(all_sprites, sheet, columns, rows, x, y)
        self.add(monster_group)
        self.image_walk = sheet
        self.attack_image = attack_sheet
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.columns, self.rows = columns, rows
        self.columns_attack, self.rows_attack = co_attack, r_attack
        self.hp = hp
        self.last_move = 0
        self.move_x, self.move_y = 0, 0
        self.attack = False
        self.attack_c = 0
        self.l_r = False

    def update(self):
        super().update()
        global hearts
        if self.rect.x > player.rect.x:
            self.move_x = -3
        elif self.rect.x < player.rect.x:
            self.move_x = 3
        if self.rect.y > player.rect.y:
            self.move_y = -3
        elif self.rect.y < player.rect.y:
            self.move_y = 3
        if self.last_move != self.move_x:
            self.l_r = not self.l_r
            for i in range(len(self.frames)):
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
        if pygame.sprite.collide_mask(self, player):
            self.attack = True
        if not self.attack:
            self.rect.x += self.move_x
            self.rect.y += self.move_y
        else:
            self.attack_c += 1
        self.last_move = self.move_x
        if self.attack_c >= 80:
            self.attack = False
            self.attack_c = 0
            self.update_frames()
            if player.max_hp != player.health:
                if player.health >= 0:
                    try:
                        for _ in range(player.max_hp - player.health):
                            if _ == 0:
                                index = -1
                            else:
                                index = -_
                            hearts[index].image = images_sprites['break_heart']
                    except Exception:
                        pass
        elif self.attack_c == 50:
            if pygame.sprite.collide_mask(self, player):
                player.health -= 1
            self.update_frames()
        if self.hp <= 0:
            monster_group.remove(self)
            all_sprites.remove(self)

    def damage(self, damage):
        self.hp -= damage

    def update_frames(self):
        rect = self.rect
        self.frames = []
        if self.attack:
            self.cut_sheet(self.attack_image, self.columns_attack, self.rows_attack)
            if self.l_r:
                for i in range(len(self.frames)):
                    self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
        else:
            self.cut_sheet(self.image_walk, self.columns, self.rows)
            if self.l_r:
                for i in range(len(self.frames)):
                    self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
        self.rect = rect


class Room:
    def __init__(self):
        self.mobs = random.randint(3, 6)
        self.checked = False


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('start_image.png'), screen_size)
    screen.blit(fon, (0, 0))
    slime_rush = Sprite(start_screen_group)
    slime_rush.image = load_image('Slime_rush.png', -1)
    slime_rush.image = pygame.transform.scale(slime_rush.image, (1500, 500)).convert_alpha()
    slime_rush.rect = (width // 9, height // 7)
    button = Button(start_screen_group, (width // 2.5, height // 1.5), images_sprites['not_pressed_button'])
    button_exit = Button(start_screen_group, (width // 2.5, height // 1.2), images_sprites['not_pressed_button'])
    font = pygame.font.SysFont("comicsans", 30)
    text = font.render('Начать игру', True, (255, 255, 255))
    text2 = font.render('Выйти', True, (255, 255, 255))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.pressed and event.button == 1:
                    return
                elif button_exit.pressed and event.button == 1:
                    terminate()
        button.image.blit(text, (button.image.get_rect().w // 3.5, button.image.get_rect().h // 4))
        button_exit.image.blit(text2, (button_exit.image.get_rect().w // 3.5,
                                       button_exit.image.get_rect().h // 4))
        screen.blit(fon, screen_size)
        start_screen_group.draw(screen)
        start_screen_group.update()
        pygame.display.flip()
        clock.tick(FPS)


def over_screen(img):
    fon = pygame.transform.scale(load_image('map.png'), screen_size)
    screen.blit(fon, (0, 0))
    text = Sprite(over_screen_group)
    text.image = pygame.transform.scale(load_image(img, -1), (500, 500)).convert_alpha()
    text.rect = (width // 2.6, height // 7)
    button = Button(over_screen_group, (width // 2.5, height // 1.5), images_sprites['not_pressed_button'])
    button_exit = Button(button_group, (width // 2.5, height // 1.2), images_sprites['not_pressed_button'])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button.pressed and event.button == 1:
                    return
                elif button_exit.pressed and event.button == 1:
                    terminate()
        button_group.draw(screen)
        button_group.update()
        over_screen_group.draw(screen)
        over_screen_group.update()
        pygame.display.flip()
        clock.tick(FPS)


def check_level(side):
    global cur_loc
    if not monster_group:
        rooms[cur_loc] = False
    if not rooms[cur_loc]:
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
            if rooms[c_loc] == 'over':
                monster = Monster((1920 - 500, 1080 - 300), images_sprites['boss'], 4, 1, 0, 0, 10,
                                  images_sprites['boss_attacking'], 6, 1)
            elif rooms[c_loc]:
                for i in range(random.randint(1, 6)):
                    mob = random.choice(['ratatuy', 'skeleton', 'zombie'])
                    if mob == 'zombie':
                        c, r = 5, 1
                    else:
                        c, r = 4, 1
                    monster = Monster((random.randint(400, 1920), random.randint(200, 980)),
                                      images_sprites[mob], 4, 1, 0, 0,
                                      random.randint(1, 6), images_sprites[f'{mob}_attacking'], c, r)
            return True
        except IndexError:
            return False


def generate_hearts():
    global hearts
    hearts = []
    for _ in range(1, player.max_hp + 1):
        heart = Heart((1915 - 128 * _, 0))
        hearts.append(heart)


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
pygame.display.set_caption('Slime Rush')
FPS = 60

images_sprites = {
    'player': load_image('Slime.png', -1),
    'skeleton': load_image('Skeleton.png', -1),
    'zombie': load_image('Zombie.png', -1),
    'ratatuy': load_image('ratatuy.png', -1),
    'player_attack': load_image('slime_attack.png', -1),
    'map': pygame.transform.scale(load_image('map.png', -1), (1920, 1080)),
    'heart': pygame.transform.scale(load_image('heart.png', -1), (128, 128)).convert_alpha(),
    'break_heart': pygame.transform.scale(load_image('heart_broken.png', -1), (128, 128)).convert_alpha(),
    'not_pressed_button': pygame.transform.scale(load_image('not_pressed_button.png', -1), (384, 96)).convert_alpha(),
    'pressed_button': pygame.transform.scale(load_image('pressed_button.png', -1), (384, 96)).convert_alpha(),
    'boss': pygame.transform.scale(load_image('Boss_slime.png', -1), (512, 512)).convert_alpha(),
    'boss_attacking': pygame.transform.scale(load_image('Boss_slime_attack.png', -1), (512, 512)).convert_alpha(),
    'zombie_attacking': load_image('Zombie_attack.png', -1),
    'skeleton_attacking': load_image('Skeleton_attack.png', -1),
    'ratatuy_attacking': load_image('ratatuy_attack.png', -1)
}
start_screen_group = SpriteGroup()
over_screen_group = SpriteGroup()
clock = pygame.time.Clock()
button_group = SpriteGroup()
heart_group = SpriteGroup()
all_sprites = SpriteGroup()
monster_group = SpriteGroup()
right, left = False, False
right_w, left_w = False, True
up, down = False, False
attack = False
c_attack = 0
cur_loc = 0
hearts = []

start_screen()
player = Slime((1920 // 2, 1080 // 2), images_sprites['player'], 4, 1, 0, 0)
generate_hearts()

rooms = [False, True, True, 'over']
running = True

while running:
    rect = player.rect
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
            if event.button == 1 and not attack:
                attack = True
                player.frames = []
                player.cut_sheet(images_sprites['player_attack'], 6, 1)
                player.rect = rect
                if left_w:
                    for i in range(len(player.frames)):
                        player.frames[i] = pygame.transform.flip(player.frames[i], True, False)
                for i in monster_group:
                    for j in range(150):
                        if i.rect.collidepoint(player.rect.x + j, player.rect.y + j):
                            i.damage(player.damage)
                            break
        if event.type == pygame.KEYUP:
            if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and not left:
                right = False
            if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and not right:
                left = False
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and not down:
                up = False
            if (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not up:
                down = False
    if player.health <= 0:
        over_screen('Game_over.png')
        button_group = SpriteGroup()
        heart_group = SpriteGroup()
        all_sprites = SpriteGroup()
        monster_group = SpriteGroup()
        right, left = False, False
        right_w, left_w = False, True
        up, down = False, False
        attack = False
        c_attack = 0
        cur_loc = 0
        hearts = []
        player = Slime((1920 // 2, 1080 // 2), images_sprites['player'], 4, 1, 0, 0)
        generate_hearts()

        rooms = [False, True, True, 'over']
        running = True
    if rooms[cur_loc] == 'over' and not monster_group:
        over_screen('Win.png')
    if attack:
        c_attack += 1
        if c_attack > 20:
            c_attack = 0
            attack = False
            player.frames = []
            player.cut_sheet(images_sprites['player'], 4, 1)
            player.rect = rect
    if right:
        player.rect.x += player.speed
        if player.rect.x + 130 > width:
            if check_level('right'):
                player.rect.x = 0
            else:
                player.rect.x -= player.speed
    elif left:
        player.rect.x -= player.speed
        if player.rect.x <= -20:
            if check_level('left'):
                player.rect.x = width - 130
            else:
                player.rect.x += player.speed
    if up:
        player.rect.y -= player.speed
        if player.rect.y + 150 // 2 < 0:
            player.rect.y += player.speed
    elif down:
        player.rect.y += player.speed
        if player.rect.y + 150 > height:
            player.rect.y = height - 150
    screen.blit(images_sprites['map'], (0, 0))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
