#!/usr/bin/env python3
"""Create one-chart-per-image comparison figures from RHCR summary_seed0.csv."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LABELS = {
    'pbs_sipp_seed0': 'PBS + SIPP',
    'pbs_astar_seed0': 'PBS + A*',
    'ecbs_sipp_seed0': 'ECBS + SIPP',
}


def read_csv(path: Path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        rd = csv.DictReader(f)
        required = {'Method','Goals','MeanPlanMs','MaxPlanMs'}
        if not required.issubset(set(rd.fieldnames or [])):
            raise ValueError('summary CSV must contain: '+', '.join(sorted(required)))
        rows=list(rd)
    if not rows:
        raise ValueError('summary CSV is empty')
    for row in rows:
        for col in ['Goals','MeanPlanMs','MaxPlanMs']:
            row[col] = float(row[col])
    return rows


def save_plot(rows, metric, ylabel, title, path, *, decimals=0):
    labels=[LABELS.get(x['Method'],x['Method']) for x in rows]
    values=[x[metric] for x in rows]
    fig,ax=plt.subplots(figsize=(8.5,5.4))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.24, top=0.80)
    bars=ax.bar(labels,values)
    ax.set_ylabel(ylabel)
    ax.set_title(title+'\nKIVA warehouse | 10 robots | 100 steps | Seed 0', loc='left', fontsize=13)
    ax.set_ylim(0,max(values)*1.20 if max(values)>0 else 1)
    ax.grid(axis='y',alpha=.25)
    ax.set_axisbelow(True)
    for bar,v in zip(bars,values):
        lab=f'{v:.{decimals}f}'
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+max(values)*.03,lab,ha='center',fontsize=11)
    fig.text(.5,.045,'Single seed (0) only — descriptive comparison, not a statistical claim.',ha='center',fontsize=9)
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=175,bbox_inches='tight',pad_inches=.14)
    plt.close(fig)
    print('Figure:',path)


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--csv',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(argv)
    rows=read_csv(args.csv)
    save_plot(rows,'Goals','Completed goals','Goal completion comparison',args.out/'completed_goals.png')
    save_plot(rows,'MeanPlanMs','Mean planning time (ms)','Planning latency comparison',args.out/'mean_planning_time_ms.png',decimals=2)
    save_plot(rows,'MaxPlanMs','Maximum planning time (ms)','Worst-call planning latency',args.out/'max_planning_time_ms.png',decimals=2)

if __name__=='__main__':
    main()
