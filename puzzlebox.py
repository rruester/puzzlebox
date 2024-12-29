#!/bin/python

import random
import copy
import time
import signal
import sys
from enum import Enum

grid = [
    [ 1, 2, 3, 4],
    [ 1, 5, 6, 4],
    [ 7, 7, 0, 0],
    [ 8,10,10, 9],
    [ 8,10,10, 9],
]

empty = 0

class PieceType(Enum):
    SINGLE = 1
    VERTICAL = 2
    HORIZONTAL = 3
    SQUARE = 4
    EMPTY = 5

piece_types = [
    PieceType.EMPTY,
    PieceType.VERTICAL,
    PieceType.SINGLE,
    PieceType.SINGLE,
    PieceType.VERTICAL,
    PieceType.SINGLE,
    PieceType.SINGLE,
    PieceType.HORIZONTAL,
    PieceType.VERTICAL,
    PieceType.VERTICAL,
    PieceType.SQUARE,
]

h = len(grid)
w = len(grid[0])

moves = []

class Pt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Pt(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Pt(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def valid(self):
        return (0 <= self.x <= w-1) and (0 <= self.y <= h-1)

def sigint_handler(sig, frame):
    print(f"Killed after {len(moves)} moves")
    sys.exit(0)

def sigquit_handler(sig, frame):
    print(f"Currently on move {len(moves)}")

def show(g=None):
    if g is None:
        g = grid

    print("_"*30)
    for y in range(h):
        for x in range(w):
            piece = g[y][x]
            print(str(piece).ljust(3), end="")
        print()

def random_point():
    return Pt(random.randint(0,w-1), random.randint(0,h-1))

def random_offset():
    return random.choice([Pt(0,1), Pt(1,0), Pt(0,-1), Pt(-1,0)])

def points_in_piece(piece):
    points_in_piece = []
    for y in range(h):
        for x in range(w):
            if grid[y][x] == piece:
                points_in_piece.append(Pt(x, y))
    return points_in_piece

def try_move_piece(piece, offset):
    new_grid = copy.deepcopy(grid)
    points = points_in_piece(piece)
    for point in points:

        point_ahead = point + offset

        if not point_ahead.valid():
            return None

        piece_ahead = grid[point_ahead.y][point_ahead.x]

        if piece_ahead not in (empty, piece):
            return None

        new_grid[point_ahead.y][point_ahead.x] = piece

        point_behind = point - offset

        if not point_behind.valid():
            new_grid[point.y][point.x] = empty
            continue

        piece_behind = grid[point_behind.y][point_behind.x]
        if piece_behind != piece:
            new_grid[point.y][point.x] = empty

    return new_grid

def solved():
    return grid[0][1] == 10 and grid[0][2] == 10

def get_equivalent_pieces(piece):
    for i in range(len(equivalents)):
        if piece in equivalents[i]:
            return equivalents[i]
    raise Exception(f"No equivalents for {piece}")

def grids_are_same(g1, g2):
    for y in range(h):
        for x in range(w):
            g1_piece = g1[y][x]
            g1_type = piece_types[g1_piece]
            g2_piece = g2[y][x]
            g2_type = piece_types[g2_piece]
            if g1_type != g2_type:
                return False
    return True

def deduplicate():
    global moves
    improved = True
    while improved:
        improved = False
        for i in range(1, len(moves)):
            target = moves[-i]
            for j in range(len(moves)-i):
                potential_match = moves[j]
                if not grids_are_same(target, potential_match):
                    continue
                moves = moves[:j] + moves[-i:]
                improved = True
                break
            if improved:
                break

def solve():
    global grid, moves
    while not solved():
        point_to_move = random_point()
        piece_to_move = grid[point_to_move.y][point_to_move.x]

        if piece_to_move == empty:
            continue

        offset = random_offset()

        new_grid = try_move_piece(piece_to_move, offset)

        if new_grid is None:
            continue

        if len(moves) > 10000:
            exit()

        moves.append(new_grid)
        grid = new_grid

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGQUIT, sigquit_handler)

solve()

print(f"Solved after {len(moves)} moves")

deduplicate()

print(f"Shortened list is {len(moves)} moves")
