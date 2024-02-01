#
# 総当たり。作れたやつはワイルドカードなしの最短が保証される。
# これに関してはワイルドカードの実装してもよいかも？
# 

import pandas as pd
import numpy as np
import ast
import os
import time

PUZZLE_FILE = './data/puzzles.csv'
PUZZLE_INFO_FILE = './data/puzzle_info.csv'
SAMPLE_FILE = './data/sample_submission.csv'
SAMPLE_FILE = './data/submission_1140030.csv'

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

# 次のパターンを網羅
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


def mask_state(state) :
    r = state.split(";")
    for i, e in enumerate(r):
        p = i%16
        row = p % 4
        col = p // 4
        if 1 <= row and row <= 2 and 1 <= col and col <= 2 : 
            pass
        else: r[i] = 'x' 
    state = ";".join(r)
    return state

# state = mask_state(state)

def solve(pid):
    global moves, source_paths, dest_paths
    
    ddf = data_df[data_df['id'] == pid]
    puzzle_type = ddf['puzzle_type'].iloc[0]
    solution_state = ddf['solution_state'].iloc[0]
    initial_state = ddf['initial_state'].iloc[0]

    initial_state = mask_state(initial_state)
    solution_state = mask_state(solution_state)

    num_wildcards = ddf['num_wildcards'].iloc[0]

    print(initial_state)
    print(solution_state)

    idf = info_df[info_df['puzzle_type'] == puzzle_type]
    allowed_moves = idf['allowed_moves'].iloc[0]    
    moves = ast.literal_eval(allowed_moves)

    new_moves = {}
    for e in moves:
        if e[-1] in ('0', '1') : continue
        new_moves[e] = moves[e]
    moves = new_moves 


    print(moves.keys())


    moves = init_reverse_moves(moves)

    source_paths = {
        initial_state: []
    }
    dest_paths = {
        solution_state: []
    }

    start_time = time.time()
    solution = None
    count = 0
    # 幅優先探索を手前と後ろの双方から行う
    while time.time() - START_TIME < RUN_TIME and time.time() - start_time < TIMEOUT:
        count += 1

        if count % 2:
            expand(source_paths)
        else:
            expand(dest_paths, reverse=True)

        overlap = set(source_paths.keys()).intersection(set(dest_paths.keys()))
        if (len(overlap)):
            overlap = list(overlap)[0]
            solution = '.'.join(source_paths[overlap] + list(reversed(dest_paths[overlap])))
            break
            
    return solution

moves = None
source_paths = None
dest_paths = None


grows = []
all_ids = sample_df['id'].unique()

all_ids = [199]
for pid in all_ids:
    if INCLUDES is not None and pid not in INCLUDES:
        print('=> [' + str(pid) + '] Not included!')
        continue
    if EXCLUDES is not None and pid in EXCLUDES:
        print('=> [' + str(pid) + '] Excluded!')
        continue
        
    df = data_df[data_df['id'] == pid]
    solution_state = df['solution_state'].iloc[0]
    size = len(solution_state.split(';'))

    # import pdb; pdb.set_trace()        
    # if MIN_SIZE is not None and size <= MIN_SIZE:
    #     print('=> [' + str(pid) + '] Skipped by lower size!')
    #     continue

    # if MAX_SIZE is not None and size >= MAX_SIZE :
    #     print('=> [' + str(pid) + '] Skipped by upper size! = ', size, f"   Type={df.iloc[0].puzzle_type}") 
    #     continue


    start_time = time.time()
    solution = solve(pid)
    end_time = time.time()
    if solution is None:
        print('=> [' + str(pid) + '] Failed!', f"   Type={df.iloc[0].puzzle_type} Time = {end_time-start_time}")           
    else:
        print('=> [' + str(pid) + '] Success!', f"   Type={df.iloc[0].puzzle_type} Time = {end_time-start_time}")        
        with open(f"solutions/{pid}.txt", "w") as fp:
            fp.write(solution)
        grows.append({'id': pid, 'moves': solution})



# def solve2(pid):
#     global moves, source_paths, dest_paths
    
#     ddf = data_df[data_df['id'] == pid]
#     puzzle_type = ddf['puzzle_type'].iloc[0]
#     solution_state = ddf['solution_state'].iloc[0]
#     initial_state = ddf['initial_state'].iloc[0]
#     num_wildcards = ddf['num_wildcards'].iloc[0]

#     idf = info_df[info_df['puzzle_type'] == puzzle_type]
#     allowed_moves = idf['allowed_moves'].iloc[0]    
#     moves = ast.literal_eval(allowed_moves)

#     moves = init_reverse_moves(moves)

#     path = sample_df[sample_df['id'] == pid].iloc[0].moves.split(".")

#     states = [initial_state]
#     for e in path :
#         state = apply_move(e, states[-1])
#         states.append(state)


#     for start in range(len(states)) :
#         source_paths = {
#             states[start]: []
#         }
#         dest_paths = {
#             states[start+8]: []
#             #solution_state: []
#         }

#         start_time = time.time()
#         solution = None
#         count = 0
#         # 幅優先探索を手前と後ろの双方から行う
#         while time.time() - START_TIME < RUN_TIME and time.time() - start_time < TIMEOUT:
#             count += 1

#             if count % 2:
#                 expand(source_paths)
#             else:
#                 expand(dest_paths, reverse=True)

#             overlap = set(source_paths.keys()).intersection(set(dest_paths.keys()))
#             if (len(overlap)):
#                 overlap = list(overlap)[0]
#                 solution = '.'.join(source_paths[overlap] + list(reversed(dest_paths[overlap])))
#                 break
                
#         print("sol = ", len(solution.split(".")), " : ", solution)
#     return solution

# for pid in (30, ):
#     df = data_df[data_df['id'] == pid]
#     start_time = time.time()
#     solution = solve2(pid)
#     end_time = time.time()

#     if solution is None:
#         print('=> [' + str(pid) + '] Failed!', f"   Type={df.iloc[0].puzzle_type} Time = {end_time-start_time}")           
#     else:
#         print('=> [' + str(pid) + '] Success!', f"   Type={df.iloc[0].puzzle_type} Time = {end_time-start_time}")        
#         with open(f"solutions/{pid}.txt", "w") as fp:
#             fp.write(solution)
#         grows.append({'id': pid, 'moves': solution})




"""
cube_2/2/2 6
cube_3/3/3 9
cube_4/4/4 12
cube_5/5/5 15
cube_6/6/6 18
cube_7/7/7 21
cube_8/8/8 24
cube_9/9/9 27
cube_10/10/10 30
cube_19/19/19 57
cube_33/33/33 99
wreath_6/6 2
wreath_7/7 2
wreath_12/12 2
wreath_21/21 2
wreath_33/33 2
wreath_100/100 2
globe_1/8 18
globe_1/16 34
globe_2/6 15
globe_3/4 12
globe_6/4 15
globe_6/8 23
globe_6/10 27
globe_3/33 70
globe_33/3 70
globe_8/25 59
"""

gdf = None
if len(grows) > 0:
    gdf = pd.DataFrame(grows)
    gdf.to_csv('good.csv', index=False)
print(gdf)

sub_df = None
if gdf is not None:
    bdf = gdf
    adf = sample_df
    rows = []
    for ri in range(len(adf)):
        pid = adf['id'].iloc[ri]
        moves = adf['moves'].iloc[ri]
        size = len(moves.split('.'))
        df = bdf[bdf['id'] == pid]
        if len(df) > 0:
            moves_b = df['moves'].iloc[0]
            size_b = len(moves_b.split('.'))
            if size_b < size:
                moves = moves_b
                print('=> (' + str(pid) + ') ' + str(size) + ' -> ' + str(size_b))
        rw = {'id': pid, 'moves': moves}
        rows.append(rw)
    sub_df = pd.DataFrame(rows)
    total = sub_df["moves"].map(lambda x: len(x.split("."))).sum()
    print("score = ", total)
    sub_df.to_csv(f'submission_{total}.csv', index=False)

# print(sub_df)