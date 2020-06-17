import pandas as pd
from client import FtxClient as ftx
from datetime import datetime
import requests
import sqlite3
from databaseEQ import sql_table, sql_insert, sql_fetch
from apscheduler.schedulers.blocking import BlockingScheduler


def telegram_bot_sendtext(bot_message):
    bot_token = 'bottoken' # get this by talking to @botfather
    bot_chatID = 'your-telegram-id' # this can be a group, use getidbot on telegram to get your id
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

def get_collateral_usd(name):
    account = ftx(subaccount_name=name)
    information = account._get(f'wallet/balances')
    df = pd.DataFrame.from_dict(information)
    df = df[df['coin'] == 'USD']
    df = df['free']
    return df.iloc[0]

def get_balance(nickname):
    account = ftx()
    information = account._get(f'subaccounts/' + nickname + '/balances')
    df = pd.DataFrame(information)
    total = df['usdValue'].sum()
    return total

def report2(value):
    date, actual, difference, increase = value
    difference = float(difference)
    if difference < 0:
        my_message = ("`Date:{}`\n"
                "\t`Decreased:${}`\n"
                "\t`Total profit:{}%`\n"
                "\t`Overall balance:${}`").format(date, difference, increase, actual)

    else:
        my_message = ("`Date:{}`\n"
                "\t`Increased:${}`\n"
                "\t`Total profit:{}%`\n"
                "\t`Overall balance:${}`").format(date, difference, increase, actual)
    telegram_bot_sendtext(my_message)


def main():
    now = datetime.now()
    date = now.strftime("%d/%m/%Y: %H:%M:%S")
    con = sqlite3.connect('equity.db')
    account = ftx()
    information = account._get(f'subaccounts/')
    df = pd.DataFrame(information)
    df = df[df['deletable'] == True]
    df['balance'] = df['nickname'].apply(get_balance)
    rows = sql_fetch(con)

    df2 = pd.DataFrame(rows)
    df2 = df2.rename(columns={0:'date',1:'equity','3':'difference','4':'increase'})
    actual = float('%.3f'%df['balance'].sum())
    difference = actual-df2['equity'].iloc[-1]
    increase = ((actual/df2['equity'].iloc[-1])-1)*100
    difference = '%.3f'%difference
    increase = '%.3f'%increase
    entry = (date, actual, difference, increase)
    sql_table(con)
    sql_insert(con, (entry))
    report2(entry)
    con.commit()

def replenish():
    bank = 'Savings'
    trading_account = 'futures'
    account = ftx(subaccount_name=bank)
    savings = (get_collateral_usd(bank))
    trading_amount = get_balance(trading_account)
    less_than = 3500
    more_than = 4700
    amount_to_transfer = 1000
    if np.less(trading_amount, less_than) and np.greater(savings, 1000):
        account.move_subaccount('USD', amount_to_transfer, bank, trading_account)
        telegram_bot_sendtext('`Your account has been replenished with ${} as your balance was less than ${}`'.format(amount_to_transfer, less_than))
    elif np.greater(trading_amount, more_than):
        amount_tomove = trading_amount - more_than
        account.move_subaccount('USD', amount_tomove, trading_account, bank)
        telegram_bot_sendtext('`Your balance was above ${}, sending ${} to bank.`'.format(more_than, amount_tomove))
    elif np.less(trading_amount, less_than) and np.less(savings, 1000):
        telegram_bot_sendtext('`Your trading account needs to replenish but you do not have enough funds to transfer. Your bank balance is ${}`'.format(savings))

scheduler = BlockingScheduler()
scheduler.add_job(main, 'cron', hour="*")
scheduler.add_job(replenish, 'cron', hour="*")
scheduler.start()

