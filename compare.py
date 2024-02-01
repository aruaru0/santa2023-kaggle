import pandas as pd
import sys


if len(sys.argv) != 3 :
    print("need 2 submission file")
    exit()


df0 = pd.read_csv(sys.argv[1])
df1 = pd.read_csv(sys.argv[2])

for i in range(len(df0)) :
    d0 = df0.iloc[i].moves.split(".")
    d1 = df1.iloc[i].moves.split(".")
    # print(len(d0), len(d1))
    if len(d0) > len(d1) :
        print(f"id:{i} {len(d0)} -> {len(d1)}")
        with open(f"compare/{i}.txt", "w") as f :
            f.write(".".join(d1))
