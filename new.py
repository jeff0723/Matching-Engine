#naming convention
#Captial 
from collections import deque
import time
AUCTION, AUCTION_PLUS_5, TRADING = 1, 2, 3
Ms = int(1e6)
OPEN_TIME = 9*60*60*Ms
CLOSE_TIME = (13*60+25)*60*Ms
MIN = 60*Ms
LIMIT, MARKET = 1, 0
ROD, IOC, FOK= 1, 2, 3
class CustomError(Exception):
	pass
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
	LOG = []#for exchange to 
	def __init__(self,close=1000):
		self.state = AUCTION
		self.benchmark = [close] # for 
		self.ncat= OPEN_TIME#initialize 9am microsecond
		self.bid = {}
		self.ask = {}
		self.bid_id = {}# price:two list limit in second ,market in first
		self.ask_id = {}
		self.order_list = {} #id:order
		self.price_series = [close]
		self.ma_5 = deque()#last five minutes obejct (time,price,volume)
		self.total_volume = 0
		self.total_dollar_volume = 0
		self.clock = 0

	def Send(self,order):
		#check state
		self.CheckTime(order.time)
		if order.price_type == MARKET:
				order.price = self.LastPrice()
		if (order.price > self.benchmark[0]*1.1) or (order.price < self.benchmark[0]*0.9):
			#invalid order
			print("close: ",self.benchmark[0])
			print("price: ",order.price)
			print("超過漲停限制")
			return
		if self.state == AUCTION:
			if order.price_type==LIMIT and order.duration_type==ROD:
				self.AddOrder(order)
				# print("order added")
				return
			else:
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
		if order.side == "BUY":
			self.bid.setdefault(order.price,0)
			self.bid_id.setdefault(order.price,[deque(),deque()])
			self.bid[order.price] += order.share
			if order.price_type == MARKET:
				self.bid_id[order.price][0].append(order.id)

			else:
				self.bid_id[order.price][1].append(order.id)
		else:
			self.ask.setdefault(order.price,0)
			self.ask_id.setdefault(order.price,[deque(),deque()])
			self.ask[order.price] += order.share
			if order.price_type == MARKET:
				self.ask_id[order.price][0].append(order.id)

			else:
				self.ask_id[order.price][1].append(order.id)
		self.order_list[order.id] = order


	def DeleteOrder(self,ID):
		order = self.order_list[ID]
		if order.side == "BUY":
			self.bid[order.price] -= order.share
			if self.bid[order.price] == 0:
				del self.bid[order.price]
			if order.price_type == MARKET:
				self.bid_id[order.price][0].remove(ID)
			else:
				self.bid_id[order.price][1].remove(ID)
		if order.side == "SELL":
			self.ask[order.price] -= order.share
			if self.ask[order.price] == 0:
				del self.ask[order.price]
			if order.price_type == MARKET:
				self.ask_id[order.price][0].remove(ID)
			else:
				self.ask_id[order.price][1].remove(ID)

		del self.order_list[ID]

	def ChangeOrder(self,ID,change):#only limit order can change
		order = self.order_list[ID]
		price = order.price
		side = order.side
		new_share = order.share - change
		if side == "SELL":
			self.ask[price] -= change
			self.order_list[ID].share = new_share
		if side == "BUY":
			self.bid[price] -= change
			self.order_list[ID].share = new_share

	def Present(self):
		print("   BID"+" "*40+"ASK")
		for price in sorted(self.ask,reverse=True):
			print("\t"*5+str(price)+": "+str(self.ask[price]))
		print('-'*55)
		for price in sorted(self.bid,reverse=True):
			print(price,": ",self.bid[price])
	def GetBestPrice(self,side):
		if side=="BUY": 
			if len(self.ask)!=0:
				return min(self.ask.keys())
			else: return -1
		if side=="SELL": 
			if len(self.bid)!=0:
				return max(self.bid.keys())
			else: return -1

	def LastPrice(self):
		return self.price_series[-1]


	def GetAvailability(self,price,side):
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

	def Fill(self, order): # return log list

		try:
			if order.side == "BUY":

				P = sorted(self.ask.keys()) # search from lowest price
				i = 0

				while self.order_list[order.id].share > 0 and i < len(P) and order.price >= P[i]:
					# Claim: at least one match except PSM
					# self.Present()

					if self.order_list[order.id].share > self.ask[P[i]]:
						# Turnover all order at price P[i]
						IDs = self.ask_id[P[i]][MARKET] + self.ask_id[P[i]][LIMIT]
						q = self.ask[P[i]]
						for Id in IDs:
							self.Turnover(Id, P[i], self.order_list[Id].share) # counter part order (full fill)
						self.Turnover(order.id, P[i], q) # current order (partial fill)
						
						i += 1 # next price

					else:
						# Claim: Can fill current order except PSM
						# First turnover market order, then limited order
						tmp = self.order_list[order.id].share
						for j in [0, 1]:
							while self.order_list[order.id].share > 0 and (P[i] in self.ask_id) and self.ask_id[P[i]][j]:

								Id = self.ask_id[P[i]][j][0] # lowest price id

								if self.order_list[order.id].share >= self.order_list[Id].share:
									self.order_list[order.id].share -= self.order_list[Id].share
									self.Turnover(Id, P[i], self.order_list[Id].share) # counter part order (full fill)
								else:
									self.Turnover(Id, P[i], self.order_list[order.id].share) # counter part order (partial fill)
									self.order_list[order.id].share = 0

						
						self.Turnover(order.id, P[i], tmp)	
						break # current order (full fill)


			if order.side == "SELL":

				P = sorted(self.bid.keys(),reverse=True) # search from lowest price
				i = 0
				print(P[i] , " match", order.price)
				while self.order_list[order.id].share > 0 and i < len(P) and order.price <= P[i]:
					# Claim: at least one match except PSM
					if self.order_list[order.id].share > self.bid[P[i]]:
						# Turnover all order at price P[i]
						print("1")
						IDs = self.bid_id[P[i]][MARKET] + self.bid_id[P[i]][LIMIT]
						q = self.bid[P[i]]
						for Id in IDs:
							self.Turnover(Id, P[i], self.order_list[Id].share) # counter part order (full fill)
						self.Turnover(order.id, P[i], q) # current order (partial fill)
						
						i += 1 # next price

					else:
						# Claim: Can fill current order except PSM
						# First turnover market order, then limited order
						print("2")
						tmp = self.order_list[order.id].share

						for j in [0, 1]:
							while self.order_list[order.id].share > 0 and (P[i] in self.bid_id) and self.bid_id[P[i]][j]:

								Id = self.bid_id[P[i]][j][0] # lowest price id

								if self.order_list[order.id].share >= self.order_list[Id].share:
									self.order_list[order.id].share -= self.order_list[Id].share
									self.Turnover(Id, P[i], self.order_list[Id].share) # counter part order (full fill)
								else:
									self.Turnover(Id, P[i], self.order_list[order.id].share) # counter part order (partial fill)
									self.order_list[order.id].share = 0

						self.Turnover(order.id, P[i], tmp) # current order (full fill)
						break


		except CustomError as e:
			print(e)
			# print("Price Stabilization Mechanism raised!")

		finally:

			if order.id in self.order_list:
				return self.order_list[order.id]
			else:
				return None

	def Turnover(self, orderId, price, volume):

		print("state:",self.state, "orderId =", orderId, "price =", price, "volume =", volume)
		assert(volume > 0)
		order = self.order_list[orderId]

		# Update moveing average
		while self.ma_5 and self.ma_5[0][0]+5*MIN >= self.clock:
			self.total_volume -= self.ma_5[0][2]
			self.total_dollar_volume -= self.ma_5[0][1] * self.ma_5[0][2]
			self.ma_5.popleft()

		# check price stabilization mechanism
		if self.state == TRADING or self.state == AUCTION_PLUS_5:

			if self.state == TRADING:
				stab_mech_price = self.total_dollar_volume / self.total_volume if self.total_volume != 0 else price_series[-1]
			elif self.state == AUCTION_PLUS_5:
				stab_mech_price = self.benchmark[-1]
			print(stab_mech_price)
			if price > stab_mech_price * 1.035 or price < stab_mech_price * 0.965:
				# Exception!!!
				print("Stab MP =", stab_mech_price)
				print(self.benchmark)
				self.state = AUCTION
				self.ncat = self.clock + 2*MIN
				raise CustomError("Price Stabilization Mechanism.")

		# add new trade into MA
		self.ma_5.append((self.order_list[orderId].time, price, volume))
		self.total_volume += volume
		self.total_dollar_volume += price*volume

		#add log 
		'''
		TODO
		'''



		# if partially fill, change order
		print("volume %d : share %d"%(volume,order.share))
		if volume < order.share:

			if order.side == "BUY":
				self.bid[order.price] -= volume
			elif order.side == "SELL":
				self.ask[order.price] -= volume
			# print(orderId)
			self.order_list[orderId].share -= volume


		else:
			# if full fill, delete order
			print("Hi")
			if order.side == "BUY":

				# modify total bid volume at this price
				self.bid[order.price] -= volume

				# Delete first element of bid_id[p][0] or bid_id[p][1]
				if self.bid_id[order.price][0]:
					self.bid_id[order.price][0].popleft()
				else:
					self.bid_id[order.price][1].popleft()

				# If nothing left, delete this price entry
				if self.bid[order.price] == 0:
					del self.bid[order.price] 
					del self.bid_id[order.price] 

			elif order.side == "SELL":

				# modify total ask volume at this price
				self.ask[order.price] -= volume

				# Delete first element of ask_id[p][0] or ask_id[p][1]
				if self.ask_id[order.price][0]:
					self.ask_id[order.price][0].popleft()
				else:
					self.ask_id[order.price][1].popleft()

				# If nothing left, delete this price entry
				if self.ask[order.price] == 0:
					del self.ask[order.price]
					del self.ask_id[order.price]
			print("Successfully remove %s orderID:%d @%d"%(order.side,
				order.id,order.price))
			del self.order_list[orderId] # delete order_list id 


	def CallAuction(self):
		# print(self.clock)
		bid = self.bid
		ask = self.ask
		bid_dict = sorted(bid, reverse = True)
		ask_dict = sorted(ask)

		if (not bid_dict) or (not ask_dict):
			return
		count_bid, count_ask = bid[bid_dict[0]], ask[ask_dict[0]]
		if bid_dict[0] < ask_dict[0]:
			return
		if bid_dict[-1] > ask_dict[-1]:
			price_range = [bid_dict[-1], ask_dict[-1]]

		# determine possible price range
		i, j = 0, 0
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
		for price in bid_dict:
			if price >= final_price: volume_bid += bid[price]
			else: break 
		for price in ask_dict:
			if price <= final_price: volume_ask += ask[price]
			else: break

		V = min(volume_ask, volume_bid)

		# Trade bid 
		acc_vol = 0
		Prices = bid_dict.copy()
		i = 0
		while V > acc_vol and i < len(Prices):
		
			IDs = self.bid_id[Prices[i]][LIMIT].copy()
			print(IDs)
			for ID in IDs:
				print("ID:%d"%ID)
				q = self.order_list[ID].share
				if acc_vol + q <= V:
					self.Turnover(ID, final_price, q)
					acc_vol += q
				elif V - acc_vol > 0:
					self.Turnover(ID, final_price, V - acc_vol)
				else:
					# V == acc_vol
					break
			i += 1
		# Trade ask
		acc_vol = 0
		Prices = ask_dict.copy()
		i = 0
		

		while V > acc_vol and i < len(Prices):

			# print(self.ask_id[Prices[i]])
			# print("HI")
			IDs = self.ask_id[Prices[i]][LIMIT].copy()
			print(IDs)
			for ID in IDs:
				q = self.order_list[ID].share
				print("SHARE: ", q)
				if acc_vol + q <= V:
					self.Turnover(ID, final_price, q)
					acc_vol += q
				elif V - acc_vol > 0:
					self.Turnover(ID, final_price, V - acc_vol)
				else:
					# V == acc_vol
					break
			i += 1

		print("Final_price =", final_price, "Deal volume =", V)


		# if volume_ask > volume_bid:
		# 	# bid fully filled
		# 	for price in bid_dict:
		# 		if price >= final_price:
		# 			IDs = self.bid_id[price][1].copy()
		# 			for ID in IDs:
		# 				self.Turnover(ID, price, self.order_list[ID].share)
		# 	# ask partially filled
		# 	volume = volume_bid
		# 	for price in ask_dict:
		# 		# the part is still fully filled
		# 		if ask[price] <= volume:
		# 			volume -= ask[price]
		# 			IDs = self.ask_id[price][1].copy()
		# 			for ID in IDs:
		# 				self.Turnover(ID, price, self.order_list[ID].share)
		# 			if volume == 0: return
		# 		# partial filled
		# 		else:
		# 			IDs = self.ask_id[price][1].copy()
		# 			for ID in IDs:
		# 				if self.order_list[ID].share < volume:
		# 					self.Turnover(ID, price, self.order_list[ID].share)
		# 					volume -= self.order_list[ID].share
		# 				else:
		# 					self.Turnover(ID, price, volume)
		# 					return
		# elif volume_bid > volume_ask:
		# 	for price in ask_dict:
		# 		if price <= final_price:
		# 			IDs = self.ask_id[price][1].copy()
		# 			for ID in IDs:
		# 				self.Turnover(ID, price, self.order_list[ID].share)
		# 	volume = volume_ask
		# 	for price in bid_dict:
		# 		if bid[price] <= volume:
		# 			volume -= bid[price]
		# 			IDs = self.bid_id[price][1].copy()
		# 			for ID in IDs:
		# 				self.Turnover(ID, price, self.order_list[ID].share)
		# 			if volume == 0: return
		# 		else:
		# 			IDs = self.ask_id[price][1].copy()
		# 			for ID in IDs:
		# 				if self.order_list[ID].share < volume:
		# 					self.Turnover(ID, price, self.order_list[ID].share)
		# 					volume -= self.order_list[ID].share
		# 				else:
		# 					self.Turnover(ID, price, volume)
		# 					return
		# else:
		# 	for price in bid_dict:
		# 		if price >= final_price:
		# 			IDs = self.bid_id[price][1].copy()
		# 			for ID in IDs:
		# 				self.Turnover(ID, price, self.order_list[ID].share)
		# 	for price in ask_dict:
		# 		if price <= final_price:
		# 			IDs = self.ask_id[price][1].copy()
		# 			for ID in IDs:
		# 				self.Turnover(ID, price, self.order_list[ID].share)

	def CheckTime(self,update_time):#check and change state 
		self.clock = update_time

		if update_time < OPEN_TIME or update_time > CLOSE_TIME:
			self.state = AUCTION
		else:

			if update_time < self.ncat: 
				next_state = AUCTION
			elif (self.ncat+5*MIN) >= update_time >= self.ncat : 
				next_state = AUCTION_PLUS_5
			else:
				next_state = TRADING

			if (next_state == AUCTION_PLUS_5 or next_state == TRADING) and self.state==AUCTION:
				print("CallAuction")
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
			print("ticker not exist")



	# def process():
	# 	input 
	# 	out = []

	# def Send(): #return log
	# 	log = OrderBooK.fill()
	# def Change():#return log

	# def __update_time():

	# def __fill():#return order

	# def __turnover():

	# def __call_auction():

def main():

	ID = 0
	# limit: time id ticker price_type duration_type share side price
	# O 8:45:40 TSLA LIMIT ROD 1000 BUY 45.5
	TYPE = {"LIMIT":LIMIT,"MARKET":MARKET,
	"ROD":ROD,"IOC":IOC,"FOK":FOK}

	exchange = Exchange()
	count = 0
	while True:

		info = input().strip().split()

		if info[0] == "O":
			if ID == 0:
				exchange.OpenBook(info[2],float(info[7]))

			a = time.strptime(info[1],"%H:%M:%S")
			now = a.tm_hour*60*60*Ms + a.tm_min*60*Ms+a.tm_sec*Ms
			
			if TYPE[info[3]]==LIMIT:
				order = Order(now,ID,info[2],TYPE[info[3]],
					TYPE[info[4]],int(info[5]),info[6],float(info[7]))

			if TYPE[info[3]]==MARKET:
				order = Order(now,ID,info[2],TYPE[info[3]],
					TYPE[info[4]],int(info[5]),info[6])
			exchange.Send(order)
			ID += 1
		if info[0] == "S":
			exchange.Show(info[1])
		# count += 1
if __name__ == "__main__":
	main()

