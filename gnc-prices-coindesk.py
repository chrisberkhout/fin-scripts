#!/usr/bin/env python

# Fetch historical prices from CoinDesk for Bitcoin
# and add them to a GnuCash file.

# CoinDesk Bitcion Price Index
# http://www.coindesk.com/api/

import piecash
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from urllib import request
import json

# config

book_file   = '/home/chris/Documents/Finances/Accounts.gnucash'
# book_file   = '/home/chris/Documents/Finances/SCRATCH.gnucash'
source      = 'CoinDesk Bitcoin Price Index'
currencies  = { 'AUD', 'EUR' }
start_date  = date(datetime.utcnow().date().year - 1, 1, 1)


# open book

book = piecash.open_book(book_file, readonly=False)


# determine uncovered dates per currency

def prices_for(book, currency_mnemonic, source):
    commodity = book.currencies(mnemonic='XBT')
    currency = book.currencies(mnemonic=currency_mnemonic)
    return {
        x for x in book.prices if
            x.currency == currency
            and x.commodity == commodity
            and x.source == source
    }

dates_covered = dict()
for currency in currencies:
    dates_covered[currency] = {
        x.date.astimezone(timezone.utc).date() for x in
            prices_for(book, currency, source)
    }

date_today = datetime.utcnow().date()
days_since_start = (date_today - start_date).days

dates_to_cover = {
    start_date + timedelta(x) for x in range(days_since_start + 1)
}

dates_uncovered = dict()
for currency in currencies:
    dates_uncovered[currency] = dates_to_cover - dates_covered[currency]


# get data, read data, add to book if missing

for currency_mnemonic in currencies:

    commodity = book.currencies(mnemonic='XBT')
    currency = book.currencies(mnemonic=currency_mnemonic)

    base_url  = "https://api.coindesk.com/v1/bpi/historical/close.json?index=USD"
    start = str(start_date)
    end = str(date_today-timedelta(1))
    source_url  = "%s&currency=%s&start=%s&end=%s" % (base_url, currency_mnemonic, start, end)

    url = request.urlopen(source_url)
    data = json.loads(url.read().decode('utf-8'))
    url.close()

    for date_str, rate_str in data['bpi'].items():
        d = date(*[ int(x) for x in date_str.split('-') ])
        rate = Decimal(str(rate_str))
        if (d in dates_uncovered[currency_mnemonic]):
            dt = datetime(d.year, d.month, d.day, 13, 0, 0, 0, timezone.utc)
            price = piecash.core.commodity.Price(commodity, currency, dt, rate, 'last', source)
            book.add(price)
            print("added %s" % (str(price)))


# save and finish

if (book.is_saved):
    print("No changes from %s" % (source))
    book.cancel() # this still seems to create a backup file
else:
    book.save()

