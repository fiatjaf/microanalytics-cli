#
# -*- encoding: utf-8 -*-

import click
import requests
import datetime
import os
try:
    from .charts import bar
except:
    from charts import bar
from prettytable import PrettyTable

today = datetime.date.today()
config_path = os.path.join(os.path.expanduser("~"), '.config', 'microanalytics')

# create config folder
if not os.path.exists(config_path):
    os.makedirs(config_path)

# get opts from config folder (or set them)
try:
    db = open(config_path + '/db').read().strip()
except:
    db = click.prompt("You haven't set the URL of your CouchDB Microanalytics \
                       database, enter it now")
    if db:
        open(config_path + '/db', 'w').write(db)

try:
    ddoc = open(config_path + '/ddoc').read().strip()
except:
    ddoc = click.prompt("Enter the name of the Design Document, if it is not 'microanalytics'",
                        default='microanalytics')
    if ddoc:
        open(config_path + '/ddoc', 'w').write(ddoc)
##

@click.group()
@click.argument('code')
def main(code):
    global token
    token = code

@main.command('events')
@click.option('--limit', '-n', default=70, help='Limit the number of events to this.')
def basic(limit):
    res = requests.get(
        db + '/_all_docs',
        headers={'Accept': 'application/json'},
        params={
            'include_docs': 'true',
            'descending': 'true',
            'endkey': '"%s-"' % token,
            'startkey': '"%s-\uffff"' % token,
            'limit': limit,
        }
    )
    table = PrettyTable(['Event', 'Date', 'Page', 'Session', 'Referrer'])
    table.align['Event'] = 'l'
    table.align['Page'] = 'l'
    table.align['Referrer'] = 'l'
    for row in reversed(res.json()['rows']):
        doc = row['doc']
        date = row['id'].split('-', 1)[1]
        table.add_row([
            doc['event'][:11],
            ' '.join(date.split('T')),
            doc['page'][-30:] if doc['page'] else '',
            doc['session'][:5],
            doc.get('referrer', '')[:20]
        ])
    click.echo('\nLast Events:')
    click.echo(table)

@main.command('sessions')
@click.option('--limit', '-n', default=45, help='Limit the number of shown days to this.')
def sessions(limit):
    res = requests.get(
        db + '/_design/' + ddoc + '/_list/unique-sessions/page-views',
        headers={'Accept': 'application/json'},
        params={
            'startkey': '["%s", "%s"]' % (token, (today - datetime.timedelta(limit)).isoformat()),
            'endkey': '["%s", "%s", {}]' % (token, today.isoformat()),
            'reduce': 'true',
            'group_level': 3
        }
    )
    data = []
    for row in res.json()['rows']:
        data.append([row['key'][1], row['value']])
    click.echo('\nNumber of unique page views per day:')
    click.echo(bar(data))


if __name__ == '__main__':
    main()
