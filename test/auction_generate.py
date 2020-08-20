import random


out = str()
with open('text.txt','w') as f:
    side = ["BUY", "SELL"]
    for i in range(10000000):
        f.write("APPL " + str(random.randrange(80, 100)) + " " 
            + str(random.randrange(100, 300000, 5)) +
             " " + random.choice(side) + "\n")

    # print(out)
