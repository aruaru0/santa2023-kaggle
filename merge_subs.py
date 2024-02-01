# ソリューションをマージしてワイルドカードを簡易的に考慮する
import pandas as pd
from sympy.combinatorics import Permutation
from multiprocess import Pool, cpu_count
from tqdm import tqdm
import sys 

p = './data/'
path = pd.read_csv(p+'puzzles.csv')
info = pd.read_csv(p+'puzzle_info.csv')
# sub = pd.read_csv(p+'sample_submission.csv')

if len(sys.argv) != 3 :
    print("need submission_xxx.csv x 2")
    exit()


# #https://www.kaggle.com/code/whats2000/a-star-algorithm-polytope-permutation
sub1 = pd.read_csv(sys.argv[1])
sub1.rename(columns={'moves':'Org'},inplace=True)
# #https://www.kaggle.com/code/crodoc/1-187-898-greedy-baseline-improvement
# sub2 = pd.read_csv('../data/submission-Kociemba-1107939.csv')
sub2 = pd.read_csv(sys.argv[2])
sub2.rename(columns={'moves':'SO23'},inplace=True)
sub = pd.merge(sub1, sub2, how='left', on='id')



sub['moves'] = sub.apply(lambda r: r['Org'] if len(r['Org'].split('.')) < len(r['SO23'].split('.')) else r['SO23'], axis=1)
sub = sub[['id','moves']]


info['allowed_moves_count'] = info['allowed_moves'].map(lambda x: {k: Permutation(v) for k, v in eval(x).items()})
paths = pd.merge(path, info, how='left', on='puzzle_type')
paths = pd.merge(paths, sub, how='left', on='id')
paths['solution_state'] = paths['solution_state'].map(lambda x: x.split(';'))
paths['initial_state'] = paths['initial_state'].map(lambda x: x.split(';'))
paths['moves'] = paths['moves'].map(lambda x: x.split('.'))
paths['allowed_moves'] = paths['allowed_moves'].map(lambda x: eval(x))
print(paths.head(1))


#Evaluation metric for Santa 2023 - https://www.kaggle.com/code/metric/santa-2023-metric
# modified - using combined paths & info dataframe

def getMoves(puzzle_id, moves, allowed_moves, state, solution_state, num_wildcards):
    #for m in moves:
        #power = 1
        #if m[0] == "-":
            #m = m[1:]
            #power = -1
        #p = allowed_moves[m]
        #state = (p ** power)(state)
    #num_wrong_facelets = sum(not(s == t) for s, t in zip(solution_state, state))
    #if num_wrong_facelets > num_wildcards:
        #print(f"Submitted moves do not solve {puzzle_id}.")
    return len(moves)

def score(sol):
    p = Pool(cpu_count()-1)
    ret = p.starmap(getMoves, sol[['id','moves','allowed_moves_count','initial_state','solution_state','num_wildcards']].values)
    p.close(); p.join()
    return sum(ret)

print("score = ", score(paths))

# subに長さを追加
sub['lengths'] = sub['moves'].map(lambda x: len(x.split('.')))
bench = {i:l for i,l in sub[['id','lengths']].values}

#----

tot = score(paths)
sub[['id','moves']].to_csv(f'submission_{tot}.csv', index=False)
print(tot)

