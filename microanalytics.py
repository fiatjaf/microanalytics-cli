#
# -*- encoding: utf-8 -*-

from __future__ import division

import click
import requests
import datetime
import dateutil.parser
import os
try:
    from .charts import bar
except:
    from charts import bar
from prettytable import PrettyTable

today = datetime.date.today()
now = datetime.datetime.now()
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

@click.group(invoke_without_command=True)
@click.argument('code')
@click.pass_context
def main(ctx, code):
    global token
    token = code

    if not ctx.invoked_subcommand:
        # called with just `microanalytics <token>`
        ctx.invoke(events)
        ctx.invoke(sessions)

@main.command('events')
@click.option('--limit', '-n', default=70, help='Limit the number of events to this.')
def events(limit):
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

@main.command('pageviews')
@click.option('--limit', '-n', default=45, help='Limit the number of shown days to this.')
def pageviews(limit):
    res = requests.get(
        db + '/_design/' + ddoc + '/_view/page-views',
        headers={'Accept': 'application/json'},
        params={
            'startkey': '["%s", "%s"]' % (token, (today - datetime.timedelta(limit)).isoformat()),
            'endkey': '["%s", "%s", {}]' % (token, today.isoformat()),
            'reduce': 'true',
            'group_level': 2
        }
    )
    data = []
    for row in res.json()['rows']:
        data.append([row['key'][1], row['value']])
    click.echo('\nNumber of page views per day:')
    click.echo(bar(data))

@main.command('referrals')
@click.option('--path', is_flag=True, help='Break values by path instead of only by domain.')
@click.option('--querystring',  is_flag=True, help='Break values by path and querystring instead of only by domain.')
@click.option('--hash',  is_flag=True, help='Break values by path , querystring and hash instead of only by domain.')
def referrals(path, querystring, hash):
    group_level = 2
    if path: group_level = 3
    if querystring: group_level = 4
    if hash: group_level = 5

    res = requests.get(
        db + '/_design/' + ddoc + '/_view/referrals',
        headers={'Accept': 'application/json'},
        params={
            'startkey': '["%s"]' % (token,),
            'endkey': '["%s", {}]' % (token,),
            'reduce': 'true',
            'group_level': group_level
        }
    )
    data = []
    for row in res.json()['rows']:
        label = row['key'][1]
        n = len(filter(bool, row['key']))
        if n > 2: label += row['key'][2]
        if n > 3: label += '?' + row['key'][3]
        if n > 4: label += row['key'][4]

        data.append([label, row['value']])
    data.sort(key=lambda x:x[1]) # sort by value

    click.echo('\nTop referrals:')
    click.echo(bar(data))

@main.group('inspect')
def inspect():
    pass

@inspect.command('sessions')
@click.option('--limit', '-n', default=10, help='Limit the number of shown days to this.')
def inspect_sessions(limit):
    res = requests.get(
        db + '/_design/' + ddoc + '/_view/inspect-sessions',
        headers={'Accept': 'application/json'},
        params={
            'startkey': '["%s", "%s"]' % (token, (now - datetime.timedelta(limit)).isoformat()),
            'endkey': '["%s", "%s", {}]' % (token, now.isoformat()),
            'reduce': 'false'
        }
    )
    sessions = {}
    sessionorder = []
    d = {}

    for row in res.json()['rows']:

        sessiondata = sessions.get(row['key'][2])
        if not sessiondata:
            sessiondata = []
            sessionorder.append(row['key'][2])

        # d holds the event_abbreviations of the names of the events
        event_name = row['key'][3]
        if event_name not in d:
            event_abbr = event_name[0]
            i = 2
            while event_abbr in d.values():
                event_abbr = event_name[0:i]
                i += 1
            d[event_name] = event_abbr
        else:
            event_abbr = d[event_name]
        # ~

        ev = {
            'name': event_abbr,
            'value': row['value'],
            'time': row['key'][1]
        }

        sessiondata.append(ev)

        sessions[row['key'][2]] = sessiondata

    for n, abbr in d.items():
        click.echo(u'%s: %s' % (n, abbr))

    click.echo()
    for session in sessionorder:
        data = sessions[session]

        allevents = []
        for ev in data:
            allevents.append(u'{}->{}'.format(ev['name'], ev['value']))

        start = dateutil.parser.parse(data[0]['time']).strftime('%b-%d %H:%M')
        end = dateutil.parser.parse(data[-1]['time']).strftime('%b-%d %H:%M')

        click.echo(
            u'{} ({}): '.format(session[:5], start) + \
            u'|'.join(allevents) + \
            u' ({})'.format(end)
        )

if __name__ == '__main__':
    main()










