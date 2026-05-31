# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 11:05:00 2013
@author: Leo
"""

import pygame
from sys import exit
from pygame.locals import *
from gameRole import *
import random

# 初始化游戏
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('飞机大战')

# 载入游戏音乐
bullet_sound = pygame.mixer.Sound('resources/sound/bullet.wav')
enemy1_down_sound = pygame.mixer.Sound('resources/sound/enemy1_down.wav')
game_over_sound = pygame.mixer.Sound('resources/sound/game_over.wav')
bullet_sound.set_volume(0.3)
enemy1_down_sound.set_volume(0.3)
game_over_sound.set_volume(0.3)
pygame.mixer.music.load('resources/sound/game_music.wav')
pygame.mixer.music.set_volume(0.25)

# 载入背景图
background = pygame.image.load('resources/image/background.png').convert()
game_over = pygame.image.load('resources/image/gameover.png')

filename = 'resources/image/shoot.png'
plane_img = pygame.image.load(filename)

# 设置玩家图片切片参数
player_rect = []
player_rect.append(pygame.Rect(0, 99, 100, 115))        # 玩家精灵图片区域
player_rect.append(pygame.Rect(165, 360, 100, 115))
player_rect.append(pygame.Rect(165, 234, 100, 115))     # 玩家爆炸精灵图片区域
player_rect.append(pygame.Rect(330, 624, 100, 115))
player_rect.append(pygame.Rect(330, 498, 100, 115))
player_rect.append(pygame.Rect(432, 624, 100, 126))

# 定义子弹对象使用的surface相关参数
bullet_rect = pygame.Rect(1004, 987, 9, 21)
bullet_img = plane_img.subsurface(bullet_rect)

# 定义普通敌机对象使用的surface相关参数
enemy1_rect = pygame.Rect(534, 612, 57, 43)
enemy1_img = plane_img.subsurface(enemy1_rect)

enemy1_down_imgs = []
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 347, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(873, 697, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 296, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(930, 697, 57, 43)))

# 定义 Boss 对象使用的 surface 相关参数
boss_rect = pygame.Rect(335, 750, 170, 250) 
boss_img = plane_img.subsurface(boss_rect)

boss_down_imgs = []
boss_down_imgs.append(plane_img.subsurface(pygame.Rect(165, 747, 165, 261)))
boss_down_imgs.append(plane_img.subsurface(pygame.Rect(330, 747, 165, 261)))
boss_down_imgs.append(plane_img.subsurface(pygame.Rect(495, 747, 165, 261)))
boss_down_imgs.append(plane_img.subsurface(pygame.Rect(660, 747, 165, 261)))

clock = pygame.time.Clock()

# 截取炸弹道具贴图 (这里切取的是精灵图里的一颗蓝色小炮弹)
prop_rect = pygame.Rect(267, 398, 63, 88) 
prop_img = plane_img.subsurface(prop_rect)

# 截取 Boss 专属炮弹贴图 (这里切取的是精灵图里的一颗红色小炮弹)
boss_bullet_rect = pygame.Rect(100, 115, 65, 111) 
boss_bullet_img = plane_img.subsurface(boss_bullet_rect)

# ==================== 核心修改：游戏主生命周期大循环 ====================
while True:
# 每次“重新开始”时，必须重置的所有游戏数据
    player_pos = [200, 600]
    player = Player(plane_img, player_rect, player_pos)
    
    enemies1 = pygame.sprite.Group()
    boss_enemies = pygame.sprite.Group()
    enemies_down = pygame.sprite.Group()
    bomb_props = pygame.sprite.Group()

    shoot_frequency = 0
    enemy_frequency = 0
    player_down_index = 16 
    score = 0

    # 重新播放背景音乐
    pygame.mixer.music.play(-1, 0.0)
    
    running = True

    # 游戏单局主循环
    while running:
        clock.tick(45)

        # 控制发射子弹频率
        if not player.is_hit:
            if shoot_frequency % 15 == 0:
                bullet_sound.play()
                player.shoot(bullet_img)
            shoot_frequency += 1
            if shoot_frequency >= 15:
                shoot_frequency = 0

        # 动态难度与生成逻辑
        if score < 5000:
            spawn_rate = 60  # 起步稍慢
        elif score < 15000:  # 扩大这个分段的范围
            spawn_rate = 50  # 即使分数高了，生成速度也控制在50帧
        else:
            spawn_rate = 40  # 最后期才降到40帧，防止屏幕被塞满

        # --- 随机生成炸弹道具 ---
        # 设置千分之二的概率，大概每 10-15 秒掉落一个
        if random.randint(1, 500) == 1:
            prop_pos = [random.randint(0, SCREEN_WIDTH - prop_rect.width), -prop_rect.height]
            prop = BombProp(prop_img, prop_pos)
            bomb_props.add(prop)

        # --- 移动道具并检测玩家拾取 ---
        for prop in bomb_props.copy():
            prop.move()
            # 检测玩家是否接到了道具 (使用像素级检测)
            if pygame.sprite.collide_mask(prop, player):
                player.bomb_count += 1  # 玩家背包炸弹数 +1
                prop.kill()             # 道具从屏幕消失
                continue
            # 道具掉出屏幕底部
            if prop.rect.top > SCREEN_HEIGHT:
                prop.kill()
        # 生成普通敌机
        if enemy_frequency % spawn_rate == 0:
            enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1_rect.width), 0]
            enemy1 = Enemy(enemy1_img, enemy1_down_imgs, enemy1_pos)
            enemies1.add(enemy1)
        enemy_frequency += 1
        if enemy_frequency >= 100:
            enemy_frequency = 0

        # 生成 Boss 敌机 (每当分数是 30000 的倍数且当前没有 Boss 时)
        if score > 0 and score % 30000 == 0 and len(boss_enemies) == 0:
            boss_pos = [random.randint(0, SCREEN_WIDTH - boss_rect.width), -boss_rect.height]
            boss = BossEnemy(boss_img, boss_down_imgs, boss_pos)
            boss_enemies.add(boss)

        # 移动玩家子弹
        for bullet in player.bullets.copy():
            bullet.move()
            if bullet.rect.bottom < 0:
                bullet.kill()

        # 移动普通敌机并检测碰撞
        for enemy in enemies1.copy():      
            enemy.move()
            if pygame.sprite.collide_mask(enemy, player):
                enemy.kill()               # 第一步：先彻底抹除物理碰撞
                enemies_down.add(enemy)    # 第二步：再加回爆炸动画组
                player.is_hit = True
                game_over_sound.play()
                break
            if enemy.rect.top > SCREEN_HEIGHT:
                enemy.kill()          

        # 移动 Boss、控制射击 并检测碰撞
        for boss in boss_enemies:
            boss.move()
            
            # --- Boss 开火逻辑 ---
            if boss.shoot_frequency % 200 == 0:  # 每 200 帧发射一颗炮弹
                boss.shoot(boss_bullet_img)
            boss.shoot_frequency += 1
            if boss.shoot_frequency >= 200:
                boss.shoot_frequency = 0

            # 玩家直接撞到 Boss 判定被击中
            if pygame.sprite.collide_mask(boss, player):
                player.is_hit = True
                game_over_sound.play()
                break
            if boss.rect.top > SCREEN_HEIGHT:
                boss_enemies.remove(boss)

            # --- 移动 Boss 的炮弹并检测是否击中玩家 ---
            for b in boss.bullets.copy():
                b.move()
                # 炮弹飞出屏幕底部则删除
                if b.rect.top > SCREEN_HEIGHT:
                    b.kill()
                
                # 如果 Boss 的炮弹打中了玩家
                if pygame.sprite.collide_mask(b, player):
                    player.is_hit = True
                    game_over_sound.play()
                    break
        # 子弹击中 Boss 逻辑
        for boss in boss_enemies:
            # 在括号最后面加上 pygame.sprite.collide_mask
            hit_bullets = pygame.sprite.spritecollide(boss, player.bullets, True, pygame.sprite.collide_mask)
            for b in hit_bullets:
                boss.hp -= 1
                if boss.hp <= 0:
                    enemies_down.add(boss)
                    boss_enemies.remove(boss)
                    score += 5000  
                    break

        # 子弹击中普通敌机逻辑
        enemies1_down = pygame.sprite.groupcollide(enemies1, player.bullets, 1, 1, pygame.sprite.collide_mask)
        for enemy_down in enemies1_down:
            enemies_down.add(enemy_down)

        # 绘制背景
        screen.fill(0)
        screen.blit(background, (0, 0))

        # 绘制玩家飞机及坠毁动画
        if not player.is_hit:
            player.img_index = shoot_frequency // 8
            screen.blit(player.image[player.img_index], player.rect)
            player.update()  # <--- 新增：正常飞行时，同步刷新尾部火焰的碰撞遮罩
        else:
            player.img_index = player_down_index // 8
            screen.blit(player.image[player.img_index], player.rect)
            player.update()  # <--- 新增：爆炸时，同步刷新破碎形状的碰撞遮罩
            
            player_down_index += 1
            if player_down_index > 47:
                running = False  # 玩家坠毁动画播放完毕

        # 绘制敌机击毁动画
        for enemy_down in enemies_down:
            if enemy_down.down_index == 0:
                enemy1_down_sound.play()
            if enemy_down.down_index > 7:
                enemies_down.remove(enemy_down)
                score += 1000
                continue
            screen.blit(enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)
            enemy_down.down_index += 1

        # 绘制所有实体
        player.bullets.draw(screen)
        enemies1.draw(screen)
        boss_enemies.draw(screen)
        bomb_props.draw(screen)
        # 绘制 Boss 的炮弹
        for boss in boss_enemies:
            boss.bullets.draw(screen)

        # 绘制 Boss 血条 (全屏压迫感大血条 - 固定在屏幕最底部)
        for boss in boss_enemies:
            # 设定血条的宽度、高度和位置
            bar_width = SCREEN_WIDTH - 40     # 宽度为屏幕宽度减去两边留白
            bar_height = 15                   # 血条变粗一点，15个像素
            bar_x = 20                        # 距离屏幕左边 20 像素
            bar_y = SCREEN_HEIGHT - 30        # 距离屏幕底部 30 像素
            
            # 画红色底色（空血槽）
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # 画绿色当前血量
            health_ratio = max(0, boss.hp / boss.max_hp)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
            # 给血条加个白色的边框，看起来更精致
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # 绘制实时得分
        score_font = pygame.font.Font(None, 36)
        score_text = score_font.render(str(score), True, (128, 128, 128))
        text_rect = score_text.get_rect()
        text_rect.topleft = [10, 10]
        screen.blit(score_text, text_rect)

        # ====== 在主界面左上角（分数下方）显示炸弹数量 ======
        bomb_text = score_font.render('Bombs: ' + str(player.bomb_count), True, (255, 0, 0)) # 用红色字显示
        bomb_rect = bomb_text.get_rect()
        bomb_rect.topleft = [10, 40]  # 放在分数下面一点
        screen.blit(bomb_text, bomb_rect)

        pygame.display.update()

        # 常规事件监听（包含 ESC 暂停逻辑 和 大招逻辑）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # --- 大招逻辑：按下空格键 ---
                if event.key == K_SPACE and player.bomb_count > 0:
                    player.bomb_count -= 1  # 消耗一颗炸弹
                    
                    # 1. 秒杀全屏普通敌机
                    for enemy in enemies1.copy():
                        enemy.kill()             # 第一步：先彻底抹除物理碰撞
                        enemies_down.add(enemy)  # 第二步：再将它加入爆炸动画组
                        # （不需要在这里 score += 1000，因为爆炸动画播完时底层会自动加分！）
                        
                    # 2. 对 Boss 造成成吨伤害
                    for boss in boss_enemies.copy():
                        boss.hp -= 10
                        for b in boss.bullets.copy():
                            b.kill()
                        if boss.hp <= 0:
                            boss.kill()             # 第一步：先抹除物理碰撞
                            enemies_down.add(boss)  # 第二步：再加入爆炸动画组
                            score += 5000
                
                # --- 暂停逻辑：按下 ESC 键 ---
                # (注意！只留下面这一个 K_ESCAPE 判断块，把之前多余的删掉)
                if event.key == K_ESCAPE: 
                    is_paused = True
                    pause_font = pygame.font.Font(None, 80)
                    pause_text = pause_font.render('PAUSED', True, (255, 215, 0))
                    text_rect = pause_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                    screen.blit(pause_text, text_rect)
                    pygame.display.update()
                    while is_paused:
                        for pause_event in pygame.event.get():
                            if pause_event.type == pygame.QUIT:
                                pygame.quit()
                                exit()
                            if pause_event.type == pygame.KEYDOWN:
                                if pause_event.key == K_ESCAPE:
                                    is_paused = False
                
        # 玩家走位控制
        key_pressed = pygame.key.get_pressed()
        if not player.is_hit:
            if key_pressed[K_w] or key_pressed[K_UP]:
                player.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                player.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                player.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                player.moveRight()

    # ==================== 核心修改：游戏结算与交互界面 ====================
    pygame.mixer.music.stop() # 停止单局背景音乐
    
    # 渲染结算画面
    screen.blit(game_over, (0, 0))
    
    # 1. 渲染最终得分
    font_score = pygame.font.Font(None, 48)
    text_score = font_score.render('Final Score: ' + str(score), True, (255, 0, 0))
    rect_score = text_score.get_rect(centerx=SCREEN_WIDTH/2, centery=250)
    screen.blit(text_score, rect_score)

    # 2. 渲染交互提示菜单 (由于默认字体不支持中文，采用标准英文提示避坑)
    font_tip = pygame.font.Font(None, 32)
    text_tip = font_tip.render('Press [R] to Restart / [Q] to Quit', True, (255, 255, 255))
    rect_tip = text_tip.get_rect(centerx=SCREEN_WIDTH/2, centery=450)
    screen.blit(text_tip, rect_tip)
    
    pygame.display.update()

    # 等待玩家做出选择的阻塞循环
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_r:          # 按下 R 键：打破等待状态，回到最外层循环重新初始化
                    waiting_for_input = False
                if event.key == K_q:          # 按下 Q 键：安全退出游戏
                    pygame.quit()
                    exit()