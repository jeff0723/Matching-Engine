import random

N = int(input())
name = input()
symbol = "TSLA"
with open(name,'w') as f:
	for i in range(N):
		order_type = random.choice([1,2])
		duration_type = random.choice([1,2,3])
		share = random.sample(range(100,10000,100),1)[0]
		side_ = random.choice([1,2])
		side = "BUY" if side_==1 else "SELL"
		if order_type==1:
			price = random.sample(range(400,550,5),1)[0] / 10
			f.write("%d %d %s %d %.2f %d %s\n"%(i,order_type,
				symbol,duration_type,price,share,side))
		if order_type==2:
			f.write("%d %d %s %d %d %s\n"%(i,order_type,
				symbol,duration_type,share,side))
