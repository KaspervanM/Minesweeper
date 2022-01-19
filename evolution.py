# Import the pygame library and initialise the game engine
from typing import Type
import pygame
from datetime import datetime
from copy import deepcopy
from pygame.mixer import pause
from interfaces.model_interface import (
    Model,
    feedforward,
    freeModel,
    getMutated,
    train_from_array,
    save_model,
    load_model,
)
from objects import Paddle, Ball
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Open a new window
size = (int(700), int(500))
# scale factors
sfx = float(size[0]) / 700.0
sfy = float(size[1]) / 500.0
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pong")
modelCount = 200
objects = []


def reset_paddles_ball(index):
    objects[index][0].rect.x = 20 * sfx
    objects[index][0].rect.y = 200 * sfy
    objects[index][1].rect.x = 670 * sfx
    objects[index][1].rect.y = 200 * sfy
    objects[index][2].rect.x = 345 * sfx
    objects[index][2].rect.y = 245 * sfy


for i in range(modelCount):
    objects.append(
        [
            Paddle(sfy, WHITE, 10 * sfx, 100 * sfy),
            Paddle(sfy, WHITE, 10 * sfx, 100 * sfy),
            Ball(sfx, sfy, WHITE, 10 * sfx, 10 * sfy, [-5, 0]),
            0,
            [],
        ]
    )
    reset_paddles_ball(i)

# This will be a list containing all the sprites we intend to use in my game.
all_sprites_list = pygame.sprite.Group()
top_sprites_list = pygame.sprite.Group()

# Add all the paddles and the balls to the list of sprites
for objl in objects:
    for obj in objl[:3]:
        all_sprites_list.add(obj)
for obj in objects[0][:3]:
    top_sprites_list.add(obj)

# The loop will carry on until the user exit the game
carryOn = True

# The clock will be used to control how fast the screen updates
clock = pygame.time.Clock()

# Initialise player scores
spd = 5

# Initialize models
seed = 0
# shape = [size[0] * size[1], 24, 1]
shape = [4, 1]
actFuncts = [2]
mutationRate = 0.5
mutationDegree = 0.25
models = []
for i in range(modelCount):
    models.append([Model(seed + i, len(shape), shape, actFuncts), 0, True])
load_model(models[0][0], "saves/model1-2021-10-08_07-41-36.dat")


def save(m1, top=False):
    filename_end = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if top:
        filename_end += "_TOP"
    save_model(m1, "saves/model1-" + filename_end + ".dat")
    print("Saved")


def plotScores():
    if len(time_per_cycle) <= 1 or len(top_score_ratio) <= 1:
        return
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.set_title(
        "Performance of an ANN trained with the evolutionary algorithm"
    )
    ax1.set_xlabel(f"Cycles of {gamespacer} games")
    ax1.set_ylabel("Score ratio per cycle")
    ax1.grid(True)
    ax1.set_ylim(0, 1)
    ax1.set_xlim(1, len(top_score_ratio))
    # ax1.set_xlim(0, len(top_score_ratio) + 1)
    ax1.xaxis.set_major_formatter(FormatStrFormatter("%d"))
    if len(top_score_ratio) < 10:
        ax1.locator_params(axis="x", nbins=len(top_score_ratio))
    # ax1.set_xticks([*range(1, len(top_score_ratio) + 1)])
    ax1.fill_between([*range(1, len(top_score_ratio) + 1)], top_score_ratio)

    ax2 = fig.add_subplot(212)
    ax2.set_title("Duration (total: %d sec)" % sum(time_per_cycle))
    ax2.set_xlabel(f"Cycles of {gamespacer} games")
    ax2.set_ylabel("Duration per cycle in seconds")
    ax2.grid(True)
    ax2.set_xlim(1, len(time_per_cycle))
    # ax2.set_xlim(0, len(time_per_cycle) + 1)
    ax2.xaxis.set_major_formatter(FormatStrFormatter("%d"))
    ax2.yaxis.set_major_formatter(FormatStrFormatter("%d"))
    if len(time_per_cycle) < 10:
        ax2.locator_params(axis="x", nbins=len(time_per_cycle))
    # ax2.set_xticks([*range(1, len(time_per_cycle) + 1)])
    ax2.plot(
        [*range(1, len(top_score_ratio) + 1)],
        time_per_cycle,
        "b",
    )
    ax2.plot(
        [*range(1, len(top_score_ratio) + 1)],
        [
            sum(time_per_cycle) / len(time_per_cycle)
            for _ in range(len(time_per_cycle))
        ],
        "m--",
    )
    ax2.annotate(
        "%.2f" % (sum(time_per_cycle) / len(time_per_cycle)),
        (1, sum(time_per_cycle) / len(time_per_cycle)),
        textcoords="offset points",
        xytext=(0, 5),
        ha="left",
    )
    fig.autofmt_xdate()
    fig.tight_layout()

    fig.savefig("Data/" + fname)
    plt.close(fig)
    plt.close()
    plt.clf()
    del fig


def getMutations(survivors):
    top_ = sorted(models, key=lambda x: x[1], reverse=True)
    top = top_[:survivors]
    freeModel(top_[survivors:])

    print("Top scores: ", [t[1] for t in top])
    top_score_ratio.append(top[0][1] / gamespacer)

    global t0
    t1 = datetime.now()
    diff = t1 - t0
    time_per_cycle.append(diff.total_seconds())
    t0 = t1

    with open("Data/" + fname + "_LOG.txt", "a+") as f:
        f.write(
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            + "\t"
            + str(cycleCounter)
            + "\tduration:"
            + str(diff.total_seconds())
            + "\t["
            + ",".join([str(t[1]) for t in top])
            + "]\n"
        )

    if top[0][1] >= int(saverequirementratio * gamespacer):
        save(top[0][0], True)
        plotScores()
        exit(0)

    newModels = []
    for index in range(survivors):
        newModels.append([top[index][0], 0, True])
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
                    ),
                    0,
                    True,
                ]
            )
    return newModels[:modelCount]


top_score_ratio = []
time_per_cycle = []
global t0
t0 = datetime.now()

counter = 0
cycleCounter = 0
spacer = 10
survivorCount = int(modelCount * 0.20)
gamespacer = 20
saverequirementratio = 0.95
speedup = False
draw_screen = True
learning = True
hard = False
topOnly = False
name = "_seed%d_s" % seed
for s in shape:
    name += str(s) + "-"
name = name[:-1] + "_a"
for a in actFuncts:
    name += str(a) + "-"
name = name[:-1]


fname = t0.strftime("%Y-%m-%d_%H-%M-%S") + name
print(fname)

with open("Data/" + fname + "_LOG.txt", "a+") as f:
    f.write(
        name
        + "\n"
        + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        + "\t"
        + str(cycleCounter)
        + f"\tto save:  {int(saverequirementratio * gamespacer)}, pool size = {modelCount}, survivor count = {survivorCount}, games per cycle = {gamespacer}, mutation rate = {mutationRate}, mutation degree = {mutationDegree}"
        + (", handicapped\n" if not hard else "\n")
    )

# -------- Main Program Loop -----------
while carryOn:
    counter += 1
    # --- Main event loop
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            carryOn = False  # Flag that we are done so we exit this loop
        elif event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_x
            ):  # Pressing the x Key will quit the game
                plotScores()
                carryOn = False
            elif event.key == pygame.K_SPACE:
                speedup = not speedup
                print("speedup: ", speedup)
            elif event.key == pygame.K_t:
                topOnly = not topOnly
                print("topOnly: ", topOnly)
            elif event.key == pygame.K_1:
                draw_screen = not draw_screen
                print("draw_screen: ", draw_screen)
            elif event.key == pygame.K_l:
                learning = not learning
                print("learning: ", learning)
            elif event.key == pygame.K_s:
                save(models[0][0])
            elif event.key == pygame.K_2:
                hard = not hard
                print("hard: ", hard)
            elif event.key == pygame.K_p:
                print("plotted")
                plotScores()

    # --- Game logic should go here
    all_sprites_list.update()

    for index in range(modelCount):
        if models[index][2]:
            # Get input data for model
            input_data = [
                objects[index][2].rect.x / size[0],
                objects[index][2].rect.y / size[1],
                (objects[index][0].rect.y + 100 * sfy / 2) / size[1],
                # (objects[index][1].rect.y + 100 * sfy / 2) / size[1],
                # objects[index][2].velocity[0] / 5,
                objects[index][2].velocity[1],
            ]

            # objects[index][4] = feedforward(models[index][0], input_data)
            out = feedforward(models[index][0], input_data)[0]

            mv1 = 0
            mv2 = 0
            # Moving the paddles according to the models

            if out <= 0.5:  # objects[index][4][0] >= 0.5:
                mv1 = -spd
                objects[index][0].moveUp(spd * sfy)
            if out > 0.5:  # objects[index][4][0] < 0.5:
                mv1 = spd
                objects[index][0].moveDown(spd * sfy)
            if counter % (spacer) == 0 or hard:
                if (
                    objects[index][2].rect.y
                    < objects[index][1].rect.y + 100 * sfy / 2
                ):
                    mv2 = -spd
                    objects[index][1].moveUp(spd * sfy)
                if (
                    objects[index][2].rect.y
                    > objects[index][1].rect.y + 100 * sfy / 2
                ):
                    mv2 = spd
                    objects[index][1].moveDown(spd * sfy)

            # Detect collisions between the ball and the paddles
            if pygame.sprite.collide_mask(
                objects[index][2], objects[index][0]
            ):
                objects[index][2].bounce(mv1)
            if pygame.sprite.collide_mask(
                objects[index][2], objects[index][1]
            ):
                objects[index][2].bounce(mv2)

            # Check if the ball is bouncing against any of the 4 walls:
            if objects[index][2].rect.x >= (690 - 20) * sfx:
                reset_paddles_ball(index)
                models[index][1] += 1
                objects[index][2].velocity[0] = (
                    objects[index][3] % 2
                ) * -10 + 5
                objects[index][2].velocity[1] = 0
                objects[index][3] += 1
            if objects[index][2].rect.x <= 20 * sfx:
                reset_paddles_ball(index)
                objects[index][2].velocity[0] = (
                    objects[index][3] % 2
                ) * -10 + 5
                objects[index][2].velocity[1] = 0
                objects[index][3] += 1
            if objects[index][2].rect.y > 490 * sfy:
                objects[index][2].velocity[1] = -objects[index][2].velocity[1]
            if objects[index][2].rect.y <= 0:
                objects[index][2].velocity[1] = max(
                    -objects[index][2].velocity[1], 1
                )

            if objects[index][3] == gamespacer:
                models[index][2] = False
                objects[index][3] = 0
            # if counter % save_spacer == 0:
            #    save(model1)
        elif all([li[2] is False for li in models]):
            cycleCounter += 1
            models = getMutations(survivorCount)

    # --- Drawing code should go here
    if draw_screen:
        # First, clear the screen to black.
        screen.fill(BLACK)
        # Draw the net
        pygame.draw.line(
            screen,
            WHITE,
            [349 * sfx, 0],
            [349 * sfx, 500 * sfy],
            int(10 * sfy),
        )

        # Now let's draw all the sprites in one go.
        if topOnly is True:
            top_sprites_list.draw(screen)
        else:
            all_sprites_list.draw(screen)

        # Display scores:
        # font = pygame.font.Font(None, int(74 * sfx))
        # text = font.render(str(scoreA), 1, WHITE)
        # screen.blit(text, (250 * sfx, 10 * sfy))
        # text = font.render(str(scoreB), 1, WHITE)
        # screen.blit(text, (420 * sfx, 10 * sfy))

        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # --- Limit to 60 frames per second
    # print("\bmv: " + str(mv) + "  ", end="\r")
    if not speedup:
        clock.tick(60)

# Once we have exited the main program loop we can stop the game engine:
pygame.quit()
