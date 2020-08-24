AUCTION = 1
AUCTION_PLUS_5 = 2
TRADING = 3
OPEN_TIME = 9*60*60*1e6
MIN = 60*1e6
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


class OrderBooK:
	LOG = []#for exchange to 
	AUCTION = 1
	AUCTION_PLUS_5 = 2
	TRADING = 3
	MIN = 
	def __init__(self,close):
		self.state = AUCTION
		self.benchmark = close # for 
		self.NCAT = OPEN_TIME#initialize 9am microsecond
		self.bid = {}
		self.ask = {}
		self.bid_id = {}# price:two list
		self.ask_id = {}
		self.price_series = []
		self.MA_5 = []#last five minutes

	def AddOrder():

	def DeleteOrder():

	def ChangeOrder():

	def Present():

	def GetBestPrice():

	def GetAvailability():

	def fill():#return log list

	def turnover():

	def call_auction():

	def check_time():#check and change state 

	


class Exchange:
	def __init__():

	def process():
		input 
		out = []

	def Send(): #return log
		log = OrderBooK.fill()
	def Change():#return log

	def __update_time():

	def __fill():#return order

	def __turnover():

	def __call_auction():



