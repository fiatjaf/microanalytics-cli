#
# -*- encoding: utf-8 -*-

import click
import requests
from .charts import bar
from prettytable import PrettyTable

@click.command()
@click.argument('token')
def stats(token):
    res = requests.get(
        'http://spooner.alhur.es:5984/microanalytics/_all_docs',
        headers={'Accept': 'application/json'},
        params={
            'include_docs': 'true',
            'descending': 'true',
            'endkey': '"%s-"' % token,
            'startkey': '"%s-\uffff"' % token,
            'limit': '100',
        }
    )
    table = PrettyTable(['Event', 'Value', 'Date', 'Page', 'Session', 'Referrer'])
    table.align['Event'] = 'l'
    table.align['Page'] = 'l'
    table.align['Referrer'] = 'l'
    for row in reversed(res.json()['rows']):
        doc = row['doc']
        table.add_row([
            doc['event'][:12],
            doc['value'][:7] if type(doc['value']) is str else doc['value'],
            doc['date'].split('T')[0],
            doc['page'][-40:],
            doc['session'][:5],
            doc.get('referrer', '')[:20]
        ])
    click.echo(table)

    res = requests.get(
        'http://spooner.alhur.es:5984/microanalytics/_design/webapp/_list/unique-sessions/page-views',
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
