#naming convention
#Captial 
from collections import deque
import time
AUCTION, AUCTION_PLUS_5, TRADING = 1, 2, 3
OPEN_TIME = 9*60*60*1e6
MIN = 60*1e6
LIMIT, MARKET = 1, 2
ROD, IOC, FOK= 1, 2, 3

class Order:
	def __init__(self,time,ID,ticker,price_type,duration_type,
		price,share,side):
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
	def __init__(self,close):
		self.state = AUCTION
		self.benchmark = close # for 
		self.ncat= OPEN_TIME#initialize 9am microsecond
		self.bid = {}
		self.ask = {}
		self.bid_id = {}# price:two list
		self.ask_id = {}
		self.order_list = {} #id:order
		self.price_series = [50]
		self.ma_5 = deque()#last five minutes obejct (time,price,volume)
		self.total_volume = 0
		self.total_dollar_volume = 0

	def Send
	def AddOrder(self,order):
		if order.side == "BUY":
			if order.price not in order.bid:
				order.bid[price] = order.share
				if order.price_type == MARKET:
					order.bid_id.append(deque([order.id]))
					order.bid_id.append(deque())
				else:
					order.bid_id.append(deque()) 
					order.bid_id.append(deque([order.id]))
			else:
				order.bid[price] += order.share
				if order.price_type == MARKET:
					order.bid_id[0].append(order.id)
				else:
					order.bid_id[1].append(order.id)
		else:
			if order.price not in order.ask:
				order.ask[price] = order.share
				if order.price_type == MARKET:
					order.ask_id.append(deque([order.id]))
					order.ask_id.append(deque())
				else:
					order.ask_id.append(deque()) 
					order.ask_id.append(deque([order.id]))
			else:
				order.ask[price] += order.share
				if order.price_type == MARKET:
					order.ask_id[0].append(order.id)
				else:
					order.ask_id[1].append(order.id)	
		self.order_list[order.id] = order


	def DeleteOrder(self, ID):
		order = self.order_list[ID]
		price_type = order.price_type
		price = order.price
		share = order.share
		if order.side == "BUY":
			self.bid[price] -= share
			if self.bid[price] == 0:
				del self.bid[price]
				del self.bid_id[price]
			else:
				if price_type == MARKET:
					order.bid_id[price][0].remove(ID)
				else: order.bid_id[price][1].remove(ID)
		else:
			self.ask[price] -= share
			if self.ask[price] == 0:
				del self.ask[price]
				del self.ask_id[price]
			else:
				if price_type == MARKET:
					order.ask_id[price][0].remove(ID)
				else: order.ask_id[price][1].remove(ID)
		self.order_list.remove(ID)
	def ChangeOrder(self, ID, change):
		"""specially for quantity change
		if price change --> DeleteOrder + AddOrder
		"""
		order = self.order_list[ID]
		changing = change - order.share
		if order.side == "BUY":
			self.bid[order.price] += changing
			order.quantity += changing
		else:
			self.ask[order.price] += changing
			order.quantity += changing
	def Present():

	def GetBestPrice():

	def GetAvailability():

	def Fill(self, order): # return log list

		try: 

			if order.side == "BUY":

				P = sorted(ask) # search from lowest price
				i = 0

				while self.order_list[order.id].share > 0 and i < len(P) and order.price >= P[i]:
					# Claim: at least one match except PSM
					if self.order_list[order.id].share >= ask[P[i]]:
						# Turnover all order at price P[i]
						for Id in ask_id[P[i]][0] + ask_id[P[i]][1]:
							self.Turnover(Id, P[i], self.order_list[Id].share) # counter part order (full fill)
							self.Turnover(order.id, P[i], ask[P[i]]) # current order (partial fill)
						
						i += 1 # next price

					else:
						# Claim: Can fill current order except PSM
						# First turnover market order, then limited order
						tmp = self.order_list[order.id].share

						for j in [0, 1]:
							while self.order_list[order.id].share > 0 and ask_id[P[i]][j]:

								Id = ask_id[P[i]][j][0] # lowest price id

								if self.order_list[order.id].share >= self.order_list[Id].share:
									self.Turnover(Id, P[i], self.order_list[Id].share) # counter part order (full fill)
								else:
									self.Turnover(Id, P[i], self.order_list[order.id].share) # counter part order (partial fill)
						
						self.Turnover(order.id, P[i], tmp) # current order (full fill)

			if order.side == "SELL":
				return None

		except:

			print("Price Stabilization Mechanism raised!")

		finally:

				if self.order_list[order.id].share > 0:
					return self.order_list[order.id]
				else:
					return None

	def Turnover(self, orderId, price, volume):

		assert(volume > 0)
		order = self.order_list[orderId]

		# Update moveing average
		while ma_5 and ma_5[0][0]+5*MIN >= order.time:
			self.total_volume -= ma_5[0][2]
			self.total_dollar_volume -= ma_5[0][1] * ma[0][2]
			ma_5.popleft()

		# check price stabilization mechanism
		if state == TRADING or AUCTION_PLUS_5:

			if state == TRADING:
				stab_mech_price = self.total_dollar_volume / self.total_volume if self.total_volume != 0 else price_series[-1]
			elif state == AUCTION_PLUS_5:
				stab_mech_price = benchmark

			if price > stab_mech_price * 1.035 or price < stab_mech_price * 0.965:
				# Exception!!!
				raise Exception("Price Stabilization Mechanism.")

		# add new trade into MA
		ma_5.append((self.order_list[orderId].time, price, volume))
		self.total_volume += volume
		self.total_dollar_volume += price*volume

		#add log 
		'''
		TODO
		'''
		
		# if partially fill, change order
		if volume < order.share:

			if order.side == "BUY":
				self.bid[order.price] -= volume
			elif order.side == "SELL":
				self.ask[order.price] -= volume

			self.order_list[orderId].share -= volume

		else:
			# if full fill, delete order
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
			
			del self.order_list[orderId] # delete order_list id 


	def CallAuction():
		bid = self.bid
		ask = self.ask
		bid_dict = sorted(bid, reverse = True)
		ask_dict = sorted(ask)

		count_bid, count_ask = bid[bid_dict[0]], ask[ask_dict[0]]
		if (not bid_dict) or (not ask_dict):
			self.benchmark.append(benchmark[-1])
			return
		if bid_dict[0] < ask_dict[0]:
			self.benchmark.append(benchmark[-1])
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

		if volume_ask > volume_bid:
			# bid fully filled
			for price in bid_dict:
				if price >= final_price:
					for ID in self.bid_id[price][1]:
						self.Turnover(ID, price, self.order_list[ID].share)
			# ask partially filled
			volume = volume_bid
			for price in ask_dict:
				# the part is still fully filled
				if ask[price] <= volume:
					volume -= ask[price]
					for ID in self.ask_id[price][1]:
						self.Turnover(ID, price, self.order_list[ID].share)
				# partial filled
				else:
					for ID in self.ask_id[price][1]:
						if self.order_list[ID].share < volume:
							self.Turnover(ID, price, self.order_list[ID].share)
							volume -= self.order_list[ID].share
						else:
							self.Turnover(ID, price, volume)
							return
		elif volume_bid > volume_ask:
			for price in ask_dict:
				if price <= final_price:
					for ID in self.ask_id[price][1]:
						self.Turnover(ID, price, self.order_list[ID].share)
			volume = volume_ask
			for price in bid_dict:
				if bid[price] <= volume:
					volume -= bid[price]
					for ID in self.bid_id[price][1]:
						self.Turnover(ID, price, self.order_list[ID].share)
				else:
					for ID in self.ask_id[price][1]:
						if self.order_list[ID].share < volume:
							self.Turnover(ID, price, self.order_list[ID].share)
							volume -= self.order_list[ID].share
						else:
							self.Turnover(ID, price, volume)
							return
		else:
			for price in bid_dict:
				if price >= final_price:
					for ID in self.bid_id[price][1]:
						self.Turnover(ID, price, self.order_list[ID].share)
			for price in ask_dict:
				if price <= final_price:
					for ID in self.ask_id[price][1]:
						self.Turnover(ID, price, self.order_list[ID].share)
	def CheckTime():#check and change state 

	


class Exchange:
	def __init__():

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
	time = 0
	ID = 0
	while True:
		I = input().strip()
		if I == "O":
			info = input().strip().split()
			if len(info)==6:
				order = 
			if len(info)==5:
		if I == "S":


