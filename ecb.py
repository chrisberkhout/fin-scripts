#!/usr/bin/env python

# ECB Euro foreign exchange reference rates
# https://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html

import piecash
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from urllib import request
from xml.etree import ElementTree

# config

book_file   = '/home/chris/Documents/Finances/SCRATCH.gnucash'
source      = 'ECB Euro foreign exchange reference rates'
# source_url  = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml' # last 90 days
source_url  = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml' # since 1999
start_date  = date(datetime.utcnow().date().year - 1, 1, 1)
commodities = { 'AUD' }


# open book

book = piecash.open_book(book_file, readonly=False)


# determine uncovered dates per commodity

def prices_for(book, commodity_mnemonic, source):
    currency = book.currencies(mnemonic='EUR')
    commodity = book.currencies(mnemonic=commodity_mnemonic)
    return {
        x for x in book.prices if
            x.currency == currency
            and x.commodity == commodity
            and x.source == source
    }

dates_covered = dict()
for commodity in commodities:
    dates_covered[commodity] = {
        x.date.astimezone(timezone.utc).date() for x in
            prices_for(book, commodity, source)
    }

date_today = datetime.utcnow().date()
days_since_start = (date_today - start_date).days

dates_to_cover = {
    start_date + timedelta(x) for x in range(days_since_start + 1)
}

dates_uncovered = dict()
for commodity in commodities:
    dates_uncovered[commodity] = dates_to_cover - dates_covered[commodity]


# get data

url = request.urlopen(source_url)
root = ElementTree.fromstring(url.read())
url.close()


# read data, add to book if missing

ns = {
    'default': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref',
    'gesmes': 'http://www.gesmes.org/xml/2002-08-01'
}

for commodity_mnemonic in commodities:
    currency = book.currencies(mnemonic='EUR')
    commodity = book.currencies(mnemonic=commodity_mnemonic)
    rate_xpath = "./*[@currency='%s']" % (commodity_mnemonic)
    for day in root.find('default:Cube', ns):
        d = date(*[ int(x) for x in day.attrib['time'].split('-') ])
        rate = (1 / Decimal(day.find(rate_xpath).attrib['rate'])).quantize(Decimal('1.0000000'))
        if (d in dates_uncovered[commodity_mnemonic]):
            dt = datetime(d.year, d.month, d.day, 13, 0, 0, 0, timezone.utc)
            price = piecash.core.commodity.Price(commodity, currency, dt, rate, 'unknown', source)
            book.add(price)
            print("added %s" % (str(price)))


# save and finish

if (book.is_saved):
    print("No changes from %s" % (source))
    book.cancel() # this still seems to create a backup file
else:
    book.save()

