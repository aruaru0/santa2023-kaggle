# 結果が間違っていないかチェックする
import sys
import pandas as pd
import numpy as np
import ast
import os
import time
from tqdm import tqdm
from collections import defaultdict

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


class Aster:
    def __init__(self, init_state, sol_state, moves, num_wild, max_depth = 21) :
        state = solution_state
        dic = defaultdict(int)
        dic[state] = 0

        self.init_state = init_state
        self.sol_state = sol_state
        self.moves = moves
        self.num_wild = num_wild
        self.max_depth = max_depth
        
        # 最終からサイズ分を作る
        print("--- a* init ---")
        MAX_SIZE = 14_000_000
        depth = 0
        prev = -1
        while len(dic) < MAX_SIZE and prev != len(dic):
            states = list(dic.keys())
            prev = len(dic)
            print(depth, len(dic))
            for state in states :
                for e in moves:
                    next_state = apply_move(e, state)
                    if next_state not in dic :
                        dic[next_state] = dic[state]+1
                        depth = max(depth, dic[state]+1)
                if len(dic) > MAX_SIZE : 
                    print("BREAK", len(dic))
                    break

        # print(dic)
        print(f"depth = {depth}, size = {len(dic)}")
        self.dic = dic
        self.time = time.time()
        self.printed = False
        self.cnt = 0

    def search(self, state, depth, paths = [], moves = []) :
        global best 

        if time.time() - self.time > 60 and self.printed == False :
            print(self.cnt)
            self.time = time.time()
            self.cnt+=1
            self.printed = True
        elif time.time() != self.time :
            self.printed = False 

        if state == self.sol_state :
            print("find:", moves)
            if best == None or len(moves) < len(best) :
                best = moves
            return True
        if depth > self.max_depth :
            return False
        
        # print(depth, state, paths, moves)
        
        done = set(paths)
        next = []
        for e in self.moves :
            next_state = apply_move(e, state)
            if next_state in done : continue
            g = depth+1
            l = self.max_depth
            if next_state in self.dic : 
                l = self.dic[next_state]
            next.append((g+l, next_state, e))

        next.sort()
        for e in next:
            ret = self.search(e[1], depth+1, paths + [e[1]], moves + [e[2]] )
            if ret == True : return True

        return False
            





for pid in range(len(sample_df)) :
    pid = 30
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
    best = None
    aster = Aster(initial_state, solution_state, moves, num_wildcards)
    aster.search(initial_state, 0)
    print(len(best), best)
    break
    # for i, e in tqdm(enumerate(path)):
    #     state = apply_move(e, state)
    #     # print(i, e, state)
    #     if e not in dic :
    #         dic[state] = i

    # if state == solution_state :
    #     print(f"No.{pid} ----- OK")
    # else :
    #     print(f"No.{pid} ----- NG")
    #     exit()

    # # break

