import urllib.request
import re

url = 'https://blog.dejavu.moe/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        gen_match = re.search(r'<meta name="generator" content="([^"]+)"', html)
        if gen_match:
            print('Generator:', gen_match.group(1))
            
        print('First 1000 chars:')
        print(html[:1000])
except Exception as e:
    print('Error:', e)
