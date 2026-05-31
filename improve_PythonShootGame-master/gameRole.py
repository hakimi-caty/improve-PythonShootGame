# -*- coding: utf-8 -*-
import pygame

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800

# 玩家子弹
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midbottom = init_pos
        self.speed = 10
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.rect.top -= self.speed

# Boss 子弹
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midtop = init_pos
        self.speed = 3  # 这里调小了速度，让它慢一些
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.rect.top += self.speed

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rect, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []
        for i in range(len(player_rect)):
            self.image.append(plane_img.subsurface(player_rect[i]).convert_alpha())
        self.rect = player_rect[0].copy()
        self.rect.topleft = init_pos
        self.speed = 8
        self.bullets = pygame.sprite.Group()
        self.img_index = 0
        self.is_hit = False
        self.mask = pygame.mask.from_surface(self.image[0])
        self.bomb_count = 0  # 初始炸弹数量为 0

    def shoot(self, bullet_img):
        bullet = Bullet(bullet_img, self.rect.midtop)
        self.bullets.add(bullet)

    def update(self):
        self.mask = pygame.mask.from_surface(self.image[self.img_index])

    def moveUp(self):
        if self.rect.top > 0: self.rect.top -= self.speed
    def moveDown(self):
        if self.rect.top < SCREEN_HEIGHT - self.rect.height: self.rect.top += self.speed
    def moveLeft(self):
        if self.rect.left > 0: self.rect.left -= self.speed
    def moveRight(self):
        if self.rect.left < SCREEN_WIDTH - self.rect.width: self.rect.left += self.speed

# 普通敌机
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.down_imgs = enemy_down_imgs
        self.speed = 2
        self.down_index = 0
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.rect.top += self.speed

# Boss 类
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self, boss_img, boss_down_imgs, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = boss_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.down_imgs = boss_down_imgs
        self.speed = 1
        self.down_index = 0
        self.hp = 15
        self.max_hp = 15
        self.direction = 1
        self.bullets = pygame.sprite.Group()
        self.shoot_frequency = 0
        self.mask = pygame.mask.from_surface(self.image)

    def shoot(self, bullet_img):
        bullet = BossBullet(bullet_img, self.rect.midbottom)
        self.bullets.add(bullet)

    def move(self):
        self.rect.top += self.speed
        self.rect.left += 2 * self.direction
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1

# 炸弹道具类 (缓慢下落)
class BombProp(pygame.sprite.Sprite):
    def __init__(self, prop_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = prop_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.speed = 2  # 道具下落速度，可以稍微慢一点方便玩家接
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.rect.top += self.speed