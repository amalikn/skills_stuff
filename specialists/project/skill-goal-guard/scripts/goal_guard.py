#!/usr/bin/env python3
"""Dependency-aware solo portfolio planner. Python stdlib only. JSON state is canonical.

GoalGuard v0.1 prototype: validates a portfolio JSON, ranks task/project/portfolio next actions and gives a scope verdict for a proposal.
Superseded in behaviour by references/decision-rules.md and references/whats-next-and-portfolio.md; rewritten in the pilot (step 4).

Usage:
  python scripts/goal_guard.py validate --state examples/portfolio.json
  python scripts/goal_guard.py next --state examples/portfolio.json --date 2026-10-27
  python scripts/goal_guard.py assess --state examples/portfolio.json --proposal examples/proposal.json
  (or `just validate`, `just next`, `just assess`)

Safety: read-only; reads the given JSON files and prints JSON to stdout; writes nothing.
"""
import argparse, datetime as dt, json, pathlib, sys

DATE=dt.date.today
VALID={'todo','in_progress','blocked','review','done','parked'}
def load(p):
    with open(p,encoding='utf8') as f: return json.load(f)
def today(s): return dt.date.fromisoformat(s) if s else None
def index(data): return {t['id']:t for p in data['projects'] for t in p.get('tasks',[])}
def validate(data):
    issues=[]; ids=set(); projects={p['id'] for p in data['projects']}
    for p in data['projects']:
        if not p.get('goal'): issues.append(f"{p['id']}: missing goal")
        if not p.get('success_criteria'): issues.append(f"{p['id']}: missing measurable success_criteria")
        for m in p.get('milestones',[]):
            if not m.get('target'): issues.append(f"{p['id']} milestone {m.get('id')}: missing target")
            if m.get('due'): today(m['due'])
        for t in p.get('tasks',[]):
            tid=t['id']
            if tid in ids: issues.append(f'duplicate task id: {tid}')
            ids.add(tid)
            if t.get('status','todo') not in VALID: issues.append(f'{tid}: invalid status')
            if not t.get('outcome'): issues.append(f'{tid}: missing expected outcome')
            if t.get('status')=='done' and not t.get('evidence'): issues.append(f'{tid}: done without evidence')
            if t.get('due'): today(t['due'])
            if t.get('milestone') and t['milestone'] not in {m['id'] for m in p.get('milestones',[])}: issues.append(f'{tid}: unknown milestone')
    tasks=index(data)
    for tid,t in tasks.items():
        for dep in t.get('depends_on',[]):
            if dep not in tasks: issues.append(f'{tid}: missing dependency {dep}')
            if dep==tid: issues.append(f'{tid}: depends on itself')
    visiting=set(); visited=set()
    def walk(tid):
        if tid in visiting: issues.append(f'dependency cycle through {tid}'); return
        if tid in visited: return
        visiting.add(tid)
        for dep in tasks[tid].get('depends_on',[]):
            if dep in tasks: walk(dep)
        visiting.remove(tid); visited.add(tid)
    for tid in tasks: walk(tid)
    if len([t for t in tasks.values() if t.get('status')=='in_progress'])>data.get('max_active_tasks',1): issues.append('portfolio WIP limit exceeded')
    for link in data.get('project_dependencies',[]):
        if link['project'] not in projects or link['depends_on_project'] not in projects: issues.append('unknown project dependency')
    return issues

def eligible(t,tasks):
    return t.get('status','todo') in ('todo','in_progress') and all(tasks.get(dep,{}).get('status')=='done' for dep in t.get('depends_on',[]))
def rank(t,p,now):
    due=today(t.get('due')) or today(p.get('due'))
    days=(due-now).days if due else 9999
    urgency=50 if days<0 else 35 if days<=2 else 20 if days<=7 else 0
    # One-man-army: favour finishing started work, urgent deadlines and declared priority.
    return (40 if t.get('status')=='in_progress' else 0)+urgency+int(t.get('priority',3))*10+int(p.get('priority',3))*5,days

def next_actions(data,when=None):
    now=today(when) if when else DATE(); tasks=index(data); per=[]; pool=[]
    for p in data['projects']:
        options=[]
        for t in p.get('tasks',[]):
            if eligible(t,tasks):
                score,days=rank(t,p,now)
                options.append((score,days,t))
                pool.append((score,days,p,t))
        options.sort(key=lambda x:(-x[0],x[1],x[2]['id']))
        pending=[t for t in p.get('tasks',[]) if t.get('status') not in ('done','parked')]
        pick=options[0][2] if options else None
        per.append({'project':p['id'],'next_task':pick['id'] if pick else None,'next_action':pick.get('next_action') if pick else None,'blocked':len([t for t in pending if t.get('status')=='blocked' or (not eligible(t,tasks) and t.get('status')=='todo')]),'open':len(pending)})
    pool.sort(key=lambda x:(-x[0],x[1],x[2]['id'],x[3]['id']))
    overall=pool[0] if pool else None
    return {'as_of':str(now),'portfolio_next':{'project':overall[2]['id'],'task':overall[3]['id'],'action':overall[3].get('next_action'),'reason':'WIP continuity, deadline proximity and explicit priority'} if overall else None,'projects':per,'task_next':{tid:{'next_action':t.get('next_action'),'ready':eligible(t,tasks),'blocked_by':[dep for dep in t.get('depends_on',[]) if tasks.get(dep,{}).get('status')!='done']} for tid,t in tasks.items()}}

def assess(data,proposal):
    tasks=index(data); tid=proposal.get('task_id'); task=tasks.get(tid)
    if not task: return {'decision':'review','reason':'No valid registered task ID','required':'link proposal to task'}
    if task.get('status') in ('done','parked'): return {'decision':'review','reason':'Task is closed or parked'}
    deps=[d for d in task.get('depends_on',[]) if tasks.get(d,{}).get('status')!='done']
    if deps: return {'decision':'review','reason':'Unmet dependencies','blocked_by':deps}
    # Semantic relationship is a model judgment recorded by agent with evidence;
    # this CLI only enforces an explicit criterion/blocker reference and scope policy.
    ref=proposal.get('criterion_id'); criteria=set(task.get('criteria_ids',[]))
    if proposal.get('necessary_blocker_id') in task.get('blocker_ids',[]) and proposal.get('necessary_blocker_id'): return {'decision':'proceed','reason':'Registered necessary blocker'}
    if ref not in criteria: return {'decision':'park','reason':'No approved acceptance criterion or registered blocker supports work'}
    if proposal.get('adds_scope'):
        return {'decision':'review','reason':'Potential scope expansion requires owner approval'}
    return {'decision':'proceed','reason':'Traceable to approved criterion; semantic necessity still requires review'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['validate','next','assess']); ap.add_argument('--state',required=True); ap.add_argument('--proposal'); ap.add_argument('--date'); args=ap.parse_args(); data=load(args.state)
    issues=validate(data)
    if args.command=='validate': result={'valid':not issues,'issues':issues}
    elif issues: result={'error':'invalid portfolio','issues':issues}
    elif args.command=='next': result=next_actions(data,args.date)
    else:
        if not args.proposal: ap.error('--proposal required for assess')
        result=assess(data,load(args.proposal))
    print(json.dumps(result,indent=2)); sys.exit(1 if ('error' in result or (args.command=='validate' and issues)) else 0)
if __name__=='__main__': main()
