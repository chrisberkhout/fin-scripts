#!/usr/bin/env python

import requests
from lxml import html
from datetime import datetime
from decimal import Decimal

# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.python-requests.org/en/latest/index.html

# TODO give or get currency code?
# TODO append to ledger file
# TODO read last from ledger file to request correct range
# TODO error handling

def generate_url(name, start, end):
    start_param = start.replace('-','')
    end_param = end.replace('-','')
    return f'https://coinmarketcap.com/currencies/{name}/historical-data/?start={start_param}&end={end_param}'

def parse(document):
    table = document.xpath('//*[@id="historical-data"]//table')[0]
    headers = [th.text for th in table.xpath('//th')]
    for tr in table.xpath('//tr[td]'):
        fields = [td.text for td in tr.xpath('td')]
        fields[0] = datetime.strptime(fields[0], '%b %d, %Y').date() # TODO force %b to be locale US_en - https://stackoverflow.com/questions/18593661/how-do-i-strftime-a-date-object-in-a-different-locale
        fields[1:] = [Decimal(field.replace(',','')) for field in fields[1:]]
        yield dict(zip(headers, fields))

def get(name, start, end):
    url = generate_url(name, start, end)
    page = requests.get(url)
    parsed = parse(html.fromstring(page.content))
    return sorted(parsed, key=lambda item: item['Date'])

d = get('bitcoin', '2017-09-21', '2017-12-21')
print(d[-1])

