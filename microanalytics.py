#
# -*- encoding: utf-8 -*-

from __future__ import division

# pyinstaller workarounds
import sys
sys.getfilesystemencoding = lambda: 'UTF-8'
##

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
    endpoint = open(config_path + '/endpoint').read().strip()
except:
    endpoint = click.prompt("You haven't set the URL of your Microanalytics instance."
                            "\nenter it now")
    if endpoint:
        open(config_path + '/endpoint', 'w').write(endpoint)
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
@click.argument('fields', nargs=-1)
def events(limit, fields):
    'Lists selected fields of last events (event, date, time, value, ip, session, page, referrer)'

    if not fields:
        fields = ('event', 'date', 'session', 'referrer')

    res = requests.get(
        endpoint + '/_all_docs',
        headers={'Accept': 'application/json'},
        params={
            'include_docs': 'true',
            'descending': 'true',
            'endkey': '"%s-"' % token,
            'startkey': '"%s-\uffff"' % token,
            'limit': limit,
        }
    )
    table = PrettyTable(fields)
    for field in fields:
        table.align[field] = 'l'
    for row in reversed(res.json()['rows']):
        doc = row['doc']
        datetime = row['id'].split('-', 1)[1]
        doc['date'], doc['time'] = datetime.split('T')
        doc['session'] = doc['session'][-5:]
        values = tuple(doc.get(field, '') for field in fields)
        table.add_row(values)
    click.echo('\nLast Events:')
    click.echo(table)

@main.command('sessions')
@click.option('--limit', '-n', default=45, help='Limit the number of shown days to this.')
def sessions(limit):
    res = requests.get(
        endpoint + '/_ddoc/_list/unique-sessions/page-views',
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
        day = datetime.datetime.strptime(row['key'][1], '%Y-%m-%d')
        if len(data): # fill the missing days
            last_day = datetime.datetime.strptime(data[-1][0], '%Y-%m-%d')
            while day > last_day + datetime.timedelta(1):
                last_day = last_day + datetime.timedelta(1)
                data.append([datetime.datetime.strftime(last_day, '%Y-%m-%d'), 0])
        data.append([datetime.datetime.strftime(day, '%Y-%m-%d'), row['value']])
    click.echo('\nNumber of unique page views per day:')
    click.echo(bar(data))

@main.command('pageviews')
@click.option('--limit', '-n', default=45, help='Limit the number of shown days to this.')
def pageviews(limit):
    res = requests.get(
        endpoint + '/_ddoc/_view/page-views',
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
        day = datetime.datetime.strptime(row['key'][1], '%Y-%m-%d')
        if len(data): # fill the missing days
            last_day = datetime.datetime.strptime(data[-1][0], '%Y-%m-%d')
            while day > last_day + datetime.timedelta(1):
                last_day = last_day + datetime.timedelta(1)
                data.append([datetime.datetime.strftime(last_day, '%Y-%m-%d'), 0])
        data.append([datetime.datetime.strftime(day, '%Y-%m-%d'), row['value']])
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
        endpoint + '/_ddoc/_view/referrals',
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

@main.command('pages')
@click.option('--domain', is_flag=True, help='Break values by domain only instead of by path.')
@click.option('--querystring',  is_flag=True, help='Break values by path and querystring instead of only by path.')
@click.option('--hash',  is_flag=True, help='Break values by path , querystring and hash instead of only by path.')
def visited_pages(domain, querystring, hash):
    group_level = 3
    if domain: group_level = 2
    if querystring: group_level = 4
    if hash: group_level = 5

    res = requests.get(
        endpoint + '/_ddoc/_view/visited-pages',
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
        if n > 2: label = row['key'][2]
        if n > 3: label += '?' + row['key'][3]
        if n > 4: label += row['key'][4]

        if not domain:
            label = '/' + '/'.join(label.split('/')[1:])

        data.append([label, row['value']])
    data.sort(key=lambda x:x[1]) # sort by value

    click.echo('\nMost visited pages:')
    click.echo(bar(data))

@main.group('inspect')
def inspect():
    pass

@inspect.command('sessions')
@click.option('--limit', '-n', default=10, help='Limit the number of shown days to this.')
def inspect_sessions(limit):
    res = requests.get(
        endpoint + '/_ddoc/_view/inspect-sessions',
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










