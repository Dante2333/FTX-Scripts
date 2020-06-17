# FTX-Scripts
Useful FTX scripts which serve multiples purposes

# Dependencies

pandas

client.py from https://github.com/ftexchange/ftx/blob/master/rest/client.py

apscheduler

You'll need a function inside the class from client.py to move assets between subaccounts:


`def move_subaccount(self, coin, amount, acc1, acc2): `
`    return self._post(f'subaccounts/transfer', {'coin': coin, 'size': amount, 'source': acc1, 'destination': acc2})`
