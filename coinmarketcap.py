#!/usr/bin/env python

import requests
from lxml import html
from datetime import datetime
from decimal import Decimal
import re

# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://docs.python-requests.org/en/latest/index.html

# TODO case class?
# TODO append to ledger file
# TODO read last from ledger file to request correct range
# TODO error handling

def generate_url(name, start, end):
    start_param = start.replace('-','')
    end_param = end.replace('-','')
    return f'https://coinmarketcap.com/currencies/{name}/historical-data/?start={start_param}&end={end_param}'

def parse_rows(document):
    table = document.xpath('//*[@id="historical-data"]//table')[0]
    headers = [th.text for th in table.xpath('//th')]
    for tr in table.xpath('//tr[td]'):
        fields = [td.text for td in tr.xpath('td')]
        fields[0] = datetime.strptime(fields[0], '%b %d, %Y').date() # TODO force %b to be locale US_en - https://stackoverflow.com/questions/18593661/how-do-i-strftime-a-date-object-in-a-different-locale
        fields[1:] = [Decimal(field.replace(',','')) for field in fields[1:]]
        yield dict(zip(headers, fields))

def parse_code(document):
    title = document.find('.//title').text
    m = re.match('(?P<name>.*?) \((?P<code>.*?)\)', title)
    return m.group('code')

def get(name, start, end):
    url = generate_url(name, start, end)
    page = requests.get(url)
    document = html.fromstring(page.content)
    code = parse_code(document)
    rows = parse_rows(document)
    return (code, sorted(rows, key=lambda item: item['Date']))

c, d = get('bitcoin', '2017-09-21', '2017-12-21')
print(c)
print(d[-1])

