"""Create/review a frozen pilot plan. Publishing requires a separate manifest review."""

import argparse
import json
from pathlib import Path
import sys

from .backfill import build_plan, stage_plan
from .core import RegistryError, canonical, safe_path


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['dry-run', 'verify-plan'])
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--plan', help='Workspace-relative frozen JSON plan for verification')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.operation == 'dry-run':
        plan = build_plan(root)
        relative = f"data-pipeline/04_review_reports/knowledge-registry-backfill-{plan['plan_sha256'][:16]}.json"
        target = safe_path(root, relative)
        content = json.dumps(plan, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_text(encoding='utf-8') != content:
                raise RegistryError('Refusing to overwrite an existing frozen plan')
        else:
            with target.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(content)
        print(canonical({'plan': relative, 'plan_sha256': plan['plan_sha256'],
                         'coverage': plan['coverage'], 'published': False}))
    else:
        if not args.plan:
            parser.error('--plan is required for verify-plan')
        plan = json.loads(safe_path(root, args.plan, source=True).read_text(encoding='utf-8'))
        staged = stage_plan(root, plan)
        print(canonical({'plan_sha256': plan['plan_sha256'], 'nodes': len(staged.nodes),
                         'edges': len(staged.edges), 'coverage': plan['coverage'], 'published': False}))


if __name__ == '__main__':
    main()
