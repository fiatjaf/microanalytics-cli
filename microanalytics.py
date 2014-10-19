#
# -*- encoding: utf-8 -*-

import click
import requests
try:
    from .charts import bar
except:
    from charts import bar
from prettytable import PrettyTable
import os

db = open(os.path.join(os.path.expanduser("~"), '.config', 'microanalytics', 'db')).read().strip()
try:
    ddoc = open(os.path.join(os.path.expanduser("~"), '.config', 'microanalytics', 'ddoc')).read().strip()
except:
    ddoc = 'microanalytics'

@click.command()
@click.argument('token')
def stats(token):
    res = requests.get(
        db + '/_all_docs',
        headers={'Accept': 'application/json'},
        params={
            'include_docs': 'true',
            'descending': 'true',
            'endkey': '"%s-"' % token,
            'startkey': '"%s-\uffff"' % token,
            'limit': '100',
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
    click.echo(table)

    res = requests.get(
        db + '/_design/' + ddoc + '/_list/unique-sessions/page-views',
        headers={'Accept': 'application/json'},
        params={
            'startkey': '["%s"]' % token,
            'endkey': '["%s", {}]' % token,
            'reduce': 'true',
            'group_level': 3
        }
    )
    data = []
    for row in res.json()['rows']:
        data.append([row['key'][1], row['value']])
    click.echo(bar(data))

if __name__ == '__main__':
    stats()

main = stats
