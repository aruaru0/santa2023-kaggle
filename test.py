import glob 


files = glob.glob("sols/*")
files.sort()

for file in files:
    with open(file, "r") as f :
        txt = f.read()
    new = len(txt.split("."))
    cur = file.replace("sols", "sol_2dir_k")
    with open(cur, "r") as f :
        txt = f.read()
    cur = len(txt.split("."))
    print(file, cur, new, "->" , new-cur)

    # print(file, len(txt))
"""
sols/388.txt 7260 7767 -> -507
sols/389.txt 7337 6860 -> 477
sols/390.txt 6585 6487 -> 98
sols/391.txt 8174 8164 -> 10
sols/392.txt 7450 6243 -> 1207
sols/393.txt 8000 6782 -> 1218
sols/394.txt 7135 7520 -> -385
sols/395.txt 9126 9108 -> 18
sols/396.txt 8725 8714 -> 11
sols/397.txt 8548 8848 -> -300
"""