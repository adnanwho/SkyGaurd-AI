import re

with open('web/app.js', 'r') as f:
    js = f.read()

ids_in_js = set(re.findall(r"\$\('([^']+)'\)", js))
print('IDs referenced in JS:', sorted(ids_in_js))

with open('web/index.html', 'r') as f:
    html = f.read()

ids_in_html = set(re.findall(r'id="([^"]+)"', html))
print('IDs in HTML:', sorted(ids_in_html))

missing = ids_in_js - ids_in_html
extra = ids_in_html - ids_in_js
print('Missing from HTML:', sorted(missing))
print('Extra in HTML (not used by JS):', sorted(extra))
