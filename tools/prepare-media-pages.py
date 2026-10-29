"""Keep newly generated readers compatible with the split media deployment.

Run from any directory: python tools/prepare-media-pages.py
Use --check in CI to report pages that still need preparation.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote, quote
import argparse, re

ROOT=Path(__file__).resolve().parents[1]
HOST='https://ravcu.github.io/turkce-akademi/'
MEDIA='https://raw.githubusercontent.com/ravcu/turkce-akademi/main/'
LOADER='<script src="/turkce-akademi/assets/js/media-loader.js?v=20261029-media1"></script>'
EXTENSIONS={'.mp3','.wav','.opus','.ogg','.m4a','.aac','.flac','.webp','.png','.jpg','.jpeg','.gif','.svg','.ico','.mp4','.webm','.woff','.woff2','.ttf','.otf','.pdf'}

def remote(value,path):
    url=urlsplit(urljoin(HOST+path,value))
    if url.netloc!='ravcu.github.io' or not url.path.startswith('/turkce-akademi/'):return value
    name=unquote(url.path.removeprefix('/turkce-akademi/'))
    if Path(name).suffix.lower() not in EXTENSIONS or not (ROOT/name).is_file():return value
    return MEDIA+quote(name,safe='/')+('?' + url.query if url.query else '')+('#'+url.fragment if url.fragment else '')

def prepare(source,path):
    if not re.search(r'<head\b',source,re.I):return source
    parts=re.split(r'(<script\b[^>]*>[\s\S]*?</script>)',source,flags=re.I)
    for i,part in enumerate(parts):
        if re.match(r'<script\b',part,re.I):continue
        part=re.sub(r'(\b(?:src|poster|href)\s*=\s*)([\"\'])(.*?)[\"\']',lambda m:m[1]+m[2]+remote(m[3],path)+m[2],part,flags=re.I)
        parts[i]=re.sub(r'url\(\s*([\"\']?)([^)\"\']+)\1\s*\)',lambda m:'url('+m[1]+remote(m[2],path)+m[1]+')',part)
    output=''.join(parts)
    if 'assets/js/media-loader.js' not in output:
        output=re.sub(r'(<head\b[^>]*>)',lambda m:m[1]+LOADER,output,count=1,flags=re.I)
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    changed=[]
    for file in [ROOT/'index.html',*sorted((ROOT/'kitaplar').rglob('*.html'))]:
        source=file.read_text();output=prepare(source,file.relative_to(ROOT).as_posix())
        if output!=source:
            changed.append(str(file.relative_to(ROOT)))
            if not args.check:file.write_text(output)
    print(('Need preparation: ' if args.check else 'Prepared: ')+str(len(changed))+' pages')
    if args.check and changed:print('\n'.join(changed));raise SystemExit(1)
