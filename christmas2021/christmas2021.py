output = ""
ec = False
cur = 64
for i in map(ord, input):
  if ec:
    cur = cur ^ abs(i - old) ^ 32
    output += chr(cur)
  old = i
  ec = True
