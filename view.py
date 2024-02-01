import pandas as pd
import sys

def read_dat(path, i) :
    with open(f"{path}/{i}.txt", "r") as f:
        s = f.read()
    return s.split(".")

if len(sys.argv) != 3 :
    print("need 2 submission file")
    exit()


info = pd.read_csv("data/puzzles.csv")


df0  = pd.read_csv(sys.argv[1])
fdir = sys.argv[2]

tot = 0
sum = 0
for i in range(len(df0)) :
    pt = info.iloc[i].puzzle_type
    d0 = df0.iloc[i].moves.split(".")
    d1 = read_dat(fdir, i)
    if len(d0) != len(d1) :
        print(f"id: {i} : {pt} : {len(d0)} -> {len(d1)} ({len(d0)-len(d1)})")
    else:
        print(f"id: {i} : {pt} : {len(d0)}")
    tot += len(d0) - len(d1)
    sum += len(d1)

print("Total = ", sum , "diff=", tot)