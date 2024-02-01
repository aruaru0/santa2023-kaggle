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
import random

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


dict2 = {
    "f0" : "F",
    "f1" : "Fw F'",
    "f2" : "Bw' B",
    "f3" : "B'",

    "-f0" : "F'",
    "-f1" : "Fw' F",
    "-f2" : "Bw B'",
    "-f3" : "B",

    "r0" : "R",
    "r1" : "Rw R'",
    "r2" : "Lw' L",
    "r3" : "L'",

    "-r0" : "R'",
    "-r1" : "Rw' R",
    "-r2" : "Lw L'",
    "-r3" : "L",

    "d0" : "D",
    "d1" : "Dw D'",
    "d2" : "Uw' U",
    "d3" : "U'",

    "-d0" : "D'",
    "-d1" : "Dw' D",
    "-d2" : "Uw U'",
    "-d3" : "U",
}

# dict2 = {
#     "f0" : "F",
#     "f1" : "2F",
#     "f2" : "2B'",
#     "f3" : "B'",

#     "-f0" : "F'",
#     "-f1" : "2F'",
#     "-f2" : "2B",
#     "-f3" : "B",

#     "r0" : "R",
#     "r1" : "2R",
#     "r2" : "2L'",
#     "r3" : "L'",

#     "-r0" : "R'",
#     "-r1" : "2R'",
#     "-r2" : "2L",
#     "-r3" : "L",

#     "d0" : "D",
#     "d1" : "2D",
#     "d2" : "2U'",
#     "d3" : "U'",

#     "-d0" : "D'",
#     "-d1" : "2D'",
#     "-d2" : "2U",
#     "-d3" : "U",

#     "f0 f0" : "F2",
#     "f1 f1" : "2F2",
#     "f2 f2"  : "2B2",
#     "f3 f3" : "B2",


#     "r0 r0" : "R2",
#     "r1 r1" : "2R2",
#     "r2 r2" : "2L2",
#     "r3 r3" : "L2",


#     "d0 d0" : "D2",
#     "d1 d1" : "2D2",
#     "d2 d2" : "2U2",
#     "d3 d3" : "U2",
# }


# rdict = {dict2[x]:x for x in dict2}


# -------------------------------------------------------------------
#  200-204
# -------------------------------------------------------------------

PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
SAMPLE_FILE = './data/sample_submission.csv'

data_df = pd.read_csv(PUZZLE_FILE)
info_df = pd.read_csv(PUZZLE_INFO_FILE)
sample_df = pd.read_csv(SAMPLE_FILE)  



for pid in range(207, 208):
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
    print("wild   : ", num_wildcards)
    #print(moves, path)
    print_cube4x4("target", solution_state)

    idx, conv_dic, rconv_dic = init_dic(solution_state)

    print(idx)
    print(conv_dic)
    print(rconv_dic)


    ##----TEST----
    state = ";".join([str(i) for i in range(4*4*6)])


    # print(state)
    # for e in paths[::-1] :
    #     if e[0] == '-' :
    #         e = e[1:]
    #     else:
    #         e = "-" + e
    #     state = apply_move(e, state)

    sol_center = []
    for i,(e, v)  in enumerate(zip(state.split(";"), initial_state.split(";"))) :
        # if i+1  in (6, 7, 10, 11, 86, 87, 90, 91) :
        # if i+1  in (6, 7, 10, 11, 22, 23, 26, 27,  54, 55, 58, 59,  86, 87, 90, 91) :
        # if i+1  in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91) :
        # if i+1  in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91, 2, 3):
        # if i+1  in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91, 2, 3, 14, 15):
        # if i+1  in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91, 2, 3, 14, 15, 5, 9):
        if i+1  in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91, 2, 3, 14, 15, 5, 9, 30, 31):
        # if i+1  in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91, 2, 3, 14, 15, 5, 9, 30, 31, 94, 95):
        # if i+1  in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91, 2, 3, 14, 15, 5, 9, 30, 31, 94, 95, 85, 89):
#

            # , 5, 8, 9, 12, 14, 15) :
            sol_center.append(e)
        else :
            sol_center.append('x')


    sol_center = ";".join(sol_center)

    state = sol_center
    for e in paths[::-1] :
        if e[0] == '-' :
            e = e[1:]
        else:
            e = "-" + e
        state = apply_move(e, state)

    print(f'"{state}",')
    print(f'"{sol_center}",')

    add_path = []

    add_path = "f3.d1.-f0.d1.f2.-r3.d1.f3.-f2.r2".split(".") #
    add_path += "d1.-f0.-f0.d2.d2.f0.d1.-f0.d2.f0.d2.f0.-d1.-d1.d2.-f0.d2".split(".")
    add_path += "d2.d1.f0.f0.-d1.-d1.-f0.-d1.-d1.f0.-d2.-d2.f0.-d2.-d2.-f0.-d2.-d2.f0.-d1.d2".split(".")
    add_path += "r1.d3.f3.r3.-f3.-r3.-d3.-r1".split(".")
    add_path += "r1.d3.f0.-d3.-f0.-r1".split(".")
    add_path += "-f1.r3.f0.-r3.f1.-r3.-f0.r3".split(".")
    # add_path += "-r1.-r2.f3.-r3.-f3.r2.d0.r3.-d0.r1".split(".")
    # add_path += "r3.-d0.d1.-r0.d0.r0.-d1.-r3".split(".")
    # add_path += "-d2.-f0.d0.f0.d2.f0.-d0.-f0".split(".")

    # add_path += paths[:7] #".split(".")

    # state = initaial_
    for e in add_path:
        state = apply_move(e, state)

    print(f'"{state}",')
    print(f'"{sol_center}",')


    print_cube4x4("state", state)
    # print(state)

    # exit()
    ##----TEST END----

    # paths = ['d0', 'd1', 'd2', 'd3']

    rpath = []
    state = "A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F"
    # state = "A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F"	
    idx2, conv_dic2, rconv_dic2 = init_dic(state)
    for e in paths[::-1] :
        if e[0] == '-' :
            e = e[1:]
        else:
            e = "-" + e
        rpath.append(e)
        state = apply_move(e, state)
    print(rpath)
    print_cube4x4("state", state)
    # initial_state = state

    scramble = ""
    for e in rpath:
        scramble += dict2[e] + " "

    scramble = " ".join(scramble.split())
    print("Scramble = ")
    print(scramble)
    # with open("tmp.txt", "w") as f :
    #     f.write(scramble)
    # break
    print("======")
    
    for e in add_path:
        state = apply_move(e, state)

    print_cube4x4("ADDPATH", state)

    # c_state = convert_to(tmp_state, idx, conv_dic)
    # print_cube4x4("INITIAL", initial_state)
    # print(c_state)
  


    c_state = convert_to(state, idx2, conv_dic2)
    print(c_state)  

    # com = subprocess.run(["java", "-cp", ".:threephase.jar:twophase.jar", "solver2", scramble], capture_output=True,  text=True).stdout.split("\n")
    com = subprocess.run(["java", "-cp", ".:threephase.jar:twophase.jar", "solver", c_state], capture_output=True,  text=True).stdout.split("\n")

    pos = 0
    while "OK" not in com[pos] : pos+=1
    pos+=1


    print(com[pos])
    result = com[pos].split()
    # result = "D Rw' D Bw R Uw' L2 B' Bw2 Rw' Dw2 B D F' Rw' U Rw2 U2 F' U' Lw2 F R2 D F2 Lw2 Bw2 U2 L2 D Fw2 F' L' F' D' R' D2 L2 B2 L' U' F' L2 U' R2 F2 U' B2 D2 F2 D2 R2".split()
    print(result)
    print("len = ", len(result))


    new_path = []
    for e in result:
        x = rdict[e].split()
        new_path += rdict[e].split()
    print(new_path)
    print("len=",len(new_path))
    new_path = add_path + new_path
    # # -x-x--x-xx-x-x-
    # s = state.split(";")
    # for i, v in enumerate(s) :
    #     if i+1 not in (6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43, 54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91) :
    #         s[i] = ' x '
    #     else :
    #         s[i] = (" 0" + str(i+1))[-2:]
    # state = ";".join(s)
    # for e in paths[::-1] :
    #     if e[0] == '-' :
    #         e = e[1:]
    #     else:
    #         e = "-" + e
    #     state = apply_move(e, state)
    # print_cube4x4("state", state)
    print(moves.keys())

    # pid:203 solution
    # new_path += ['-d3', '-r1', '-r2', 'd1', 'd2', 'r1', 'r2', 'd3', '-r1', '-r2', '-d1', '-d2', 'r1', 'r2',
    #              'r0', 'f0', '-r0', 'f0','r0', 'f0', '-r0', 'f0','r0', 'f0', '-r0', 'f0','r0', 'f0', '-r0', 'f0','r0', 'f0', '-r0', 'f0',
    #     ]

    # new_path += "-d3 r1 r2 d1 d2 -r1 -r2 d3 r1 r2 -d1 -d2 -r1 -r2".split()  # upper

    # new_path += "-f3 r1 r2 f1 f2 -r1 -r2 f3 r1 r2 -f1 -f2 -r1 -r2".split()  # back
    # new_path += "-f0 r1 r2 f1 f2 -r1 -r2 f0 r1 r2 -f1 -f2 -r1 -r2".split() # front
    # # new_path += "r3 d1 d2 r1 r2 -d1 -d2 -r3 d1 d2 -r1 -r2 -d1 -d2".split() # bottom
    # new_path += "r0 f1 f2 r1 r2 -f1 -f2 -r0 f1 f2 -r1 -r2 -f1 -f2".split() # right
    # new_path += "r0 f1 f2 r1 r2 -f1 -f2 -r0 f1 f2 -r1 -r2 -f1 -f2".split() # right
    # new_path += "-f3 -r1 -r2 f1 f2 r1 r2 f3 -r1 -r2 -f1 -f2 r1 r2".split()
    # new_path += "d0 -r1 -r2 -d1 -d2 r1 r2 -d0 -r1 -r2 d1 d2 r1 r2".split()
    # # new_path += "d0 r3 -d0 r3 d0 r3 -d0 r3 d0 r3 -d0 r3 d0 r3 -d0 r3 d0 r3 -d0 r3".split()  # left180
    # new_path += "d0 r0 -d0 r0 d0 r0 -d0 r0 d0 r0 -d0 r0 d0 r0 -d0 r0 d0 r0 -d0 r0".split()  # right180
    # new_path += "d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3".split()  # right180

    # new_path += "d3 r1 r2 d1 d2 -r1 -r2 -d3 r1 r2 -d1 -d2 -r1 -r2".split() # front
    # # new_path += "d0 f1 f2 d1 d2 -f1 -f2 -d0 f1 f2 -d1 -d2 -f1 -f2".split()
    # # new_path += "d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3".split()
    # new_path += "-d3 r1 r2 d1 d2 -r1 -r2 d3 r1 r2 -d1 -d2 -r1 -r2".split()  # upper
    # new_path += "d0 -r1 -r2 -d1 -d2 r1 r2 -d0 -r1 -r2 d1 d2 r1 r2".split()
    # new_path += "r0 d1 d2 -r1 -r2 -d1 -d2 -r0 d1 d2 r1 r2 -d1 -d2".split()
    # new_path += "r3 -d3 -r3 -d3 r3 -d3 -r3 -d3 r3 -d3 -r3 -d3 r3 -d3 -r3 -d3 r3 -d3 -r3 -d3".split()  # upper180
    # new_path += "-f3 -d1 -d2 f1 f2 d1 d2 f3 -d1 -d2 -f1 -f2 d1 d2".split()

    # new_path += "-r3 -f1 -f2 -r1 -r2 f1 f2 r3 -f1 -f2 r1 r2 f1 f2".split()
    # new_path += "d0 f1 f2 -d1 -d2 -f1 -f2 -d0 f1 f2 d1 d2 -f1 -f2".split()
    # new_path += "r0 -f1 -f2 -r1 -r2 f1 f2 -r0 -f1 -f2 r1 r2 f1 f2".split()

    # new_path += "r3 -d3 -r3 -d3 r3 -d3 -r3 -d3 r3 -d3 -r3 -d3 r3 -d3 -r3 -d3 r3 -d3 -r3 -d3".split()  # upper180
    # new_path += "d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3 d0 f3 -d0 f3".split()  # back180
    # new_path += "d0 r3 -d0 r3 d0 r3 -d0 r3 d0 r3 -d0 r3 d0 r3 -d0 r3 d0 r3 -d0 r3".split()  # left180
    new_path += "d0 r0 -d0 r0 d0 r0 -d0 r0 d0 r0 -d0 r0 d0 r0 -d0 r0 d0 r0 -d0 r0".split()  # right180
    # new_path += "d0 f0 -d0 f0 d0 f0 -d0 f0 d0 f0 -d0 f0 d0 f0 -d0 f0 d0 f0 -d0 f0".split() # front180
    # new_path += "r3 d0 -r3 d0 r3 d0 -r3 d0 r3 d0 -r3 d0 r3 d0 -r3 d0 r3 d0 -r3 d0".split() # bottom180
    # new_path += "r3 -f1 -f2 -r1 -r2 f1 f2 -r3 -f1 -f2 r1 r2 f1 f2".split()
    # new_path += "-f3 d1 d2 f1 f2 -d1 -d2 f3 d1 d2 -f1 -f2 -d1 -d2".split()
    new_path += "d0 f1 f2 -d1 -d2 -f1 -f2 -d0 f1 f2 d1 d2 -f1 -f2".split()
    new_path += "d0 -r1 -r2 -d1 -d2 r1 r2 -d0 -r1 -r2 d1 d2 r1 r2".split()


    """
                N0  N1  N2  N3                                  
                N4  N5  N6  N7                                  
                N8  N9  N10 N11                                 
                N12 N13 N14 N15                                 
N64 N65 N66 N67 N16 N17 N18 N19 N32 N33 N34 N35 N48 N49 N50 N51 
N68 N70 N74 N71 N20 N22 N26 N23 N36 N37 N38 N39 N52 N54 N58 N55 
N72 N69 N73 N75 N24 N21 N25 N27 N40 N41 N42 N43 N56 N53 N57 N59 
N76 N77 N78 N79 N28 N29 N30 N31 N44 N45 N46 N47 N60 N61 N62 N63 
                N80 N81 N82 N83                                 
                N84 N89 N85 N87                                 
                N88 N90 N86 N91                                 
                N92 N93 N94 N95
"""

    state = initial_state

    # state = "A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;A;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;B;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;D;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;E;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F;F"
    # new_path = ['d3']

    for i, e in enumerate(new_path):
        state = apply_move(e, state)
        # print_cube4x4(f"{e}:{i}", state)

    print(state)
    print(solution_state)
    print("num_wildcards", num_wildcards)
    print_cube4x4("RESULT", state)
    if valid_check(state, solution_state, num_wildcards) == False :
        print("error", pid)
    else :
        print(new_path)
        print(f"pid={pid}:{org_len}-{len(new_path)}={org_len - len(new_path)}")
        with open(f"./sol_rubik2/{pid}.txt", "w") as f :
            f.write(".".join(new_path))


"""
========================================
-d3:54
========================================
                 x   x   x   x                                  
                 x  06  07   x                                  
                 x  11  10   x                                  
                 x   x   x   x                                  
 x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x  
 x  42  38   x   x  55  58   x   x  75  74   x   x  27  23   x  
 x  39  43   x   x  59  54   x   x  70  71   x   x  26  22   x  
 x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x  
                 x   x   x   x                                  
                 x  86  90   x                                  
                 x  91  87   x                                  
                 x   x   x   x       

                 
        A B A B                 
        A A B B                 
        A B A B                 
        A B A B                 
E F E F B C B C C D C D D E D E 
E E F F B B B C C D D D D E D E 
E F E F B C C C C C C D D E D E 
E F E F B C B C C D C D D E D E 
        F A F A                 
        F F A A                 
        F F A A                 
        F A F A   
"""

