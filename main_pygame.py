import pygame
from copy import deepcopy
from random import choice, randrange
import glob
import os
from itertools import *
#
bg = None
game_bg = None
#
def get_theme_list():
  os.chdir("bg")
  a=list(glob.glob("a*.jpg"))
  b=list(glob.glob("b*.jpg"))
  c=[]
  i=0
  while(i<len(a)):
    d=[]
    d.append(a[i])
    d.append(b[i])
    c.append(d)
    i+=1
  os.chdir("..")
  print(c)
  return(c)
#
def change_theme(afile,bfile):
  global bg
  global game_bg
  os.chdir("bg")
  bg = pygame.image.load(afile).convert()
  game_bg = pygame.image.load(bfile).convert()
  os.chdir("..")
#
thlist = get_theme_list()
#
pygame.init()
#
W, H = 10, 20
FPS = 60
#
RES = pygame.display.get_desktop_sizes()[0]
RES = tuple([i//2 for i in RES])
SW = RES[0]
SH = RES[1]
#
TILE = RES[1]//(H+2)
#
GAME_RES = W * TILE, H * TILE
#
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

grid = [
    pygame.Rect(x * TILE, y * TILE, TILE, TILE)
    for x in range(W) for y in range(H)
]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [
    [pygame.Rect(x + W // 2, y + 1, 1, 1)
    for x, y in fig_pos]
    for fig_pos in figures_pos
]
figure_rect = pygame.Rect(
    0,
    0,
    TILE-2,
    TILE-2,
)
field = [[0 for i in range(W)] for j in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000

change_theme(thlist[0][0],
             thlist[0][1])
nex = 1


main_font = pygame.font.Font('font/font.ttf', 65)
font = pygame.font.Font('font/font.ttf', 45)

title_tetris = main_font.render('TETRIS', True, pygame.Color('red'))
title_score = font.render('score:', True, pygame.Color('white'))
title_record = font.render('record:', True, pygame.Color('white'))

get_color = lambda: (
    randrange(30, 256),
    randrange(30, 256),
    randrange(30, 256)
)

get_color = lambda: (14,44,112)

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')


def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))


while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(
        bg,
        (SW//2-(W*TILE)//2, SH//2-(H*TILE)//2),
    )
    sc.blit(
        game_sc,
        (SW//2-(W*TILE)//2, SH//2-(H*TILE)//2),
    )
    game_sc.blit(
        game_bg,
        (0, 0)
    )
    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)
    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
            elif event.key == pygame.K_SPACE:
                change_theme(thlist[nex][0],
                             thlist[nex][1])
                if(nex<len(thlist)-1):
                    nex += 1
                else:
                    nex = 0
    # move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break
    # move y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break
    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break
    # check lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1
    # compute score
    score += scores[lines]
    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)
    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)
    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)
    # draw titles
    sc.blit(title_tetris, (505, 30))
    sc.blit(title_score, (535, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 840))
    sc.blit(title_record, (525, 650))
    sc.blit(font.render(record, True, pygame.Color('gold')), (550, 710))
    # game over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)
