#!/usr/bin/env python3
"""Read-only Meta daily/weekly reporting, historical replay and local report ledger.

No campaign mutation, message delivery, scheduling or approval execution exists here.
Imports and --help never read credentials or perform network calls.
"""
from __future__ import annotations
import argparse
import calendar
import csv
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler
from zoneinfo import ZoneInfo


class ReportError(ValueError):
    pass


def number(value):
    try:
        result = Decimal(str(value or '0').replace(',', ''))
    except InvalidOperation as exc:
        raise ReportError('Invalid numeric metric') from exc
    if not result.is_finite() or result < 0:
        raise ReportError('Metrics must be finite and nonnegative')
    return float(result)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def load_config(path):
    c = json.loads(Path(path).read_text())
    if c.get('schema_version') != 1 or c.get('mode') != 'report_only':
        raise ReportError('Only schema 1 report_only configuration is supported')
    if not re.fullmatch(r'\d+', c['account_id']):
        raise ReportError('Invalid account ID')
    if not re.fullmatch(r'v\d+\.\d+', c['api_version']):
        raise ReportError('Explicit API version required')
    ZoneInfo(c['account_timezone'])
    if not c.get('campaigns') or not c.get('segments'):
        raise ReportError('Explicit campaign-ID to segment mapping required')
    for campaign, segment in c['campaigns'].items():
        if not re.fullmatch(r'\d+', campaign) or segment not in c['segments']:
            raise ReportError('Invalid campaign mapping')
    for segment in c['segments'].values():
        if segment.get('api_field') not in ('actions','conversions') or not re.fullmatch(r'[a-zA-Z0-9_.]+', segment.get('api_action_type','')):
            raise ReportError('Each segment requires one explicit API field and action type')
        if not segment.get('csv_count_column') and not segment.get('csv_result_indicators'):
            raise ReportError('Each segment requires an explicit CSV order metric')
        target = segment.get('target_cpa')
        if target is not None and number(target) <= 0:
            raise ReportError('Target CPA must be positive or null')
    if c.get('monthly_budget') is not None and number(c['monthly_budget']) <= 0:
        raise ReportError('Monthly budget must be positive or null')
    return c


def day_range(start, end):
    return [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]


def window_dates(day):
    previous_end = day.replace(day=1) - timedelta(days=1)
    previous_start = previous_end.replace(day=1)
    prior_mtd_end = previous_start.replace(day=min(day.day, previous_end.day))
    # Most recently completed Monday-Sunday window as of the report date.
    week_end = day - timedelta(days=(day.weekday()+1) % 7)
    return {
        'day': (day, day), 'previous_day': (day-timedelta(days=1),)*2,
        'same_weekday': (day-timedelta(days=7),)*2,
        'previous_7_days': (day-timedelta(days=7), day-timedelta(days=1)),
        'month_to_date': (day.replace(day=1), day),
        'previous_month_comparable': (previous_start, prior_mtd_end),
        'previous_month': (previous_start, previous_end),
        'completed_week': (week_end-timedelta(days=6), week_end),
        'previous_week': (week_end-timedelta(days=13), week_end-timedelta(days=7)),
    }


def import_csv(path, config, coverage_start, coverage_end, observed_at):
    rows, seen, dates = [], set(), set()
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        spend_field = f"Amount spent ({config['currency']})"
        required = {'Reporting starts', 'Reporting ends', 'Campaign ID', 'Account ID', spend_field, 'Results', 'Result indicator'}
        if not required <= set(reader.fieldnames or []):
            raise ReportError('CSV needs daily rows, account/campaign IDs, spend, Results and Result indicator')
        level = 'ad' if 'Ad ID' in reader.fieldnames else 'campaign'
        for raw in reader:
            entity = raw.get('Ad ID') if level == 'ad' else raw['Campaign ID']
            if not entity or entity == '0':
                continue  # Meta totals row: never sum it a second time.
            if raw['Account ID'] != config['account_id']:
                raise ReportError('Wrong account in CSV')
            day = raw['Reporting starts']
            if day != raw['Reporting ends']:
                raise ReportError('Export must have a daily breakdown')
            if not coverage_start <= day <= coverage_end:
                raise ReportError('Row outside declared CSV coverage')
            date.fromisoformat(day)
            key = (day, entity)
            if key in seen:
                raise ReportError('Duplicate day/entity; remove overlapping exports or extra breakdowns')
            seen.add(key); dates.add(day)
            cid = raw['Campaign ID']
            segment = config['campaigns'].get(cid, 'unmapped')
            goal = config['segments'].get(segment, {})
            field = goal.get('csv_count_column')
            if field:
                orders = number(raw.get(field)) if field in raw else None
            else:
                indicator = raw['Result indicator']
                orders = (number(raw['Results']) if indicator in goal.get('csv_result_indicators', [])
                          else 0.0 if not indicator and not raw['Results'] and segment != 'unmapped' else None)
            rows.append(dict(day=day, account_id=config['account_id'], campaign_id=cid,
                             entity_id=entity, name=raw.get('Ad name', raw.get('Campaign name', entity)),
                             segment=segment, spend=number(raw[spend_field]), orders=orders,
                             impressions=number(raw.get('Impressions')),
                             clicks=number(raw.get('Link clicks')),
                             attribution=raw.get('Attribution setting', 'unknown')))
    # A declared range cannot turn a wholly missing CSV day into observed zero.
    if not set(day_range(date.fromisoformat(coverage_start), date.fromisoformat(coverage_end))) <= dates:
        raise ReportError('CSV is missing complete dates within its declared coverage')
    return dict(schema_version=1, source='ads_manager_csv', account_id=config['account_id'],
                timezone=config['account_timezone'], currency=config['currency'],
                coverage_start=coverage_start, coverage_end=coverage_end, observed_at=observed_at,
                level=level, source_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                attribution_basis='Ads Manager export; settings recorded per row', rows=rows)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def api_get(config, token, suffix, params):
    # Fixed host, account and GET endpoints. Never follow a returned URL or redirect with credentials.
    if suffix not in ('', '/insights'):
        raise ReportError('Only account metadata and insights reads are allowed')
    url = f"https://graph.facebook.com/{config['api_version']}/act_{config['account_id']}{suffix}?{urlencode(params)}"
    request = Request(url, headers={'Authorization': 'Bearer '+token}, method='GET')
    try:
        with build_opener(NoRedirect).open(request, timeout=60) as response:
            return json.load(response)
    except HTTPError as exc:
        raise ReportError(f'Meta read failed (HTTP {exc.code}); check access, version, quota and fields. No partial report saved.') from None
    except (URLError, json.JSONDecodeError, TimeoutError):
        raise ReportError('Meta read failed; no partial report saved') from None


def api_snapshot(config, start, end):
    token = os.environ.get('META_ADS_READ_TOKEN')
    if not token:
        raise ReportError('META_ADS_READ_TOKEN is not set. Browser sign-in does not provide API authorization.')
    account = api_get(config, token, '', {'fields':'account_id,currency,timezone_name'})
    for key, expected in [('account_id', config['account_id']), ('currency',config['currency']), ('timezone_name',config['account_timezone'])]:
        if str(account.get(key)) != expected:
            raise ReportError('Live account identity, currency or timezone differs from configuration')
    params = dict(level='ad', time_increment=1, time_range=json.dumps({'since':start,'until':end}),
                  fields='account_id,date_start,date_stop,campaign_id,ad_id,ad_name,spend,impressions,inline_link_clicks,actions,conversions', limit=500)
    rows, seen, cursors = [], set(), set()
    for _ in range(1000):
        payload = api_get(config, token, '/insights', params)
        if 'error' in payload or not isinstance(payload.get('data'), list):
            raise ReportError('Invalid Insights response; no partial report saved')
        for raw in payload['data']:
            if str(raw['account_id']) != config['account_id'] or raw['date_start'] != raw['date_stop']:
                raise ReportError('Unexpected account or nondaily API row')
            if not start <= raw['date_start'] <= end:
                raise ReportError('API row outside requested range')
            key=(raw['date_start'], raw['ad_id'])
            if key in seen:
                raise ReportError('Duplicate API row')
            seen.add(key)
            segment=config['campaigns'].get(raw['campaign_id'], 'unmapped')
            goal=config['segments'].get(segment, {})
            field=goal.get('api_field'); action=goal.get('api_action_type')
            matches=[a for a in raw.get(field, []) if a['action_type']==action] if field else []
            if len(matches)>1:
                raise ReportError('Duplicate goal action; refusing double count')
            orders=number(matches[0]['value']) if matches else 0.0 if segment!='unmapped' else None
            rows.append(dict(day=raw['date_start'], account_id=config['account_id'], campaign_id=raw['campaign_id'],
                             entity_id=raw['ad_id'], name=raw['ad_name'], segment=segment,
                             spend=number(raw['spend']), orders=orders, impressions=number(raw['impressions']),
                             clicks=number(raw.get('inline_link_clicks')), attribution='Meta current ad-set/conversion settings'))
        paging=payload.get('paging', {})
        if not paging.get('next'):
            break
        cursor=paging.get('cursors', {}).get('after')
        if not cursor or cursor in cursors:
            raise ReportError('Incomplete pagination; no partial report saved')
        cursors.add(cursor); params['after']=cursor
    else:
        raise ReportError('Pagination limit reached; no partial report saved')
    return dict(schema_version=1, source='marketing_api', account_id=config['account_id'],
                timezone=config['account_timezone'], currency=config['currency'], coverage_start=start, coverage_end=end,
                observed_at=datetime.now(timezone.utc).isoformat(), level='ad',
                attribution_basis='Meta current ad-set/conversion settings; reconcile to Ads Manager before unattended use', rows=rows)


def aggregate(snapshot, start, end, segment=None, campaign=None, entity=None):
    if start.isoformat()<snapshot['coverage_start'] or end.isoformat()>snapshot['coverage_end']:
        return None
    rows=[r for r in snapshot['rows'] if start.isoformat()<=r['day']<=end.isoformat()
          and (segment is None or r['segment']==segment)
          and (campaign is None or r['campaign_id']==campaign)
          and (entity is None or r['entity_id']==entity)]
    spend=sum(Decimal(str(r['spend'])) for r in rows)
    missing=any(r['orders'] is None for r in rows)
    orders=None if missing else sum(r['orders'] or 0 for r in rows)
    days=(end-start).days+1
    return dict(spend=float(spend), orders=orders, cpa=float(spend)/orders if orders else None,
                daily_spend=float(spend)/days, daily_orders=orders/days if orders is not None else None, days=days)


def pct(current, prior):
    return (current/prior-1)*100 if current is not None and prior is not None and prior>0 else None


def money(value):
    return 'not available' if value is None else f'{value:,.2f}'


def count(value):
    return 'not available' if value is None else f'{value:,.1f}'


def esc(value):
    text=html.escape(str(value), quote=True).replace('|','/').replace('\n',' ')
    return re.sub(r'([\\`*_{}\[\]()#!])', r'\\\1', text)


def build_report(snapshot, config, day, cadence):
    if snapshot['account_id']!=config['account_id'] or snapshot['timezone']!=config['account_timezone'] or snapshot['currency']!=config['currency']:
        raise ReportError('Snapshot identity differs from configuration')
    observed=datetime.fromisoformat(snapshot['observed_at'])
    if observed.tzinfo is None:
        raise ReportError('Extraction timestamp must include a timezone')
    if observed.astimezone(ZoneInfo(config['account_timezone'])).date() <= day:
        raise ReportError('Source was extracted before the report day completed')
    today=datetime.now(ZoneInfo(config['account_timezone'])).date()
    if day>=today:
        raise ReportError('Only completed account-timezone days can be reported')
    windows=window_dates(day)
    primary='day' if cadence=='daily' else 'completed_week'
    comparisons=['previous_7_days','previous_day','same_weekday'] if cadence=='daily' else ['previous_week']
    if any(aggregate(snapshot,*windows[w]) is None for w in [primary,*comparisons]):
        raise ReportError('Source does not cover all required comparison dates')
    warnings=list(config.get('measurement_notes', []))
    unmapped={r['campaign_id'] for r in snapshot['rows'] if r['segment']=='unmapped' and r['spend']>0
              and windows['month_to_date'][0].isoformat()<=r['day']<=day.isoformat()}
    if unmapped:
        warnings.append('Unmapped campaigns have spend: '+', '.join(sorted(unmapped))+'. Included in account spend; excluded from segment CPA.')
    attrs=sorted({r['attribution'] for r in snapshot['rows'] if r['spend']>0 and windows['previous_7_days'][0].isoformat()<=r['day']<=day.isoformat()})
    if len(attrs)>1:
        warnings.append('Multiple attribution settings are present; comparisons are directional until settings are reconciled.')
    report=dict(schema_version=1, entity=config['entity'], day=day.isoformat(), cadence=cadence,
                account_id=config['account_id'], currency=config['currency'], source=snapshot['source'], source_observed_at=snapshot['observed_at'],
                source_hash=digest(snapshot), config_hash=digest(config), account_timezone=config['account_timezone'],
                mode='report_only', warnings=warnings, attribution_settings=attrs, segments={}, recommendations=[])
    lines=[f"# {config['entity']} Meta {cadence} report — {day}", '',
           '**Reporting only. No account settings changed.**', '',
           f"Source: {snapshot['source']}; observed {snapshot['observed_at']}. Account days: {config['account_timezone']}. Currency: {config['currency']}.",
           'Orders below are Meta-attributed conversion events, not verified completed orders or unique acquired customers. Recent conversions can revise.', '',
           f"Primary window: {windows[primary][0]} through {windows[primary][1]}.", '',
           'CPA is total spend divided by total orders, including for the seven-day baseline; daily CPAs are never averaged.', '']
    for segment, goal in config['segments'].items():
        results={name:aggregate(snapshot,*dates,segment=segment) for name,dates in windows.items()}
        report['segments'][segment]=results
        results['changes']={name:{metric:pct(results[primary][metric], results[name][metric]) for metric in ('daily_spend','daily_orders','cpa')} for name in comparisons}
        current=results[primary]; target=goal.get('target_cpa')
        lines += [f"## {goal['label']} — target CPA {money(target)} {config['currency']}", '', '| Window | Spend/day | Orders/day | CPA | CPA change vs baseline |', '| --- | ---: | ---: | ---: | ---: |']
        for name in [primary,*comparisons]:
            row=results[name]; change=pct(current['cpa'], row['cpa']) if name!=primary else None
            lines.append(f"| {name.replace('_',' ')} | {money(row['daily_spend'])} | {count(row['daily_orders'])} | {money(row['cpa'])} | {'—' if change is None else f'{change:+.1f}%'} |")
        if current['orders'] is None:
            recommendation='Investigate missing or incompatible order metrics before judging efficiency.'
        elif current['orders']==0:
            recommendation='No attributed orders in this window. Check delivery and conversion tracking; recheck after attribution matures before proposing a pause.'
        elif target is None:
            recommendation='Set an approved target before judging acquisition efficiency.'
        elif current['cpa']>target:
            recommendation=f"CPA is {(current['cpa']/target-1)*100:.1f}% above target. Review the highest-spend above-target campaigns below and investigate tracking, landing-page conversion and recent agency changes. Keep any budget or targeting change as a proposal."
        else:
            recommendation='CPA is within target. Review the preceding seven days and tracking quality before proposing more budget; do not increase spend from one day alone.'
        rec=dict(segment=segment, action='investigate' if current['cpa'] is None or (target and current['cpa']>target) else 'review', text=recommendation,
                 status='proposed', requires_human_approval=True)
        rec['id']=digest([config['entity'],day.isoformat(),cadence,segment,rec['text']])[:16]
        report['recommendations'].append(rec)
        lines += ['',recommendation,'']
    mtd=aggregate(snapshot,*windows['month_to_date']); prior=aggregate(snapshot,*windows['previous_month_comparable']); prior_full=aggregate(snapshot,*windows['previous_month'])
    cap=config.get('monthly_budget'); month_days=calendar.monthrange(day.year,day.month)[1]
    forecast=mtd['spend']/day.day*month_days if mtd else None
    remaining=cap-mtd['spend'] if cap is not None and mtd else None
    budget=dict(approved_monthly_cap=cap,mtd_spend=mtd['spend'] if mtd else None,
                previous_comparable_spend=prior['spend'] if prior else None,
                previous_month_spend=prior_full['spend'] if prior_full else None,
                linear_month_end_forecast=forecast,remaining=remaining,
                remaining_daily_allowance=max(0,remaining)/(month_days-day.day) if remaining is not None and day.day<month_days else None)
    report['budget']=budget
    lines += ['## Budget', '',f"Approved monthly cap: {money(cap)}. MTD spend: {money(budget['mtd_spend'])}. Remaining: {money(remaining)}.",
              f"Linear month-end forecast: {money(forecast)}. Prior comparable MTD spend: {money(budget['previous_comparable_spend'])}; previous full month: {money(budget['previous_month_spend'])}.",
              f"Remaining average daily allowance: {money(budget['remaining_daily_allowance'])}. This is a reporting calculation, not a budget setting or a direction to spend it.",
              'Meta daily delivery varies. The monthly cap is monitored here, not enforced in Ads Manager. Efficiency takes priority over using the whole cap.', '']
    if remaining is not None and remaining<0:
        report['warnings'].append('Monthly spend is already over the approved cap. Notify the owner and recommend immediate review; this reporter cannot stop spend.')
    elif cap and forecast and forecast>cap:
        report['warnings'].append('Linear pacing projects above the monthly cap. Review remaining commitments and propose a budget adjustment for approval.')
    campaigns=[]
    for cid, segment in config['campaigns'].items():
        period=windows['previous_7_days'] if cadence=='daily' else windows['completed_week']
        metric=aggregate(snapshot,*period,campaign=cid)
        if metric and metric['spend']>0:
            campaigns.append(dict(campaign_id=cid,segment=segment,**metric))
    campaigns.sort(key=lambda x:x['spend'],reverse=True)
    report['campaign_review']=campaigns
    lines += ['## Campaigns to inspect', '', 'Ranked by spend in the preceding seven complete days (daily report) or completed week (weekly report). These are review candidates, not pause instructions.', '', '| Campaign ID | Segment | Spend | Orders | CPA | Target |','| --- | --- | ---: | ---: | ---: | ---: |']
    for row in campaigns[:15]:
        lines.append(f"| {row['campaign_id']} | {row['segment']} | {money(row['spend'])} | {count(row['orders'])} | {money(row['cpa'])} | {money(config['segments'][row['segment']].get('target_cpa'))} |")
    creative=[]
    if cadence=='weekly' and snapshot['level']=='ad':
        ads={r['entity_id']:r for r in snapshot['rows'] if r['segment']!='unmapped'}
        for aid,row in ads.items():
            metric=aggregate(snapshot,*windows['completed_week'],entity=aid)
            if metric and metric['spend']>0:
                creative.append(dict(ad_id=aid,name=row['name'],segment=row['segment'],**metric))
        creative.sort(key=lambda x:x['spend'],reverse=True)
        lines += ['', '## Creative review inputs', '', 'Highest-spend ads; ad names are labels, not evidence of their visual content. Review actual assets before assigning angles, promises, outcomes or making variants.', '', '| Ad | Segment | Spend | Orders | CPA |','| --- | --- | ---: | ---: | ---: |']
        for row in creative[:20]:
            lines.append(f"| {row['ad_id']} — {esc(row['name'])} | {row['segment']} | {money(row['spend'])} | {count(row['orders'])} | {money(row['cpa'])} |")
        lines += ['', 'For each supported performer: inspect the asset, record the angle/promise/outcome/proof/format, propose one controlled variation and its hypothesis. Separately propose new concepts based on customer and competitor evidence. Competitor longevity is not performance proof. No automatic one-day winner/loser decisions.']
    report['creative_review']=creative
    lines += ['', '## Data quality and follow-up', '']
    lines += ['- '+w for w in report['warnings']] or ['- No configured measurement warning; this does not prove tracking correctness.']
    lines += ['- Re-pull overlapping dates on each API run; retain both as-of snapshots so attribution revisions remain visible.',
              '- This first pilot has no live external-change-history feed. Record agency changes and outcomes explicitly; do not attribute movement to an unverified change.',
              '- Hold scaling recommendations while material measurement issues remain unresolved. Targets do not establish profitability.',
              '- Approvals, executions and observed outcomes are separate ledger events. This tool cannot execute changes.', '']
    report['markdown']='\n'.join(lines)
    return report


def ledger_identity(value):
    return {k:value[k] for k in ('entity','account_id','currency','account_timezone')}


def check_ledger_identity(db, identity):
    for row in db.execute('SELECT report_json FROM reports'):
        stored=json.loads(row[0])
        if any(stored.get(k)!=v for k,v in identity.items()):
            raise ReportError('History folder belongs to a different account or identity; use a separate folder')


def history_context(output, before_day, identity):
    database=Path(output)/'history.sqlite3'
    if not database.exists():
        return {'prior_reports':[], 'events':[]}
    # Read only; files and prior narrative remain evidence, never instructions.
    with sqlite3.connect(f"file:{database.resolve()}?mode=ro", uri=True) as db:
        check_ledger_identity(db, identity)
        prior=[];seen=set()
        for rid, day, cadence, raw in db.execute('SELECT run_id,day,cadence,report_json FROM reports WHERE day < ? ORDER BY day DESC,saved_at DESC',(before_day,)):
            if (day,cadence) in seen:continue
            seen.add((day,cadence));data=json.loads(raw)
            prior.append(dict(run_id=rid,day=day,cadence=cadence,recommendations=data['recommendations']))
            if len(prior)==3:break
        events=[dict(zip(('run_id','recommendation_id','event_type','actor','evidence','recorded_at'),row)) for row in db.execute('SELECT run_id,recommendation_id,event_type,actor,evidence,recorded_at FROM events ORDER BY recorded_at DESC LIMIT 20')]
    return {'prior_reports':prior,'events':events}


def save_report(report, snapshot, output):
    output=Path(output)
    if (output/'history.sqlite3').exists():
        with sqlite3.connect(f"file:{(output/'history.sqlite3').resolve()}?mode=ro",uri=True) as db:
            check_ledger_identity(db,ledger_identity(report))
    output.mkdir(parents=True,exist_ok=True)
    os.chmod(output,0o700)
    # Content-addressed, idempotent reruns. A changed data/config snapshot creates a new run.
    run_id=digest({k:v for k,v in report.items() if k!='markdown'})[:20]
    base=output / f"{report['day']}-{report['cadence']}-{run_id}"
    for suffix,payload in [('.md',report['markdown']),('.json',json.dumps(report,indent=2))]:
        path=base.with_suffix(suffix); path.write_text(payload); path.chmod(0o600)
    database=output/'history.sqlite3'
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE IF NOT EXISTS reports (run_id TEXT PRIMARY KEY, day TEXT, cadence TEXT, report_json TEXT, snapshot_json TEXT, saved_at TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, run_id TEXT, recommendation_id TEXT, event_type TEXT, actor TEXT, evidence TEXT, recorded_at TEXT)')
        db.execute('INSERT OR IGNORE INTO reports VALUES (?,?,?,?,?,?)',(run_id,report['day'],report['cadence'],json.dumps(report),json.dumps(snapshot),datetime.now(timezone.utc).isoformat()))
    database.chmod(0o600)
    return base.with_suffix('.md'),run_id


def record_event(output,run_id,recommendation_id,event_type,actor,evidence):
    if not actor.strip() or not evidence.strip():
        raise ReportError('Actor and evidence are required; an event never grants execution capability')
    database=Path(output)/'history.sqlite3'
    if not database.exists():
        raise ReportError('Report history does not exist')
    with sqlite3.connect(database) as db:
        row=db.execute('SELECT report_json FROM reports WHERE run_id=?',(run_id,)).fetchone()
        if not row:
            raise ReportError('Unknown run ID')
        if recommendation_id and recommendation_id not in {r['id'] for r in json.loads(row[0])['recommendations']}:
            raise ReportError('Unknown recommendation ID')
        if event_type in ('approved','rejected','executed','outcome') and not recommendation_id:
            raise ReportError('Recommendation ID required for this event')
        payload=[run_id,recommendation_id,event_type,actor,evidence]
        db.execute('INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?)',(digest(payload)[:20],*payload,datetime.now(timezone.utc).isoformat()))


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    run=sub.add_parser('report',help='Create a read-only report from a CSV replay or live API reads')
    run.add_argument('--config',required=True,type=Path); run.add_argument('--output',required=True,type=Path)
    run.add_argument('--date',help='Completed account day; defaults to yesterday')
    run.add_argument('--cadence',choices=['daily','weekly'],default='daily')
    source=run.add_mutually_exclusive_group(required=True)
    source.add_argument('--csv',type=Path); source.add_argument('--api',action='store_true')
    run.add_argument('--coverage-start');run.add_argument('--coverage-end');run.add_argument('--observed-at')
    event=sub.add_parser('record',help='Record human decisions or externally verified changes; never executes them')
    event.add_argument('--output',required=True,type=Path);event.add_argument('--run-id',required=True)
    event.add_argument('--recommendation-id');event.add_argument('--actor',required=True);event.add_argument('--evidence',required=True)
    event.add_argument('--event',required=True,choices=['approved','rejected','executed','outcome','external_change','note'])
    args=p.parse_args(argv)
    try:
        if args.command=='record':
            record_event(args.output,args.run_id,args.recommendation_id,args.event,args.actor,args.evidence)
            print('Ledger event recorded. No Meta action performed.');return 0
        config=load_config(args.config)
        day=date.fromisoformat(args.date) if args.date else datetime.now(ZoneInfo(config['account_timezone'])).date()-timedelta(days=1)
        if args.csv:
            if not all([args.coverage_start,args.coverage_end,args.observed_at]):
                raise ReportError('CSV replay requires --coverage-start, --coverage-end and --observed-at')
            datetime.fromisoformat(args.observed_at)
            snapshot=import_csv(args.csv,config,args.coverage_start,args.coverage_end,args.observed_at)
        else:
            earliest=min(start for start,end in window_dates(day).values())
            snapshot=api_snapshot(config,earliest.isoformat(),day.isoformat())
        report=build_report(snapshot,config,day,args.cadence)
        report['history']=history_context(args.output,day.isoformat(),ledger_identity(config))
        report['markdown']+='\n## Prior reports and decisions\n\n'
        if not report['history']['prior_reports'] and not report['history']['events']:
            report['markdown']+='No earlier report or decision is recorded in this pilot ledger.\n'
        for prior in report['history']['prior_reports']:
            report['markdown']+=f"- Prior {prior['cadence']} report: {prior['day']} (run {prior['run_id']}); review its recommendations before repeating them.\n"
        for event in report['history']['events']:
            report['markdown']+=f"- Recorded {esc(event['event_type'])} by {esc(event['actor'])}: {esc(event['evidence'])}\n"
        path,run_id=save_report(report,snapshot,args.output)
        print(json.dumps({'report':str(path.resolve()),'run_id':run_id,'source':snapshot['source'],'mode':'report_only'}))
        return 0
    except (ReportError,KeyError,TypeError,ValueError) as exc:
        # Config/data errors never include token-bearing HTTP URLs.
        print(f'Report not produced: {exc}',file=sys.stderr);return 2


if __name__=='__main__':
    raise SystemExit(main())
