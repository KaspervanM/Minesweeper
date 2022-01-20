import random
import sys
import pygame as pg
import numpy as np
import collections

WIDTH = 200
GREY = (128, 128, 128)  # rgb value
DARKGREY = (105, 105, 105)
WHITE = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
BOARD_SIZE = 20
WIDTH = HEIGHT = BOARD_SIZE * 20  # window dimensions
NUM_BOMBS = 40


colors = [RED, BLUE, GREEN, PURPLE, MAGENTA, ORANGE, YELLOW, BLACK]
# random.seed(1)


def init_board():
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    for i in range(NUM_BOMBS):
        # while count(board) < 40:
        row = random.randint(1, BOARD_SIZE-1)
        column = random.randint(1, BOARD_SIZE-1)
        board[row][column] = 9
    # print(np.array(board))
    # print("\n")
    return board


def count(board):
    ret = 0
    for row in board[0]:
        for col in board:
            if board[row][col] == 9:
                print(board[row][j])
                ret += 1
    return ret


def create_grid():
    board = init_board()
    pg.init()
    SQUARE_SIZE = 20
    win = pg.display.set_mode((HEIGHT, WIDTH))
    win.fill(GREY)
    pg.display.set_caption("Minesweeper")
    font = pg.font.SysFont('Arial', 25)
    BOMB_IMG = pg.image.load("bomb.png")
    FLAG_IMG = pg.image.load("flag.png")
    rect2 = BOMB_IMG.get_rect()
    rect3 = FLAG_IMG.get_rect()
    moveable = True
    done = False
    lost = False
    called = [[]]
    found = 0

    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            # draw grid
            rectColor = WHITE
            rect = pg.Rect(y * SQUARE_SIZE, x * SQUARE_SIZE,
                           SQUARE_SIZE, SQUARE_SIZE)
            pg.draw.rect(win, rectColor, rect, 1)

    while not done:
        for event in pg.event.get():
            if moveable and event.type == pg.MOUSEBUTTONDOWN:
                Mouse_x, Mouse_y = pg.mouse.get_pos()
                print(np.array(board))
                if event.button == 1:
                    if board[Mouse_y // 20][Mouse_x // 20] != 9:
                        board = uncover_squares(
                            board, [Mouse_y // 20, Mouse_x // 20])
                        # print(np.array(board))

                        for row in range(len(board)):
                            for col in range(len(board)):
                                if board[row][col] != 0 and board[row][col] != 9:
                                    if board[row][col] == -1:
                                        rect4 = pg.Rect(
                                            col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                                        pg.draw.rect(win, WHITE, rect4, 0)
                                    else:
                                        rect4 = pg.Rect(
                                            col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                                        pg.draw.rect(win, WHITE, rect4, 0)
                                        render_num(win, font, board[row][col],
                                                   colors[board[row][col]], col*20, row*20)

                        if board[Mouse_y // 20][Mouse_x // 20] != -1:
                            rect6 = pg.Rect(
                                Mouse_x//20 * 20, Mouse_y//20 * 20, SQUARE_SIZE, SQUARE_SIZE)

                            render_num(win, font, board[Mouse_y // 20][Mouse_x//20],
                                       colors[board[Mouse_y // 20][Mouse_x//20]], Mouse_x, Mouse_y)

                            #pg.draw.rect(win, DARKGREY, rect6, 0)
                    if board[Mouse_y // 20][Mouse_x//20] == 9:
                        display_img(win, BOMB_IMG, Mouse_x, Mouse_y, rect2)
                        moveable = False
                        pg.display.set_caption("You lost!")
                        lost = True

                if event.button == 3 and board[Mouse_y // 20][Mouse_x // 20] not in range(len(colors)):
                    if board[Mouse_y // 20][Mouse_x // 20] == 9:
                        found += 1
            if found == NUM_BOMBS and not any(0 in x for x in board):
                moveable = False
                pg.display.set_caption("You won!")
            if event.type == pg.QUIT:
                done = True
        pg.display.update()  # update display

    pg.quit()
    sys.exit()


def render_num(screen, font, num, color, mouse_x, mouse_y):
    screen.blit(font.render(str(num), True, color),
                (mouse_x // 20 * 20, mouse_y // 20 * 20))


def display_img(screen, img, mouse_x, mouse_y, rect):
    screen.blit(img, (mouse_x//20 * 20, mouse_y//20 * 20), rect)


def uncover_squares(board, move):
    neighbors = [(-1, 0), (-1, 1), (0, 1), (1, 1),
                 (1, 0), (1, -1), (0, -1), (-1, -1)]
    uncover(move[0], move[1], len(board), len(board[0]), board, neighbors)
    return board


def uncover(i, j, m, n, board, neighbors):
    if board[i][j] != 0:
        return
    mine_count = 0
    for cell in neighbors:
        # make sure the search is in bounds of array, then check if neighbor is a bomb
        if 0 <= i + cell[0] < m and 0 <= j + cell[1] < n and board[i + cell[0]][j + cell[1]] == 9:
            mine_count += 1
    if mine_count == 0:
        board[i][j] = -1
    else:
        board[i][j] = mine_count
        return
    for cell in neighbors:
        if 0 <= i + cell[0] < m and 0 <= j + cell[1] < n:
            uncover(i + cell[0], j + cell[1], m, n,
                    board, neighbors)  # call neighbors


if __name__ == "__main__":
    create_grid()
