
class LimitOrder:
	# ordertype orderid timestamp product quantity side
	# price_type: 1 limited 2 market 
	# duration_type : 1 ROD 2 IOC 3 FOK
	def __init__(self,orderId,product,duration_type,price,quantity,side):
		self.id = orderId 
		self.product = product
		self.price_type = 1
		self.duration_type = duration_type
		self.price = price 
		self.quantity = quantity
		self.side = side

class MarketOrder:
	def __init__(self,order_id,product,duration_type,quantity,side):
		self.id = order_id
		self.product = product
		self.price_type = 2
		self.duration_type = duration_type
		self.quantity = quantity
		self.side = side

class OrderBook:
	# bid ask price volume 
	# resting can only be limited order
	def __init__(self):
		#price : list of order
		self.bid = {}#price : value
		self.bid_id = {}# price : list of order_id
		self.ask = {}
		self.ask_id = {}
		self.orderId = {}
	
	def addOrder(self,order):#only add limited order
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
	
	def getAvaiblility(self,price,side):
		volume = 0
		if side == "BUY":
			for p in sorted(self.ask):
				if(p <= price):
					volume += self.ask[p]
				else:
					break
		if side == "SELL":
			for p in sorted(self.bid,reverse=True):
				if(p >= price):
					volume += self.bid[p]
				else:
					break

		return volume

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
		self.price = {}
		self.time = 0

	def Send(self,order):
		if order.price_type == 2:
			if order.product in self.price:
				market_price = self.price[order.product]
				order = LimitOrder(order.id,order.product,
							order.duration_type,market_price,order.quantity,order.side)
			else:
				print("Your order is failed")
				return
		if order.product not in self.orderbook:
			if order.duration_type==1:
				self.orderbook[order.product]= OrderBook()
				self.orderbook[order.product].addOrder(order)
				log = "Order id: "+str(order.id)+" is submitted."
				print(log)
				self.log.append(log)
				self.id[order.id] = order.product
			else:
				print("Your order is failed")
			return 
		#
		side = order.side
		best = self.orderbook[order.product].getBestPrice(side)
		available = self.orderbook[order.product].getAvaiblility(order.price,side)
		if side == "BUY":
			if best == -1:
				if order.duration_type == 1:

					self.orderbook[order.product].addOrder(order)
					log = "Order id: "+str(order.id)+" is submitted."
					print(log)
					self.log.append(log)
					self.id[order.id] = order.product
				else:
					print("flag 1 ")
					print("Your order is failed")
					return
			else:

				if best <= order.price:
					if order.duration_type==3:
						if (available < order.quantity):
							print("Your order is failed")
							return

					product = order.product 
					p = self.orderbook[product].getBestPrice(side)
					while(order!= None and p <= order.price):
						order = self.fill(order,p)
						p = self.orderbook[product].getBestPrice(side)
						if(p == -1 and order!= None):
							# self.orderbook[order.product].addOrder(order)
							# log = "Order id: "+str(order.id)+" is submitted."
							# print(log)
							# self.log.append(log)
							break
					if order!=None:
						if order.duration_type==2:
							print("Order id: " ,str(order.id)," ",order.quantity,"share is cancel.")
							return 
						self.orderbook[product].addOrder(order)
						log = "Order id: "+str(order.id)+" is submitted."
						print(log)
						self.log.append(log)

				else:
					if order.duration_type == 1:
						self.orderbook[order.product].addOrder(order)
						log = "Order id: "+str(order.id)+" is submitted."
						print(log)
						self.log.append(log)
						self.id[order.id] = order.product
					else:
						print("Your order is failed")
					return

		if side == "SELL":
			if best==-1:
				if order.duration_type == 1:
					self.orderbook[order.product].addOrder(order)
					log = "Order id: "+str(order.id)+" is submitted."
					print(log)
					self.log.append(log)
					self.id[order.id] = order.product
				else:
					print("Your order is failed")
					return
			else:
				if best >= order.price:
					if order.duration_type==3:
						if (available < order.quantity):
							print("Your order is failed")
							return

					product = order.product 
					p = self.orderbook[product].getBestPrice(side)
					while(order!= None and p >= order.price):
						order = self.fill(order,p)
						p = self.orderbook[product].getBestPrice(side)
						if(p == -1 and order!= None):
							# self.orderbook[order.product].addOrder(order)
							# log = "Order id: "+str(order.id)+" is submitted."
							# print(log)
							# self.log.append(log)
							break
					if order!=None:
						if order.duration_type==2:
							print("Order id: " ,str(order.id)," ",order.quantity,"share is cancel.")
							return 
						self.orderbook[product].addOrder(order)
						log = "Order id: "+str(order.id)+" is submitted."
						print(log)
						self.log.append(log)

				else:
					if order.duration_type == 1:
						self.orderbook[order.product].addOrder(order)
						log = "Order id: "+str(order.id)+" is submitted."
						print(log)
						self.log.append(log)
						self.id[order.id] = order.product
					else:
						print("Your order is failed")
					return
	
	def Cancel(self,_id):
		if _id in self.id:
			product = self.id[_id]
			self.orderbook[product].deleteOrder(_id)
			print("Successfully remove order: ", _id)
			del self.id[_id]
		else:
			print("ID doesnt exist")
	def fill(self,order,best):
		share = order.quantity
		side = order.side
		product = order.product
		self.price[product] = best
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
	def show_market_price(sefl,product):
		print(self.price[product])
	def market_price(self,product):
		return self.price[product]
	def show_orderbook(self,product):
		if product in self.orderbook:
			self.orderbook[product].present()
		else:
			print('There is no order yet')
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
	# O 1
	# TSLA 1 43.6 1000 BUY
	# O 2 
	# TSLA 2 1000 BUY
	while True:
		I = input().strip().split()
		try:
			if I[0] == "O":
				if I[1] == '1':
					info = input().strip().split()
					order = LimitOrder(N,info[0],int(info[1]),float(info[2]),int(info[3]),info[4])
				
				if I[1] == '2':
					info = input().strip().split()
					order = MarketOrder(N,info[0],int(info[1]),int(info[2]),info[3])
				exchange.Send(order)
				N += 1
			elif I[0] == "C":
				info = input().strip()
				exchange.Cancel(int(info))
			elif I[0] == "S":
				info = input().strip()
				exchange.show_orderbook(info)
			elif I[0] == "N":
				exchange.next()
			elif I[0] == "E":
				exchange.show_execution()
			else:
				continue

		except Exception as e:
			print(e)
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
	main()


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
'''
you can comment like this.
'''

