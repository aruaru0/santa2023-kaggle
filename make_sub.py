import pandas as pd
import sys

if len(sys.argv) != 2:
    print("input file name")
    exit(0)

sample_submission = pd.read_csv("data/sample_submission.csv")
sol = sys.argv[1]

print("solution files = ", sol)

moves = []
for id_ in sample_submission["id"]:
    with open(f"{sol}/{id_}.txt") as fp:
        solution_str = fp.read()
        moves.append(solution_str)

sample_submission["moves"] = moves
total = sample_submission["moves"].map(lambda x: len(x.split("."))).sum()
print(total)
sample_submission.to_csv(f"submission_{total}.csv", index=False)
