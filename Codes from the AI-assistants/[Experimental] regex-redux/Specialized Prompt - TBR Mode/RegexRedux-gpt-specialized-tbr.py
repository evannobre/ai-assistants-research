import sys, re
text = sys.stdin.read()
rules = [(re.compile(pat), rep) for pat,rep in patterns]
total = 0
changed = True
while changed:
    changed = False
    for regex, rep in rules:
        new, cnt = regex.subn(rep, text)
        if cnt > 0:
            total += cnt
            text = new
            changed = True
print(total)
