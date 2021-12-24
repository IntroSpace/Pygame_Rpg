import os
import sys

import pygame
import pygame_menu

pygame.init()
WIDTH, HEIGHT = 1920, 1080
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.key.set_repeat(1, 20)
ACC = 0.4
FRIC = -0.10
COUNT = 0
vec = pygame.math.Vector2
FPS = 60
FPS_CLOCK = pygame.time.Clock()
pygame.display.set_caption("Game")
tile_size = HEIGHT // 20

# группа блоков
tiles_group = pygame.sprite.Group()
# группа всех спрайтов, кроме игрока
other_group = pygame.sprite.Group()


# Анимации для бега вправо
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


run_animation_RIGHT = [load_image("Player_Sprite_R.png"), load_image("Player_Sprite2_R.png"),
                       load_image("Player_Sprite3_R.png"), load_image("Player_Sprite4_R.png"),
                       load_image("Player_Sprite5_R.png"), load_image("Player_Sprite6_R.png")]

# Анимации для бега влево
run_animation_LEFT = [load_image("Player_Sprite_L.png"), load_image("Player_Sprite2_L.png"),
                      load_image("Player_Sprite3_L.png"), load_image("Player_Sprite4_L.png"),
                      load_image("Player_Sprite5_L.png"), load_image("Player_Sprite6_L.png")]

attack_animation_RIGHT = [load_image("Player_Sprite_R.png"), load_image("Player_Attack_R.png"),
                          load_image("Player_Attack2_R.png"), load_image("Player_Attack2_R.png"),
                          load_image("Player_Attack3_R.png"), load_image("Player_Attack3_R.png"),
                          load_image("Player_Attack4_R.png"), load_image("Player_Attack4_R.png"),
                          load_image("Player_Attack5_R.png"), load_image("Player_Attack5_R.png"),
                          load_image("Player_Sprite_R.png")]
attack_animation_LEFT = [load_image("Player_Sprite_L.png"), load_image("Player_Attack_L.png"),
                         load_image("Player_Attack2_L.png"), load_image("Player_Attack2_L.png"),
                         load_image("Player_Attack3_L.png"), load_image("Player_Attack3_L.png"),
                         load_image("Player_Attack4_L.png"), load_image("Player_Attack4_L.png"),
                         load_image("Player_Attack5_L.png"), load_image("Player_Attack5_L.png"),
                         load_image("Player_Sprite_L.png")]


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bgimage = pygame.transform.scale(load_image('background.jpg'), (1920, 1080))
        self.bgY = 0
        self.bgX = 0

    def render(self):
        surface.blit(self.bgimage, (self.bgX, self.bgY))


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(load_image("ground.png"), (1920, 300))
        self.rect = self.image.get_rect()
        self.rect.y = 780

    def render(self):
        surface.blit(self.image, (self.rect.x, self.rect.y))


class Tile(pygame.sprite.Sprite):
    def __init__(self, name, pos, *groups):
        super(Tile, self).__init__(tiles_group, *groups)
        self.image = pygame.transform.scale(load_image(name), (tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=(pos[0] * tile_size, pos[1] * tile_size))


class Land(Tile):
    def __init__(self, pos, *groups):
        super(Land, self).__init__('land.png', pos, *groups)


class Stone1(Tile):
    def __init__(self, pos, *groups):
        super(Stone1, self).__init__('stone1.png', pos, *groups)


class Sand(Tile):
    def __init__(self, pos, *groups):
        super(Sand, self).__init__('sand.png', pos, *groups)


class Level:
    @staticmethod
    def new_level(data):
        res_player = None
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile == 'L':
                    Land((x, y), other_group)
                if tile == 'S':
                    Sand((x, y), other_group)
                if tile == 'R':
                    Stone1((x, y), other_group)
                if tile == 'P':
                    res_player = Player((x, y))
        return res_player


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = load_image("Player_Sprite_R.png")
        self.rect = self.image.get_rect()
        # Атака
        self.attacking = False
        self.attack_frame = 0
        # Движение
        self.jumping = False
        self.running = False
        self.move_frame = 0
        # Позиция и направление
        self.vx = 0
        self.pos = vec((pos[0] * tile_size, pos[1] * tile_size))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"
        self.block_right = self.block_left = 0

    def move(self):
        sprite_list = pygame.sprite.spritecollide(self, other_group, False)
        self.block_right = self.block_left = 0
        if sprite_list:
            for sprite in sprite_list:
                rect = sprite.rect
                if not self.block_right and rect.collidepoint(self.rect.midright):
                    self.block_right = 1
                if not self.block_left and rect.collidepoint(self.rect.midleft):
                    self.block_left = 1

        self.acc = vec(0, 0.5)
        if abs(self.vel.x) > 0.5:
            self.running = True
        else:
            self.running = False
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.acc.x = -ACC
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.acc.x = ACC
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        if self.block_left:
            if self.vel.x < 0 or (self.vel.x == 0 and self.acc.x < 0):
                self.acc.x = self.vel.x = 0
        if self.block_right:
            if self.vel.x > 0 or (self.vel.x == 0 and self.acc.x > 0):
                self.acc.x = self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        self.rect.midbottom = self.pos

    def update(self):
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.jump()
        if self.move_frame > 10:
            self.move_frame = 0
            return
        if not self.jumping and self.running:
            if self.vel.x > 0:
                self.image = run_animation_RIGHT[self.move_frame // 2]
                self.direction = "RIGHT"
            elif self.vel.x == 0:
                if self.direction == 'RIGHT':
                    self.image = run_animation_RIGHT[self.move_frame // 2]
                elif self.direction == 'LEFT':
                    self.image = run_animation_LEFT[self.move_frame // 2]
            else:
                self.image = run_animation_LEFT[self.move_frame // 2]
                self.direction = "LEFT"
            self.move_frame += 1
        if self.jumping:
            self.move_frame = 4 * 2
            if self.vel.x > 0:
                self.direction = 'RIGHT'
            if self.vel.x < 0:
                self.direction = 'LEFT'
        if abs(self.vel.x) < 1 and self.move_frame != 0:
            self.move_frame = 0
            if self.direction == "RIGHT":
                self.image = run_animation_RIGHT[self.move_frame // 2]
            elif self.direction == "LEFT":
                self.image = run_animation_LEFT[self.move_frame // 2]

    def attack(self):
        if self.attack_frame > 10:
            self.attack_frame = 0
            self.attacking = False
        if self.direction == "RIGHT":
            self.image = attack_animation_RIGHT[self.attack_frame]
        elif self.direction == "LEFT":
            self.correction()
            self.image = attack_animation_LEFT[self.attack_frame]
        self.attack_frame += 1

    def correction(self):
        ...
        # if self.attack_frame == 1:
        #     self.pos.x -= 20
        # if self.attack_frame == 10:
        #     self.pos.x += 20

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.vel.y = -12

    def gravity_check(self):
        if self.vel.y > 0:
            if pygame.sprite.spritecollide(player, other_group, False):
                sprites = pygame.sprite.spritecollide(player, other_group, False)
                for sprite in sprites:
                    if sprite.rect.collidepoint(self.rect.bottomleft[0] + 5, self.rect.bottomleft[1])\
                            or sprite.rect.collidepoint(self.rect.bottomright[0] - 5, self.rect.bottomright[1]):
                        self.pos.y = sprite.rect.top + 1
                        self.vel.y = 0
                        self.jumping = False
        elif self.vel.y < 0:
            if pygame.sprite.spritecollide(player, other_group, False):
                for sprite in pygame.sprite.spritecollide(player, other_group, False):
                    if sprite.rect.collidepoint(self.rect.topleft[0] + 5, self.rect.topleft[1])\
                            or sprite.rect.collidepoint(self.rect.topright[0] - 5, self.rect.topright[1]):
                        self.vel.y *= -1
                        self.acc.y *= -1
                        break


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


def set_difficulty(value, difficulty):
    pass


def load_level_data(filename):
    with open(f'levels/{filename}.map', mode='r', encoding='utf8') as f:
        return Level.new_level(map(str.strip, f.readlines()))


background = Background()
player = load_level_data('level1')


def start_the_game():
    running = True
    while running:
        player.gravity_check()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not player.attacking:
                        player.attack()
                        player.attacking = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not player.attacking:
                        player.attack()
                        player.attacking = True
        surface.fill((0, 0, 0))
        player.update()
        if player.attacking:
            player.attack()
        player.move()
        background.render()
        tiles_group.draw(surface)
        surface.blit(player.image, player.rect)
        pygame.display.flip()
        FPS_CLOCK.tick(FPS)


menu = pygame_menu.Menu('Welcome', 1920, 1080,
                        theme=pygame_menu.themes.THEME_DARK)

menu.add.text_input('Name: ', default='John Doe')
menu.add.selector('Difficulty: ', [('Hard', 3), ('Medium', 2), ('Easy', 1)], onchange=set_difficulty)
menu.add.button('Play', start_the_game)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(surface)