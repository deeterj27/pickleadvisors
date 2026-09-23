#!/usr/bin/env python3
"""Stage public files only; keep source, tests, and build dependencies out of hosting."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'_site'
if out.is_symlink():raise SystemExit('Refusing a symlink output directory')
if out.exists():shutil.rmtree(out)
out.mkdir()
for folder in ['advisory','media','about','audit','capital','resources','assets','pickle-assets']:
 shutil.copytree(ROOT/folder,out/folder,dirs_exist_ok=True)
for path in ROOT.iterdir():
 if path.is_file() and (path.suffix in ['.html','.png','.jpeg','.svg','.xml'] or path.name in ['CNAME','robots.txt','llms.txt'] or (path.suffix=='.txt' and len(path.stem)==32)):
  shutil.copy2(path,out/path.name)
(out/'.nojekyll').touch()
print('Staged public pages and assets in _site/.')
