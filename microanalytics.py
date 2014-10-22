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

@main.group('inspect')
def inspect():
    pass

@inspect.command('sessions')
def inspect_sessions():
    res = requests.get(
        db + '/_design/' + ddoc + '/_view/inspect-sessions',
        headers={'Accept': 'application/json'},
        params={
            'descending': 'true',
            'endkey': '["%s", "%s"]' % (token, (now - datetime.timedelta(5)).isoformat()),
            'startkey': '["%s", "%s", {}]' % (token, now.isoformat()),
            'reduce': 'false'
        }
    )
    sessions = {}
    summaries = {}
    globalsummary = {}
    d = {}

    for row in res.json()['rows']:

        sessiondata = sessions.get(row['key'][2], [])
        summarydata = summaries.get(row['key'][2], {})

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

        summarydata[event_abbr] = summarydata.get(event_abbr, 0)
        summarydata[event_abbr] += 1

        globalsummary[event_abbr] = globalsummary.get(event_abbr, 0)
        globalsummary[event_abbr] += 1

        ev = {
            'itv': '',
            'name': event_abbr,
            'value': row['value']
        }

        if len(sessiondata):
            last = sessiondata.pop()
            itv = dateutil.parser.parse(last) - dateutil.parser.parse(row['key'][1])
            s = int(itv.seconds)
            m = int(itv.seconds/60)
            h = int(m/60)
            if s == 0:
                ev['itv'] = ':: less than a second after'
            else:
                ev['itv'] = ':: after '
                ev['itv'] += '%s seconds' % s if s < 60 else '%s minutes' % m if m < 60 else "%s hours" % h

        sessiondata.append(ev)
        sessiondata.append(row['key'][1])

        sessions[row['key'][2]] = sessiondata
        summaries[row['key'][2]] = summarydata

    for n, abbr in d.items():
        click.echo('%s: %s' % (n, abbr))

    for session, data in sessions.items():
        click.echo()

        for ev in data:
            if type(ev) is not dict: continue

            itv = ev.get('itv', '')
            click.echo('%s: %s -> %s %s' % (session[:5], ev['name'], ev['value'], itv))

        # print session summary
        click.echo('-----------')
        summary = summaries[session]
        click.echo(
            ', '.join(tuple('%s: %s' % (name, count) for name, count in summary.items())) + \
            '    | ' + \
            session[:5] + \
            ' totals'
        )
        # ~

    click.echo()
    click.echo('===========')
    click.echo(
        ', '.join(tuple('%s: %s' % (name, count) for name, count in globalsummary.items())) + \
        '    | totals'
    )

if __name__ == '__main__':
    main()










