from interfaces.model_interface import (
    Model,
    train_from_file,
    save_model,
)


SEED = 0
SHAPE = [81, 10, 10, 3]
ACT_FUNCTS = [4, 4, 2]

MODEL = Model(SEED, len(SHAPE), SHAPE, ACT_FUNCTS)
ITERATIONS = 10000
LEARNING_RATE = .1
PATH_TO_FILE = "Data/2022-01-24_15-42-26_trainingdata.txt"
BATCH_SIZE = 100
PERCENTAGE_OF_DATA_NOT_TO_TRAIN = 0
TRAINING_DATA_SEED = 0

train_from_file(MODEL,
                ITERATIONS,
                LEARNING_RATE,
                PATH_TO_FILE,
                BATCH_SIZE,
                PERCENTAGE_OF_DATA_NOT_TO_TRAIN,
                TRAINING_DATA_SEED)

NAME = f"_SEED{SEED}_s"
for s in SHAPE:
    NAME += str(s) + "-"
NAME = NAME[:-1] + "_a"
for a in ACT_FUNCTS:
    NAME += str(a) + "-"
NAME = NAME[:-1]

save_model(MODEL, "saves/" + NAME + ".txt")
