# Equity monitor and replenish collateral

# dependencies 

pandas

client.py from https://github.com/ftexchange/ftx/blob/master/rest/client.py

apscheduler

You'll need a function inside the class from client.py to move assets between subaccounts:

`def move_subaccount(self, coin, amount, acc1, acc2): `
`    return self._post(f'subaccounts/transfer', {'coin': coin, 'size': amount, 'source': acc1, 'destination': acc2})`

# utility

The point of this file is to save date, equity, difference and % increase into a database for further investigation. It uses 1hr but you can do the period that you prefer by modifying the apscheduler cron time.
Replenish will move collateral back and forth, moving out the profits and replenishing the account as needed every 1hr
