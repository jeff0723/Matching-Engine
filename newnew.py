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
opp = lambda x : BUY+SELL-x
less_than_or_equal = lambda x, y, side: (x == y) or ( ( x < y ) == (side == BUY) )
less_than = lambda x, y, side:  (( x < y ) and (side == BUY)) or (( x > y ) and (side != BUY))


class Order:
	def __init__(self, time, ID, ticker, price_type, duration_type,
		share, side, price=0):
		self.time = time
		self.id = ID
		self.ticker = ticker
		self.price_type = price_type
		self.duration_type = duration_type
		self.price = price
		self.share = share
		self.side = side

	def Print(self):
		Pt = { MARKET: "MARKET", LIMIT: "LIMIT" }
		Dt = { ROD: "ROD", IOC: "IOC", FOK: "FOK" }
		St = { BUY: "BUY", SELL: "SELL" }
		print("-> Id: %d,  %s  %s  %s  %d  %s  %1.f" 
				% (self.id, self.ticker, Pt[self.price_type], Dt[self.duration_type], self.share, St[self.side], self.price))


class OrderBook:
	LOG = [] # for exchange to 
	def __init__(self, ticker, close=1000):
		# My ticker
		self.ticker = ticker
		# time variables
		self.clock = 0
		self.state = AUCTION
		self.ncat= OPEN_TIME # initialize 9am microsecond. 
		# If state now is AUCTION, ncat means next_call_auction_time, 
		# otherwise, ncat means previous call_auction_time

		# history variables
		self.benchmark = [close] # for 
		self.price_series = [close]
		# order book variables
		self.book = [{}, {}] # [bid, ask], price : vol
		self.id_book = [{}, {}] # [bid, ask], price : order_id
		self.market_order = deque()
		self.order_list = {} # id:order
		# handle moving average variables
		self.ma_5 = deque() # last five minutes obejct (time,price,volume)
		self.total_volume = 0
		self.total_dollar_volume = 0


	def Send(self, order):
		# print("check state")
		self.CheckTime(order.time)
		# print("check price...")
		if order.price_type == MARKET:
			p = self.LastPrice()
			if order.side == BUY:
				# why can't we use  order.price = self.benchmark[0]*1.1  ??
				order.price = max(p, max(self.book[BUY]) if self.book[BUY] else p, max(self.book[SELL]) if self.book[SELL] else p)
			if order.side == SELL:
				order.price = min(p, min(self.book[BUY]) if self.book[BUY] else p, min(self.book[SELL]) if self.book[SELL] else p)

		elif (order.price > self.benchmark[0]*1.1) or (order.price < self.benchmark[0]*0.9):
			# invalid order
			self.AddLog("*** 超過漲迭停限制 ***")
			return

		self.AddLog("Received OrderId %d." % (order.id))
		order.Print()
		if self.state == AUCTION:
			# check order type valid
			if order.price_type == LIMIT and order.duration_type == ROD:
				self.AddOrder(order)
			else:
				self.AddLog("Order %d failed! LIMIT ROD only during auction time." % (order.id))
				return
		else:
			if order.duration_type == FOK:
				if order.share > self.GetAvailability(order.price,order.side):
					return	
			# print("開始 fill ")
			leftover = self.Fill(order)	
			if order.duration_type == ROD and leftover:
				self.AddOrder(leftover)
				

	def AddOrder(self,order):
		if order.price_type == MARKET:
			# This occurs only when there is NO opposite order to match, so we hang the market order
			self.market_order.append(order.id)
		else:
			self.book[order.side].setdefault(order.price,0)
			self.book[order.side][order.price] += order.share
			self.id_book[order.side].setdefault(order.price, deque())
			self.id_book[order.side][order.price].append(order.id)
		
		self.order_list[order.id] = order
		self.AddLog("Time: %d. %s OrderId %d is added." % (self.clock, self.ticker, order.id))


	def DeleteOrder(self,ID):
		# assert(ID in self.order_list)
		order = self.order_list[ID]
		if order.price_type == MARKET:
			self.market_order.popleft()
		else:
			# remove vol=order.share at that price
			self.book[order.side][order.price] -= order.share
			if self.book[order.side][order.price] == 0:
				del self.book[order.side][order.price]
			# remove from id_book
			self.id_book[order.side][order.price].remove(ID)
		# remove from order_list 
		self.AddLog("Time: %d. %s OrderId %d is removed." % (self.clock, self.ticker, ID))
		del self.order_list[ID]


	def ChangeOrder(self, ID, change): # only limit order can change
		assert(change > 0)
		order = self.order_list[ID]
		if order.price_type == LIMIT:
			# remove vol=change at that price
			self.book[order.side][order.price] -= change
		# reduce vol=change of the order 
		self.order_list[ID].share -= change
		assert(self.order_list[ID].share > 0)
		self.AddLog("Time: %d. %s OrderId %d is changed." % (self.clock, self.ticker, ID))


	def Present(self):
		print('\n', "="*22, self.ticker , "="*22)
		print("   BID" + " "*40 + "ASK")
		for price in sorted(self.book[SELL],reverse=True):
			print(" "*30+str(price)+": "+str(self.book[SELL][price]), self.id_book[SELL][price]) 
		print('-'*55)
		for price in sorted(self.book[BUY],reverse=True):
			print(str(price) +" :  " +str(self.book[BUY][price]), self.id_book[BUY][price])
		print()
		print(" Market orders: ", list(self.market_order))
		print(" Last price: ", self.LastPrice())
		st = { AUCTION: "AUCTION", 
			   AUCTION_PLUS_5: "AUCTION_PLUS_5", 
			   TRADING: "TRADING"}
		print(" State: ", st[self.state])
		print('', "="*50, '\n')


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


	#============ private function =======================#
	def AddLog(self, msg): # Add text message through this function
		print(msg)


	def GetAvailability(self, price, side):
		volume = 0
		for p in sorted(self.book[side], reverse=(side==SELL)):
			if less_than_or_equal(p, price, side):
				volume += self.book[side][p]
			else:
				break
		return volume


	def Fill(self, order):

		pre_p = 0 # means pre-execution-price
		# Check market orders...
		if order.share > 0 and self.market_order and self.order_list[self.market_order[0]].side == opp(order.side):
			# match opposite market order!
			while order.share > 0 and self.market_order and less_than_or_equal(self.order_list[self.market_order[0]].price, order.price, order.side):
				mo = self.order_list[self.market_order[0]]
				if mo.price != pre_p and self.Check_Stab_Mech(mo.price):
					break
				else:
					pre_p = mo.price 
					q = min(mo.share, order.share)
					self.Execute(mo.id, mo.price, q) # in order_list
					self.ExecLog(order, mo.price, q) # not in order_list
					self.Acc_MA(mo.price, q)
					order.share -= q

		Prices = sorted(self.book[opp(order.side)], reverse=(order.side==SELL))
		i = 0
		pre_p = 0

		# print("Check limit orders...")
		while order.share > 0 and i < len(Prices) and less_than_or_equal(Prices[i], order.price, order.side):
			# print("At least one match except PSM")
			if Prices[i] != pre_p and self.Check_Stab_Mech(Prices[i]):
				break
			else:
				pre_p = Prices[i]
				ID = self.id_book[opp(order.side)][Prices[i]][0]
				q = min(self.order_list[ID].share, order.share)
				self.Execute(ID, Prices[i], q)
				self.ExecLog(order, Prices[i], q)
				self.Acc_MA(Prices[i], q)
				order.share -= q

			# if no order at this price level...
			if Prices[i] not in self.book[opp(order.side)]:
				i += 1
		
		if order.share == 0:
			return None
		else:
			return order


	def Acc_MA(self, price, volume):
		self.ma_5.append((self.clock, price, volume))
		self.total_volume += volume
		self.total_dollar_volume += price * volume


	def Check_Stab_Mech(self, price):

		# Update MA
		while self.ma_5 and self.ma_5[0][0] + 5*MIN >= self.clock:
			self.total_volume -= self.ma_5[0][2]
			self.total_dollar_volume -= self.ma_5[0][1] * self.ma_5[0][2]
			self.ma_5.popleft()

		# Determine smp
		if self.state == AUCTION_PLUS_5:
			smp = self.benchmark[-1]
		elif self.state == TRADING:
			if self.total_volume > 0:
				smp = self.total_dollar_volume / self.total_volume
			else:
				smp = self.LastPrice()
		# check +-3.5%
		if price > smp * 1.035 or price < smp * 0.965:
			# check more exception case...
			if ( self.clock + 5*MIN <= CLOSE_TIME ) :
				self.Start_Stab_Mech()
				return True
		# else
		return False
		

	def Start_Stab_Mech(self):
		self.AddLog("*** 價格穩定機制啟動 ***\n")
		# 1. Delete market order
		for ID in self.market_order.copy():
			self.DeleteOrder(ID)
		# 2. Change state to AUCTION, reset ncat
		self.state = AUCTION
		self.ncat = self.clock + 2*MIN 


	def CallAuction(self):
		# print(self.clock)
		self.AddLog("---- Call Auction ----")
		bid = self.book[BUY]
		ask = self.book[SELL]
		sortP = [sorted(self.book[BUY].keys(), reverse = True), sorted(self.book[SELL].keys())]
		# sortP[BUY] decreasing, sortP[SELL] increasing
		if (not bid) or (not ask):
			# one of them is empty
			return
		if sortP[BUY][0] < sortP[SELL][0]:
			# No order can match
			self.AddLog("End of Auction... No order can match.")
			return
		# if sortP[BUY][-1] > sortP[SELL][-1]:
		# 	price_range = [sortP[BUY][-1], sortP[SELL][-1]]

		# determine possible price range
		count_bid, count_ask = bid[sortP[BUY][0]], ask[sortP[SELL][0]]
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

		# Execute 
		for side in [BUY, SELL]:
			acc_vol = 0
			Prices = sortP[side].copy()
			i = 0
			while V > acc_vol and i < len(Prices):
			
				IDs = self.id_book[side][Prices[i]].copy()
				for ID in IDs:

					q = min(self.order_list[ID].share, V - acc_vol)
					self.Execute(ID, final_price, q)
					# Do not Acc_MA here!!
					acc_vol += q
				i += 1

		self.AddLog("End of Auction... \nFinal_price = %.1f, Total deal volume = %d\n" % (final_price, V))
		self.benchmark.append(final_price)


	def Execute(self, ID, price, volume):
		# write execution log, and delete ID from self.order_list
		# assert(ID in self.order_list)
		self.ExecLog(self.order_list[ID], price, volume)
		if volume == self.order_list[ID].share:
			self.DeleteOrder(ID)
		else:
			self.ChangeOrder(ID, volume)


	def ExecLog(self, order, price, volume): 
		# write execution log, 
		# call this function if order.id is not in self.order_list
		assert(volume > 0)

		if volume == order.share:
			msg = "full"
		else:
			msg = "partial"

		print("Time: %d. "%(self.clock) + "%s OrderId %d is %s fill @%.1f with volume %d" % (self.ticker, order.id, msg, price, volume))
		
		self.price_series.append(price)


	def CheckTime(self, update_time): # check and change state 

		assert(update_time >= self.clock) # time monotone
		self.clock = update_time

		if update_time < OPEN_TIME or update_time > CLOSE_TIME:
			self.state = AUCTION

		else:
			if update_time < self.ncat: 
				next_state = AUCTION
			elif (self.ncat + 5*MIN) >= update_time >= self.ncat : 
				next_state = AUCTION_PLUS_5
			else:
				next_state = TRADING

			if (next_state == AUCTION_PLUS_5 or next_state == TRADING) and self.state==AUCTION:
				self.clock = self.ncat
				self.CallAuction()
				self.clock = update_time
				# clear MA_5 data
				self.ma_5 = deque()
				self.total_dollar_volume = 0
				self.total_volume = 0

			self.state = next_state
			


class Exchange:
	def __init__(self):
		self.open = (8*60+30)*60*Ms
		self.close = (13*60+30)*60*Ms
		self.orderbook = {}
		# self.close_price = {}

	def OpenBook(self,ticker,price):
		self.orderbook[ticker] = OrderBook(ticker, price)

	def Send(self,order):
		# print(type(order.time))
		self.orderbook.setdefault(order.ticker,OrderBook(order.ticker))
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












