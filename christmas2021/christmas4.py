def remove_first_word(s : str):
    """
    Removes first word and the first whitespace after it
    """
    return s[len(s.split()[0]) + 1:]

output = ""

for c, n in zip(map(ord, remove_first_word(m.content)), map(ord, m.author.display_name)):
    output += chr((c ^ n) ^ ((m.created_at.minute & 1) << 8))
