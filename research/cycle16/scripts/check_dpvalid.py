import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://amsacta.unibo.it/id/eprint/7710/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        html = resp.read().decode('utf-8')
        titles = re.findall(r'<title>(.*?)</title>', html, re.I | re.S)
        print('Page title:', titles)
        # Find all download links / documents
        links = re.findall(r'href="([^"]+)"', html)
        ams_links = [l for l in links if 'amsacta.unibo.it' in l or '/7710/' in l]
        print('Matching links count:', len(ams_links))
        for l in sorted(set(ams_links)):
            print('LINK:', l)
except Exception as e:
    print('Error:', e)
