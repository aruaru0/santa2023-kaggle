# 結果が間違っていないかチェックする
import sys
import pandas as pd
import numpy as np
import ast
import os
import time
from tqdm import tqdm

PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
SAMPLE_FILE = './data/sample_submission.csv'

if len(sys.argv) != 2 :
    print("need filename")
    exit()

print("FILE = ", sys.argv[1])

SAMPLE_FILE = sys.argv[1]

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


pid = 1

tot = 0
for pid in range(len(sample_df)) :
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
    path = pdf['moves'].iloc[0].split(".")


    # print(ddf)
    # print(idf)
    # print(path)


    state = initial_state
    tot += len(path)
    for e in tqdm(path):
        state = apply_move(e, state)
        # print(e, state)

    cnt = 0
    for x, y in zip(state.split(";"), solution_state.split(";")):
        if x != y : cnt+=1
    postfix = ""

    # print(cnt)
    # print(state)
    # print(solution_state)

    if cnt <= num_wildcards :
        print(f"No.{pid} ----- OK")
    else :
        print(f"No.{pid} ----- NG")
        postfix = "_NG"
        exit()

    with open(f"check/{pid}{postfix}.txt", "w") as f :
        f.write(pdf['moves'].iloc[0])


print(f"Score = {tot}")