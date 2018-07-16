# -*- coding: utf-8 -*-

import time
import hashlib
import requests
import json
import decimal
import sys

symbol = ''

# authentication info from Coinbene
apiid = ''
secret = ''

# use GET requests for this
URL_MARKET = 'http://api.coinbene.com/v1/market/'

# use POST requests for this
URL_TRADE = 'http://api.coinbene.com/v1/trade/'

# to satisfy API formatting requirements
headers = {'content-type': 'application/json;charset-utf-8', 
		   'Connection': 'keep-alive'}

# provides decimal representation of float up to most significant digit
# @return: string rep of float
def float_to_str(f_num):
	contxt = decimal.Context()
	contxt.prec = 20

	dec = contxt.create_decimal(repr(f_num))
	return format(dec, 'f')

# @return: epoch time in milliseconds converted to timestamp
def get_timestamp():
	return int(round(time.time() * 1000))

# creates a signature of all info
# @return: sign 
def create_sign(**kwargs):

	sign_strings = []
	for key, val in kwargs.items():
		sign_strings.append('{}={}'.format(key, val))
	sign_strings.sort()
	sign_fullstr = '&'.join(sign_strings)
	sign = sign_fullstr.upper()

	encoded_sign = hashlib.md5(sign.encode('utf-8')).hexdigest()
	return encoded_sign	

# sends a GET/POST request to API
# @return: response in json format
def http_request(url, params, req_type):
	try:
		if req_type == 'GET':
			r = requests.get(url = url, params = params, headers = headers)
		else:
			r = requests.post(url = url, data = params, headers = headers)

	except requests.exceptions.ConnectionError as e:
		print('Request failed:', e)
	else:
		if r.status_code == 200:
			return json.loads(r.text)
		else:
			print(r.status_code, r.reason)
			return None

