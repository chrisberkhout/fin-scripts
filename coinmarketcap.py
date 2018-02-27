#!/usr/bin/env python

import requests
from lxml import html
from datetime import datetime
from decimal import Decimal
import re
from collections import namedtuple

# TODO read last from ledger file to request correct range
# TODO error handling

def generate_url(identifier, start, end):
    start_param = start.replace('-','')
    end_param = end.replace('-','')
    return f'https://coinmarketcap.com/currencies/{identifier}/historical-data/?start={start_param}&end={end_param}'

def parse_rows(document):
    def normalize_header_name(name):
        return name.lower().translate(str.maketrans(' ', '_'))
    table = document.xpath('//*[@id="historical-data"]//table')[0]
    headers = [normalize_header_name(th.text) for th in table.xpath('//th')]
    Row = namedtuple('Row', headers)
    for tr in table.xpath('//tr[td]'):
        fields = [td.text for td in tr.xpath('td')]
        fields[0] = datetime.strptime(fields[0], '%b %d, %Y').date() # TODO force %b to be locale US_en - https://stackoverflow.com/questions/18593661/how-do-i-strftime-a-date-object-in-a-different-locale
        fields[1:] = [Decimal(field.replace(',','')) for field in fields[1:]]
        yield Row(*fields)

HistoricalData = namedtuple('HistoricalData', ['identifier', 'name', 'code', 'currency', 'rows'])

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

def print_pricedb(data):
    for row in data.rows:
        date = str(row.date).translate(str.maketrans('-','/'))
        time = '00:00:00'
        print(f"P {date} {time} {data.code} {data.currency} {row.open}")

d = get('ripple', '2017-09-21', '2017-12-21')
print_pricedb(d)
