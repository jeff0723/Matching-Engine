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