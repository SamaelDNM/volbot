###### volbot

# Overview

This bot creates volume for a specified symbol on the Coinbene exchange using the Coinbene API. This is my first side project as I have recently gotten interested in software development as well as cryptocurrency, so I decided to give it a go. This is just a template for interacting with the Coinbene API and was created only for the sole purpose of generating volume. It is not intended to generate any profit, and I am not promoting it for such a use as well. I had fun learning to deal with RESTFUL api, and I hope it is of some help to people that want to try as well!

# Implementation

The bot itself uses very simple Python libraries and uses the [Coinbene API](). There is a restriction imposed, where the user inputs a time/amount/both restriction, and at which point, the bot will come to a stop. To use the bot, you must have an account at Coinbene and generate an APIID as well as a secret key.

# Usage

$python vol_bot.py

After the command, there will be prompts for tickers involved in the trade, restriction type, and restriction length, amount, or both.

# License

MIT
