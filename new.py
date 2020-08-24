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
			if order.price not in self.bid:
				self.bid[order.price] = order.share
				self.bid_id[order.price] = [order.id]
			else:
				self.bid[order.price] += order.share
				self.bid_id[order.price].append(order.id)
		if order.side == "SELL":
			if order.price not in self.ask:
				self.ask[order.price] = order.share
				self.ask_id[order.price] = [order.id]
			else:
				self.ask[order.price] += order.share
				self.ask_id[order.price].append(order.id)


	def DeleteOrder():

	def ChangeOrder():

	def Present():

	def GetBestPrice():

	def GetAvailability():

	def Fill():#return log list

	def Turnover():

	def CallAuction():

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


