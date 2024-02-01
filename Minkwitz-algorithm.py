from tqdm import tqdm
import pandas as pd
import numpy as np
import networkx as nx
from itertools import chain, product, combinations
from sympy.combinatorics.perm_groups import Permutation,PermutationGroup
from sympy.combinatorics.perm_groups import _distribute_gens_by_base,_orbits_transversals_from_bsgs
import sys

sys.setrecursionlimit(10**6)


p = './data/'
path = pd.read_csv(p + 'puzzles.csv')
info = pd.read_csv(p + 'puzzle_info.csv')
# sub = pd.read_csv(p + 'sample_submission.csv')
sub = pd.read_csv('submission_649754.csv')


path = pd.merge(path,info)

# A class for maintainig permutations and factorization over a SGS
class PermWord:
    def __init__(self, perms=[], words=[]):
        self.words = words
        self.permutation = perms
        self.flag = True

    @staticmethod
    def is_identity(self):
        return (self.words.len()==0)

    def inverse(self):
        inv_perm = ~self.permutation
        inv_word = invwords(self.words)
        return PermWord(inv_perm,inv_word)

    def __mul__(self, other):
        result_perm = self.permutation * other.permutation
        result_words = simplify(self.words + other.words)
        return PermWord(result_perm, result_words)

# A class generating factorization of permutations over a Strong Generating Set (SGS)
# The SGS is obtained using the sympy implementation for Schreier–Sims algorith
# The Minkwith algorithm (https://www.sciencedirect.com/science/article/pii/S0747717198902024)
# is used for mantainig a short word representation 

deterministic = False

class SGSPermutationGroup:
    def __init__(self, gensi=[]):
        gens = gensi.copy()
        gen0= [gensi[p] for p in gens]
        
        geninvs={}
        sizes = []
        for s in list(gens):
            sizes.append(gens[s].size)
            if s[0] != '-': 
                s1 = ~gens[s]
                gens["-" + s] = s1
                geninvs[s] = '-' + s
                geninvs['-' + s] = s    
        self.gens = gens
        self.geninvs = geninvs
        self.N = max(sizes)
        # Create the permutation group
        #gen0= [gens[p] for p in gens]
        G = PermutationGroup(gen0)
        self.G = G
        # obtain the strong generating set
        if deterministic:
            G.schreier_sims()
            self.base = G.base
            self.bo = G.basic_orbits
            self.bt = G.basic_transversals
            print(len(self.base))
        else:
            base,trans, orbits = schreier_sims_random(G)
            self.base = base
            self.bo = orbits
            self.bt = trans
        
     
        self.lo = [len(x) for x in self.bo]
        self.so = np.sum(self.lo)
        self.nu = None

    
    #   n: max number of rounds
    #   s: reset each s rounds
    #   w: limit for word size
    
    def getShortWords(self,n=10000,s=2000,w=20):
        self.nu = buildShortWordsSGS(self.N, self.gens, self.base, n, s, w, self.so)


    def FactorPermutation(self,target):
        if self.nu == None:
            print('Execute getShortWords')
            return None
        return  factorizeM(self.N, self.gens, self.base, self.nu, target)

    def CheckQuality(self):
        test = test_SGS(self.N,self.nu,self.base)
        qual = quality(self.N, self.nu, self.base)
        return test,qual

    def swapBase(self,i):
        S = self.G
        base, gens = S.baseswap(S.base, S.strong_gens, i, randomized=False)
        self.base = base

        
        
def schreier_sims_random(G):
    base, strong_gens = G.schreier_sims_random(consec_succ=5)
    strong_gens_distr =_distribute_gens_by_base(base, strong_gens)
    basic_orbits, transversals, slps = _orbits_transversals_from_bsgs(base,\
                strong_gens_distr, slp=True)

    # rewrite the indices stored in slps in terms of strong_gens
    for i, slp in enumerate(slps):
        gens = strong_gens_distr[i]
        for k in slp:
            slp[k] = [strong_gens.index(gens[s]) for s in slp[k]]

    transversals = transversals
    basic_orbits = [sorted(x) for x in basic_orbits]
    return base, transversals,basic_orbits
        
def applyPerm(sol):
    if sol == []:
        return Permutation(size = PG.N)
    target = PG.gens[sol[0]]
    for m in sol[1:]:
        target = target*PG.gens[m]
    return target       

#Check if a solution is valid

def apply_move(moves, move, state):
    m = move
    s = state.split(';')

    move_list = moves[m]
    new_state = []
    for i in move_list:
        new_state.append(s[i])
    s = new_state

    return ';'.join(s)
    
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


def validate(moves, initial_state, solution_state, solution, num_wildcards):
    sols = solution.split('.')
    cur_state = initial_state
    for s in sols:
        if s not in moves:
            return False
        cur_state = apply_move(moves, s, cur_state)
    err_cnt = sum(c!=e for c,e in zip(cur_state.split(';'), solution_state.split(';')))
    if err_cnt <= num_wildcards:
        return True,cur_state
    else:
        return False,cur_state

def val_score(i,sol):
    initial_state = path.initial_state.values[i]
    solution_state = path.solution_state.values[i]
    moves = eval(path.allowed_moves.values[i])
    moves = init_reverse_moves(moves)
    num_wildcards = path.num_wildcards.values[i]
    solution = sol

    return validate(moves, initial_state, solution_state, solution, num_wildcards)

#

def oneStep(N, gens, base, i, t, nu):
    j = t.permutation.array_form[base[i]]  # b_i ^ t
    t1 = t.inverse()
    if nu[i][j] is not None:
        result = t * nu[i][j]
        result.words = simplify(result.words)
        if len(t.words) < len(nu[i][j].words):
            nu[i][j] = t1
            oneStep(N, gens, base, i, t1, nu)
    else:
        nu[i][j] = t1
        oneStep(N, gens, base, i, t1, nu)
        result =  PermWord(Permutation(N),[])
    return result

def oneRound(N, gens, base, lim, c, nu, t):
    i = c
    while i < len(base) and len(t.words)>0 and len(t.words) < lim:
        t = oneStep(N, gens, base, i, t, nu)
        i += 1

def oneImprove(N, gens, base, lim, nu):
    for j in range(len(base)):
        for x in nu[j]:
            for y in nu[j]:
                if x != None and y != None  and (x.flag or y.flag):
                    t = x * y
                    oneRound(N, gens, base, lim, j, nu, t)

        for x in nu[j]:
            if x is not None:
                pw = x
                x.flag = False

def fillOrbits(N, gens, base, lim, nu):
    for i in range(len(base)):
        orbit = []  # partial orbit already found
        for y in nu[i]:
            if y is not None:
                j = y.permutation.array_form[base[i]]
                if j not in orbit:
                    orbit.append(j)
        for j in range(i + 1, len(base)):
            for x in nu[j]:
                if x is not None:
                    x1 = x.inverse()
                    orbit_x = [x.permutation.array_form[it] for it in orbit]
                    new_pts = [p for p in orbit_x if p not in orbit]

                    for p in new_pts:
                        t1 = x1 * (nu[i][x1.permutation.array_form[p]])
                        t1.words = simplify(t1.words)
                        if len(t1.words) < lim:
                            nu[i][p] = t1




# Options:
#   n: max number of rounds
#   s: reset each s rounds
#   w: limit for word size
#   so: sum  orbits size

#
def buildShortWordsSGS(N, gens, base, n, s, w, so):
    nu = [[None for _ in range(N)] for _ in range(len(base))]
    for i in range(len(base)):
        nu[i][base[i]] = PermWord(Permutation(N),[])
    nw = 0
    maximum = n
    lim = float(w)
    cnt = 0
    with tqdm(total= so) as pbar:   
        iter_gen = chain.from_iterable(product(list(gens), repeat=i) for i in range(1,12))
        for gen in iter_gen:
            cnt += 1
            if cnt >= maximum or nw == so :
                break

            perm = gen_perm_from_word(gens,gen)
            pw = PermWord(perm,list(gen))
            oneRound(N, gens, base, lim, 0, nu, pw)
            nw0 =nw
            nw =  np.sum([np.sum([x!=None for x in nu_i]) for nu_i in nu])
            deltanw = nw-nw0
            pbar.update(deltanw)
            if cnt % s == 0:
                oneImprove(N, gens, base, lim, nu)
                if nw < so:
                    fillOrbits(N, gens, base, lim, nu)
                lim *= 5 / 4
                
    return nu

def factorizeM(N, gens, base, nu, target):
    result_list = []
    perm = target
    for i in range(len(base)):
        omega = perm.array_form[base[i]]
        perm *= nu[i][omega].permutation
        result_list = result_list + nu[i][omega].words

    if not perm == Permutation(size = N+1):
        print("failed to reach identity, permutation not in group")

    return simplify(invwords(result_list))

def gen_perm_from_word(gens,words):
    res = gens[words[0]]
    for w in words[1:]:
        res = res * gens[w]
    return res

def invwords(ws):
    inv_ws = [geninvs[g] for g in ws]
    inv_ws.reverse() 
    return inv_ws


#remove invers generators in concatenation
def simplify(ff):
    if not ff:
        return ff
    # find adjacent inverse generators
    zero_sum_indices = [(i, i + 1) for i in range(len(ff) - 1) if ff[i] == geninvs[ff[i + 1]] ]
    # If there is no more simplications
    if not zero_sum_indices:
        return ff
    # remove inverse pairs
    for start, end in zero_sum_indices:
        return simplify(ff[:start] + ff[end + 1:])
    return ff


    
def test_SGS(N,nu,base):
    result = True
    for i in range(len(base)):
        # diagonal identities
        p = nu[i][base[i]].words
        if p != []:
            result = False
            print('fail identity')
            
        for j in range(N):
            if j in nu[i]:
                p =nu[i][j].permutation.array_form 
                # stabilizes points upto i
                for k in range(i):
                    p2 = p[base[k]]
                    if p2 != base[k]:
                        result = False
                        print('fail stabilizer',i,j,k)

                
                # correct transversal at i
                if p[j] != base[i]:
                    result = False  
                    print('fail traversal ',i,j)
    return result

def quality(N, nu, base):
    result = 0
    for i in range(len(base)):
        maxlen = 0
        for j in range(N):
            if nu[i][j] is not None:
                wordlen = len(nu[i][j].words)
                if wordlen > maxlen:
                    maxlen = wordlen
        result += maxlen
    return result



            


def ReduceFactor(PG,s,maxl = 15):
    l0 = len(s)
    l1 = l0+1
    while (l0!=l1):
        a= []
        # Find shortcuts using fast factorization of permutations
        ls = len(s)
        for i in range(ls):
            for j in range(maxl):
                j1= i+j
                if j1 < ls:
                    target = applyPerm(s[i:j1+1])
                    sol = PG.FactorPermutation(target)
                    if len(sol)<(j1-i):
                        a.append((i,j1+1,{'weight':len(sol)}))
        # Find shortest path
        G = nx.path_graph(ls+1,nx.DiGraph)
        G.add_edges_from(a)
        opt = nx.dijkstra_path(G, 0, ls)
        #opt = nx.shortest_path(G, 0, ls, method = 'bellman-ford')
        sopt =[]
        for i,j in zip(opt,opt[1:]):
            if j-i == 1:
                sopt.append(s[i])
            else:
                target = applyPerm(s[i:j])
                sol= PG.FactorPermutation(target)
                sopt = sopt + sol
        l1=l0
        s = sopt
        l0 = len(s) 

        if applyPerm(s) != applyPerm(sopt):
            print('error',s,sopt)  
            break
    return sopt

ltypes = [
# 'cube_2/2/2',
# 'wreath_6/6',
# 'wreath_7/7',
# 'globe_6/4'
# 'globe_3/4'
# 'globe_6/10'
'globe_6/8'
# 'globe_1/8',
# 'globe_8/25',
]

nretry = 1
for type in ltypes:
    print(type)
   
    ids = sub[path.puzzle_type == type].id.values
    gens = eval(info[info.puzzle_type == type].allowed_moves.values[0])
    N =max([max(gens[g]) for g in gens])+1
    gens = {g:Permutation(gens[g],size = N) for g in gens}
    
    
    for _ in range(nretry):
        sols = sub[path.puzzle_type == type].moves.values
        ll = sub.loc[path.puzzle_type == type,'moves'] .map(lambda x: len(x.split("."))).sum()
        print('Sum moves ', ll)
        PG = SGSPermutationGroup(gens)
        print('Dim:',PG.N,'Lenght base;',len(PG.base),'Sum Orbits:',PG.so)
        geninvs = PG.geninvs
        # Options:
        #   n: max number of rounds
        #   s: reset each s rounds
        #   w: limit for word size
        #   so: sum  orbits size
        PG.getShortWords(n=100000, s=1000, w=500)
        # PG.getShortWords(n=200000, s=2000, w=500)
        print(PG.CheckQuality())
    

        for i,sol in enumerate(sols):
            sol = sol.split('.')
            sol.reverse()
            target = applyPerm(sol)
            ss = PG.FactorPermutation(target)
            if len(ss) > len(sol):
                ss = sol
            ss = ReduceFactor(PG,ss,10)
            if target != applyPerm(ss):
                print('error',applyPerm(sol),applyPerm(ss)) 
                continue
            ss.reverse()
    
            flag,_ =val_score(ids[i],'.'.join(ss))
            #if len(ss)<len(sol):
            print(ids[i],len(sol),'->',len(ss),flag)
            if (len(ss)<len(sol) and flag):
                sub.loc[sub.id == ids[i],'moves'] = '.'.join(ss)
                sub.to_csv("submission_Minkwitz_tmp.csv")
        ll = sub.loc[path.puzzle_type == type,'moves'] .map(lambda x: len(x.split("."))).sum()
        print( 'Sum moves', ll)
        

sub.to_csv("submission_Minkwitz.csv")
        
