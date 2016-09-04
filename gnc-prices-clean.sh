#!/bin/bash

# Remove user entered prices from GnuCash's price database.

# When a multi-currency transaction is entered, GnuCash automatically adds
# the exchange rate to its price database. However, for reporting purposes it
# is preferable for the price database to contain only the automatically
# fetched, official prices. Individual transactions and splits retain their
# own currency and price information outside of the price database.

book_file='/home/chris/Documents/Finances/accounts/Accounts.gnucash'
backup_csv="$book_file.deleted-prices.csv"

target="FROM prices WHERE source = 'user:xfer-dialog' OR source = 'user:price-editor' OR source = 'user:price'"
matches=`sqlite3 $book_file "SELECT count(*) $target"`

sqlite3 -csv $book_file "SELECT * $target" >> $backup_csv
sqlite3 $book_file "DELETE $target" && echo "Cleaned out $matches prices."
