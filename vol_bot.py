# -*- coding: utf-8 -*-

import time
import sys
import random
import json
import numpy as np
from decimal import Decimal
from utils import *
from actions import *

"""
General Notes: ask = sell, bid = buy

@Input Params: 
- type of restriction (time limit or number of coins)
- how many coins, time, or both depending on restriction type

"""

def round_two_decimals(num):
	dec = Decimal(num)
	return float(round(dec, 2))

def sell_and_buy_orders(bids, asks, amount):

	bid_price = bids[0]['price']
	ask_price = asks[0]['price']
	num_bids = int(round((ask_price - bid_price)*1e8)) - 1
	inc = 1e-08

	print('Price range: ' + str(bid_price) + ' to ' + str(ask_price))

	# the increment must be calculated separately to match the precision of price
	possible_sell_prices = np.linspace(bid_price+inc, bid_price+inc+(inc*num_bids), num_bids, endpoint = False)


	if len(possible_sell_prices) == 0:
		place_order([bids[0]['price'], bids[0]['quantity']], 'ask')
		return False

	else:
		random_index = random.randint(0, len(possible_sell_prices)-1)
		random_price = Decimal(possible_sell_prices[random_index])
		random_price_adj = float(round(random_price, 10))
		print(random_price_adj)

		if place_order([random_price_adj, amount], 'ask'):
			if place_order([random_price_adj, amount], 'bid'):
				return True
	return False

# stagger trades in random intervals
def stagger():
	wait_time = random.randint(5, 25)
	print('Wait:', wait_time, ' seconds.')
	time.sleep(wait_time)

# check if time elapsed has passed time_limit
# exit program if so
def check_time_limit(start_time, time_limit):
	time_elapsed = time.time()-start_time
	if time_elapsed > time_limit:
		print(str(float(time_elapsed/60)) + ' minutes have passed.')
		return False
	return True

def successful_trade(response, restriction_type, limit):
	print('------------------------------------------------------------------')
	orderbook = response['orderbook']
	bids = orderbook['bids']
	asks = orderbook['asks']
				
	# trades between 5000 and 15000 in increments of 25
	# change this for min/max amount of coins at any given trade
	amount_to_exchange = random.randint(50, 3001) * 25
	if restriction_type == 'coin' or restriction_type == 'both':
		amount_to_exchange = min(amount_to_exchange, round_two_decimals(limit))
	
	if amount_to_exchange == 0:
		trade = False
	else:
		print('Amount_to_exchange:', amount_to_exchange)
			
		# get combination of bids and asks that trade same volume/quantity
		trade = sell_and_buy_orders(bids, asks, amount_to_exchange)
	return trade, amount_to_exchange

def run_trades(symbol, restriction_type, limit):
	if restriction_type == 'coin':
		total_amount = limit
		while limit > 0:
			response = get_orderbook(symbol, 5)
			
			# # get combination of bids and asks that trade same volume/quantity
			trade, amount_to_exchange = successful_trade(response, restriction_type, limit)
			if trade:
				limit -= amount_to_exchange
				print('!!!!!!!!!!!!!!!!!')
				print(str(total_amount-limit) + ' volume generated!')
				print(str(limit) + ' coins to go!')
				print('!!!!!!!!!!!!!!!!!')
			
			stagger()

		return total_amount

	elif restriction_type == 'time':
		amount_traded = 0

		start_time = time.time()
		while check_time_limit(start_time, limit):
			response = get_orderbook(symbol, 5)

			# # get combination of bids and asks that trade same volume/quantity
			trade, amount_to_exchange = successful_trade(response, restriction_type, limit)
			if trade:
				amount_traded += amount_to_exchange
				print('!!!!!!!!!!!!!!!!!')
				print(str(amount_traded) + ' volume generated!')
				print(str((limit - (time.time()-start_time))/60) + ' minutes left!')
				print('!!!!!!!!!!!!!!!!!')

			stagger()

		return amount_traded

	else:
		time_to_trade = limit[0]
		amount_to_trade = limit[1]

		amount_traded = 0

		#five_min_counter = 1
		start_time = time.time()
		while check_time_limit(start_time, time_to_trade):

			temp_start = time.time()
			five_min_limit = amount_to_trade / (time_to_trade/300)
			while check_time_limit(temp_start, 300):
				response = get_orderbook(symbol, 5)
				trade, amount_to_exchange = successful_trade(response, restriction_type, five_min_limit)
				
				# if the 5 minute amount limit is finished, rest
				if amount_to_exchange == 0:
					if (time.time()-temp_start) < 300:
						time.sleep(300-(time.time()-temp_start))
					print('\nWaiting until 5 minutes zzzzz\n')
					break

				if trade:
					amount_traded += amount_to_exchange
					five_min_limit -= amount_to_exchange
					print('!!!!!!!!!!!!!!!!!')
					print(str(amount_traded) + ' volume generated!')
					print(str((time_to_trade - (time.time()-start_time))/60) + ' minutes left!')
					print('!!!!!!!!!!!!!!!!!')
				
				stagger()

		return amount_traded

if __name__ == '__main__':

	# get the two tickers for trading and create trade symbol
	tickers = []
	tickers.append(input('\nEnter token ticker you want to trade: ').upper())
	tickers.append(input('\nEnter other token/coin ticker you want to trade: ').upper())
	symbol = tickers[0].lower() + tickers[1].lower()

	# get restriction type and starting statistics
	restriction_type = input('\nEnter restriction type (time/coin/both): ').lower()
	start_balances = get_balances(tickers)
	start_volume = get_volume(symbol)

	if restriction_type == 'time':
		time_limit = int(input('\nEnter total duration to run bot (in hours): ')) * 3600
		amount_traded = run_trades(symbol, restriction_type, time_limit)


	elif restriction_type == 'coin':
		amount_limit = int(input('\nEnter total volume you would like to generate: '))
		amount_traded = run_trades(symbol, restriction_type, amount_limit)

	# trades the amount or less than the amount specified (will never exceed)
	elif restriction_type == 'both':
		time_limit = int(input('\nEnter total duration to run bot (in hours): ')) * 3600
		amount_limit = int(input('\nEnter total volume you would like to generate: '))
		amount_traded = run_trades(symbol, restriction_type, [time_limit, amount_limit])

	else:
		print('\nInvalid input. Please enter an option between "time", "coin", and "both".\n')
		sys.exit(1)

	# get ending stats
	end_balances = get_balances(tickers)
	end_volume = get_volume(symbol)

	# print results
	print('------------------------------------------------------------------\n')
	print(str(amount_traded) + ' volume generated in total.')
	print('Starting balances:\n{}: {}\n{}: {}\n'.format(tickers[0], start_balances[0], tickers[1], start_balances[1]))
	print('Final balances:\n{}: {}\n{}: {}\n'.format(tickers[0], end_balances[0], tickers[1], end_balances[1]))
	print('Start volume: {}, End volume: {}\n'.format(start_volume, end_volume))


