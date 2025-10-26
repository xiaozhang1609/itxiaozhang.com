---
title: Python小游戏开发：贪吃蛇的实现
permalink: /python-mini-game-development-snake-implementation/
date: 2024-03-27 13:54:02
description: 本文介绍了如何使用Python和Pygame库开发经典的贪吃蛇小游戏。提供详细的玩法，和完整的代码。
category: 
- 编程案例
tags:
- python
- 贪吃蛇
---

> 原文地址：<https://itxiaozhang.com/python-mini-game-development-snake-implementation/>  

## 介绍

这是一个经典的贪吃蛇游戏，通过 Pygame 库实现。玩家控制蛇在屏幕上移动，吃掉食物以增长蛇的长度，同时避免撞到墙壁或蛇身。游戏包含主菜单、得分显示和重玩功能。

## 玩法

1. **启动游戏**：运行 `snake_game.py` 文件，打开游戏界面。
2. **主菜单**：
   - 使用上下方向键选择菜单项。
   - 按回车键确认选择。
   - 菜单选项包括开始游戏、继续游戏、暂停游戏和结束游戏。
3. **控制蛇**：
   - 使用方向键（上下左右）控制蛇的移动方向。
   - 吃掉红色方块（食物）以增加长度和得分。
4. **游戏重启**：
   - 当蛇撞到墙壁或自身时，游戏结束。
   - 按空格键重新开始游戏。

## 游戏目标

- 尽可能吃掉更多食物，获得更高的得分。
- 避免撞到墙壁或自身，使蛇尽量长时间存活。

## 代码

```python
import pygame
import random

WIDTH = 600
HEIGHT = 600

class Snake:
    def __init__(self, screen):
        self.screen = screen
        self.body = []
        self.fx = pygame.K_RIGHT
        self.init_body()

    def init_body(self, length=5):
        left, top = (100, 100)
        for i in range(length):
            if self.body:
                left, top = self.body[0].left, self.body[0].top
                node = pygame.Rect(left + 20, top, 20, 20)
            else:
                node = pygame.Rect(left, top, 20, 20)
            self.body.insert(0, node)

    def draw_snake(self):
        for n in self.body:
            pygame.draw.rect(self.screen, (62, 122, 178), n, 0)

    def add_node(self):
        if self.body:
            left, top = self.body[0].left, self.body[0].top
            if self.fx == pygame.K_RIGHT:
                left += 20
            elif self.fx == pygame.K_LEFT:
                left -= 20
            elif self.fx == pygame.K_UP:
                top -= 20
            else:
                top += 20
            node = pygame.Rect(left, top, 20, 20)
            self.body.insert(0, node)

    def del_node(self):
        self.body.pop()

    def move(self):
        self.del_node()
        self.add_node()

    def change(self, fx):
        LR = [pygame.K_LEFT, pygame.K_RIGHT]
        UD = [pygame.K_UP, pygame.K_DOWN]
        if fx in LR + UD:
            if fx in LR and self.fx in LR:
                return
            if fx in UD and self.fx in UD:
                return
            self.fx = fx

    def is_dead(self):
        if self.body[0].left not in range(WIDTH):
            return True
        if self.body[0].top not in range(HEIGHT):
            return True
        if self.body[0] in self.body[1:]:
            return True

class Food:
    def __init__(self):
        self.node = pygame.Rect(60, 80, 20, 20)
        self.flag = False

    def set(self):
        all_x_point = range(20, WIDTH - 20, 20)
        all_y_point = range(20, HEIGHT - 20, 20)
        left = random.choice(all_x_point)
        top = random.choice(all_y_point)
        self.node = pygame.Rect(left, top, 20, 20)
        self.flag = False

    def reset(self):
        self.flag = True

def show_text(screen, pos, text, color, font_size=20):
    cur_font = pygame.font.SysFont('SimHei', font_size)
    text_fmt = cur_font.render(text, 1, color)
    screen.blit(text_fmt, pos)

def show_score(screen, score, high_score):
    score_text = f'得分: {score}    最高分: {high_score}'
    show_text(screen, (WIDTH - 280, 30), score_text, (0, 0, 0))

def main_menu(screen):
    menu_font = pygame.font.SysFont('SimHei', 40)
    menu_options = ['开始游戏', '继续游戏', '暂停游戏', '结束游戏']
    selected_option = 0

    while True:
        screen.fill((255, 255, 255))

        # 绘制标题
        title_text = menu_font.render('贪吃蛇', True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        # 绘制菜单选项
        for i, option in enumerate(menu_options):
            if i == selected_option:
                color = (0, 255, 0)  # 选中的菜单项为绿色
            else:
                color = (0, 0, 0)  # 其他菜单项为黑色
            option_text = menu_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(WIDTH // 2, 200 + i * 60))
            screen.blit(option_text, option_rect)

        # 处理用户输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    return selected_option

        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    pygame.display.set_caption("贪吃蛇")

    # 显示主菜单界面
    selected_option = main_menu(screen)

    # 根据选择的菜单项执行相应的操作
    if selected_option == 0:  # 开始游戏
        score = 0
        high_score = 0
        sk = Snake(screen)
        fd = Food()
        dead = False

        # 读取历史最高分
        try:
            with open('high_score.txt', 'r') as file:
                high_score = int(file.read())
        except FileNotFoundError:
            pass

        clock = pygame.time.Clock()

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
                if e.type == pygame.KEYDOWN:
                    if not dead:
                        sk.change(e.key)
                    if e.key == pygame.K_SPACE:
                        score = 0
                        sk = Snake(screen)
                        fd = Food()
                        dead = False

            screen.fill((255, 255, 255))
            sk.draw_snake()
            if not dead:
                sk.move()

            if sk.is_dead():
                show_text(screen, (140, 160), '我一定会回来的', (202, 92, 85), 30)
                show_text(screen, (180, 320), '按 空格 重新开始', (116, 181, 103), 20)
                dead = True

                # 更新最高分
                if score > high_score:
                    high_score = score
                    with open('high_score.txt', 'w') as file:
                        file.write(str(high_score))

            if fd.flag:
                fd.set()
            pygame.draw.rect(screen, (255, 0, 0), fd.node, 0)

            if sk.body[0].colliderect(fd.node):
                score += 1
                sk.add_node()
                fd.reset()

            show_score(screen, score, high_score)

            pygame.display.update()
            clock.tick(10)
    elif selected_option == 1:  # 继续游戏
        # 继续之前的游戏
        pass
    elif selected_option == 2:  # 暂停游戏
        # 实现暂停游戏的功能
        pass
    elif selected_option == 3:  # 结束游戏
        pygame.quit()
        return

if __name__ == '__main__':
    main()
```

---
▶ 如果您需要远程电脑维修或者编程开发，请[加我微信](https://itxiaozhang.netlify.app/)咨询。 
▶ 本网站的部分内容可能来源于网络，仅供大家学习与参考，如有侵权请联系我核实删除。  
▶ **我是小章，目前全职提供电脑维修和IT咨询服务。如果您有任何电脑相关的问题，都可以问我噢。**  
