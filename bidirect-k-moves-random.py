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
    
# -------------------------------------------------------------------
class ExceedMaxSizeError(RuntimeError):
    pass

def get_shortest_path(
    moves: dict[str, tuple[int, ...]], max_size: int 
) -> dict[tuple[int, ...], list[str]]:
    n = len(next(iter(moves.values())))

    state = tuple(range(n))
    cur_states = [state]

    shortest_path: dict[tuple[int, ...], list[str]] = {}
    shortest_path[state] = []

    # 初期パターンからK回置換を繰り返して到達できるパターンを全探索する
    # もし、パターンが登録されていなければshottest_pathにパターンを登録する
    for k in range(100):
        next_states = []
        for state in cur_states:
            for move_name, perm in moves.items():
                if k > 8 and random.random() > 0.5 : continue
                next_state = tuple(state[i] for i in perm)
                if next_state in shortest_path:
                    continue
                shortest_path[next_state] = shortest_path[state] + [move_name]

                if max_size is not None and len(shortest_path) > max_size:
                    return shortest_path, k
                    raise ExceedMaxSizeError

                if len(shortest_path)%1000000 == 0 : print(len(shortest_path), k)
                next_states.append(next_state)
        cur_states = next_states

    return shortest_path, 100

# ルービックキューブ上に表示
def print_cube3x3(s, status):
    print("="*40)
    print(s)
    print("="*40)
    st = status.split(";")
    pos = 0
    blank = ' ' if len(st[3]) == 1 else '   '
    p = [[blank for _ in range(12)] for _ in range(9)]
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


def make_states(state, moves) :
    ret = {}
    s = state.split(";")
    for e in moves:
        t = ";".join([s[i] for i in e])
        if t in ret :
            if len(ret[t]) > len(e) : ret[t] = moves[e]
        else:
            ret[t] = moves[e]
    return ret        


# -------------------------------------------------------------------
# 30-149
parser = argparse.ArgumentParser()
parser.add_argument("--problem_id", type=int, required=True)
parser.add_argument("--limit", type=int, default=100000) 
parser.add_argument("--csv_file", type=str, required=True)
args = parser.parse_args()

PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
SAMPLE_FILE = args.csv_file

data_df = pd.read_csv(PUZZLE_FILE)
info_df = pd.read_csv(PUZZLE_INFO_FILE)
sample_df = pd.read_csv(SAMPLE_FILE)    

prev_puzzle_type = ""
shortest_path = ""

pid = args.problem_id
print("="*20)
print(f"PID: {pid}")
ddf = data_df[data_df['id'] == pid]
puzzle_type = ddf['puzzle_type'].iloc[0]
solution_state = ddf['solution_state'].iloc[0]
initial_state = ddf['initial_state'].iloc[0]
num_wildcards = ddf['num_wildcards'].iloc[0]

idf = info_df[info_df['puzzle_type'] == puzzle_type]
allowed_moves = idf['allowed_moves'].iloc[0]    
moves = ast.literal_eval(allowed_moves)
moves = init_reverse_moves(moves)

pdf = sample_df[sample_df['id']==pid]
paths = pdf['moves'].iloc[0].split(".")

# 処理したファイルがあればをちらも参照
file = f"./sol_2dir_k/{pid}.txt"
if os.path.isfile(file) :
    with open(file, "r") as f:
        s = f.read()
    s = s.split(".")
    if len(paths) > len(s) :
        paths = s
        print(f"-->  use shotest file {file} : len = {len(paths)}")


org_len = len(paths)

# print("INIT   : ", initial_state)
# print("TARGET : ", solution_state)

# とりあえず、状態遷移を作成
state = initial_state
states = [state]
for e in paths:
    state = apply_move(e, state)
    states.append(state)
# print(state)

#print(moves, path)

max_size = args.limit
# if puzzle_type == 'cube_3/3/3' :
#     max_size = 1000000
# elif  'wreath' in puzzle_type :
#     max_size = 200000

# とりあえず、パスを作成しておく
if prev_puzzle_type != puzzle_type :

    shortest_path, K = get_shortest_path(moves,  max_size)
    K-=1
    # K = 2# ⭐︎⭐︎⭐︎⭐︎⭐︎⭐︎⭐︎
    # while True:
    #     try:
    #         shortest_path = get_shortest_path(moves, K, None if K == 2 else max_size)
    #     except ExceedMaxSizeError:
    #         break
    #     if len(shortest_path) > max_size : break
    #     if puzzle_type == "cube_3/3/3" and K == 6 : break
    #     K += 1
    #     # break # ⭐︎⭐︎⭐︎⭐︎⭐︎⭐︎⭐︎
    # K -= 1
    # print(f"K: {K}")
    print(f"Number of shortest_path: {len(shortest_path)} ({max_size})")
    prev_puzzle_type = puzzle_type

# for e in shortest_path :
#     if len(shortest_path[e]) == K :
#         print("!"*80)
#         print(shortest_path[e])
#         break

# 開始パターン
step = K*2
start = make_states(states[0], shortest_path)
pos = 0
new_path = []
tot = 0
with tqdm(total=len(paths), desc=f"Score: {tot}") as pbar:
    while pos < len(paths):
        end_pos = min(len(paths), pos + step)
        end = make_states(states[end_pos], shortest_path)
        overlap = set(start.keys()).intersection(set(end.keys()))
        # print(states[pos], states[end_pos])
        min_path = paths[pos:end_pos]
        state = states[pos]
#        print(state)
#         for e in min_path:
#             state = apply_move(e, state)
#             print(state)
#         print("----")

        if len(overlap) != 0 :
            for e in overlap :
                if len(min_path) > len(start[e]) + len(end[e]) :
                    l = start[e]
                    for v in end[e][::-1] :
                        if v[0] == '-' : v = v[1:]
                        else: v = '-' + v
                        l.append(v)
                    min_path = l 
                    # print("overlap", min_path, start[e], end[e], start[e] + end[e])
            # print(pos, min_path, len(min_path), 2*K)
        # print(min_path,len(min_path), len(paths[pos:end_pos]) - len(min_path))
        tot += len(paths[pos:end_pos]) - len(min_path)

        # print("2nd", min_path)
        # state_new = states[pos]
        # print(state_new)
        # for e in min_path:
        #     state_new = apply_move(e, state_new)
        #     print(state_new)
        # print("----")
        # print(states[end_pos])
        # print("====")
        # if state != state_new : 
        #     print("Wrong move")
        #     break
        new_path += min_path
        pbar.update(K*2)
        pbar.set_description(f"Score: {tot}")
        start = end
        pos = end_pos

# print(f"{len(paths) - len(new_path)}")
# print("-------> ", new_path)
state = initial_state
for e in new_path :
    state = apply_move(e, state)
    
# print(state)
score = len(new_path) - len(paths)
print(f"Score = {score} ({len(paths)}->{len(new_path)})")

if valid_check(state, solution_state, num_wildcards) == False :
    print(f"error in {pid}")
    exit()

if score < 0 :
    with open(f"sol_2dir_k/{pid}.txt", "w") as f :
        f.write(".".join(new_path))


    