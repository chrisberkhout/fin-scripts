#!/bin/bash

# DATE_TODAY := $(shell dround today)
# DATE_START := 2014-01-01
# DATE_START_MON := $(shell dround $(DATE_START) Mon)

# DATES_CMD := dseq $(DATE_START_MON) 7d $(DATE_TODAY)
# DATES_COUNT := $(shell $(DATES_CMD) | wc -l)




# piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; > $@

# ledger -f output/accounts.txt --begin 2015-07-01 --end 2015-08-01 --flat -X EUR bal expenses | head -n -2

# output/net.csv: QUERY = \(assets or liabilities\)
# output/net-ex-s.csv: QUERY = \(assets or liabilities\) and not \(super\)
# output/net-ex-s-b.csv: QUERY = \(assets or liabilities\) and not \(super or bitcoin\)
# output/net-ex-s-b-c.csv: QUERY = \(assets or liabilities\) and not \(super or bitcoin or charity\)
# output/net-ex-s-b-l.csv: QUERY = \(assets or liabilities\) and not \(super or bitcoin or loan\)




set -x

# brunswick apartment
# tax
# charity
# berlin apartment
# food and bev
# other
# liabilities credits
# liabilities debits

begin=2015-07-01
end=2015-08-01
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR bal expenses:brunswick
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR bal expenses:tax
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR bal expenses:charity
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR bal expenses:berlin
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR bal expenses:food
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR bal expenses and not \(brunswick or tax or charity or berlin or food\)
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR -l 'amount<{0.0}' bal liabilities
piecash_ledger.py ~/Documents/Finances/Accounts.gnucash | grep -v ^\; | ledger -f - --begin $begin --end $end --flat -X EUR -l 'amount>={0.0}' bal liabilities

# e.g. just debits/credits...
# ledger -f output/accounts.txt --begin 2015-07-01 --end 2015-08-01 --flat -X EUR -l "amount>={0.0}" bal liabilities
# ledger -f output/accounts.txt --begin 2015-07-01 --end 2015-08-01 --flat -X EUR -l "amount<{0.0}" bal liabilities

