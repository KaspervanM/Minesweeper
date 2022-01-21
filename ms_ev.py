"""Trains AI to play minesweeper using an evolutionary algorithm
"""
import sys
from random import randrange, seed
from ctypes import windll
from operator import itemgetter
from datetime import datetime
from pygame.locals import Rect
import pygame as pg
from interfaces.model_interface import (
    Model,
    feedforward,
    freeModel,
    getMutated,
    save_model,
)

seed(1)

# Initialize models
MODEL_COUNT = 200
SURVIVOR_COUNT = int(MODEL_COUNT * 0.20)
SAVE_REQUIREMENT_RATIO = 0.95
GAME_SPACER = 10
CYCLE_COUNTER = 0
SEED = 0
SHAPE = [81, 10, 10, 2]
ACT_FUNCTS = [4, 4, 2]
MUTATION_RATE = 0.5
MUTATION_DEGREE = 0.25
OBJECTS = []
for i in range(MODEL_COUNT):
    # boxes, blocksleft, checkedBoxes, fitness, gamecount, model, clickCounter
    OBJECTS.append([[], 0, [], 0, 0, Model(
        SEED + i, len(SHAPE), SHAPE, ACT_FUNCTS), 0])
print(OBJECTS)
print(len(OBJECTS))

#load_model(models[0][0], "saves/model1-2021-10-08_07-41-36.dat")

NAME = f"_SEED{SEED}_s"
for s in SHAPE:
    NAME += str(s) + "-"
NAME = NAME[:-1] + "_a"
for a in ACT_FUNCTS:
    NAME += str(a) + "-"
NAME = NAME[:-1]
fname = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + NAME

with open("Data/" + fname + "_LOG.txt", "a+", encoding="utf8") as f:
    f.write(
        NAME
        + "\n"
        + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        + "\t"
        + str(CYCLE_COUNTER)
        + f"\tto save:  {(SAVE_REQUIREMENT_RATIO * (81 - 10))}, pool size = {MODEL_COUNT}, \
survivor count = {SURVIVOR_COUNT}, games per cycle = {GAME_SPACER}, \
mutation rate = {MUTATION_RATE}, mutation degree = {MUTATION_DEGREE}\n"
    )


def save(model, top=False):
    filename_end = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if top:
        filename_end += "_TOP"
    save_model(model, "saves/model1-" + filename_end + ".dat")
    print("Saved")

# To do: void that changes the models in OBJECTS


def get_mutations(survivors):
    top_ = sorted(OBJECTS, key=itemgetter(3), reverse=True)
    top = top_[:survivors]
    freeModel([o[5] for o in top_[survivors:]])
    #print("TOP: ", top)

    print("Top scores: ", [t[3] for t in top])

    with open("Data/" + fname + "_LOG.txt", "a+", encoding="utf8") as file:
        file.write(
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            + "\t"
            + str(CYCLE_COUNTER)
            + "\t["
            + ",".join([str(t[3]) for t in top])
            + "]\n"
        )

    if top[0][3] >= int(SAVE_REQUIREMENT_RATIO * (81 - 10)):
        save(top[0][5], True)
        sys.exit()

    new_count = MODEL_COUNT - survivors
    new_objects = []
    #OBJECTS.append([[], 0, [], 0, 0, Model( SEED + i, len(SHAPE), SHAPE, ACT_FUNCTS), 0])
    for top_index in range(survivors):
        new_objects.append([[], 0, [], 0, 0, top[top_index][5], 0])
        for new_obj_index in range(int(new_count / survivors + 0.5)):
            new_objects.append(
                [[], 0, [], 0, 0,
                    Model(
                        obj=getMutated(
                            top[top_index][5],
                            SEED + top_index + new_obj_index,
                            MUTATION_RATE,
                            MUTATION_DEGREE,
                        )), 0
                 ]
            )
    return new_objects[:MODEL_COUNT]


def message_box(title, text, style):
    return windll.user32.MessageBoxW(0, text, title, style)


pg.init()
mine = pg.image.load("images/mine.png")
pg.display.set_icon(pg.image.load("images/icon.png"))
surfObj = pg.display.set_mode((173, 200))
pg.display.set_caption("Minesweeper")

white = pg.Color(255, 255, 255)
black = pg.Color(0, 0, 0)

blockSurf = pg.image.load("images/block.png")
blockSurfBlank = pg.image.load("images/blankblock.png")

warn1 = pg.image.load("images/block1.png")
warn2 = pg.image.load("images/block2.png")
warn3 = pg.image.load("images/block3.png")
warn4 = pg.image.load("images/block4.png")
warn5 = pg.image.load("images/block5.png")
warn6 = pg.image.load("images/block6.png")
warn7 = pg.image.load("images/block7.png")
warn8 = pg.image.load("images/block8.png")
explode = pg.image.load("images/explode.png")


class Box():
    # flag = -3 # -3 = NO FLAG; -2 = FLAGGED; -1 = ?; 0 = BLANK; 1-8 = WARN; 9 = Exploded
    isBomb = False
    index = 0
    x = 0
    y = 0

    def __init__(self, box_pos):
        self.box_pos = box_pos
        self.flag = -3


refBlock = Box(Rect(-100, -100, 0, 0))
refBlock.x = -10
refBlock.y = -10
selBlock = refBlock


def draw_box():
    pg.draw.line(surfObj, black, (10, 10), (163, 10))
    pg.draw.line(surfObj, black, (10, 10), (10, 163))
    pg.draw.line(surfObj, black, (10, 163), (163, 163))
    pg.draw.line(surfObj, black, (163, 10), (163, 163))


def draw_boxes_init(obj):
    for x in range(0, 9):
        for y in range(0, 9):
            bo = Box(Rect(x*17+10, y*17+10, 17, 17))
            bo.index = len(obj[0])
            bo.x = x
            bo.y = y
            obj[0].append(bo)
            surfObj.blit(blockSurf, (x*17 + 10, y*17 + 10))


def pick_bombs(obj):
    num_bombs = 0
    while num_bombs < 10:   # CHange to 10
        x = randrange(0, len(obj[0]))
        if not obj[0][x].isBomb:
            obj[0][x].isBomb = True
            num_bombs += 1


def draw_boxes(obj):
    obj[1] = 0
    for b in obj[0]:
        if b.flag == -3:
            obj[1] += 1
            surfObj.blit(blockSurf, b.box_pos)
        elif b.flag == 0:
            if not b in obj[2]:
                path_find(obj, b)
            surfObj.blit(blockSurfBlank, b.box_pos)
        elif b.flag == 9:
            surfObj.blit(explode, b.box_pos)
            lose(obj)
            return
        elif b.flag == 1:
            surfObj.blit(warn1, b.box_pos)
        elif b.flag == 2:
            surfObj.blit(warn2, b.box_pos)
        elif b.flag == 3:
            surfObj.blit(warn3, b.box_pos)
        elif b.flag == 4:
            surfObj.blit(warn4, b.box_pos)
        elif b.flag == 5:
            surfObj.blit(warn5, b.box_pos)
        elif b.flag == 6:
            surfObj.blit(warn6, b.box_pos)
        elif b.flag == 7:
            surfObj.blit(warn7, b.box_pos)
        elif b.flag == 8:
            surfObj.blit(warn8, b.box_pos)
    if obj[1] == 10:
        win(obj)


def box_at(boxes, x, y):
    for b in boxes:
        if b.x == x and b.y == y:
            return b
    return None


def warnInteger(boxes, b):
    return (box_at(boxes, b.x - 1, b.y), box_at(boxes, b.x + 1, b.y), box_at(boxes, b.x, b.y - 1), box_at(boxes, b.x, b.y + 1), box_at(boxes, b.x - 1, b.y - 1), box_at(boxes, b.x + 1, b.y + 1), box_at(boxes, b.x + 1, b.y - 1), box_at(boxes, b.x - 1, b.y + 1))


def get_warn(boxes, b):
    warn = 0
    neighbors = warnInteger(boxes, b)
    if not neighbors:
        return 0
    for boxelem in neighbors:
        if boxelem and boxelem.isBomb:
            warn += 1
    return warn


boxesToPath = []


def crossFind(boxes, b):
    return (box_at(boxes, b.x, b.y-1), box_at(boxes, b.x-1, b.y), box_at(boxes, b.x+1, b.y), box_at(boxes, b.x, b.y+1))


def path_find(obj, b):
    for bo in crossFind(obj[0], b):
        if bo and get_warn(obj[0], bo) == 0:
            bo.flag = 0
    for bo2 in warnInteger(obj[0], b):
        if bo2:
            w = get_warn(obj[0], bo2)
            if w > 0 and w < 9:
                bo2.flag = w
    obj[2].append(b)


def lose(obj):
    #message_box("Sorry, you lost!", "You lose!  " + str(OBJECTS.index(obj)), 0)
    obj[3] += (81 - 10 - obj[1]) / GAME_SPACER  # fitness
    obj[4] += 1  # gamecount
    resetGame(obj)


def win(obj):
    print("win!")
    #message_box("Congrats, you won!", "You win!  " + str(obj[1]), 0)
    obj[3] += (81 - 10 - obj[1]) / GAME_SPACER  # fitness
    obj[4] += 1
    resetGame(obj)


def resetGame(obj):
    obj[0][:] = []
    obj[1] = 0
    obj[2] = []
    obj[6] = 0
    draw_boxes_init(obj)
    pick_bombs(obj)


for objec in OBJECTS:
    resetGame(objec)

while True:
    surfObj.fill(white)

    draw_box()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    for index, objec in enumerate(OBJECTS):
        draw_boxes(objec)
        if objec[4] < GAME_SPACER:
            boxes1d = []
            for box_elem in objec[0]:
                boxes1d.append(box_elem.flag)

            # process

            output = feedforward(objec[5], boxes1d)
            # [int(output // 9 - .5), int(output % 9 - .5)]
            coords = [int(output[0]*8), int(output[1]*8)]
            objec[6] += 1
            if objec[6] == 81 - 20:
                lose(objec)
            else:
                #print(index, ": ", objec[1], ", ", coords)
                selBlock = box_at(objec[0], coords[0], coords[1])

                selBlock.flag = get_warn(objec[0], selBlock)
                if selBlock.flag == 0:
                    boxesToPath.append(selBlock)
                    path_find(objec, selBlock)
                if selBlock.isBomb:
                    selBlock.flag = 9
        elif all(obj[4] == GAME_SPACER for obj in OBJECTS):
            CYCLE_COUNTER += 1
            print("MUTATE_--------------------")
            OBJECTS = get_mutations(SURVIVOR_COUNT)
            for obje in OBJECTS:
                resetGame(obje)

    pg.display.update()
    # pg.time.Clock().tick(30)
