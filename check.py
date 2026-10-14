#!/usr/bin/env python3
import importlib.util
import copy
import json
import tempfile
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"dist"
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs=[];self.ids=[];self.h1=0;self.main=0;self.meta=[];self.title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h1": self.h1+=1
        if tag=="main": self.main+=1
        if tag=="title": self.title=True
        if tag=="meta": self.meta.append(a)
        if "id" in a: self.ids.append(a["id"])
        if tag=="img": assert "alt" in a
        for attr in ("href","src"):
            if a.get(attr): self.refs.append(a[attr])
parsed={}
for path in OUT.rglob("*.html"):
    p=Parser();p.feed(path.read_text());parsed[path.resolve()]=p
    assert p.h1==1 and p.main==1, str(path)
    assert len(p.ids)==len(set(p.ids)), str(path)
    assert p.title and any(m.get("name")=="description" for m in p.meta)
    assert all(t not in path.read_text() for t in ("LaPierre","YOUR_EMAIL",'href="#"',"@/"))
count=0
for path,p in parsed.items():
    if path.name=="404.html": continue
    for ref in p.refs:
        u=urlparse(ref)
        if u.scheme or u.netloc: continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if target.is_dir():target=target/"index.html"
        assert target.is_relative_to(OUT.resolve()) and target.is_file(), (path,ref)
        if u.fragment and target in parsed: assert u.fragment in parsed[target].ids,(path,ref)
        count+=1
data=json.loads((ROOT/"content/portfolio.json").read_text())
assert data["name"]=="Aiden Lapierre"
assert [c["award"] for c in data["conferences"]]==["","Honorable mention for best delegate","Honorable mention for best delegate","Honorable mention for best delegate","Best delegate"]
if not data["contact"]["approved"]:assert "mailto:" not in (OUT/"contact/index.html").read_text()
print(f"PASS: {len(parsed)} HTML documents, {count} local links, metadata, IDs, spelling, awards and contact privacy")
spec=importlib.util.spec_from_file_location("portfolio_build",ROOT/"build.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as directory:
    temp=Path(directory);m.ROOT=temp;m.OUT=temp/"dist"
    (temp/"assets").mkdir()
    (temp/"assets/test.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="30" height="20"><rect width="30" height="20" fill="gray"/></svg>')
    m.DATA=copy.deepcopy(m.DATA)
    m.DATA["galleries"][0]["photos"]=[{"src":"assets/test.svg","width":30,"height":20,"title":"Test image","alt":"Synthetic rectangle for validation","featured":True,"variants":[{"src":"assets/test.svg","width":30}]}]
    m.main()
    gallery=(m.OUT/"photography/landscape/index.html").read_text()
    assert 'data-full="../../assets/test.svg"' in gallery
    assert 'srcset="../../assets/test.svg 30w"' in gallery
    assert '<dialog id="viewer"' in gallery and 'aria-label="View Test image"' in gallery
    assert 'fetchpriority="high"' in (m.OUT/"index.html").read_text()
    m.DATA["galleries"][0]["photos"][0]["src"]="../secret.txt"
    try:m.validate()
    except ValueError:pass
    else:raise AssertionError("Unsafe path accepted")
print("PASS: populated photograph build, responsive image variants, viewer markup and unsafe-path rejection")
subprocess.run(["node","--check",str(ROOT/"assets/gallery.js")],check=True)
print("PASS: JavaScript syntax")
