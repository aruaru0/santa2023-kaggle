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
    
# -------------------------------------------------------------------
class ExceedMaxSizeError(RuntimeError):
    pass

def get_shortest_path(
    moves: dict[str, tuple[int, ...]], K: int, max_size: int 
) -> dict[tuple[int, ...], list[str]]:
    n = len(next(iter(moves.values())))

    state = tuple(range(n))
    cur_states = [state]

    shortest_path: dict[tuple[int, ...], list[str]] = {}
    shortest_path[state] = []

    # 初期パターンからK回置換を繰り返して到達できるパターンを全探索する
    # もし、パターンが登録されていなければshottest_pathにパターンを登録する
    for _ in range(100 if K is None else K):
        next_states = []
        for state in cur_states:
            for move_name, perm in moves.items():
                next_state = tuple(state[i] for i in perm)
                if next_state in shortest_path:
                    continue
                shortest_path[next_state] = shortest_path[state] + [move_name]

                if max_size is not None and len(shortest_path) > max_size:
                    raise ExceedMaxSizeError

                if len(shortest_path)%1000000 == 0 : print(len(shortest_path), K)
                next_states.append(next_state)
        cur_states = next_states

    return shortest_path

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

max_size = args.limit + len(paths)

# -------------------
# グラフを作成する
# -------------------
node = [[] for _ in range(max_size)]
pat2idx = defaultdict(int)
pair = set()


cur_cnt = 0

#とりあえず、状態遷移を作成
print("Make Graph....")
state = initial_state
pat2idx[state] = 0
for e in paths:
    From = pat2idx[state]
    next = apply_move(e, state)
    if next not in pat2idx :
        pat2idx[next] = len(pat2idx)
    To = pat2idx[next]
    if (From, To) not in pair :
        node[From].append((To, e))
        pair.add((From, To))
    if (To, From) not in pair :
        if e[0] == '-' : e = e[1:]
        else : e = '-' + e
        node[To].append((From, e))
        pair.add((To, From))

    state = next

if valid_check(state, solution_state, num_wildcards) :
    print('OK')

# max_sizeになるまで繰り返す
move_list = list(moves.keys())

K = 1

# next_nodesを追加中⭐︎
next_nodes = set(pat2idx.keys())
while len(pat2idx) < max_size :
    nodes = list(next_nodes)
    next_nodes = set()
    # print(len(nodes))
    for state in nodes:
        for e in move_list:
            From = pat2idx[state]
            next = apply_move(e, state)
            if next not in pat2idx :
                pat2idx[next] = len(pat2idx)
                next_nodes.add(next) # 次の候補に追加
                if len(pat2idx)%1000000 == 0 :
                    print(f"  {len(pat2idx)} nodes... {len(pair)} edges...")   
            To = pat2idx[next]
            if (From, To) not in pair :
                node[From].append((To, e))
                pair.add((From, To))
            if (To, From) not in pair :
                if e[0] == '-' : e = e[1:]
                else : e = '-' + e
                node[To].append((From, e))
                pair.add((To, From))

            # state = next
            if len(pat2idx) >= max_size: break 
        if len(pat2idx) >= max_size: break    
    K+=1


print("K = ", K, len(pat2idx))
# print(node[:len(pat2idx)])
# print(node[:len(pat2idx)])

# スタートとゴールを設定
start = 0
end = set()
if num_wildcards != 0:
    for e in pat2idx:
        if valid_check(e, solution_state, num_wildcards) :
            end.add(pat2idx[e])
else:
    end.add(pat2idx[solution_state])

print(f"start = {start} , goal = {end}")

# -------------------
# BSF
# -------------------
print("BSF....")

inf = 10**18
dist = [inf for _ in range(max_size)]
ipath = [-1 for _ in range(max_size)]
q = deque([start])
dist[start] = 0

while len(q) != 0 :
    cur = q[0]
    q.popleft()
    for e, _ in node[cur]:
        if dist[e] > dist[cur] + 1 :
            dist[e] = dist[cur]+1
            ipath[e] = cur
            q.append(e)


#見つけた最短経路のパスを作成
def make_route(goal) :
    ret = [goal]
    pos = goal
    while ipath[pos] != -1 :
        pos = ipath[pos]
        ret.append(pos)

    p = []
    ret = ret[::-1]
    for i, e in enumerate(ret) :
        if e == goal: break
        for to, val in node[e] :
            if to == ret[i+1] :
                p.append(val)
                break
    return p , ret   


print("make Path...")
new_path = None
for e in end:
    path, rt = make_route(e)
    print("Goal = ", e, "len = ", len(path))
    if new_path is None or len(path) < len(new_path) :
        new_path = path
        route = rt

# idx2pat = {pat2idx[e]:e for e in pat2idx}

print("------")
state = initial_state
for i, e in enumerate(new_path) :
    state = apply_move(e, state)
    # print(route[i+1])
    # print("  ",state)
    # print("  ",idx2pat[route[i+1]])

if valid_check(state, solution_state, num_wildcards) == False :
    print(f"Error...{pid}")
    exit()

# print(new_path)
score = len(new_path)  - len(paths)
print(f"Score = {len(new_path)} - {len(paths)} = {score}")
    
if score < 0 :
    print("Update.")
    with open(f"sol_2dir_k/{pid}.txt", "w") as f :
        f.write(".".join(new_path))