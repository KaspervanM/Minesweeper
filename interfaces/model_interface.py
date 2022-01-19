#!/bin/bash; C:/Program\ Files/Git/usr/bin/sh.exe
"""Provides Model class and functions as an interface for the NNModel.dll.

Model holds the data required for an operational neural network (weights,
biases, activation functions, etc.) feedforward takes input and returns the
output calculated by the model. train_from_file trains the model according to
the training data in the given file. train_from_array trains the model
according to the training data given.
"""

from ctypes import (
    CDLL,
    c_int,
    c_uint,
    c_double,
    c_char_p,
    c_void_p,
    c_bool,
    POINTER,
    byref,
    _reset_cache,
)
from os.path import isfile

__author__ = "Kasper van Maasdam"
__copyright__ = "Copyright 2022, school research project"
__credits__ = ["Kasper van Maasdam", "Tom Lokhorst"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Kasper van Maasdam"
__email__ = "kaspervanm@gmail.com"
__status__ = "Development"

lib = CDLL("C:\Users\maasd\OneDrive\Documenten\VSC\Python\Minesweeper-1\interfaces\DLL\NNModel.dll")


class Model(object):
    """Interface for the Model in NNModel.dll.

    Methods:
    getWeights: Returns the weights of the model.
    getBiases: Returns the biases of the model.
    getShape: Returns the shape of the model.
    getActFuncts: Returns the activation functions of the model.
    """

    def __init__(
        self, seed=None, size=None, shape=None, actFuncts=None, obj=None
    ):
        """Returns new Model object with seed, size, shape, actFuncts.

        Arguments:
        seed (int): The seed for generating weights and biases. If -1, random.
        size (uint): The size of the model, a.k.a. the amout of layers.
        shape (uint list): The number of nodes of each layer.
        actFuncts (uint list): The activation functions of each layer.
        obj (Model object): The model object to assign.

        Note: shape length should be size and that of actFuncts size - 1.
        Also, if obj is provided, all other arguments will be ignored.

        Raises:
        ValueError: Raised if invalid arguments are passed or shape or
        actFuncts are of incorrect length.
        """

        if obj is not None:
            self.obj = obj
        else:

            if seed <= -1:
                raise ValueError(
                    "seed is %d, but should be -1 or higher." % seed
                )
            if size <= 1:
                raise ValueError(
                    "size is %d, but should be higher than 1." % size
                )
            if any(x < 1 for x in shape):
                raise ValueError(
                    "Invalid shape. All layers should be greater than 0."
                )
            if any(x < 0 or x > 14 for x in actFuncts):
                raise ValueError(
                    "Invalid activation function. All activation functions \
should be greater than or equal to 0 and smaller than 15."
                )
            if len(shape) != size:
                raise ValueError(
                    "Invalid shape length: %d. Expected: %d"
                    % (len(shape), size)
                )
            if len(actFuncts) != size - 1:
                raise ValueError(
                    "Invalid actFuncts length: %d. Expected: %d"
                    % (len(actFuncts), size - 1)
                )

            lib.Model_new.argtypes = [
                c_int,
                c_uint,
                POINTER(c_uint),
                POINTER(c_uint),
            ]
            lib.Model_new.restype = c_void_p

            cshape = (c_uint * len(shape))(*shape)
            cactFuncts = (c_uint * len(actFuncts))(*actFuncts)
            self.obj = lib.Model_new(seed, size, cshape, cactFuncts)

        lib.Model_getWeights.argtypes = [c_void_p, POINTER(c_uint)]
        lib.Model_getWeights.restype = POINTER(c_double)

        lib.Model_getBiases.argtypes = [c_void_p, POINTER(c_uint)]
        lib.Model_getBiases.restype = POINTER(c_double)

        lib.Model_getShape.argtypes = [c_void_p, POINTER(c_uint)]
        lib.Model_getShape.restype = POINTER(c_uint)

        lib.Model_getActFuncts.argtypes = [c_void_p, POINTER(c_uint)]
        lib.Model_getActFuncts.restype = POINTER(c_uint)

    def getWeights(self):
        """Returns the weights of the model."""
        csize = c_uint()
        weights = lib.Model_getWeights(self.obj, byref(csize))
        li = [weights[i] for i in range(csize.value)]
        lib.freeOutD(weights)
        return li

    def getBiases(self):
        """Returns the biases of the model."""
        csize = c_uint()
        biases = lib.Model_getBiases(self.obj, byref(csize))
        li = [biases[i] for i in range(csize.value)]
        lib.freeOutD(biases)
        return li

    def getShape(self):
        """Returns the shape of the model."""
        csize = c_uint()
        shape = lib.Model_getShape(self.obj, byref(csize))
        li = [shape[i] for i in range(csize.value)]
        lib.freeOutI(shape)
        return li

    def getActFuncts(self):
        """Returns the activation functions of the model."""
        csize = c_uint()
        actFuncts = lib.Model_getActFuncts(self.obj, byref(csize))
        li = [actFuncts[i] for i in range(csize.value)]
        lib.freeOutI(actFuncts)
        return li


lib.Model_getMutated.argtypes = [c_void_p, c_int, c_double, c_double]
lib.Model_getMutated.restype = c_void_p

lib.feedforward.argtypes = [c_void_p, POINTER(c_double)]
lib.feedforward.restype = POINTER(c_double)

lib.freeOutD.argtypes = [POINTER(c_double)]
lib.freeOutD.restype = c_void_p

lib.freeOutI.argtypes = [POINTER(c_uint)]
lib.freeOutI.restype = c_void_p

lib.freeOutM.argtypes = [c_void_p]
lib.freeOutM.restype = c_void_p

lib.trainFromFile.argtypes = [
    c_void_p,
    c_uint,
    c_double,
    c_char_p,
    c_uint,
    c_double,
    c_int,
]
lib.trainFromFile.restype = c_void_p

lib.trainFromArray.argtypes = [
    c_void_p,
    c_uint,
    c_double,
    POINTER(c_double),
    c_uint,
    c_uint,
    c_double,
    c_int,
]
lib.trainFromArray.restype = c_void_p

lib.saveModel.argtypes = [c_void_p, c_char_p]
lib.saveModel.restype = c_bool

lib.loadModel.argtypes = [c_void_p, c_char_p]
lib.loadModel.restype = c_void_p

lib.createBitmap.argtypes = [c_void_p, c_char_p]
lib.createBitmap.restype = c_bool

# _reset_cache()


def getMutated(model, seed, rate, degree):
    """Interface for the mutateModel function in NNModel.dll

    Arguments:
    model (Model object): The model used as a template.
    seed (int): The seed for generating mutations. If below 0, random.
    rate (double): The chance of a weight or bias to mutate.
    degree (double): The degree of change: how much the parameter changes.

    Return:
    Returns a mutated copy of the input model.
    """
    return lib.Model_getMutated(
        model.obj, c_int(seed), c_double(rate), c_double(degree)
    )


def freeModel(models):
    """Interface for the freeOut function in NNModel.dll

    Arguments:
    models (list of Model objects): The models to be freed.
    """
    for model in models:
        lib.freeOutM(model[0].obj)


def feedforward(model, inp):
    """Interface for the feedforward function in NNModel.dll

    Arguments:
    model (Model object): The model used by the feedforward function.
    inp (list double): The input for the Model object.

    Raises:
    ValueError: Raises if the input is of incorrect length.

    Return:
    Returns the output values in a list.
    """
    shape = model.getShape()
    if len(inp) != shape[0]:
        raise ValueError(
            "Invalid inp length: %d. Expected: %d" % (len(inp), shape[0])
        )

    cinput = (c_double * len(inp))(*inp)
    output = lib.feedforward(model.obj, cinput)
    li = [output[i] for i in range(shape[-1])]
    lib.freeOutD(output)
    return li


def train_from_file(
    model,
    iterations,
    learning_rate,
    path_to_file,
    batch_size,
    percentage_of_data_not_to_train,
    training_data_seed,
):
    """Interface for the trainFromFile function in NNModel.dll.

    Arguments:
    model (Model object): The model that will be trained.
    iterations (uint): The number of times the training data will be iterated.
    learning_rate (double): A factor in all changes to the weights and biases.
    path_to_file (string): The path to the file containing the training data.
    batch_size (uint): Amount of training data samples each batch will contain.
    percentage_of_data_not_to_train (double): -- Not yet included.
    training_data_seed (int): Shuffle training data. -1: random -2: no shuffle.

    Note: The last batch of training data may be smaller than batch_size.

    Raises:
    ValueError: Raised if invalid arguments are passed.
    FileNotFoundError: Raised if path_to_file can not be found.
    """
    if training_data_seed <= -2:
        raise ValueError(
            "seed is %d, but should be -2 or higher." % training_data_seed
        )
    if iterations < 1:
        raise ValueError(
            "iterations is %d, but should be higher than 1." % iterations
        )
    if batch_size < 1:
        raise ValueError(
            "batch_size is %d, but should be higher than 1." % batch_size
        )
    if percentage_of_data_not_to_train < 0:
        raise ValueError(
            "percentage_of_data_not_to_train is %d, \
but should be higher than 1."
            % percentage_of_data_not_to_train
        )
    if not isfile(path_to_file):
        raise FileNotFoundError("%s not found." % path_to_file)
    cname = c_char_p()
    cname.value = path_to_file.encode()
    lib.trainFromFile(
        model.obj,
        c_uint(iterations),
        c_double(learning_rate),
        cname,
        c_uint(batch_size),
        c_double(percentage_of_data_not_to_train),
        c_int(training_data_seed),
    )


def train_from_array(
    model,
    iterations,
    learning_rate,
    trainingDataArray,
    batch_size,
    percentage_of_data_not_to_train,
    training_data_seed,
):
    """Interface for the trainFromArray function in NNModel.dll.

    Arguments:
    model (Model object): The model that will be trained.
    iterations (uint): The number of times the training data will be iterated.
    learning_rate (double): A factor in all changes to the weights and biases.
    trainingDataArray (list double): The array containing the training data.
    batch_size (uint): Amount of training data samples each batch will contain.
    percentage_of_data_not_to_train (double): -- Not yet included.
    training_data_seed (int): Shuffle training data. -1: random -2: no shuffle.

    Note: The last batch of training data may be smaller than batch_size.

    Raises:
    ValueError: Raised if invalid arguments are passed.
    """
    if training_data_seed <= -2:
        raise ValueError(
            "seed is %d, but should be -2 or higher." % training_data_seed
        )
    if iterations < 1:
        raise ValueError(
            "iterations is %d, but should be higher than 1." % iterations
        )
    if batch_size < 1:
        raise ValueError(
            "batch_size is %d, but should be higher than 1." % batch_size
        )
    if percentage_of_data_not_to_train < 0:
        raise ValueError(
            "percentage_of_data_not_to_train is %d, \
but should be higher than 1."
            % percentage_of_data_not_to_train
        )
    try:
        if any(len(ele) != 2 for ele in trainingDataArray):
            raise ValueError("Incorrect shape of trainingDataArray")
    except TypeError:
        raise TypeError("Incorrect shape of trainingDataArray")

    flat_trainingDataArray = [
        item
        for sublist in trainingDataArray
        for subsublist in sublist
        for item in subsublist
    ]
    cflat_trainingDataArray = (c_double * len(flat_trainingDataArray))(
        *flat_trainingDataArray
    )
    lib.trainFromArray(
        model.obj,
        c_uint(iterations),
        c_double(learning_rate),
        cflat_trainingDataArray,
        c_uint(len(trainingDataArray)),
        c_uint(batch_size),
        c_double(percentage_of_data_not_to_train),
        c_int(training_data_seed),
    )


def save_model(model, filename):
    cname = c_char_p()
    cname.value = filename.encode()
    return lib.saveModel(model.obj, cname)


def load_model(model, path_to_file):
    if not isfile(path_to_file):
        raise FileNotFoundError("%s not found." % path_to_file)
    cname = c_char_p()
    cname.value = path_to_file.encode()
    lib.loadModel(model.obj, cname)


def createBitmap(model, filename):
    cname = c_char_p()
    cname.value = filename.encode()
    return lib.createBitmap(model.obj, cname)


if __name__ == "__main__":  # code to execute if called from command-line
    pass
