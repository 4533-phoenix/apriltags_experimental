import numpy
import ast
import re

def check_input(input):
    return re.match("\[(.+)\]", input)

if __name__ == "__main__":
    section = input("Matrix: ")

    while not check_input(section):
        section += input("> ")

    matrix = ast.literal_eval(section)

    print(numpy.array(matrix).reshape(4, 4).tolist())