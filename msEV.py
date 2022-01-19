import pygame
import sys
from random import randrange
from pygame.locals import *
from ctypes import windll
from datetime import datetime
from interfaces.model_interface import (
    Model,
    feedforward,
    freeModel,
    getMutated,
    train_from_array,
    save_model,
    load_model,
)

from operator import itemgetter


# Initialize models
modelCount = 2
survivorCount = int(modelCount * 0.20)
saverequirementratio = 0.95
gamespacer = 5
cycleCounter = 0
seed = 0
shape = [81, 5, 1]
actFuncts = [4, 2]
mutationRate = 0.5
mutationDegree = 0.25
objects = []
for i in range(modelCount):
    # boxes, blocksleft, checkedBoxes, fitness, gamecount, model, clickCounter
    objects.append([[], 0, [], 0, 0, Model(
        seed + i, len(shape), shape, actFuncts), 0])
print(objects)

#load_model(models[0][0], "saves/model1-2021-10-08_07-41-36.dat")

name = "_seed%d_s" % seed
for s in shape:
    name += str(s) + "-"
name = name[:-1] + "_a"
for a in actFuncts:
    name += str(a) + "-"
name = name[:-1]
fname = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + name

with open("Data/" + fname + "_LOG.txt", "a+") as f:
    f.write(
        name
        + "\n"
        + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        + "\t"
        + str(cycleCounter)
        + f"\tto save:  {int(saverequirementratio)}, pool size = {modelCount}, survivor count = {survivorCount}, games per cycle = {gamespacer}, mutation rate = {mutationRate}, mutation degree = {mutationDegree}"
    )


def save(m1, top=False):
    filename_end = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if top:
        filename_end += "_TOP"
    save_model(m1, "saves/model1-" + filename_end + ".dat")
    print("Saved")

# To do: void that changes the models in objects


def getMutations(survivors):
    top_ = sorted(objects, key=itemgetter(3), reverse=True)
    top = top_[:survivors]
    freeModel([o[5] for o in top_[survivors:]])
    print(top)

    print("Top scores: ", [t[1] for t in top])

    with open("Data/" + fname + "_LOG.txt", "a+") as f:
        f.write(
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            + "\t"
            + str(cycleCounter)
            + "\t["
            + ",".join([str(t[1]) for t in top])
            + "]\n"
        )

    if top[0][1] >= int(saverequirementratio * gamespacer):
        save(top[0][0], True)
        exit(0)

    #newModels = []
    for index in range(survivors):
        #newModels.append([top[index][0], 0, [], 0, 0])
        newCount = modelCount - survivors
        for i in range(int(newCount / survivors + 0.5)):
            newModels.append(
                [
                    Model(
                        obj=getMutated(
                            top[index][0],
                            seed + index + i,
                            mutationRate,
                            mutationDegree,
                        )
                    ), 0, [], 0, 0,
                ]
            )
    # return newModels[:modelCount]


def MessageBox(title, text, style):
    return windll.user32.MessageBoxW(0, text, title, style)


pygame.init()
bomb = pygame.image.load("bomb.png")
pygame.display.set_icon(bomb)
surfObj = pygame.display.set_mode((173, 200))
pygame.display.set_caption("Minesweeper")

red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)

blue = pygame.Color(0, 0, 255)
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)

font = pygame.font.Font("UniversLTStd-BoldEx.otf", 18)

blockSurf = pygame.image.load("block.png")
blockSurfSel = pygame.image.load("selblock.png")
blockSurfBlank = pygame.image.load("blankblock.png")

warn1 = pygame.image.load("block1.png")
warn2 = pygame.image.load("block2.png")
warn3 = pygame.image.load("block3.png")
warn4 = pygame.image.load("block4.png")
warn5 = pygame.image.load("block5.png")
warn6 = pygame.image.load("block6.png")
warn7 = pygame.image.load("block7.png")
warn8 = pygame.image.load("block8.png")
explode = pygame.image.load("explode.png")
question = pygame.image.load("question.png")

clock = pygame.image.load("time.png")


class box():
    # flag = -3 # -3 = NO FLAG; -2 = FLAGGED; -1 = ?; 0 = BLANK; 1-8 = WARN; 9 = Exploded
    isBomb = False
    index = 0
    x = 0
    y = 0

    def __init__(self, boxPos):
        self.boxP = boxPos
        self.flag = -3


refBlock = box(Rect(-100, -100, 0, 0))
refBlock.x = -10
refBlock.y = -10
selBlock = refBlock


def drawBox():
    pygame.draw.line(surfObj, black, (10, 10), (163, 10))
    pygame.draw.line(surfObj, black, (10, 10), (10, 163))
    pygame.draw.line(surfObj, black, (10, 163), (163, 163))
    pygame.draw.line(surfObj, black, (163, 10), (163, 163))


def drawBoxesInit(obj):
    for x in range(0, 9):
        for y in range(0, 9):
            bo = box(Rect(x*17+10, y*17+10, 17, 17))
            bo.index = len(obj[0])
            bo.x = x
            bo.y = y
            obj[0].append(bo)
            surfObj.blit(blockSurf, (x*17 + 10, y*17 + 10))


for obj in objects:
    drawBoxesInit(obj)


def pickBombs(obj):
    numBombs = 0
    while numBombs < 10:   # CHange to 10
        x = randrange(0, len(obj[0]))
        if not obj[0][x].isBomb:
            obj[0][x].isBomb = True
            numBombs += 1


for obj in objects:
    pickBombs(obj)


def drawBoxes():
    for obj in objects:
        obj[1] = 0
        for b in obj[0]:
            if b.flag == -3:
                obj[1] += 1
                surfObj.blit(blockSurf, b.boxP)
            elif b.flag == 0:
                if not b in obj[2]:
                    pathFind(obj, b)
                surfObj.blit(blockSurfBlank, b.boxP)
            elif b.flag == 9:
                surfObj.blit(explode, b.boxP)
                lose(obj)
            elif b.flag == -1:
                surfObj.blit(question, b.boxP)
            elif b.flag == 1:
                surfObj.blit(warn1, b.boxP)
            elif b.flag == 2:
                surfObj.blit(warn2, b.boxP)
            elif b.flag == 3:
                surfObj.blit(warn3, b.boxP)
            elif b.flag == 4:
                surfObj.blit(warn4, b.boxP)
            elif b.flag == 5:
                surfObj.blit(warn5, b.boxP)
            elif b.flag == 6:
                surfObj.blit(warn6, b.boxP)
            elif b.flag == 7:
                surfObj.blit(warn7, b.boxP)
            elif b.flag == 8:
                surfObj.blit(warn8, b.boxP)
        if obj[1] == 10:
            win(obj)


def isInBounds():
    return Rect(10, 10, 153, 153).collidepoint(e.pos)


def overBlock(boxes):
    for b in boxes:
        if b.boxP.collidepoint(e.pos):
            return b


def boxAt(boxes, x, y):
    for b in boxes:
        if b.x == x and b.y == y:
            return b


def warnInteger(boxes, b):
    try:
        if b.x < 9 and b.x > 0 and b.y > 0 and b.y < 9:
            return (boxAt(boxes, b.x - 1, b.y), boxAt(boxes, b.x + 1, b.y), boxAt(boxes, b.x, b.y - 1), boxAt(boxes, b.x, b.y + 1), boxAt(boxes, b.x - 1, b.y - 1), boxAt(boxes, b.x + 1, b.y + 1), boxAt(boxes, b.x + 1, b.y - 1), boxAt(boxes, b.x - 1, b.y + 1))
        elif b.x > 8 and b.y > 0 and b.y < 9:
            return (boxAt(boxes, b.x - 1, b.y), boxAt(boxes, b.x - 1, b.y - 1), boxAt(boxes, b.x - 1, b.y + 1))
        elif b.x < 1 and b.y > 0 and b.y < 9:
            return (boxAt(boxes, b.x + 1, b.y), boxAt(boxes, b.x + 1, b.y - 1), boxAt(boxes, b.x + 1, b.y + 1), boxAt(boxes, b.x, b.y+1), boxAt(boxes, b.x, b.y-1))
        elif b.y < 1 and b.x > 0 and b.x < 9:
            return (boxAt(boxes, b.x, b.y + 1), boxAt(boxes, b.x + 1, b.y + 1), boxAt(boxes, b.x-1, b.y), boxAt(boxes, b.x+1, b.y), boxAt(boxes, b.x-1, b.y+1))
        elif b.y == 0 and b.x == 0:
            return (boxAt(boxes, 1, 0), boxAt(boxes, 1, 1), boxAt(boxes, 0, 1))
    except Exception as msg:
        return None


def getWarn(boxes, b):
    warn = 0
    try:
        neighbors = warnInteger(boxes, b)
        if not neighbors:
            return 0
        for b in neighbors:
            try:
                if b and b.isBomb:
                    warn = warn + 1
            except Exception as e:
                print("Couldn't detect if neighbor is bomb..." + str(e))
        return warn
    except Exception as ee:
        print("Couldn't find warn int..." + str(ee))
        return warn


boxesToPath = []


def crossFind(boxes, b):
    if b.x == 0 and b.y == 0:
        return (boxAt(boxes, 0, 1), boxAt(boxes, 1, 0))
    elif b.x == 0 and b.y == 9:
        return (boxAt(boxes, 0, 8), boxAt(boxes, 1, 9))
    elif b.x == 9 and b.y == 0:
        return (boxAt(boxes, 8, 0), boxAt(boxes, 9, 1))
    elif b.x == 9 and b.y == 9:
        return (boxAt(boxes, 8, 9), boxAt(boxes, 9, 8))
    elif b.x > 0 and b.x < 9 and b.y > 0:
        return (boxAt(boxes, b.x, b.y-1), boxAt(boxes, b.x-1, b.y), boxAt(boxes, b.x+1, b.y), boxAt(boxes, b.x, b.y+1))
    elif b.x == 0 and b.y > 0 and b.y < 9:
        return (boxAt(boxes, b.x, b.y-1), boxAt(boxes, b.x, b.y+1), boxAt(boxes, b.x+1, b.y))
    elif b.x == 9 and b.y > 0 and b.y < 9:
        return (boxAt(boxes, b.x-1, b.y), boxAt(boxes, b.x, b.y-1), boxAt(boxes, b.x, b.y+1))
    elif b.y == 0 and b.x > 0 and b.x < 9:
        return (boxAt(boxes, b.x - 1, b.y), boxAt(boxes, b.x+1, b.y), boxAt(boxes, b.x, b.y+1))
    elif b.y == 9 and b.x > 0 and b.x < 9:
        return (boxAt(boxes, b.x - 1, b.y), boxAt(boxes, b.x+1, b.y), boxAt(boxes, b.x, b.y-1))


def pathFind(obj, b):
    for bo in crossFind(obj[0], b):
        if bo and getWarn(obj[0], bo) == 0:
            bo.flag = 0
    for bo2 in warnInteger(obj[0], b):
        w = getWarn(obj[0], bo2)
        if w > 0 and w < 9:
            bo2.flag = w
    obj[2].append(b)


def lose(obj):
    #MessageBox("Sorry, you lost!", "You lose!  " + str(objects.index(obj)), 0)
    obj[3] += (81 - obj[1]) / gamespacer  # fitness
    obj[4] += 1  # gamecount
    resetGame(obj)


def win(obj):
    MessageBox("Congrats, you won!", "You win!", 0)
    resetGame(obj)


def resetGame(obj):
    obj[0][:] = []
    obj[1] = 0
    obj[2] = []
    obj[6] = 0
    drawBoxesInit(obj)
    pickBombs(obj)


while True:
    surfObj.fill(white)

    drawBox()
    drawBoxes()

    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()

    for index, obj in enumerate(objects):
        if not obj[4] == 5:
            boxes1d = []
            for b in obj[0]:
                boxes1d.append(b.flag)

            # process

            output = feedforward(obj[5], boxes1d)[0]
            output *= 81
            coords = [int(output % 9), int(output // 9)]
            obj[6] += 1
            if obj[6] == 80:
                lose(obj)

            #print(index, ": ", obj[1], ", ", coords)

            for b in obj[0]:
                if [b.x, b.y] == coords:
                    selBlock = b
                    break

            selBlock.flag = getWarn(obj[0], selBlock)
            if selBlock.flag == 0:
                boxesToPath.append(selBlock)
                pathFind(obj, selBlock)
            if selBlock.isBomb:
                selBlock.flag = 9

            if selBlock.flag == -3:
                surfObj.blit(blockSurfSel, selBlock.boxP)

    if all([obj[4] == gamespacer for obj in objects]):
        cycleCounter += 1
        print("MUTATE_--------------------")
        getMutations(survivorCount)

    pygame.display.update()
    pygame.time.Clock().tick(30)
