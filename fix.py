with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix SOS - move left so zoom controls visible
old1 = 'bottom:42px; right:10px; z-index:500;\n            background:#cc0000;'
new1 = 'bottom:42px; right:52px; z-index:500;\n            background:#cc0000;'
content = content.replace(old1, new1)

# Fix GPS - move left too
old2 = 'bottom:80px; right:10px; z-index:500;\n            background:var(--panel); border:1px solid var(--accent);'
new2 = 'bottom:80px; right:52px; z-index:500;\n            background:var(--panel); border:1px solid var(--accent);'
content = content.replace(old2, new2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')