output = ""

for b in map(ord, input):
    output += chr(b ^ 11)
