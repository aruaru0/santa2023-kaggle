from typing import Tuple
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
import random

globe_dims = {
    'globe_1/8': (2, 16),
    'globe_1/16': (2, 32),
    'globe_2/6': (3, 12),
    'globe_3/4': (4, 8),
    'globe_6/4': (7, 8),
    'globe_6/8': (7, 16),
    'globe_6/10': (7, 20),
    'globe_3/33': (4, 66),
    'globe_8/25': (9, 50)
}

def display_globe(state, type='globe_8/25'):
    tiles = state.split(';')
    rows, cols = globe_dims[type]
    for j in range(cols):
        print(("    " + str(j))[-4:], end='')
    print()
    for i in range(rows):
        for j in range(cols):
            print(("    " + tiles[i*cols + j])[-4:], end='')
        print()


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

def expand(paths, reverse=False):
    states = list(paths.keys())
    for s in states:
        for m in moves:
            if reverse:
                next_s = reverse_move(m, s)
                if not next_s in paths:
                    paths[next_s] = paths[s] + [m]
            else:
                next_s = apply_move(m, s)
                if not next_s in paths:
                    paths[next_s] = paths[s] + [m]

def valid_check(state : str, target : str, num_wild :int) :
    cnt = 0
    for x, y in zip(state.split(";"), target.split(";")):
        if x != y : cnt+=1
    if cnt <= num_wild:
        return True
    return False


def init_dic() :
    data = {
        # 1: [14, "f14 -r0 f14 r0 f14 -r0 f14 -r1 f14 r0 r1 f14"],
        # 2: [15, "f15 -r1 f15 -r0 f15 -r1 f15 r1 f15 r0 r1 f15"],
        # 3: [15, "f14 -r1 -r0 -r1 f14 r1 f14 r0 f14 -r0 f14 r0 r1 f14"],      
        # 4: [15, "f13 -r0 -r1 -r0 -r1 f13 r1 f13 r0 f13 -r0 f13 r0 r1 r0 f13"],     
        # 5: [15, "f13 -r0 -r1 -r0 -r1 f13 -r0 f13 -r1 f13 r1 f13 r0 r1 r0 r1 r0 f13"],    
        # 6: [15, "f12 -r1 -r0 -r1 -r0 -r1 -r0 f12 r1 f12 r0 f12 -r0 f12 r1 r0 -r1 r0 r1 r0 r1 f12"],   
        # 7: [15, "f12 -r1 -r0 -r1 -r0 -r1 -r0 -r1 f12 r1 f12 r0 f12 -r0 f12 r0 r1 r0 r1 r0 r1 f12"],      
        # 8: [15, "f11 -r0 -r1 -r0 -r1 -r0 -r1 -r0 -r1 f11 r1 f11 r0 f11 -r0 f11 r0 r1 r0 r1 r0 r1 r0 f11"],   
        # 9: [31, "f23 -r0 -r0 -r0 -r0 -r0 -r0 -r0 -r0 -r1 f23 r1 f23 r0 f23 -r0 f23 r0 r0 r0 r0 r0 r0 r0 r0 f23"],       
    
        1: [14, "f14 -r0 f14 r0 f14 -r0 f14 -r1 f14 r0 r1 f14"],
        2: [15, "f15 -r1 f15 -r0 f15 -r1 f15 r1 f15 r0 r1 f15"],
        3: [15, "f14 -r1 -r0 -r1 f14 r1 f14 r0 f14 -r0 f14 r0 r1 f14"],      
        4: [15, "f13 -r0 -r1 -r0 -r1 f13 r1 f13 r0 f13 -r0 f13 r0 r1 r0 f13"],     
        5: [15, "f13 -r0 -r1 -r0 -r1 f13 -r0 f13 -r1 f13 r1 f13 r0 r1 r0 r1 r0 f13"],    
        6: [15, "f12 -r1 -r0 -r1 -r0 -r1 -r0 f12 r1 f12 r0 f12 -r0 f12 r1 r0 -r1 r0 r1 r0 r1 f12"],   
        7: [15, "f12 -r1 -r0 -r1 -r0 -r1 -r0 -r1 f12 r1 f12 r0 f12 -r0 f12 r0 r1 r0 r1 r0 r1 f12"],      
        8: [15, "f11 -r0 -r1 -r0 -r1 -r0 -r1 -r0 -r1 f11 r1 f11 r0 f11 -r0 f11 r0 r1 r0 r1 r0 r1 r0 f11"],     
        9: [31, "f23 -r0 -r0 -r0 -r0 -r0 -r0 -r0 -r0 -r1 f23 r1 f23 r0 f23 -r0 f23 r0 r0 r0 r0 r0 r0 r0 r0 f23"],       
        10: [31, "f26 -r0 -r1 -r0 -r1 -r0 -r1 -r0 -r1 -r0 -r1 f26 r1 f26 r0 f26 -r0 f26 r0 r1 r0 r1 r0 r1 r0 r1 r0 f26"],        
        11: [31, "-r0 f26 -r0 -r1 -r0 -r1 -r0 -r1 -r0 -r1 -r0 -r1 f26 -r0 f26 -r1 f26 r1 f26 r0 r1 r0 r1 r0 r1 r0 r1 r0 r1 r0 f26 r0"],          }
    dic = {}
    for e in data:
        pos, pat = data[e]
        pat = pat.split()
        x = []
        for v in pat:
            if v[0] == 'f' :
                n = int(v[1:]) - pos
                x.append(['f', n])
            else:
                x.append([v])
        dic[e] = x
    return dic





def calc_lower_pos(cur :int, target :int, rdic: dict,  mod :int = 32) -> Tuple[str, int] :
    n = sorted(list(db.keys()), reverse=True)

    diff = cur - target
    idx = -1
    for e in n:
        if e <= diff :
            idx = e
            break
    print(idx, diff)

    ret = []
    for e in db[idx]:
        if e[0] == "f" :
            pos = (e[1] + cur)%mod
            if pos < 0 :
                pos = (pos + mod)%mod
            v = e[0] + str(pos)
            ret.append(v)
        else :
            if e[0][0] == '-' :
                ret.append('-' + rdic[e[0][1:]])
            else:
                ret.append(rdic[e[0]])

    # print(ret)
    return ret, cur-idx
    


# now = 15
# tgt = 1


# path = []
# while now != tgt :
#     ret, now = calc_lower_pos(now, tgt, rdic = dic, mod=66)
    
#     print(now)
#     print(*ret)
#     path += ret

# print(*path)

# exit()

parser = argparse.ArgumentParser()
parser.add_argument("--problem_id", type=int, required=True)
args = parser.parse_args()


PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
SAMPLE_FILE = './data/sample_submission.csv'

RUN_TIME = 60 * 60 * 11
START_TIME = time.time()
TIMEOUT = 60 * 5

INCLUDES = None
EXCLUDES = None
MIN_SIZE = None
MAX_SIZE = 24 + 1

data_df = pd.read_csv(PUZZLE_FILE)
info_df = pd.read_csv(PUZZLE_INFO_FILE)
sample_df = pd.read_csv(SAMPLE_FILE)  


pid = args.problem_id

ddf = data_df.iloc[pid]
puzzle_type = ddf.puzzle_type
solution_state = ddf.solution_state
initial_state = ddf.initial_state
num_wildcards = ddf.num_wildcards

idf = info_df[info_df['puzzle_type'] == puzzle_type]
allowed_moves = idf['allowed_moves'].iloc[0]    
moves = ast.literal_eval(allowed_moves)

moves = init_reverse_moves(moves)

pdf = sample_df.iloc[pid]
path = pdf.moves.split(".")

state = ddf.solution_state
num_state = ";".join([str(i) for i in range(50*9)])
for e in path[::-1]:
    if e[0] == '-' :
        e = e[1:]
    else :
        e = '-' + e
    state = apply_move(e, state)
    num_state = apply_move(e, num_state)

print("STATE = ", state)
print("INIT  = ", ddf.initial_state)
print("NUMS  = ", num_state)
print("-"*80)

with open(f"tmp/{pid}.txt", "r") as f :
    newpath = f.read()

newpath = newpath.split(".")

for e in newpath:
    state = apply_move(e, state)
    num_state = apply_move(e, num_state)

print("START = ", state)
print("NUMS  = ", num_state)

display_globe(solution_state)
print("="*80)
display_globe(state)

db = init_dic()

# row5
dic = {'r0':'r3', 'r1':'r5'}
c = 5
for i in range(50*c, 50*(c+1)-4) :
    target = i
    # s = list(map(int, num_state.split(";")))
    # for j in range(i, 66*3) :
    #     if s[j] == i :
    #         cur = j
    #         break
    s = state.split(";")
    t = solution_state.split(";")
    cur = i
    for j in range(i, 50*(c+1)) :
        if s[j] == t[i] :
            cur = j
            break
    print(cur%50, target%50)
    p = []
    while cur != target :
        ret, cur = calc_lower_pos(cur, target, rdic = dic, mod=50)
        p += ret

    newpath += p

    for e in p:
        state = apply_move(e, state)
        num_state = apply_move(e, num_state)
    print("="*80)
    display_globe(state)
 

# row6
dic = {'r0':'r2', 'r1':'r6'}
c = 6
for i in range(50*c, 50*(c+1)-4) :
    target = i
    # s = list(map(int, num_state.split(";")))
    # for j in range(i, 66*3) :
    #     if s[j] == i :
    #         cur = j
    #         break
    s = state.split(";")
    t = solution_state.split(";")
    cur = i
    for j in range(i, 50*(c+1)) :
        # print(t[i], "->", s[j])
        if s[j] == t[i] :
            cur = j
            break
    print(cur%50, target%50)
    p = []
    while cur != target :
        ret, cur = calc_lower_pos(cur, target, rdic = dic, mod=50)
        p += ret

    newpath += p

    for e in p:
        state = apply_move(e, state)
        num_state = apply_move(e, num_state)
    print("="*80)
    display_globe(state)


# row7
dic = {'r0':'r1', 'r1':'r7'}
c = 7
for i in range(50*c, 50*(c+1)-4) :
    target = i
    # s = list(map(int, num_state.split(";")))
    # for j in range(i, 66*3) :
    #     if s[j] == i :
    #         cur = j
    #         break
    s = state.split(";")
    t = solution_state.split(";")
    cur = i
    for j in range(i, 50*(c+1)) :
        # print(t[i], "->", s[j])
        if s[j] == t[i] :
            cur = j
            break
    print(cur%50, target%50)
    p = []
    while cur != target :
        ret, cur = calc_lower_pos(cur, target, rdic = dic, mod=50)
        p += ret

    newpath += p

    for e in p:
        state = apply_move(e, state)
        num_state = apply_move(e, num_state)
    print("="*80)
    display_globe(state)
 
# row8
dic = {'r0':'r0', 'r1':'r8'}
c = 8
for i in range(50*c, 50*(c+1)-4) :
    target = i
    # s = list(map(int, num_state.split(";")))
    # for j in range(i, 66*3) :
    #     if s[j] == i :
    #         cur = j
    #         break
    s = state.split(";")
    t = solution_state.split(";")
    cur = i
    for j in range(i, 50*(c+1)) :
        # print(t[i], "->", s[j])
        if s[j] == t[i] :
            cur = j
            break
    print(cur%50, target%50)
    p = []
    while cur != target :
        ret, cur = calc_lower_pos(cur, target, rdic = dic, mod=50)
        p += ret

    newpath += p

    for e in p:
        state = apply_move(e, state)
        num_state = apply_move(e, num_state)
    print("="*80)
    display_globe(state)


tmp_path = []
for e in newpath :
    if len(tmp_path) == 0 :
        tmp_path.append(e)
        continue
    if e[0] == 'f' :
        if  e == tmp_path[-1] : # ２つで消す
            tmp_path = tmp_path[:-1]
        else :
            tmp_path.append(e)
    else:
        v = tmp_path[-1]
        if v[0] == '-' : v = v[1:]
        else: v = '-' + v
        if e == v : 
            tmp_path = tmp_path[:-1]
        else :
            tmp_path.append(e)            

newpath = tmp_path

print(len(newpath))

state = ddf.initial_state
for e in newpath:
    state = apply_move(e, state)

display_globe(state)

if valid_check(state, solution_state, num_wildcards) :
    print("Found Path=", len(newpath))
    with open(f"./{pid}_solved.txt", "w") as f :
        f.write(".".join(newpath))
