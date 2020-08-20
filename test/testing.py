from matching_engine import *
import time 
exchange = Exchange()
start = time.time()
name = input()
with open(name,'r') as f:
	for line in f:
		l = line.strip().split()
		if l[1]=='1':
			order = LimitOrder(int(l[0]),l[2],int(l[3]),float(l[4]),int(l[5]),l[6])
		elif l[1] == '2':
			order = MarketOrder(int(l[0]),l[2],int(l[3]),int(l[4]),l[5])
		exchange.Send(order)
end = time.time()
print(end-start)
logs = exchange.return_log()
with open("result.txt",'w') as f:
	for log in logs:
		f.write(log+'\n')

