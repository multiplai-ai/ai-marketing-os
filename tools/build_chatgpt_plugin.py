#!/usr/bin/env python3
"""Build the ChatGPT library package from canonical SOPs; never publish it."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import zipfile
import yaml
try:
    from tools.build_claude_plugin import included, VERSION
    from tools.release_content import path_issue, content_issues
except ModuleNotFoundError:
    from build_claude_plugin import included, VERSION
    from release_content import path_issue, content_issues


def build(root: Path, output: Path, version: str) -> Path:
    root = root.resolve()
    if not VERSION.fullmatch(version):
        raise ValueError('invalid release version')
    source = json.loads((root / '.claude-plugin/plugin.json').read_text())
    if source['version'] != version:
        raise ValueError('manifest and requested version differ')
    ids = yaml.safe_load((root / 'sops/manifest.yaml').read_text())['sops']
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', sid) for sid in ids):
        raise ValueError('invalid workflow inventory')
    if set(ids) != {p.parent.name for p in (root / 'sops').glob('*/SKILL.md')}:
        raise ValueError('workflow inventory mismatch')
    files = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if not included(relative) or relative.parts[0] == '.claude-plugin':
            continue
        if path.is_symlink():
            raise ValueError(f'symlink rejected: {relative}')
        if not path.is_file():
            continue
        name = relative.as_posix()
        data = path.read_bytes()
        issues = ([path_issue(name)] if path_issue(name) else []) + content_issues(name, data)
        if issues:
            raise ValueError(f'{name}: {issues}')
        files[name] = data
    for sid in sorted(ids):
        text = (root / f'sops/{sid}/SKILL.md').read_text()
        front = text.split('---', 2)
        if len(front) != 3 or front[0].strip():
            raise ValueError(f'invalid skill header: {sid}')
        header = yaml.safe_load(front[1])
        if header.get('name') != sid or not header.get('description'):
            raise ValueError(f'invalid skill identity: {sid}')
        # Generated entrypoints contain no independent procedural copy. Relative
        # paths in the canonical document remain relative to its original folder.
        router = '---\n' + yaml.safe_dump({'name': sid, 'description': header['description']},sort_keys=False) + '---\n\n'
        router += f'Read and follow [the complete {sid} workflow](../../sops/{sid}/SKILL.md) before starting.\n'
        router += 'Resolve its references relative to that source file, not this generated entrypoint.\n'
        router += 'The package root also contains tools used by some workflows. Run only tools that\n'
        router += 'the selected workflow requires and the host supports. Report missing capabilities;\n'
        router += 'keep user inputs and outputs outside the installed library.\n'
        files[f'skills/{sid}/SKILL.md'] = router.encode()
    manifest = {
        '$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
        'name': source['name'], 'version': version, 'description': source['description'],
        'author': source['author'],
        'extensions': {'com.openai': {'interface': {
            'displayName': 'AI Marketing OS', 'shortDescription': 'Practical marketing workflows',
            'longDescription': source['description'] + ' Uses your host capabilities and sources; individual workflows may need web access, files or tools.',
            'developerName': 'MultiplAI', 'category': 'Productivity',
            'capabilities': ['Interactive'],
            'defaultPrompt': 'Help me choose and run an AI Marketing OS workflow for my business.'
        }}}
    }
    files['plugin.json'] = (json.dumps(manifest,indent=2)+'\n').encode()
    output.mkdir(parents=True,exist_ok=True)
    target = output / f'ai-marketing-os-chatgpt-plugin-{version}.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo('ai-marketing-os/'+name,date_time=(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            archive.writestr(info,data)
    return target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,default=Path('dist'))
    parser.add_argument('--version',required=True)
    args=parser.parse_args()
    print(build(args.root,args.output,args.version))

if __name__=='__main__':
    main()
