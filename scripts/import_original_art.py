"""Import original public Google Sites images into GitHub Pages assets."""
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from pathlib import Path
from io import BytesIO
import re
from PIL import Image

SOURCE = "https://sites.google.com/view/atom-first-biology/home"
OUT = Path("assets/original")
OUT.mkdir(parents=True, exist_ok=True)

def fetch(url):
    req = Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urlopen(req, timeout=35) as response:
        return response.read()

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        if tag != "img": return
        a = dict(attrs)
        for key in ("src","data-src"):
            u = a.get(key,"")
            if u.startswith("http"): self.urls.append(u)
html = fetch(SOURCE).decode("utf-8",errors="replace")
p=Images();p.feed(html)
urls=list(dict.fromkeys(p.urls))
images=[]
for url in urls:
    try:
        data=fetch(url)
        im=Image.open(BytesIO(data))
        w,h=im.size
        if w >= 900 and h >= 160:
            images.append((w,h,data,url))
    except Exception as e:
        print("Skipped:",str(e)[:120])
print("Found large images:",[(x[0],x[1]) for x in images])
# The original homepage uses a wide painted header and an illustrated atom-scale strip.
headers=[x for x in images if x[0]/x[1] >= 2.8 and x[1] >= 260]
strips=[x for x in images if x[0]/x[1] >= 3.5 and x[1] <= 300]
if not headers or not strips:
    raise RuntimeError("Original image matches not found; no placeholder images will be committed.")
for item,name in [(headers[0],"header-art.jpg"),(strips[0],"atom-scale.png")]:
    im=Image.open(BytesIO(item[2])).convert("RGB" if name.endswith(".jpg") else "RGBA")
    im.save(OUT/name)
    print("Saved",name,im.size)
