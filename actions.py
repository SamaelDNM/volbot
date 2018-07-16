# -*- coding: utf-8 -*-

import sys
from utils import *

############################################################

# BASIC ACTIONS

# get ticker info
def get_ticker(symbol):
	url = URL_MARKET + 'ticker'
	params = {'symbol': symbol}
	response = http_request(url, params, 'GET')
	return response

# get list of bids and asks
def get_orderbook(symbol, depth = 10):
	url = URL_MARKET + 'orderbook'
	params = {'symbol': symbol, 'depth': depth}
	response = http_request(url, params, 'GET')
	return response

# get listed trades 
def get_trades(symbol, size = 10):
	url = URL_MARKET + 'trades'
	params = {'symbol': symbol, 'size': size}
	response = http_request(url, params, 'GET')
	return response

# check balances of tickers/coins for the account
def check_balance(data_dict):
	url = URL_TRADE + 'balance'
	sign = create_sign(**data_dict)
	del data_dict['secret']
	data_dict['sign'] = sign
	data_dict = json.dumps(data_dict)
	response  = http_request(url, data_dict, 'POST')
	return response

# place a bid/ask order
def place_order(order, order_type):
	url = URL_TRADE + 'order/place'
	price = order[0]
	quantity = float(order[1])

	if order_type == 'bid':
		# enter ticker for second argument
		if enough_balance(order, ''):
			data_dict = {
				'apiid': apiid, 
				'price': float_to_str(price),
				'quantity': quantity,
				'symbol': symbol,
				'type': 'buy-limit',
				'timestamp': get_timestamp(),
				'secret': secret}
			sign = create_sign(**data_dict)
			del data_dict['secret']
			data_dict['sign'] = sign

			data_dict = json.dumps(data_dict)
			response = http_request(url, data_dict, 'POST')

			if validate_order(response, sign, order_type):
				print('Price', price, '    Quantity:', quantity, '     ' + order_type.upper() + ' Trade: Success!')
				return True
			
	elif order_type == 'ask':

		# enter ticker for second argument
		if enough_balance(order, ''):
			data_dict = {
				'apiid': apiid, 
				'price': float_to_str(price),
				'quantity': quantity,
				'symbol': symbol,
				'type': 'sell-limit',
				'timestamp': get_timestamp(),
				'secret': secret}
			sign = create_sign(**data_dict)
			del data_dict['secret']
			data_dict['sign'] = sign

			data_dict = json.dumps(data_dict)
			response = http_request(url, data_dict, 'POST')

			if validate_order(response, sign, order_type):
				print('Price', price, '    Quantity:', quantity, '     ' + order_type.upper() + ' Trade: Success!')
				return True

	# separate repsonse for order that went through and order that didn't go through
	print('Price', price, '    Quantity:', quantity, '     ' + order_type.upper() + ' Trade: Failure')
	return False

# check the placed order status
def check_order_status(data_dict):
	url = URL_TRADE + 'order/info'
	sign = create_sign(**data_dict)
	del data_dict['secret']
	data_dict['sign'] = sign
	data_dict = json.dumps(data_dict)
	response = http_request(url, data_dict, 'POST')
	return response

# cancel a placed order
def cancel_order(data_dict):
	url = URL_TRADE + 'order/cancel'
	sign = create_sign(**data_dict)
	del data_dict['secret']
	data_dict['sign'] = sign
	data_dict = json.dumps(data_dict)
	response = http_request(url, data_dict, 'POST')
	return response

# check for all open orders
def check_open_orders(data_dict):
	url = URL_TRADE + 'order/open-orders'
	sign = create_sign(**data_dict)
	del data_dict['secret']
	data_dict['sign'] = sign
	data_dict = json.dumps(data_dict)
	response = http_request(url, data_dict, 'POST')
	return response

############################################################

# HELPER FUNCTIONS

# check there was no error in the request (syntactically, which gives a status error)
# check order was filled, else cancel until successful
# @return: True if no error, False if either error above
def validate_order(response, sign, order_type):
	if response['status'] == 'error':
		return False

	if order_type == 'bid':
		orderid = response['orderid']
		data_dict = {'apiid': apiid,
					 'orderid': orderid,
					 'timestamp': get_timestamp(),
					 'secret': secret}
		response = check_order_status(data_dict)

		order_status = (response['order'])['orderstatus']

		if order_status == 'unfilled' or order_status == 'partialFilled':
			data_dict = {'apiid': apiid,
					     'orderid': orderid,
						 'timestamp': get_timestamp(),
						 'secret': secret}

			while True:
				response = cancel_order(data_dict)
				if response['status'] == 'ok' and response['orderid'] == orderid:
					break
			return False

	return True

# check if there is enough balance of a specified ticker to satisfy the order
def enough_balance(order, ticker):
	data_dict = {'apiid': apiid,
				 'secret': secret,
				 'timestamp': get_timestamp(),
				 'account': 'exchange'}

	response = check_balance(data_dict)
	balances = response['balance']

	amount_available = 0

	# find balance of desired coin
	for i in range(len(balances)):
		if balances[i]['asset'] == ticker:
			amount_available = int(float(balances[i]['available']))
			break

	if amount_available == 0:
		print('Need more {}s!'.format(ticker))
		sys.exit(1)
	elif order[1] <= amount_available:
		return True
	else:
		return False

# gets the balances of input tickers
def get_balances(tickers):
	balances = []

	for ticker in tickers:
		data_dict = {'apiid': apiid,
				 'secret': secret,
				 'timestamp': get_timestamp(),
				 'account': 'exchange'}

		# make sure there is a complete response
		while True:
			response = check_balance(data_dict)
			if response['status'] == 'ok':
				break

		assets = response['balance']

		for i in range(len(assets)):
			if assets[i]['asset'] == ticker:
				balances.append(float(assets[i]['available']))
				break

	return balances

# gets the volume of specified symbol
def get_volume(symbol):
	while True:
		response = get_ticker(symbol)
		if response['status'] == 'ok':
			break

	info = response['ticker'][0]

	return float(info['24hrVol'])

############################################################

# test methods
if __name__ == '__main__':
	print(get_ticker(symbol))
