#!/usr/bin/env python

# Fetch historical prices from the European Central Bank.
#
# ECB Euro foreign exchange reference rates
# https://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html

from datetime import datetime, timedelta
from urllib import request
from xml.etree import ElementTree
from decimal import Decimal
import re
import sys
import argparse

#---fetch-----------------------------------------------------------------------

def get(currency, start, end):
    almost_90_days_ago = str(datetime.now().date() - timedelta(days=85))
    if start > almost_90_days_ago:
        source_url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml' # last 90 days
    else:
        source_url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml' # since 1999

    url = request.urlopen(source_url)
    data = url.read()
    url.close()

    all_rows = parse(currency, data)
    selected = [ (d, r) for d, r in all_rows if d >= start and d <= end ]

    return list(reversed(selected))

def parse(currency, data):
    root = ElementTree.fromstring(data)
    namespaces = {
        'default': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref',
        'gesmes': 'http://www.gesmes.org/xml/2002-08-01'
    }
    for day in root.find('default:Cube', namespaces):
        date = day.attrib['time']
        rate_xpath = f"./*[@currency='{currency}']"
        rate = Decimal(day.find(rate_xpath).attrib['rate'])
        yield (date, rate)

#---print-----------------------------------------------------------------------

def print_pricedb(counter_currency, data):
    base_currency = 'EUR'
    for date, rate in data:
        date = str(date).translate(str.maketrans('-','/'))
        time = '00:00:00'
        print(f"P {date} {time} {base_currency} {counter_currency} {rate}")

def print_csv(counter_currency, data):
    base_currency = 'EUR'
    if not data:
        print("WARNING: no price data", file=sys.stderr)
    else:
        print(f"date,{base_currency},{counter_currency}")
        for date, rate in data:
            print(",".join([date, "1.0000", str(rate)]))

#---read-dates-from-ledger-file-------------------------------------------------

def price_dates(filename):
    with open(filename, 'r') as f:
        for line in f.read().splitlines():
            match = re.match(r"^P (\d{4}).(\d\d).(\d\d) ", line)
            if (match):
                date = datetime.strptime(match.expand("\g<1>\g<2>\g<3>"), '%Y%m%d').date()
                yield date

def last_price_date(filename):
    return sorted(price_dates(filename))[-1]

#---argument-parsing------------------------------------------------------------

def valid_date(s):
    if s == 'today':
        return today()
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def today():
    return str(datetime.now().date())

def start_after(filename):
    return str(last_price_date(filename) + timedelta(days=1))

def expected_currency(s):
    expected = ['USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF', 'PLN', 'RON',
                'SEK', 'CHF', 'ISK', 'NOK', 'HRK', 'RUB', 'TRY', 'AUD', 'BRL',
                'CAD', 'CNY', 'HKD', 'IDR', 'ILS', 'INR', 'KRW', 'MXN', 'MYR',
                'NZD', 'PHP', 'SGD', 'THB', 'ZAR']
    if s in expected:
        return s
    else:
        msg = f"Not an expected currency: '{s}'."
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='Fetch historical price data from the European Central Bank.')

parser.add_argument('currency', metavar='CURRENCY', type=expected_currency,
                    help='counter currency to show against base of 1 EUR (example: USD)')

parser.add_argument('--start', dest='start', type=valid_date,
                    default='1999-01-01',
                    help='start date (default: 1999-01-01)')

parser.add_argument('--start-after', dest='start', metavar='FILE', type=start_after,
                    help='Ledger file with prices to start after')

parser.add_argument('--end', dest='end', type=valid_date,
                    default=today(),
                    help='end date (default: today)')

parser.add_argument('--csv', dest='csv', action='store_true',
                    help='print data as csv (instead of Ledger pricedb format)')

#---run-------------------------------------------------------------------------

args = parser.parse_args()

data = get(args.currency, args.start, args.end)

if args.csv:
    print_csv(args.currency, data)
else:
    print_pricedb(args.currency, data)
