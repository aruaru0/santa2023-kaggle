import sys
import pandas as pd
import numpy as np
import ast
import os
import time
from tqdm import tqdm
from collections import defaultdict
import copy
from itertools import combinations
import subprocess
import gc
import argparse
from collections import deque

# -------------------------------------------------------------------
def init_reverse_moves(moves):
    new_moves = {}
    
    for m in moves.keys():
        new_moves[m] = moves[m]
        xform = moves[m]
        m_inv = '-' + m
        xform_inv = len(xform) * [0]
        for i in range(len(xform)):
            xform_inv[xform[i]] = i
        new_moves[m_inv] = xform_inv

    return new_moves

def apply_move(move, state):

    m = move
    s = state.split(';')

    move_list = moves[m]
    new_state = []
    for i in move_list:
        new_state.append(s[i])
    s = new_state

    return ';'.join(s)

def reverse_move(move, state):
    m = move[1:] if move[0] == '-' else '-' + move
    return apply_move(m, state)

def valid_check(state, target, num_wild) :
    cnt = 0
    for x, y in zip(state.split(";"), target.split(";")):
        if x != y : cnt+=1
    if cnt <= num_wild:
        return True
    return False

def print_cube3x3(s, status):
    print("="*40)
    print(s)
    print("="*40)
    st = status.split(";")
    pos = 0
    p = [[' ' for _ in range(12)] for _ in range(9)]
    start = [(0,3), (3,3), (3,6), (3, 9), (3, 0), (6, 3)]
    for i in range(6) :
        sy, sx = start[i]
        for j in range(9) :
            val = st[i*9+j]
            dx = j%3
            dy = j//3
            px = sx + dx
            py = sy + dy
            if len(val) == 2 : val += ' '
            p[py][px] = val
    for i in range(9) :
        for j in range(12) :
            print(p[i][j], end=' ')
        print()
    
def print_cube(status, n) :
    s = status.split(";")
    p = [1, 2, 3, 4, 0, 5]
    n2 = n*n
    for e in p :
        sel = s[e*n2:(e+1)*n2:]        
        l = []
        for i in range(3, -1, -1) :
            l += sel[i*n:(i+1)*n]
        # print(l)
        print(" ".join(l),end="  | ")
    print("")

def valid_check(state, target, num_wild) :
    cnt = 0
    for x, y in zip(state.split(";"), target.split(";")):
        if x != y : cnt+=1
    if cnt <= num_wild:
        return True
    return False

parser = argparse.ArgumentParser()
parser.add_argument("--problem_id", type=int, required=True)
parser.add_argument("--path_dir", type=str, required=True)
args = parser.parse_args()

PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'

data_df = pd.read_csv(PUZZLE_FILE)
info_df = pd.read_csv(PUZZLE_INFO_FILE)

pid = args.problem_id
print(f"PID: {pid}")
ddf = data_df[data_df['id'] == pid]

puzzle_type = ddf['puzzle_type'].iloc[0]
solution_state = ddf['solution_state'].iloc[0]
initial_state = ddf['initial_state'].iloc[0]
num_wildcards = ddf['num_wildcards'].iloc[0]

if puzzle_type == "globe_33/3" : puzzle_type = "globe_3/33"

idf = info_df[info_df['puzzle_type'] == puzzle_type]
allowed_moves = idf['allowed_moves'].iloc[0]    
moves = ast.literal_eval(allowed_moves)
moves = init_reverse_moves(moves)

# 処理したファイルがあればをちらも参照
file = f"{args.path_dir}/{pid}.txt"
if os.path.isfile(file) :
    with open(file, "r") as f:
        s = f.read()
    paths = s.split(".")
    

# print(paths)

size = 19

center = size/2



dic = {'f':'b', 'r':'l', 'd':'u'}

# state = solution_state.replace("A", "4").replace("B", "0").replace("C", "1").replace("D", "2").replace("E","3").replace("F","5")
with open("scramble.txt", "w") as f:
    for i, e in enumerate(paths[::-1]) :
        if e[0] == '-' :
            e = e[1:]
        else:
            e = '-' + e
        sign = 1
        v = e
        if e[0] == '-' :
            sign = -1
            v = e[1:]
        m = v[0]
        n = int(v[1:])
        f.write(f"Move({m.upper()},{n},{sign});\n")    
        # print("-----------------")
        # print(i+1, ":", v, f"Move({m.upper()},{n},{sign});")
        # print_cube(state, 4)
        # state = apply_move(e, state)
        # print_cube(state, 4)
    # for e in paths[::-1] :
    #     if e[0] == '-' :
    #         e = e[1:]
    #     else:
    #         e = '-' + e

    #     sign = 1
    #     if e[0] == '-' :
    #         sign = -1
    #         e = e[1:]
    #     m = e[0]
    #     n = int(e[1:])
    #     if n > center :
    #         m = dic[m]
    #         n = size - 1 - n
    #         sign *= -1
    #     f.write(f"Move({m.upper()},{n},{sign});\n")


L = "L"
D = "D"
U = "U"
R = "R"
F = "F"
B = "B"

rdic = {'B':'f', 'L':'r', 'U':'d'}

with open("sol.txt", "r") as f:
    mvs = eval("[" + f.read() + "]")



# initial_state = initial_state.replace("A", "4").replace("B", "0").replace("C", "1").replace("D", "2").replace("E","3").replace("F","5")

paths = []
state = initial_state
for i, e in enumerate(mvs) :
    m, n, sign = e
    if m in rdic :
        m = rdic[m]
        sign *= -1
        n = size - 1 - n
    else :
        m = m.lower()
    mv = m + str(n)
    if sign < 0 :
        mv = "-" + mv
    for j in range(abs(sign)) :
        if mv not in moves :
            print(e, mv)
        paths.append(mv)
        state = apply_move(mv, state)
    # print((i+1),  ":",  e, mv, sign, ":-------------------------------",)
    # # print(state)
    # print_cube(state, size)
    # print(" ")

state = initial_state
# print_cube3x3("initial" , state)
print("INI", initial_state)
for i, e in enumerate(paths) :
    state = apply_move(e, state)
    # print_cube3x3(str(i+1) + ":" + str(e) + mv, state)
print("SOL",solution_state)
print("RES", state, size)

if valid_check(state, solution_state, num_wildcards) :
    print("ok")
    print(len(paths))
    with open(f"./{pid}.txt", "w") as f :
        f.write(".".join(paths))




# for i, e in enumerate(mvs) :
#     m, n, sign = e
#     if m in rdic :
#         m = rdic[m]
#         sign *= -1
#         n = size - 1 - n
#     else :
#         m = m.lower()
#     mv = m + str(n)
#     if sign < 0 :
#         mv = "-" + mv
#     for j in range(abs(sign)) :
#         state = apply_move(mv, state)    
#     # state = apply_move(mv, state)
#     print((i+1),  ":", e, mv, sign)
#     print_cube3x3(str(i+1) + ":" + str(e) + mv, state)

# print(state)
    
    

# size2 = 3**2

# m = {"A":4, "B":0, "C":1, "D":2, "E":3, "F":5}

# state = initial_state.split(";")

# a = []
# for e in state:
#     a.append(m[e])

# renum = [1,2,3,4,0,5]
# b = []
# for i in renum :
#     b += a[i*size2:(i+1)*size2]

# print(a)
# print(b)
