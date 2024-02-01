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

# -------------------------------------------------------------------
# use https://github.com/cs0x7f/TPR-4x4x4-Solver/tree/master
#
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


# ルービックキューブ上に表示
def print_cube4x4(s, status):
    print("="*40)
    print(s)
    print("="*40)
    st = status.split(";")
    pos = 0
    blank = ' ' if len(st[3]) == 1 else '   '
    p = [[blank for _ in range(16)] for _ in range(12)]
    start = [(0,4), (4,4), (4,8), (4, 12), (4, 0), (8, 4)]
    for i in range(6) :
        sy, sx = start[i]
        for j in range(16) :
            val = st[i*16+j]
            dx = j%4
            dy = j//4
            px = sx + dx
            py = sy + dy
            if len(val) == 2 : val += ' '
            p[py][px] = val
    for i in range(12) :
        for j in range(16) :
            print(p[i][j], end=' ')
        print()




def init_dic(state) :
    to_labels = ['U']*16 + ['R']*16 + ['F']*16 + ['D']*16 + ['L']*16 + ['B']*16
    from_labels = ['A']*16 + ['C']*16 + ['B']*16 + ['F']*16 + ['E']*16 + ['D']*16
    idx = [(y, i) for i, (x, y) in enumerate(zip(to_labels, from_labels))]

    idx.sort()
    idx = [i for _, i in idx]
    from_labels2 = ['N'+str(i) for i in range(96)]
    from_labels2 = [from_labels2[i] for i in idx]

    if "A" not in state :
        from_labels = from_labels2

    conv_dic = {f:t for f, t in zip(from_labels, to_labels)}
    rconv_dic = {t:f for f, t in zip(from_labels, to_labels)}

    return idx, conv_dic, rconv_dic

def convert_to(state, idx, dic) :
    ret = ['' for _ in range(4*4*6)]
    for i, e in enumerate(state.split(';')) :
        ret[idx[i]] = dic[e]
    return "".join(ret) 


def valid_check(state, target, num_wild) :
    cnt = 0
    for x, y in zip(state.split(";"), target.split(";")):
        if x != y : cnt+=1
    if cnt <= num_wild:
        return True
    return False



dict = {
        'r0' : "R",
        '-r0' : "R'",
        'r0 r1' : "Rw",
        '-r0 -r1' : "Rw'",
        '-r2 -r3' : "Lw",
        'r2 r3' : "Lw'",
        '-r3' : "L",
        'r3' : "L'",

        'f0' : "F",
        '-f0' : "F'",
        'f0 f1' : "Fw",
        '-f0 -f1' : "Fw'",
        '-f2 -f3' : "Bw",
        'f2 f3' : "Bw'",
        '-f3' : "B",
        'f3' : "B'",

        'd0' : "D",
        '-d0' : "D'",
        'd0 d1' : "Dw",
        '-d0 -d1' : "Dw'",
        '-d2 -d3' : "Uw",
        'd2 d3' : "Uw'",
        '-d3' : "U",
        'd3' : "U'",
        #---
        'r0 r0' : "R2",
        'r0 r0 r1 r1' : "Rw2",
        '-r2 -r2 -r3 -r3' : "Lw2",
        '-r3 -r3' : "L2",

        'f0 f0' : "F2",
        'f0 f0 f1 f1' : "Fw2",
        '-f2 -f2 -f3 -f3' : "Bw2",
        '-f3 -f3' : "B2",

        'd0 d0' : "D2",
        'd0 d0 d1 d1' : "Dw2",
        '-d2 -d2 -d3 -d3' : "Uw2",    
        '-d3 -d3' : "U2",    

        #---
        '-f0 -f1 -f2 -f3' : "z'",
        'f0 f1 f2 f3' : "z",

        '-d0 -d1 -d2 -d3' : "y",
        'd0 d1 d2 d3' : "y'",

        'r0 r1 r2 r3' : "x" ,
        '-r0 -r1 -r2 -r3' : "x'", 
        #---
        'f0 f1 f2 f3 f0 f1 f2 f3' : "z2",

        'd0 d1 d2 d3 d0 d1 d2 d3' : "y2",

        'r0 r1 r2 r3 r0 r1 r2 r3' : "x2" ,
}


rdict = {dict[x]:x for x in dict}

# -------------------------------------------------------------------
#  150-209
# -------------------------------------------------------------------

PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
SAMPLE_FILE = './data/sample_submission.csv'

data_df = pd.read_csv(PUZZLE_FILE)
info_df = pd.read_csv(PUZZLE_INFO_FILE)
sample_df = pd.read_csv(SAMPLE_FILE)  



for pid in range(200, 201):
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
    org_len = len(paths)

    print("INIT   : ", initial_state)
    print("TARGET : ", solution_state)
    #print(moves, path)
    print_cube4x4("target", solution_state)

    idx, conv_dic, rconv_dic = init_dic(solution_state)

    print(idx)
    print(conv_dic)
    print(rconv_dic)

    if pid >= 200 and pid < 205:
        tmp_state = "A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F"
        idx, conv_dic, rconv_dic = init_dic(tmp_state)
        state = tmp_state
        for e in paths[::-1]:
            if e[0] == '-' :
                e = e[1:]
            else:
                e = "-" + e
            state = apply_move(e, state)
        print_cube4x4(e, state)
        print(state)

        # initial_state = solution_state
        c_state = convert_to(state, idx, conv_dic)
    else :
        c_state = convert_to(initial_state, idx, conv_dic)
    print_cube4x4("INITIAL", initial_state)
    print(c_state)


    com = subprocess.run(["java", "-cp", ".:threephase.jar:twophase.jar", "solver", c_state], capture_output=True,  text=True).stdout.split("\n")
    pos = 0
    while "OK" not in com[pos] : pos+=1
    pos+=1


    print(com[pos])
    result = com[pos].split()
    print(result)


    new_path = []
    for e in result:
        x = rdict[e].split()
        # print(x)
        new_path += rdict[e].split()

    print(new_path)

    state = initial_state
    for e in new_path:
        state = apply_move(e, state)
        # print_cube4x4(e, state)

    print_cube4x4("RESULT", state)

    
    if valid_check(state, solution_state, num_wildcards) == False :
        print("result", state)
        print("target", solution_state)
        print("error", pid)
    else :
        print(new_path)
        print(f"pid={pid}:{org_len}-{len(new_path)}={org_len - len(new_path)}")

        with open(f"./sol_rubik2/{pid}.txt", "w") as f :
            f.write(".".join(new_path))
