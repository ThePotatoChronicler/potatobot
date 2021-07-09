#1.
# @add_command()
# async def christmas(m):
#     if len(m.content.split()) > 1:
#         await m.channel.send(("".join([chr((len(x) % 27) + 96) if len(x) != 27 else " " for x in m.content.strip().split()[1:]])).capitalize())
#     else:
#         await m.channel.send('Usage: ``p!christmas [message]``')

#2.


# @add_command(("christmas", "christmas2", "christmas3", "christmas4", "christmas5"))
# async def christmas(m):
#     await m.channel.send('Thanks, <@483737489463443456>')


@add_command()
async def christmas(m):
    if len(m.content.split()) > 1:
        await m.channel.send(("".join([
            chr((len(x) % 27) + 96) if len(x) != 27 else " "
            for x in m.content.strip().split()[1:]
        ])).capitalize())
    else:
        await m.channel.send('Usage: ``p!christmas [message]``')


@add_command()
async def christmas2(m):
    if len(m.content.split()) > 1:
        await m.channel.send("".join([
            chr(((len(x) + i) % 27) + 96) if len(x) != 27 else " "
            for i, x in enumerate(m.content.split()[1:])
        ]).capitalize())
    else:
        await m.channel.send('Usage: ``p!christmas2 [message]``')


@add_command()
async def christmas3(m):
    if len(m.content.split()) > 1:
        await m.channel.send("".join([
            chr(((len(x) + (i**2) + len(m.author.display_name)) % 27) + 96) if
            (len(x) + (i**2) + len(m.author.display_name)) % 27 != 0 else " "
            for i, x in enumerate(m.content.split()[1:])
        ]).capitalize().replace('@', ' '))
    else:
        await m.channel.send('Usage: ``p!christmas3 [message]``')


@add_command()
async def christmas4(m):
    if len(m.content.split()) > 1:
        await m.channel.send("".join([
            chr(max((len(x) + (i**2)), 0))
            for i, x in enumerate(m.content.split()[1:])
        ]).capitalize().replace('@', ' '))
    else:
        await m.channel.send('Usage: ``p!christmas4 [message]``')


@add_command()
async def christmas5(m):
    if len(m.content.split()) > 1:
        prc = lambda x: ord(x)**2
        await m.channel.send(("".join([
            chr(sum(map(prc, x)) % 1114111) for x in m.content.split()[1:]
        ])).capitalize().replace('@', ' '))
    else:
        await m.channel.send('Usage: ``p!christmas5 [message]``')
