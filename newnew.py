# newnew.py
from collections import deque
import time
import sys
AUCTION, AUCTION_PLUS_5, TRADING = 1, 2, 3
Ms = int(1e6)
OPEN_TIME = 9*60*60*Ms
CLOSE_TIME = (13*60+25)*60*Ms
MIN = 60*Ms
LIMIT, MARKET = 1, 0
ROD, IOC, FOK= 1, 2, 3
BUY, BID, SELL, ASK = 0, 0, 1, 1

class Order:
	def __init__(self,time,ID,ticker,price_type,duration_type,
		share,side,price=0):
		self.time = time
		self.id = ID
		self.ticker = ticker
		self.price_type = price_type
		self.duration_type = duration_type
		self.price = price
		self.share = share
		self.side = side

class OrderBook:
	LOG = [] # for exchange to 
	def __init__(self,close=1000):
		self.state = AUCTION
		self.benchmark = [close] # for 
		self.ncat= OPEN_TIME # initialize 9am microsecond
		self.book = [{}, {}] # [bid, ask]
		self.id_book = [{}, {}]# [bid, ask], price : two list limit in second ,market in first
		self.order_list = {} # id:order
		self.price_series = [close]
		self.ma_5 = deque()#last five minutes obejct (time,price,volume)
		self.total_volume = 0
		self.total_dollar_volume = 0
		self.clock = 0
	
	def AddLog(self, msg):
		print(msg)

	def Send(self, order):
		#check state
		self.CheckTime(order.time)
		if order.price_type == MARKET:
				order.price = self.LastPrice()

		if (order.price > self.benchmark[0]*1.1) or (order.price < self.benchmark[0]*0.9):
			#invalid order
			print("close: ", self.benchmark[0])
			print("price: ", order.price)
			print("超過漲停限制")
			return

		if self.state == AUCTION:
			if order.price_type == LIMIT and order.duration_type == ROD:
				self.AddOrder(order)
				# print("order added")
			return
		else:
			if order.duration_type == FOK:
				if order.share > self.GetAvailability(order.price,order.side):
					return
			self.AddOrder(order)
			print("開始fill")
			leftover = self.Fill(order)
			if order.duration_type == IOC and leftover!=None:
				self.DeleteOrder(leftover.id)

	def AddOrder(self,order):
		self.book[order.side].setdefault(order.price,0)
		self.book[order.side][order.price] += order.share
		self.id_book[order.side].setdefault(order.price,[deque(),deque()])
		self.id_book[order.side][order.price][order.price_type].append(order.id)
		self.order_list[order.id] = order

	def DeleteOrder(self,ID):
		order = self.order_list[ID]
		# if order.side == "BUY":
		self.book[order.side][order.price] -= order.share
		if self.book[order.side][order.price] == 0:
			del self.book[order.side][order.price]
		self.id_book[order.side][order.price][order.price_type].remove(ID)
		
		del self.order_list[ID]

	def ChangeOrder(self, ID, change):#only limit order can change
		order = self.order_list[ID]
		self.book[order.side][order.price] -= change
		self.order_list[ID].share -= change
		assert(self.order_list[ID].share > 0)

	def Present(self):
		print("   BID"+" "*40+"ASK")
		for price in sorted(self.book[SELL],reverse=True):
			print("\t"*5+str(price)+": "+str(self.book[SELL][price]))
		print('-'*55)
		for price in sorted(self.book[BUY],reverse=True):
			print(price,": ",self.book[BUY][price])
	
	def GetBestPrice(self,side):

		if len(self.book[side])!=0:
			if side == BUY:
				return min(self.book[side].keys())
			else:
				return max(self.book[side].keys())
		else: 
			return -1

	def LastPrice(self):
		return self.price_series[-1]

	def GetAvailability(self, price, side):

		volume = 0

		for p in sorted(self.book[side], reverse=(side==SELL)):
			if p == price or ((p < price) == (side == BUY)):
				volume += self.book[side][p]
			else:
				break

		return volume

	def Fill(self, order): # return log list
		'''
		TODO
		'''
		return None

	def Check_Stab_Mech(self, price):
		'''
		TODO
		'''

	def Turnover(self, orderId, price, volume):
		'''
		TODO 
		'''
		return True

	def CallAuction(self):
		# print(self.clock)
		bid = self.book[BUY]
		ask = self.book[SELL]
		sortP = [sorted(self.book[BUY].keys(), reverse = True), sorted(self.book[SELL].keys())]

		if (not sortP[BUY]) or (not sortP[SELL]):
			return
		count_bid, count_ask = bid[sortP[BUY][0]], ask[sortP[SELL][0]]
		if sortP[BUY][0] < sortP[SELL][0]:
			return
		if sortP[BUY][-1] > sortP[SELL][-1]:
			price_range = [sortP[BUY][-1], sortP[SELL][-1]]

		# determine possible price range
		i, j = 0, 0
		while sortP[BUY][i] > sortP[SELL][j]:
			if count_bid > count_ask:
				j += 1
				if j == len(sortP[SELL]): 
					price_range = [sortP[BUY][i], sortP[SELL][j-1]]
					break
				count_ask += ask[sortP[SELL][j]]
			elif count_bid < count_ask:
				i += 1
				if i == len(sortP[BUY]): 
					price_range = [sortP[BUY][i-1], sortP[SELL][j]]
					break
				count_bid += bid[sortP[BUY][i]]
			else:
				i += 1
				j += 1
				if i == len(sortP[BUY]) or j == len(sortP[SELL]):
					price_range = [sortP[BUY][i-1], sortP[SELL][j-1]]
					break
				count_bid += bid[sortP[BUY][i]]
				count_ask += ask[sortP[SELL][j]]

		else:
			if sortP[BUY][i] == sortP[SELL][j]:
				price_range = [sortP[BUY][i], sortP[SELL][j]]
			elif count_bid - bid[sortP[BUY][i]] == count_ask - ask[sortP[SELL][j]]:
				price_range = [sortP[BUY][i-1], sortP[SELL][j-1]]
			elif count_bid - bid[sortP[BUY][i]] > count_ask - ask[sortP[SELL][j]]:
				price_range = [sortP[BUY][i-1], sortP[SELL][j]]
			else:
				price_range = [sortP[BUY][i], sortP[SELL][j-1]]

		# determine final price
		benchmark = self.price_series[-1]
		if price_range[0] >= benchmark >= price_range[1]:
			final_price = benchmark
		elif benchmark > price_range[0]:
			final_price = price_range[0]
		else:
			final_price = price_range[1]

		# update price series
		self.price_series.append(final_price)
		self.benchmark.append(final_price)

		# determine which side is fully filled and which side is partially filled
		volume_bid, volume_ask = 0, 0
		for price in sortP[BUY]:
			if price >= final_price: volume_bid += bid[price]
			else: break 
		for price in sortP[SELL]:
			if price <= final_price: volume_ask += ask[price]
			else: break

		V = min(volume_ask, volume_bid)

		# Trade 
		for x in [BUY, SELL]:
			acc_vol = 0
			Prices = sortP[x].copy()
			i = 0
			while V > acc_vol and i < len(Prices):
			
				IDs = self.id_book[x][Prices[i]][LIMIT].copy()
				#print(IDs)
				for ID in IDs:
					#print("ID:%d"%ID)
					q = self.order_list[ID].share
					'''
					TODO 改掉 Turnover
					'''
					if acc_vol + q <= V:
						self.Turnover(ID, final_price, q)
						acc_vol += q
					elif V - acc_vol > 0:
						self.Turnover(ID, final_price, V - acc_vol)
					else:
						# V == acc_vol
						break
				i += 1

		print("Final_price =", final_price, ", Total deal volume =", V)


	def CheckTime(self, update_time): # check and change state 
		self.clock = update_time

		if update_time < OPEN_TIME or update_time > CLOSE_TIME:
			self.state = AUCTION

		else:
			if update_time < self.ncat: 
				next_state = AUCTION
			elif (self.ncat + 5 * MIN) >= update_time >= self.ncat : 
				next_state = AUCTION_PLUS_5
			else:
				next_state = TRADING

			if (next_state == AUCTION_PLUS_5 or next_state == TRADING) and self.state==AUCTION:
				self.AddLog("Call Auction!")
				self.CallAuction()

			self.state = next_state
			


class Exchange:
	def __init__(self):
		self.open = (8*60+30)*60*Ms
		self.close = (13*60+30)*60*Ms
		self.orderbook = {}
		# self.close_price = {}

	def OpenBook(self,ticker,price):
		self.orderbook[ticker] = OrderBook(price)

	def Send(self,order):
		# print(type(order.time))
		self.orderbook.setdefault(order.ticker,OrderBook())
		if order.time < self.open or order.time > self.close:
			return
		else:
			# self.orderbook[order.ticker].CheckTime(order.time)
			self.orderbook[order.ticker].Send(order)

	def Show(self,ticker):
		if ticker in self.orderbook:
			self.orderbook[ticker].Present()
		else:
			print("Ticker not exist.")



def main():

	'''
	order input: 
		time
		ticker 
		price_type 
		duration_type 
		share 
		side 
		(price)
	'''
	# O 8:45:40 TSLA LIMIT ROD 1000 BUY 45.5
	# S TSLA

	TYPE = {"BUY":BUY,
			"SELL":SELL,
			"LIMIT":LIMIT,
			"MARKET":MARKET,
			"ROD":ROD,
			"IOC":IOC,
			"FOK":FOK }

	exchange = Exchange()
	count = 0
	ID = 0
	
	while True:

		info = input().strip().split()

		if not info:
			continue
			
		if info[0] == "O":
			if ID == 0:
				exchange.OpenBook(info[2],float(info[7]))

			a = time.strptime(info[1],"%H:%M:%S")
			now = a.tm_hour*60*60*Ms + a.tm_min*60*Ms+a.tm_sec*Ms
			
			if TYPE[info[3]] == LIMIT:
				order = Order(now,
							  ID,
							  info[2],
							  TYPE[info[3]],
							  TYPE[info[4]],
							  int(info[5]),
							  TYPE[info[6]],
							  float(info[7]))

			if TYPE[info[3]] == MARKET:
				order = Order(now,
							  ID,
							  info[2],
							  TYPE[info[3]],
							  TYPE[info[4]],
							  int(info[5]),
							  TYPE[info[6]])

			exchange.Send(order)
			ID += 1

		if info[0] == "S":
			exchange.Show(info[1])




if __name__ == "__main__":
	main()





