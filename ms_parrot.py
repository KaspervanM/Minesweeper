import sys
from random import randrange
from ctypes import windll
from datetime import datetime
from json import dumps, loads
import pygame as pg
from pygame.locals import Rect, QUIT, MOUSEBUTTONUP


def message_box(title, text, style):
    return windll.user32.MessageBoxW(0, text, title, style)


pg.init()
MINE = pg.image.load("images/MINE.png")
pg.display.set_icon(pg.image.load("images/icon.png"))
SURF_OBJ = pg.display.set_mode((173, 200))
pg.display.set_caption("Minesweeper")

WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(0, 0, 0)

FONT = pg.font.Font("resources/UniversLTStd-BoldEx.otf", 18)

BLOCK_SURF = pg.image.load("images/block.png")
BLOCK_SURF_BLANK = pg.image.load("images/blankblock.png")

WARN_1 = pg.image.load("images/block1.png")
WARN_2 = pg.image.load("images/block2.png")
WARN_3 = pg.image.load("images/block3.png")
WARN_4 = pg.image.load("images/block4.png")
WARN_5 = pg.image.load("images/block5.png")
WARN_6 = pg.image.load("images/block6.png")
WARN_7 = pg.image.load("images/block7.png")
WARN_8 = pg.image.load("images/block8.png")
EXPLODE = pg.image.load("images/explode.png")
FLAG = pg.image.load("images/flag.png")
QUESTION = pg.image.load("images/question.png")

CLOCK = pg.image.load("images/time.png")

BOXES = []
NUM_BOMBS = 0

FILENAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_trainingdata"


def write_file(training_data):
    if training_data:
        text = dumps(training_data) + ",\n"
    else:
        text = "["
    with open("Data/" + FILENAME + ".txt", "a+", encoding="utf8") as file:
        file.write(text)


def close_file():
    with open("Data/" + FILENAME + ".txt", "a+", encoding="utf8") as file:
        file.write("]")


def remove_line():
    with open("Data/" + FILENAME + ".txt", "r+", encoding="utf8") as file:
        lines = "".join(file.read().splitlines())[:-1] + "]"
    print(lines)
    with open("Data/" + FILENAME + ".txt", "w+", encoding="utf8") as file:
        file.write((dumps(loads(lines)[:-1]))[:-1]+",")


write_file(None)


def get_training_data(selected_box, has_flagged):
    input_data = []
    for box_elem in BOXES:
        input_data.append((box_elem.flag + 3)/12)
    desired_output = [selected_box.x_coords / 8,
                      selected_box.y_coords / 8,
                      int(has_flagged)]
    return [input_data, desired_output]


class Box():
    # flag = -3 # -3 = NO FLAG; -2 = FLAGGED; -1 = ?; 0 = BLANK; 1-8 = WARN; 9 = Exploded
    is_bomb = False
    index = 0
    x_coords = 0
    y_coords = 0

    def __init__(self, box_pos):
        self.box_pos = box_pos
        self.flag = -3


def draw_box():
    pg.draw.line(SURF_OBJ, BLACK, (10, 10), (163, 10))
    pg.draw.line(SURF_OBJ, BLACK, (10, 10), (10, 163))
    pg.draw.line(SURF_OBJ, BLACK, (10, 163), (163, 163))
    pg.draw.line(SURF_OBJ, BLACK, (163, 10), (163, 163))


def draw_box_init():
    for x_coords in range(0, 9):
        for y_coords in range(0, 9):
            box_ob = Box(Rect(x_coords*17+10, y_coords*17+10, 17, 17))
            box_ob.index = len(BOXES)
            box_ob.x_coords = x_coords
            box_ob.y_coords = y_coords
            BOXES.append(box_ob)
            SURF_OBJ.blit(BLOCK_SURF, (x_coords*17 + 10, y_coords*17 + 10))


draw_box_init()


def pick_bombs():
    global NUM_BOMBS
    while NUM_BOMBS < 10:
        x_coords = randrange(0, len(BOXES))
        if not BOXES[x_coords].is_bomb:
            BOXES[x_coords].is_bomb = True
            NUM_BOMBS += 1


pick_bombs()
FLAGS_USED = 0
CHECKED_BOXES = []
BLOCKS_LEFT = 0


def draw_boxes():
    global FLAGS_USED
    global BLOCKS_LEFT
    FLAGS_USED = 0
    BLOCKS_LEFT = 0
    for box_ob in BOXES:
        if box_ob.flag == -3:
            BLOCKS_LEFT += 1
            SURF_OBJ.blit(BLOCK_SURF, box_ob.box_pos)
        elif box_ob.flag == 0:
            if not box_ob in CHECKED_BOXES:
                path_find(box_ob)
            SURF_OBJ.blit(BLOCK_SURF_BLANK, box_ob.box_pos)
        elif box_ob.flag == 9:
            SURF_OBJ.blit(EXPLODE, box_ob.box_pos)
            lose()
        elif box_ob.flag == -2:
            SURF_OBJ.blit(FLAG, box_ob.box_pos)
            BLOCKS_LEFT += 1
            FLAGS_USED += 1
        elif box_ob.flag == -1:
            SURF_OBJ.blit(QUESTION, box_ob.box_pos)
        elif box_ob.flag == 1:
            SURF_OBJ.blit(WARN_1, box_ob.box_pos)
        elif box_ob.flag == 2:
            SURF_OBJ.blit(WARN_2, box_ob.box_pos)
        elif box_ob.flag == 3:
            SURF_OBJ.blit(WARN_3, box_ob.box_pos)
        elif box_ob.flag == 4:
            SURF_OBJ.blit(WARN_4, box_ob.box_pos)
        elif box_ob.flag == 5:
            SURF_OBJ.blit(WARN_5, box_ob.box_pos)
        elif box_ob.flag == 6:
            SURF_OBJ.blit(WARN_6, box_ob.box_pos)
        elif box_ob.flag == 7:
            SURF_OBJ.blit(WARN_7, box_ob.box_pos)
        elif box_ob.flag == 8:
            SURF_OBJ.blit(WARN_8, box_ob.box_pos)
    if BLOCKS_LEFT == 10:
        win()


def is_in_bounds(event):
    return Rect(10, 10, 153, 153).collidepoint(event.pos)


def over_block(pos):
    for box_ob in BOXES:
        if box_ob.box_pos.collidepoint(pos):
            return box_ob


def box_at(x_coords, y_coords):
    for box_ob in BOXES:
        if box_ob.x_coords == x_coords and box_ob.y_coords == y_coords:
            return box_ob


def warn_integer(box_ob):
    return (box_at(box_ob.x_coords - 1, box_ob.y_coords),
            box_at(box_ob.x_coords + 1, box_ob.y_coords),
            box_at(box_ob.x_coords, box_ob.y_coords - 1),
            box_at(box_ob.x_coords, box_ob.y_coords + 1),
            box_at(box_ob.x_coords - 1, box_ob.y_coords - 1),
            box_at(box_ob.x_coords + 1, box_ob.y_coords + 1),
            box_at(box_ob.x_coords + 1, box_ob.y_coords - 1),
            box_at(box_ob.x_coords - 1, box_ob.y_coords + 1))


def get_warn(box_ob):
    warn = 0
    neighbors = warn_integer(box_ob)
    if not neighbors:
        return 0
    for neighbors_box_ob in neighbors:
        if neighbors_box_ob and neighbors_box_ob.is_bomb:
            warn = warn + 1
    return warn


boxesToPath = []


def cross_find(box_ob):
    return (box_at(box_ob.x_coords, box_ob.y_coords-1),
            box_at(box_ob.x_coords-1, box_ob.y_coords),
            box_at(box_ob.x_coords+1, box_ob.y_coords),
            box_at(box_ob.x_coords, box_ob.y_coords+1))


def path_find(box_ob):
    for box_elem in cross_find(box_ob):
        if box_elem and get_warn(box_elem) == 0:
            box_elem.flag = 0
    for bo2 in warn_integer(box_ob):
        if bo2:
            warn = get_warn(bo2)
            if 0 < warn < 9:
                bo2.flag = warn
    CHECKED_BOXES.append(box_ob)


LAST_GAME = 0


def lose():
    message_box("Sorry, you lost!", "You lose!", 0)
    remove_line()
    reset_game()


def win():
    message_box("Congrats, you won!", "You win!", 0)
    reset_game()


def reset_game():
    global BOXES
    global NUM_BOMBS
    global FLAGS_USED
    global CHECKED_BOXES
    global BLOCKS_LEFT
    global LAST_GAME
    BOXES[:] = []
    NUM_BOMBS = 0
    draw_box_init()
    pick_bombs()
    FLAGS_USED = 0
    CHECKED_BOXES = []
    BLOCKS_LEFT = 0
    LAST_GAME = pg.time.get_ticks()


def game_loop():
    SURF_OBJ.fill(WHITE)
    SURF_OBJ.blit(CLOCK, (10, 173))
    SURF_OBJ.blit(MINE, (147, 173))

    mine_text = FONT.render(str(10-FLAGS_USED), True, BLACK)
    mine_text_pos = mine_text.get_rect()
    mine_text_pos.topleft = (120, 173)
    SURF_OBJ.blit(mine_text, mine_text_pos)
    if LAST_GAME != 0:
        mins = (pg.time.get_ticks() - LAST_GAME) / 1000 / 60
        secs = (pg.time.get_ticks() - LAST_GAME) / 1000 % 60
    else:
        mins = pg.time.get_ticks() / 1000 / 60
        secs = pg.time.get_ticks() / 1000 % 60
    mins_string = ""
    secs_string = ""
    if secs < 10:
        secs_string = "0" + str(int(secs))
    else:
        secs_string = str(int(secs))
    if mins < 10:
        mins_string = "0" + str(int(mins))
    else:
        mins_string = str(int(mins))

    min_text = FONT.render(mins_string + ":" + secs_string, True, BLACK)
    min_text_pos = min_text.get_rect()
    min_text_pos.topleft = (30, 173)
    SURF_OBJ.blit(min_text, min_text_pos)

    draw_box()
    draw_boxes()

    for pg_event in pg.event.get():
        if pg_event.type == QUIT:
            close_file()
            pg.quit()
            sys.exit()
        elif pg_event.type == MOUSEBUTTONUP:
            if is_in_bounds(pg_event):
                selected_block = over_block(pg.mouse.get_pos())
                if pg_event.button == 1:
                    write_file(get_training_data(selected_block, False))
                    selected_block.flag = get_warn(selected_block)
                    if selected_block.flag == 0:
                        boxesToPath.append(selected_block)
                        path_find(selected_block)
                    if selected_block.is_bomb:
                        selected_block.flag = 9
                elif pg_event.button == 3:
                    write_file(get_training_data(selected_block, True))
                    if selected_block.flag == -3:
                        selected_block.flag = -2
                    elif selected_block.flag == -2:
                        selected_block.flag = -1
                    elif selected_block.flag == -1:
                        selected_block.flag = -3

    pg.display.update()
    pg.time.Clock().tick(30)


while True:
    game_loop()
