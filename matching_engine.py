import time
class Order:
	def __init__(self, orderID, name, price, quantity, side):
		self.id = orderID
		self.name = name
		self.price = price
		self.quantity = quantity
		self.side = side
class Orderbook:
	def __init__(self):
		self.bid = {} # price : quantity
		self.bid_id = {} # price : id
		self.ask = {} # price : quantity
		self.ask_id = {} # price : id
		self.orderID = {} # id : order
	def addorder(self, order):
		if order.side == "BUY":
			if order.price in self.bid:
				self.bid[order.price] += order.quantity
				self.bid_id[order.price].append(order.id)
			else: 
				self.bid[order.price] = order.quantity
				self.bid_id[order.price] = [order.id]
		else:
			if order.price in self.ask:
				self.ask[order.price] += order.quantity
				self.ask_id[order.price].append(order.id)
			else: 
				self.ask[order.price] = order.quantity
				self.ask_id[order.price] = [order.id]
		self.orderID[order.id] = order
	def deleteorder(self, ID):
		"""
		Need ID to know which side the order in.
		"""
		order = self.orderID[ID]
		if order.side == "BUY":
			self.bid[order.price] -= order.quantity
			if self.bid[order.price] == 0:
				del self.bid[order.price]
			self.bid_id[order.price].remove(ID)
		else:
			self.ask[order.price] -= order.quantity
			if self.ask[order.price] == 0:
				del self.ask[order.price]
			self.ask_id[order.price].remove(ID)
		del self.orderID[ID]			
	def getBestprice(self, side):
		if side == "BUY":
			if len(self.ask) > 0:
				return min(self.ask.keys())
			else: return -1
		else:
			if len(self.bid) > 0:
				return min(self.bid.keys())
			else: return -1
	def Change(self, ID, change):
		order = self.orderID[ID]
		if order.side == "BUY":
			self.bid[order.price] += change
			# Change order quantity
			order.quantity += change
		else:
			self.ask[order.price] += change
			order.quantity += change
	def present(self):
		print("   BID" + " " * 40 + "ASK")
		for key in sorted(self.ask.keys(), reverse = True):
			print(" " * 40 + str(key), end = " ")
			print(self.ask[key])
		print("-" * 55)
		for key in sorted(self.bid.keys(), reverse = True):
			print(key, end = " ")
			print(self.bid[key])	
class Exchange:
	def __init__(self):
		# every product has a orderbook
		self.orderbook = {} # product:orderbook
		self.id = {} # id : product
		self.log = []
		self.execution = []
		self.time = 0
	def Send(self, order):
		# create orderbook for new product
		# log notification
		# register id
		if order.name not in self.orderbook:
			self.orderbook[order.name] = Orderbook()
		self.orderbook[order.name].addorder(order)
		self.id[order.id] = order.name
		log = str(order.id) + " " + str(order.name) + " is submitted"
		self.log.append(log)
		# self.Fill(order)
	def Fill(self, order):
		side = order.side
		while order.quantity > 0:
			best = self.orderbook[order.name].getBestprice(side)	
			if side == "BUY":
				# trade
				## log traded transaction
				## delete order from orderbook
				if order.price >= best > 0:
					counter_party_id = self.orderbook[order.name].ask_id[best][0]
					counter_party_order = self.orderbook[order.name].orderID[counter_party_id]
					if order.quantity > counter_party_order.quantity:
						# change quantity
						self.orderbook[order.name].Change(order.id, -counter_party_order.quantity)
						log = str(counter_party_id) + " " + str(counter_party_order.name) + " was traded."
						print(log)
						self.log.append(log)
						self.orderbook[order.name].deleteorder(counter_party_id)
					elif order.quantity == counter_party_order.quantity:
						self.orderbook[order.name].deleteorder(order.id)
						log = str(order.id) + " " + str(order.name) + " was traded."
						print(log)
						self.log.append(log)
						self.orderbook[order.name].deleteorder(counter_party_id)
						log = str(counter_party_id) + " " + str(counter_party_order.name) + " was traded."
						print(log)
						self.log.append(log)
					else:
				 		self.orderbook[order.name].Change(counter_party_id, -order.quantity)
				 		log = str(order.id) + " " + str(order.name) + " was traded."
				 		print(log)
				 		self.log.append(log)
				 		self.orderbook[order.name].deleteorder(order.id)
				# not good price available
				else: return
			else:
				if best >= order.price > 0:
					counter_party_id = self.orderbook[order.name].bid_id[best][0]
					counter_party_order = self.orderbook[order.name].orderID[counter_party_id]
					if order.quantity > counter_party_order.quantity:
						# change quantity
						self.orderbook[order.name].Change(order.id, -counter_party_order.quantity)
						log = str(counter_party_id) + " " + str(counter_party_order.name) + " was traded."
						print(log)
						self.log.append(log)
						self.orderbook[order.name].deleteorder(counter_party_id)
					elif order.quantity == counter_party_order.quantity:
						self.orderbook[order.name].deleteorder(order.id)
						log = str(order.id) + " " + str(order.name) + " was traded."
						print(log)
						self.log.append(log)
						self.orderbook[order.name].deleteorder(counter_party_id)
						log = str(counter_party_id) + " " + str(counter_party_order.name) + " was traded."
						print(log)
						self.log.append(log)
					else:
				 		self.orderbook[order.name].Change(counter_party_id, -order.quantity)
				 		log = str(order.id) + " " + str(order.name) + " was traded."
				 		print(log)
				 		self.log.append(log)
				 		self.orderbook[order.name].deleteorder(order.id)
				else: return
	def Cancel(self, ID):
		name = self.id[ID]
		self.orderbook[name].deleteorder(ID)
		del self.id[ID]		
	def Show(self, name):
		self.orderbook[name].present()
	def Call_Auction(self, name):
		bid = self.orderbook[name].bid
		ask = self.orderbook[name].ask
		bid_dict = sorted(bid, reverse = True)
		ask_dict = sorted(ask)
		i, j = 0, 0
		count_bid, count_ask = bid[bid_dict[0]], ask[ask_dict[0]]
		if (not bid_dict) or (not ask_dict):
			print("no price")
		if bid_dict[0] < ask_dict[0]:
			print("no price")
		if bid_dict[-1] > ask_dict[-1]:
			price_range = [bid_dict[-1], ask_dict[-1]]

		while bid_dict[i] > ask_dict[j]:
			if count_bid > count_ask:
				j += 1
				if j == len(ask_dict): 
					price_range = [bid_dict[i], ask_dict[j-1]]
					break
				count_ask += ask[ask_dict[j]]
			elif count_bid < count_ask:
				i += 1
				if i == len(bid_dict): 
					price_range = [bid_dict[i-1], ask_dict[j]]
					break
				count_bid += bid[bid_dict[i]]
			else:
				i += 1
				j += 1
				if i == len(bid_dict) or j == len(ask_dict):
					price_range = [bid_dict[i-1], ask_dict[j-1]]
					break
				count_bid += bid[bid_dict[i]]
				count_ask += ask[ask_dict[j]]
		else:
			if bid_dict[i] == ask_dict[j]:
				price_range = [bid_dict[i], ask_dict[j]]
			elif count_bid - bid[bid_dict[i]] == count_ask - ask[ask_dict[j]]:
				price_range = [bid_dict[i-1], ask_dict[j-1]]
			elif count_bid - bid[bid_dict[i]] > count_ask - ask[ask_dict[j]]:
				price_range = [bid_dict[i-1], ask_dict[j]]
			else:
				price_range = [bid_dict[i], ask_dict[j-1]]
		# test code
		"""
		for i in range(1, len(bid_dict)):
			bid[bid_dict[i]] += bid[bid_dict[i-1]]
		for i in range(1, len(ask_dict)):
			ask[ask_dict[i]] += ask[ask_dict[i-1]]  
		for key in bid_dict:
			print(key, bid[key])
		for key in ask_dict:
			print(key, ask[key])
		"""
		print("price_range = ", price_range)
class Execution:
	def __init__(self, orderID, name, price, quantity, time):
		self.id = orderID
		self.name = name
		self.price = price
		self.quantity = quantity
		self.time = time
def main():
	exchange = Exchange()
	time = 0
	N = 0
	with open('text.txt','r') as f:
		for line in f:
			I = input().strip()
			# order
			if I == "O":
				info = input().strip().split()
				order = Order(N, info[0], float(info[1]), int(info[2]), info[3])
				exchange.Send(order)
				N += 1
			elif I == "Sh":
				info = input()
				exchange.Show(info)
			# change
			elif I == "Ch":
				info = input()
				exchange.Cancel(info)
				exchange.Send(order)
			# cancel
			elif I == "Ca":
				info = input()
				exchange.Cancel(ID)
			elif I == "quit":
				return
			elif I == "Auction":
				info = input()
				exchange.Call_Auction(info)
			else:
				continue
# def main2():
# 	exchange = Exchange()
# 	N = 0
# 	with open('text.txt','r') as f:
# 		for line in f:
# 			info = line.strip().split()
# 			order = Order(N, info[0], float(info[1]), int(info[2]), info[3])
# 			exchange.Send(order)
# 			N += 1
# 	print("Data Loaded")
# 	start = time.time()
# 	exchange.Call_Auction("APPL")
# 	end = time.time()
# 	print(end-start)
			

if __name__ == '__main__':
	main()
"""
O
APPL 96 20 SELL
O
APPL 96 40 BUY
O
APPL 98 40 SELL
O
APPL 99 20 BUY
O
APPL 98 30 BUY
O
APPL 94 30 SELL
Auction
APPL
"""
# main2()
"""
O
APPL 100 30 BUY
O
APPL 99 20 BUY
O
APPL 98 50 BUY
O
APPL 97 30 BUY
O
APPL 96 20 BUY
O
APPL 100 70 SELL
O
APPL 99 60 SELL
O
APPL 98 50 SELL
O
APPL 97 40 SELL
O
APPL 96 10 SELL
Auction
APPL
"""

