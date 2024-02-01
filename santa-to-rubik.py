import sys
import pandas as pd
import numpy as np
import ast
import os
import time
from tqdm import tqdm
from collections import defaultdict
import copy

# 30-149
pid = 149
base = ['-r', '-f']
result = "F U' B D B R U D2 B L F' R' D2 B U2 L' B2 L F U2 F2 R2 D2 R' F2 D2 L2 U2 D2 F2 R2 U2 R2 B2 L2 U2 F2 B2 L2".split(" ")
rot = []
for e in base:
    for i in range(3):
        rot.append(e+str(i))



PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
SAMPLE_FILE = './data/sample_submission.csv'

# if len(sys.argv) != 2 :
#     print("need filename")
#     exit()

# print("FILE = ", sys.argv[1])
# SAMPLE_FILE = sys.argv[1]

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


# ルービックキューブ上に表示
def print_cube3x3(s, status):
    print("="*40)
    print(s)
    print("="*40)
    st = status.split(";")
    pos = 0
    p = [['   ' for _ in range(12)] for _ in range(9)]
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
print_cube3x3("target", solution_state)

# 下のパスをオートで変換するものを作れば良い
# paths = ['d1', 'f0', 'r2', 'd1']
# paths = ['-d0','-d2', '-r2', 'f2', '-d0', '-d2', 'd0', 'd1', 'd2', 'd0', 'd1', 'd2']
# state = copy.copy(solution_state)
# for path in paths:
#     state = apply_move(path, state)
#     print_cube3x3(path, state)

# paths = ['f0','f1','f2', 'f0','f1','f2']
# for path in paths:
#     state = apply_move(path, state)
#     print_cube3x3(path, state)


def init_moves() :
    ret = {}
    s = ['f', 'd', 'r']
    for e in s :
        for i in range(3):
            ret[e+str(i)] = (e+str(i), 1)
    return ret

"""
r1  : fとdが入れ替わって、d: 0,1,2 -> f: 0,1,2 f: 0,1,2 -> d:2,1,0(±の回転も反転)  
-r1 : fとdが入れ替わって、f: 0,1,2 -> d: 0,1,2 d: 0,1,2 -> f:2,1,0(±の回転も反転) 
f1  : dとrが入れ替わって、r: 0,1,2 -> d:0,1,2  d: 0,1,2 -> r:2,1,0(±の回転も反転) 
-f1 : dとrが入れ替わって、d: 0,1,2 -> r:0,1,2  r: 0,1,2 -> d:2,1,0(±の回転も反転)  
d1  : rとfが入れ替わって、f: 0,1,2 -> r:0,1,2  r: 0,1,2 -> f:2,1,0(±の回転も反転)   
-d1 : rとfが入れ替わって、r: 0,1,2 -> f:0,1,2  f: 0,1,2 -> r:2,1,0(±の回転も反転) 
"""
def change_moves(move, cur) :
    tmp = copy.deepcopy(cur)
    # print("change_moves", move, tmp)
    if move == 'r1' :
        for i in range(3) : # 0,1,2 -> 0,1,2
            x, f = cur['d'+str(i)]
            tmp['f'+str(i)] = (x, f)
        for i in range(3) : # 0,1,2 -> 2,1,0
            x, f = cur['f'+str(i)]
            tmp['d'+str(2-i)] = (x, -f)
    if move == '-r1' :
        for i in range(3) : # 0,1,2 -> 0,1,2
            x, f = cur['f'+str(i)]
            tmp['d'+str(i)] = (x, f)
        for i in range(3) : # 0,1,2 -> 2,1,0
            x, f = cur['d'+str(i)]
            tmp['f'+str(2-i)] = (x, -f)
    if move == 'f1' :
        for i in range(3) : # 0,1,2 -> 0,1,2
            x, f = cur['r'+str(i)]
            tmp['d'+str(i)] = (x, f)
        for i in range(3) : # 0,1,2 -> 2,1,0
            x, f = cur['d'+str(i)]
            tmp['r'+str(2-i)] = (x, -f)
    if move == '-f1' :
        for i in range(3) : # 0,1,2 -> 0,1,2
            x, f = cur['d'+str(i)]
            tmp['r'+str(i)] = (x, f)
        for i in range(3) : # 0,1,2 -> 2,1,0
            x, f = cur['r'+str(i)]
            tmp['d'+str(2-i)] = (x, -f)
    if move == 'd1' :
        for i in range(3) : # 0,1,2 -> 0,1,2
            x, f = cur['f'+str(i)]
            tmp['r'+str(i)] = (x, f)
        for i in range(3) : # 0,1,2 -> 2,1,0
            x, f = cur['r'+str(i)]
            tmp['f'+str(2-i)] = (x, -f)
    if move == '-d1' :
        for i in range(3) : # 0,1,2 -> 0,1,2
            x, f = cur['r'+str(i)]
            tmp['f'+str(i)] = (x, f)
        for i in range(3) : # 0,1,2 -> 2,1,0
            x, f = cur['f'+str(i)]
            tmp['r'+str(2-i)] = (x, -f)
    return tmp


"""
r1  : fとdが入れ替わって、d: 0,1,2 -> f: 0,1,2 f: 0,1,2 -> d:2,1,0(±の回転も反転)  
-r1 : fとdが入れ替わって、f: 0,1,2 -> d: 0,1,2 d: 0,1,2 -> f:2,1,0(±の回転も反転) 
f1  : dとrが入れ替わって、r: 0,1,2 -> d:0,1,2  d: 0,1,2 -> r:2,1,0(±の回転も反転) 
-f1 : dとrが入れ替わって、d: 0,1,2 -> r:0,1,2  r: 0,1,2 -> d:2,1,0(±の回転も反転)  
d1  : rとfが入れ替わって、f: 0,1,2 -> r:0,1,2  r: 0,1,2 -> f:2,1,0(±の回転も反転)   
-d1 : rとfが入れ替わって、r: 0,1,2 -> f:0,1,2  f: 0,1,2 -> r:2,1,0(±の回転も反転) 
"""
# state = solution_state
# paths = ['d1']
# cur = init_moves()
# for path in paths:
#     state = apply_move(path, state)
#     print_cube3x3(path, state)
#     cur = change_moves(path, cur)

# print(init_moves())
# print(cur)


def modify_move(move, cur_moves) :
    if move[0] == '-' :
        flag = -1
        move = move[1:]
    else:
        flag = 1

    m, f = cur_moves[move]

    if m[1] == '1' :
        m = [m[0]+'0', m[0]+'2']
        flag *= -1
    else:
        m = [m]
    ret = []
    for e in m:            
        tmp = f*flag
        if tmp == -1 :
            e = "-" + e
        ret.append(e)
    return ret



# print(modify_move('-f1', cur))

# print(paths)

print("--"*40)
paths = pdf['moves'].iloc[0].split(".")
# paths = paths[:len(paths)]
print(pdf, len(paths))

# paths = "f0.r1.-r0.-f0.f1.-r2.r0.-r1.d0.f2".split(".")
initial_state = copy.copy(solution_state)
# print_cube3x3("s", initial_state)
for e in paths[::-1]:
    if e[0] == '-' :
        e = e[1:]
    else:
        e = "-" + e
    initial_state = apply_move(e, initial_state)
    # print_cube3x3(e, initial_state)

print("INIT   : ", initial_state)
print("TARGET : ", solution_state)
print("move", paths)

cur_state = solution_state
cur_state2 = solution_state
# paths = ['f0', 'r0', 'd0', 'd1']
new_paths = []
cur_moves = init_moves()
for e in paths[::-1]:
    if e[0] == '-' :
        e = e[1:]
    else:
        e = "-" + e
    cur_state = apply_move(e, cur_state)
    path = modify_move(e, cur_moves)
    new_paths += path
    # print("path", e, "new_path", new_paths, cur_moves)
    for v in path:
        cur_state2 = apply_move(v, cur_state2)
    
    # print_cube3x3("CUR", cur_state)
    # print_cube3x3("CUR2", cur_state2)

    # print(e, cur_moves)
    cur_moves = change_moves(e, cur_moves)
    # print(e, cur_moves)
    # print(e, path)

print_cube3x3("initial", initial_state)

print_cube3x3("Result", cur_state)
cur_state = solution_state
for e in new_paths :
    cur_state = apply_move(e, cur_state)
print_cube3x3("initial", initial_state)
print_cube3x3("Result2", cur_state)


print("CHECK-MOVE")
state = initial_state
print(rot)
for e in rot:
    state = apply_move(e, state)
print_cube3x3("initial-rot", state)

print("new = ", new_paths)
print("movedict = ", cur_moves)

"""
対応
r0, r2, f0, f2, d0, d2
R, L, F, B, D, U
"""
dict = {
    'r0' : "R",
    '-r0' : "R'",
    '-r2' : "L",
    'r2' : "L'",

    'f0' : "F",
    '-f0' : "F'",
    '-f2' : "B",
    'f2' : "B'",

    'd0' : "D",
    '-d0' : "D'",
    '-d2' : "U",
    'd2' : "U'",
    #---
    'r0 r0' : "R2",
    'r2 r2' : "L2",

    'f0 f0' : "F2",
    'f2 f2' : "B2",

    'd0 d0' : "D2",
    'd2 d2' : "U2",
}


# new_paths = "f2 f0 r0 r2 d0 d0 -d2 r2".split()

Rubik = []
for e in new_paths:
    Rubik.append(dict[e])

print("CUBE", "--"*40)
print(" ".join(Rubik))
print("--"*40)
# exit(0)

# for e in new_paths:
#     solution_state = apply_move(e, solution_state)

# print_cube3x3("INIT", initial_state)
# print_cube3x3("XXX", solution_state)

# state = initial_state
# paths = ['f0','f1','f2'] * 2
# print(path)
# for e in paths:
#     state = apply_move(e, state)
# print_cube3x3("initial-rot", state)

# R U2 B2 U' R F2 D L2 F L2 F2 L' F B2 R' D2 R' U2 L U2 L U2 R F2 U2 L2 F2 L2 D2 F2 U2 
# U' R2 F B' U D2 F' U2 B2 L' D2 R2 F R' B R U2 R' F2 R U2 F2 R D2 L' U2 F2 U2 R2 U2 F2 L2 B2 R2 U2 R2 U2 B2 




rdict = {dict[e]:e for e in dict}

sol = []
for e in result:
    sol.append(rdict[e])

sol = " ".join(sol).split(" ")
print(result)
print(sol)

paths = rot+sol
print("SOLVE")
state = initial_state
print_cube3x3("START", state)
# paths = ['r0', 'r2']
for e in paths:
    state = apply_move(e, state)
    print_cube3x3(e, state)
print(state)

print("-------")
print(".".join(paths))
print("-------")

print(solution_state)
print(" ".join(Rubik))

with open(f'../../go/src/Rubik/e{pid}.txt', "w") as f :
    f.write(" ".join(Rubik))
with open(f"{pid}.txt", "w") as f :
    f.write(".".join(paths))

new_len = len(paths)
print(f"{org_len} - {new_len} = {org_len - new_len}")
# print(solution_state)
# print_cube3x3("sol", solution_state)
