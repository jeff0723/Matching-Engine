class Order:
	# ordertype orderid timestamp product quantity side
	def __init__(self,orderId,product,price,quantity,side):
		self.id = orderId 
		self.product = product
		self.price = price 
		self.quantity = quantity
		self.side = side
class OrderBook:
	# bid ask price volume 
	def __init__(self):
		#price : list of order
		self.bid = {}#price : value
		self.bid_id = {}# price : list of order_id
		self.ask = {}
		self.ask_id = {}
		self.orderId = {}
	def addOrder(self,order):
		if order.side == "BUY":
			if order.price not in self.bid:
				self.bid[order.price] = order.quantity
				self.bid_id[order.price] = [order.id]
			else:
				self.bid[order.price] += order.quantity
				self.bid_id[order.price].append(order.id)
		if order.side == "SELL":
			if order.price not in self.ask:
				self.ask[order.price] = order.quantity
				self.ask_id[order.price] = [order.id]
			else:
				self.ask[order.price] = order.quantity
				self.ask_id[order.price].append(order.id)

		self.orderId[order.id] = order
	def deleteOrder(self,_id):
		order = self.orderId[_id]
		if order.side == "BUY":
			self.bid[order.price] -= order.quantity
			if self.bid[order.price] == 0:
				del self.bid[order.price]
			self.bid_id[order.price].remove(_id)
		if order.side == "SELL":
			self.ask[order.price] -= order.quantity
			if self.ask[order.price]==0:
				del self.ask[order.price]
			self.ask_id[order.price].remove(_id)

		del self.orderId[_id]


	def getBestPrice(self,side):
		if(side=="BUY"): 
			if len(self.ask)!=0:
				return min(self.ask.keys())
			else: return -1
		if(side=="SELL"): 
			if len(self.bid)!=0:
				return max(self.bid.keys())
			else: return -1
	def Change(self,order_id,change):
		order = self.orderId[order_id]
		price = order.price
		side = order.side
		new_share = order.quantity - change
		if side == "SELL":
			self.ask[price] -= change
			self.orderId[order_id].quantity = new_share
		if side == "BUY":
			self.bid[price] -= change
			self.orderId[order_id].quantity = new_share


	def present(self):
		print("   BID"+" "*40+"ASK")
		for price in sorted(self.ask,reverse=True):
			print("\t"*5+str(price)+": "+str(self.ask[price]))
		print('-'*55)
		for price in sorted(self.bid,reverse=True):
			print(price,": ",self.bid[price])




class Exchange:
	#partial fill
	#submit order / cancel order / match order / update orderbook
	#update with iteration
	def __init__(self):
		self.orderbook = {} # product : orderbook
		self.id = {} #id: product
		self.log =[]
		self.execution = []
		self.time = 0

	def Send(self,order):
		if order.product not in self.orderbook:
			self.orderbook[order.product]= OrderBook()
			self.orderbook[order.product].addOrder(order)
			log = "Order id: "+str(order.id)+" is submitted."
			print(log)
			self.log.append(log)
			self.id[order.id] = order.product
			return 

		side = order.side
		best = self.orderbook[order.product].getBestPrice(side)
		if side == "BUY":
			if best==-1:
				self.orderbook[order.product].addOrder(order)
				log = "Order id: "+str(order.id)+" is submitted."
				print(log)
				self.log.append(log)
				self.id[order.id] = order.product
				return
			else:
				if best <= order.price:
					product = order.product 
					p = self.orderbook[product].getBestPrice(side)
					while(order!= None and p <= order.price):
						if(p== -1):
							self.orderbook[order.product].addOrder(order)
							log = "Order id: "+str(order.id)+" is submitted."

							break
						order = self.fill(order,p)
						p = self.orderbook[product].getBestPrice(side)
					if order!=None:
						self.orderbook[product].addOrder(order)
						log = "Order id: "+str(order.id)+" is submitted."
						print(log)
						self.log.append(log)

				else:
					self.orderbook[order.product].addOrder(order)
					log = "Order id: "+str(order.id)+" is submitted."
					print(log)
					self.log.append(log)
					self.id[order.id] = order.product
					return

		if side == "SELL":
			if best==-1:
				self.orderbook[order.product].addOrder(order)
				log = "Order id: "+str(order.id)+" is submitted."
				print(log)
				self.log.append(log)
				self.id[order.id] = order.product

				return
			else:
				if best >= order.price:
					product = order.product 
					p = self.orderbook[product].getBestPrice(side)
					while(order!= None and p >= order.price):
						order = self.fill(order,p)
						p = self.orderbook[product].getBestPrice(side)
					if order!=None:
						self.orderbook[product].addOrder(order)
						log = "Order id: "+str(order.id)+" is submitted."
						print(log)
						self.log.append(log)

				else:
					self.orderbook[order.product].addOrder(order)
					log = "Order id: "+str(order.id)+" is submitted."
					print(log)
					self.log.append(log)
					self.id[order.id] = order.product
					return
	
	def Cancel(self,_id):
		if _id in self.id:
			product = self.id[_id]
			self.orderbook[product].deleteOrder(_id)
			print("Successfully remove order: ", _id)
			del self.id[_id]
		else:
			print("Id doesnt exist")
	def fill(self,order,best):
		share = order.quantity
		side = order.side
		product = order.product
		if side == "BUY":
			while(share > 0 and len(self.orderbook[product].ask_id[best]) > 0):
				counter_part_id = self.orderbook[product].ask_id[best][0]
				counter_part = self.orderbook[product].orderId[counter_part_id]
				if(share >= counter_part.quantity):
					# print("order id: ",counter_part.id," is filled.")
					self.orderbook[product].deleteOrder(counter_part.id)
					self.execution.append(Execution(counter_part_id,
						product,best,counter_part.quantity,self.time))
					self.execution.append(Execution(order.id,
						product,best,counter_part.quantity,self.time))
					share -= counter_part.quantity

				else:
					# print("partial fill order id: ",counter_part.id," ",share)
					self.execution.append(Execution(counter_part_id,
						product,best,share,self.time))
					self.execution.append(Execution(order.id,
						product,best,share,self.time))
					self.orderbook[product].Change(counter_part.id,share)
					share = 0
		if side == "SELL":
			while(share > 0 and len(self.orderbook[product].bid_id[best]) > 0):
				counter_part_id = self.orderbook[product].bid_id[best][0]
				counter_part = self.orderbook[product].orderId[counter_part_id]
				if(share >= counter_part.quantity):
					# print("order id: ",counter_part.id," is filled.")
					self.orderbook[product].deleteOrder(counter_part.id)
					
					self.execution.append(Execution(counter_part_id,
						product,best,counter_part.quantity,self.time))
					self.execution.append(Execution(order.id,
						product,best,counter_part.quantity,self.time))
					share -= counter_part.quantity
				else:
					# print("partial fill order id: ",counter_part.id," ",share)
					self.execution.append(Execution(counter_part_id,
						product,best,share,self.time))
					self.execution.append(Execution(order.id,
						product,best,share,self.time))
					
					self.orderbook[product].Change(counter_part.id,share)
					share = 0
		if share > 0: 
			# print("partial fill order id: ",order.id," ",order.quantity- share)
			order.quantity = share
			return order
				# self.orderbook[order.product].addOrder(order)

		else:
			print("order id: ",order.id," is filled.")
			return None
	def show_orderbook(self,product):
		self.orderbook[product].present()
	def next(self):
		self.time += 1
	def show_execution(self):
		for exe in self.execution:
			exe.present()


class Execution:
	def __init__(self,order_id,product,price,share,time):
		self.id = order_id
		self.product = product
		self.price = price 
		self.share = share
		self.time = time
	def present(self):
		print("TIME ",self.time,": ",self.id, " ",self.product, " ",self.price,"@",self.share)	

def main():
	exchange = Exchange()
	time = 0
	N = 0
	while True:
		I = input().strip()
		if I == "O":
			info = input().strip().split()
			order = Order(N,info[0],float(info[1]),int(info[2]),info[3])
			exchange.Send(order)
			N += 1
		elif I == "C":
			info = input().strip()
			exchange.Cancel(int(info))
		elif I == "S":
			info = input().strip()
			exchange.show_orderbook(info)
		elif I == "N":
			exchange.next()
		elif I == "E":
			exchange.show_execution()
		else:
			continue
def main2():
	exchange = Exchange()
	time = 0
	N = 0
	with open("test1.txt",'r') as a:
		for line in a:
			print(line)
			I = a.readline().strip().split()
			if I[0] == "O":

				order = Order(N,I[1],float(I[2]),int(I[3]),I[4])
				exchange.Send(order)
				N += 1
			elif I[0] == "C":
				exchange.Cancel(int(I[1]))
			elif I[0] == "S":
				exchange.show_orderbook(I[1])
			elif I[0] == "N":
				exchange.next()
			elif I[0] == "E":
				exchange.show_execution()
	print('finish')



if __name__ == "__main__":
	main2()


# o = OrderBook()
# count = 0;
# for i in range(5):
# 	order = Order(count,"T",40-i,1000,"BUY")
# 	o.addOrder(order)
# 	count += 1 
# for i in range(5):
# 	order = Order(count,"T",40.5+i,1000,"SELL")
# 	o.addOrder(order)
# 	count += 1
# o.present()


