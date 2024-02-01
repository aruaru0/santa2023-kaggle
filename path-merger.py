import pandas as pd
import argparse
import ast
from collections import deque
from tqdm import tqdm
import os

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


#見つけた最短経路のパスを作成
def make_route(goal, ipath, node) :
    ret = [goal]
    pos = goal
    while ipath[pos] != -1 :
        pos = ipath[pos]
        ret.append(pos)
    # print(ret)

    p = []
    ret = ret[::-1]
    for i, e in enumerate(ret) :
        if e == goal: break
        f = ret[i]
        t = ret[i+1]
        p.append(node[f][t])
    return p , ret   
    
# -------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--problem_id", type=int, required=True)
parser.add_argument("--limit", type=int,  default=100000)
parser.add_argument('files', nargs='+')   
args = parser.parse_args()

pid = args.problem_id
limit = args.limit

PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
data_df = pd.read_csv(PUZZLE_FILE)
info_df = pd.read_csv(PUZZLE_INFO_FILE)
ddf = data_df[data_df['id'] == pid]
puzzle_type = ddf['puzzle_type'].iloc[0]
solution_state = ddf['solution_state'].iloc[0]
initial_state = ddf['initial_state'].iloc[0]
num_wildcards = ddf['num_wildcards'].iloc[0]


print("[info]")
print(f"pid: {pid}")
print(f"type: {puzzle_type}, num_wildcards: {num_wildcards}")

idf = info_df[info_df['puzzle_type'] == puzzle_type]
allowed_moves = idf['allowed_moves'].iloc[0]    
moves = ast.literal_eval(allowed_moves)
moves = init_reverse_moves(moves)


node_cnt = 0
node = [{} for _ in range(limit+1)]
nodedict = dict()

# 処理したファイルがあればをちらも参照
min_path = ""
min_size = 10**18
file = f"./result_merge/{pid}.txt"
if os.path.isfile(file) :
    with open(file, "r") as f:
        s = f.read()
    s = s.split(".")
    min_path = s
    min_size = len(s)


print("[READ] path file...")
nodedict[initial_state] = 0

for f in tqdm(args.files) :
    df = pd.read_csv(f) 
    pdf = df[df['id']==pid]
    paths = pdf['moves'].iloc[0].split(".")
    if len(paths) < min_size :
        min_size = len(paths)
        min_path = paths

    prev = initial_state
    state = initial_state
    for path in paths : 
        state = apply_move(path, state)
        # print(state)
        if state not in nodedict :
           nodedict[state] = len(nodedict)
        if prev != "" : # １つ前がある場合はつなぐ
            f = nodedict[prev]
            t = nodedict[state]
            # print(f"{prev}, from = {f}, to={t}")
            node[f][t] = path
            if path[0] == '-' : path = path[1:]
            else: path = '-' + path
            node[t][f] = path                
        prev = state
        if len(nodedict) >= limit:
            print("error: limit is not enough")
            exit()



# append nodes
print("[Add] Extra nodes...", limit)
with tqdm(total=limit-len(nodedict)) as pbar :
    prevlen = -1
    nodes = list(nodedict)
    while len(nodedict) < limit :
        if len(nodedict) == prevlen : break
        prevlen = len(nodedict)
        next_nodes = []
        for e in nodes :
            prev = e
            for e in moves:
                if len(nodedict) >= limit : break
                state = apply_move(e, prev)
                if state not in nodedict : 
                    nodedict[state] = len(nodedict)
                    next_nodes.append(state)
                    pbar.update(1)
                f = nodedict[prev]
                t = nodedict[state]
                # print(f"{prev}, from = {f}, to={t}")
                node[f][t] = e
                if e[0] == '-' : e = e[1:]
                else: e = '-' + e
                node[t][f] = e                
            if len(nodedict) >= limit : break
        nodes = next_nodes

print(f"num of nodes = {len(nodedict)}")


# set start and end
print("Check GOAL")
start = nodedict[initial_state]
if num_wildcards != 0 :
    end = []
    for e in nodedict:
        if valid_check(e, solution_state, num_wildcards) :
            end.append(nodedict[e])
else:
    end = [nodedict[solution_state]]




#-----------------------------------------------
# BSF
n = len(nodedict)
inf = 10**9
dist = [inf for _ in range(n)]
route = [-1 for _ in range(n)]

q = deque([start])
dist[start] = 0

# for i, e in enumerate(node[:len(nodedict)]):
#     print(i, e)
while len(q) != 0 :
    cur = q.popleft()
    for e in  node[cur]:
        if dist[e] > dist[cur] + 1 :
            dist[e] = dist[cur] + 1
            route[e] = cur
            q.append(e)


sel = end[0]
distL = inf
for e in end:
    if dist[e] < distL :
        distL = dist[e]
        sel = e


new_path = min_path
path, _ = make_route(sel, route, node)
if len(new_path) > len(path) :
    new_path = path

# print(new_path)

print("[Check] check new path")
state = initial_state
for e in new_path :
    state = apply_move(e, state)


print("[valid check]")
if valid_check(state, solution_state, num_wildcards) == False :
    print(f"Error...{pid}")
    exit()

score = len(new_path)  - min_size
print(f"Score = {len(new_path)} - {len(min_path)} = {score}")


file = f"result_merge/{pid}.txt"
print("write path --> ", file)
with open(file, "w") as f :
    f.write(".".join(new_path))
    