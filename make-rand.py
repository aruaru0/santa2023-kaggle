import random

random.seed(22) 

n = 10
p = ["f","d","r"]

move = []
for i in range(n) :
    pi = random.randint(0, 2)
    pn = random.randint(0, 2)
    pf = random.randint(0, 1)
    
    x = p[pi] + str(pn)
    if pf == 1 : x = '-' + x
    print(x)
    move.append(x)

print(".".join(move))
