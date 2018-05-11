#!/usr/bin/env python

import requests
from lxml import html
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import re
from collections import namedtuple
import argparse

# TODO error handling

#---fetch-----------------------------------------------------------------------

HistoricalData = namedtuple('HistoricalData', ['identifier', 'name', 'code', 'currency', 'rows'])

def generate_url(identifier, start, end):
    start_param = start.replace('-','')
    end_param = end.replace('-','')
    return f'https://coinmarketcap.com/currencies/{identifier}/historical-data/?start={start_param}&end={end_param}'

def parse_number(s):
    if s == '-':
        return None
    else:
        return Decimal(s.replace(',',''))

def parse_rows(document):
    def normalize_header_name(name):
        return name.lower().translate(str.maketrans(' ', '_'))
    table = document.xpath('//*[@id="historical-data"]//table')[0]
    headers = [normalize_header_name(th.text) for th in table.xpath('//th')]
    Row = namedtuple('Row', headers)
    for tr in table.xpath('//tr[td]'):
        fields = [td.text for td in tr.xpath('td')]
        fields[0] = datetime.strptime(fields[0], '%b %d, %Y').date() # TODO force %b to be locale US_en - https://stackoverflow.com/questions/18593661/how-do-i-strftime-a-date-object-in-a-different-locale
        fields[1:] = [parse_number(field) for field in fields[1:]]
        yield Row(*fields)

def get(identifier, start, end):
    url = generate_url(identifier, start, end)
    page = requests.get(url)
    document = html.fromstring(page.content)

    title = document.find('.//title').text
    m = re.match('(?P<name>.*?) \((?P<code>.*?)\)', title)
    name = m.group('name')
    code = m.group('code')

    currency = 'USD'
    rows = sorted(parse_rows(document), key=lambda item: item.date)

    return HistoricalData(identifier, name, code, currency, rows)

#---print-----------------------------------------------------------------------

def print_pricedb(data):
    for row in data.rows:
        date = str(row.date).translate(str.maketrans('-','/'))
        time = '00:00:00'
        print(f"P {date} {time} {data.code} {data.currency} {row.open}")

#---read-dates-from-file--------------------------------------------------------

# TODO remove unused code here

def dates_following(filename):
    start = last_price_date(filename) + timedelta(days=1)
    end = datetime.now().date()
    return (start, end)

def last_price_date(filename):
    return sorted(price_dates(filename))[-1]

def price_dates(filename):
    with open(filename, 'r') as f:
        for line in f.read().splitlines():
            match = re.match(r"^P (\d{4}).(\d\d).(\d\d) ", line)
            if (match):
                date = datetime.strptime(match.expand("\g<1>\g<2>\g<3>"), '%Y%m%d').date()
                yield date

# d1, d2 = dates_following("ripple.pricedb")
# print(str(d1))
# print(str(d2))

# print(str(last_price_date("ripple.pricedb")))

#-------------------------------------------------------------------------------

def valid_date_str(s):
    if s == 'today':
        return today_str()
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def today_str():
    return str(datetime.now().date())

parser = argparse.ArgumentParser(description='Fetch historical data from CoinMarketCap.com.')

parser.add_argument('identifier', metavar='ID', type=str,
                    help='currency or coin identifier (example: bitcoin)')

parser.add_argument('--start', dest='start', type=valid_date_str,
                    default='2009-01-03',
                    help='start date (default: 2009-01-03)')

parser.add_argument('--end', dest='end', type=valid_date_str,
                    default=today_str(),
                    help='end date (default: today)')

args = parser.parse_args()

# TODO add argument --start-after PRICEDB
# TODO add argument --full, to print full info instead of pricedb

# print(args.identifier)
# print(args.start)
# print(args.end)

d = get(args.identifier, args.start, args.end)
print_pricedb(d)

