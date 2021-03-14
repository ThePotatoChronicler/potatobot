import os
from keep_alive import keep_alive # repl.it keep_alive function

print('Starting Potato Overlord!')

import discord
import requests
import datetime
import sqlite3 as sqlite

database                = sqlite.Connection('data.db')    # Database
dbcursor                = database.cursor()               # Cursor to edit the database with
prefix                  = 'p!'                            # Prefix
version                 = '0.6.9 - Malice'                # Version
intents                 = discord.Intents.default()       # Default intents
intents.members         = True                            # So that bot can access members
defment                 = discord.AllowedMentions(everyone=False, roles=False, users=True)
client                  = discord.Client(intents=intents) # Create client
client.allowed_mentions = defment                         # Sets who can be mentioned

commandsDict = {}  # Globalization


def add_command(alias=None):
    def wrapper(function):
        if alias == None:
            commandsDict[str(function.__name__)] = function
        else:
            for name in tuple(alias):
                commandsDict[str(name)] = function

    return wrapper

def save_sort_to_db(t, m_id, c_id, a, l):
    li = ' '.join(str(i) for i in l)
    dbcursor.execute('SELECT message FROM sorts WHERE message = ?', [m_id])

    if dbcursor.fetchone():
        dbcursor.execute('UPDATE sorts SET amount = ?, list = ? WHERE message = ?', (a, li, m_id))
    else:
        dbcursor.execute('INSERT INTO sorts(type, message, channel, amount, list) VALUES(?, ?, ?, ?, ?)', (t, m_id, c_id, a, li))

    database.commit()

def remove_sort_from_db(m_id):
    dbcursor.execute('DELETE FROM sorts WHERE ?', [m_id])

    database.commit()

def board(lin, symbol='#', height=10):
    try:
        lint = lin.copy()
        lmax = max(lint)
        lmin = min(lint)
        out = ['' for _ in range(height)]
        for value in lint:
            a = round(height * ((value - lmin) / (lmax - lmin)))
            for i, _ in enumerate(out):
                if a >= i:
                    out[i] = out[i] + symbol
                else:
                    out[i] = out[i] + ' '

        return "\n".join(out[::-1])
    except ZeroDivisionError:
        return (symbol + '\n') * 10


def boardgen(lin, symbol='#', symbolv='@', height=10):
    pass


@add_command()
async def nonamechange(m):
    if m.author.guild_permissions.manage_nicknames:
        for role in m.guild.get_member(int(m.content.split()[1])).roles:
            if role.name == 'Unchanging':
                await m.guild.get_member(
                    int(m.content.split()[1])
                ).remove_roles(role,
                    reason=
                    f'Issued command by {m.author.display_name + "#" + m.author.discriminator}'
                )
                return
        else:
            for role in m.guild.roles:
                if role.name == 'Unchanging':
                    await m.guild.get_member(
                        int(m.content.split()[1])
                    ).add_roles(
                        role,
                        reason=
                        f'Issued command by {m.author.display_name + "#" + m.author.discriminator}'
                    )
                    return

    else:
        m.channel.send('You need ``Manage Nicknames`` permission to do this!')


@add_command(('version', 'ver'))
async def ver(m):
    await m.channel.send(f'Potato Overlord version: {version}')


@add_command()
async def ping(m):
    await m.channel.send(
        f'Pong! `{datetime.datetime.now(tz=datetime.timezone.utc) - m.created_at.replace(tzinfo=datetime.timezone.utc)}`'
    )


@add_command()
async def pong(m):
    await m.channel.send(
        f'Ping! `{datetime.datetime.now(tz=datetime.timezone.utc) - m.created_at.replace(tzinfo=datetime.timezone.utc)}`'
    )


@add_command()
async def lockdown(m):
    overwrite = m.channel.overwrites_for(m.guild.default_role)
    overwrite.send_messages = False
    moderator = False

    # Checks if the person is a mod
    for role in m.author.roles:
        if role.name == 'Moderator' or role.name == 'moderator':
            moderator = True
            break

    if moderator or m.author.guild_permissions.manage_channels:
        await m.channel.set_permissions(m.guild.default_role, overwrite=overwrite,
                                        reason=f"Command sent by {m.author.name}#{m.author.discriminator}")
        await m.channel.send(f"Aight, locked down on behalf of {m.author.mention}.")
    else:
        await m.channel.send("You do not have the right to do this", delete_after=5)


@add_command()
async def unlockdown(m):
    overwrite = m.channel.overwrites_for(m.guild.default_role)
    overwrite.send_messages = True
    moderator = False

    # Checks if the person is a mod
    for role in m.author.roles:
        if role.name == 'Moderator' or role.name == 'moderator':
            moderator = True
            break

    if moderator or m.author.guild_permissions.manage_channels:
        await m.channel.set_permissions(m.guild.default_role, overwrite=overwrite,
                                        reason=f"Command sent by {m.author.name}#{m.author.discriminator}")
        await m.channel.send(f"Aight, unlocked on behalf of {m.author.mention}.")
    else:
        await m.channel.send("You do not have the right to do this", delete_after=5)

@add_command()
async def commands(m):
    await m.channel.send(
        f'List of commands: `{", ".join(sorted(list(commandsDict.keys())))}`'
    )


@add_command()
async def xkcd(m):
    if len(m.content.split()) == 1:
        from random import randint
        await m.channel.send(f'https://xkcd.com/{randint(1, 2422)}/')
        return
    elif len(m.content.split()) == 2:
        try:
            await m.channel.send(
                f'https://xkcd.com/{int(m.content.split()[1])}/')
            return
        except ValueError:
            await m.channel.send(
                f'``{m.content.split()[1]}`` isn\'t an integer!')


@add_command()
async def cat(m):
    await m.channel.send(
        requests.get('https://api.thecatapi.com/v1/images/search').json()[0]
        ['url'])


@add_command()
async def dog(m):
    await m.channel.send(
        requests.get('https://api.thedogapi.com/v1/images/search').json()[0]
        ['url'])


@add_command()
async def ownermail(m):
    await m.delete()
    if len(m.content.split()) > 1:
        await m.guild.owner.send(
            f'Channel: {m.channel.mention} in {m.guild.name}\nMember: {m.author.mention} ({m.author.name}#{m.author.discriminator})\nMessage: {" ".join(m.content.split()[1:])}'
        )
    else:
        await m.channel.send(
            f'Usage: `{prefix}ownermail [message]`', delete_after=2)


@add_command()
async def modmail(m):
    await m.delete()
    if len(m.content.split()) > 1:
        for role in m.guild.roles:
            if role.name == 'Moderator':
                for member in role.members:
                    await member.send(
                        f'Channel: {m.channel.mention} in {m.guild.name}\nMember: {m.author.mention} ({m.author.name}#{m.author.discriminator})\nMessage: {" ".join(m.content.split()[1:])}'
                    )
                if not m.guild.owner in role.members:
                    await m.guild.owner.send(
                        f'**Modmail**\nChannel: {m.channel.mention} in {m.guild.name}\nMember: {m.author.mention} ({m.author.name}#{m.author.discriminator})\nMessage: {" ".join(m.content.split()[1:])}'
                    )
                break
    else:
        await m.channel.send(
            f'Usage: `{prefix}modmail [message]`', delete_after=2)


# @add_command2(('bogosort', 'bogo'))
# async def bogosort(m):
#     from random import shuffle
#     amount = 0
#     board = boardgen()
#     if len(m.content.split()) < 2:
#         return
#     message = await m.channel.send('Starting bogosort!')
#     sort = [int(x) if float(x)%1 == 0 else float(x) for x in m.content.split()[1:]]
#     while not all(x <= y for x, y in zip(sort, sort[1:])):
#         await message.edit(content=f'```{board(sort)}```Shuffles: ``{amount}``')
#         shuffle(sort)
#         amount += 1

#     await message.edit(content=f"```{board(sort)}```Sorted in {amount} shuffle{'' if amount == 1 else 's'}! {sort}")


@add_command(('bogosort', 'bogo'))
async def bogosort(m):
    from random import shuffle
    amount = 0
    if len(m.content.split()) < 2:
        return
    message = await m.channel.send('Starting bogosort!')
    sort = [
        int(x) if float(x) % 1 == 0 else float(x)
        for x in m.content.split()[1:]
    ]

    while not all(x <= y for x, y in zip(sort, sort[1:])):
        await message.edit(content=f'```{board(sort)}```Shuffles: ``{amount}``'
                           )
        shuffle(sort)
        amount += 1

        if amount % 20 == 0:
            save_sort_to_db(0, message.id, m.channel.id, amount, sort)

    await message.edit(
        content=
        f"```{board(sort)}```Sorted in {amount} shuffle{'' if amount == 1 else 's'}! {sort}"
    )
    remove_sort_from_db(message.id)


@add_command(('bubblesort', 'bubble'))
async def bubblesort(m):
    amount = 0
    if len(m.content.split()) < 2:
        return
    message = await m.channel.send('Starting bubblesort!')
    sort = [
        int(x) if float(x) % 1 == 0 else float(x)
        for x in m.content.split()[1:]
    ]

    for i in range(len(sort)):
        for j in range(len(sort) - 1 - i):
            await message.edit(
                content=f"```{board(sort)}```Comparisons: ``{amount}``")
            if sort[j] > sort[j + 1]:
                sort[j], sort[j + 1] = sort[j + 1], sort[j]
            amount += 1

            if amount % 20 == 0:
                save_sort_to_db(1, message.id, m.channel.id, amount, sort)

    await message.edit(
        content=
        f"```{board(sort)}```Sorted in {amount} comparison{'' if amount == 1 else 's'}! {sort}"
    )
    remove_sort_from_db(message.id)


@add_command(('insertionsort', 'insertion'))
async def insertionsort(m):
    amount = 0
    if len(m.content.split()) < 2:
        return
    message = await m.channel.send('Starting insertionsort!')
    sort = [
        int(x) if float(x) % 1 == 0 else float(x)
        for x in m.content.split()[1:]
    ]

    for i in range(1, len(sort)):
        key = sort[i]
        j = i - 1
        while j >= 0 and key < sort[j]:
            amount += 2
            sort[j + 1] = sort[j]
            j -= 1
            if amount % 20 == 0:
                save_sort_to_db(2, message.id, m.channel.id, amount, sort)
            await message.edit(
                content=f'```{board(sort)}```Comparisons: ``{amount}``')
        else:
            amount += 1
        sort[j + 1] = key
        await message.edit(
            content=f'```{board(sort)}```Comparisons: ``{amount}``')

    await message.edit(
        content=
        f"```{board(sort)}```Sorted in {amount} comparison{'' if amount == 1 else 's'}! {sort}"
    )
    remove_sort_from_db(message.id)




@client.event
async def on_ready():  # Executes when bot connects
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name='p! >w>'))
    print('Potato Overlord is ready!')
    
    funcs = []

    # Bogosort
    async def f1(m_id, c_id, a, l):
        from random import shuffle
        amount = a
        message = client.get_channel(c_id).get_partial_message(m_id)
        sort = [
            int(x) if float(x) % 1 == 0 else float(x)
            for x in l.split(' ')
        ]

        while not all(x <= y for x, y in zip(sort, sort[1:])):
            await message.edit(content=f'```{board(sort)}```Shuffles: ``{amount}``'
                               )
            shuffle(sort)
            amount += 1

            if amount % 20 == 0:
                save_sort_to_db(0, m_id, c_id, amount, sort)

        await message.edit(
            content=
            f"```{board(sort)}```Sorted in {amount} shuffle{'' if amount == 1 else 's'}! {sort}"
        )
        remove_sort_from_db(m_id)

    funcs.append(f1)

    # Bubblesort
    async def f2(m_id, c_id, a, l):
        amount = a
        message = client.get_channel(c_id).get_partial_message(m_id)
        sort = [
            int(x) if float(x) % 1 == 0 else float(x)
            for x in l.split(' ')
        ]

        for i in range(len(sort)):
            for j in range(len(sort) - 1 - i):
                await message.edit(
                    content=f"```{board(sort)}```Comparisons: ``{amount}``")
                if sort[j] > sort[j + 1]:
                    sort[j], sort[j + 1] = sort[j + 1], sort[j]
                amount += 1

                if amount % 20 == 0:
                    save_sort_to_db(1, m_id, c_id, amount, sort)

        await message.edit(
            content=
            f"```{board(sort)}```Sorted in {amount} comparison{'' if amount == 1 else 's'}! {sort}"
        )
        remove_sort_from_db(m_id)

    funcs.append(f2)

    async def f3(m_id, c_id, a, l):
        amount = a
        message = client.get_channel(c_id).get_partial_message(m_id)
        sort = [
            int(x) if float(x) % 1 == 0 else float(x)
            for x in l.split(' ')
        ]

        for i in range(1, len(sort)):
            key = sort[i]
            j = i - 1
            while j >= 0 and key < sort[j]:
                amount += 2
                sort[j + 1] = sort[j]
                j -= 1
                save_sort_to_db(2, m_id, c_id, amount, sort)
                await message.edit(
                    content=f'```{board(sort)}```Comparisons: ``{amount}``')
            else:
                amount += 1
            sort[j + 1] = key
            await message.edit(
                content=f'```{board(sort)}```Comparisons: ``{amount}``')

        await message.edit(
            content=
            f"```{board(sort)}```Sorted in {amount} comparison{'' if amount == 1 else 's'}! {sort}"
        )
        remove_sort_from_db(m_id)

    funcs.append(f3)

    # Restart all saved sorts
    dbcursor.execute('SELECT * FROM sorts')
    for fetched in dbcursor.fetchall():
        t, *args = fetched
        await funcs[t](*args)


@client.event
async def on_disconnect():  # Executes when bot loses connection
    print('Disconnected!')


@client.event
async def on_message(m):  # Executes on every message

    # Exit if message was sent by the bot
    if m.author == client.user:
        return

    # Checks if sent from a guild
    if isinstance(m.channel,
                  discord.TextChannel):  # Checks if it was sent in a guild
        if (m.channel.name == 'letter_wars' or m.channel.name == 'letter-wars'
            ) and not len(m.content.strip()) == 1:
            await m.delete()
            return

        if m.channel.name == 'hex_wars' or m.channel.name == 'hexadecimal_wars':
            await m.delete()
            await m.channel.send(
                discord.utils.escape_mentions(
                    f'{m.author.display_name} : {m.content.encode("utf-8").hex()}'
                ).replace(':', r'\:'))
            return

        if m.channel.name == 'binary-wars' or m.channel.name == 'binary_wars':
            await m.delete()
            await m.channel.send(
                f'{m.author.display_name} : {"".join(bin(ord(x))[2:] for x in m.content)}'
            )
            return

        if m.content.startswith(prefix):
            try:
                await commandsDict[f'{m.content.split()[0][len(prefix):]}'](m)
            except KeyError:
                await m.channel.send('Command doesn\'t exist!')
            except Exception as e:
                await m.author.send('An error has occured, you should contact Potato with the following error:')
                await m.author.send(e)
                raise e

    else:
        if m.author.id == 185421198094499840 and m.content == 'close':
            m.channel.send('Closing.')
            await client.close()


@client.event
async def on_member_update(bm, am):
    for role in am.roles:
        if role.name == 'Unchanging' and am.display_name != am.name:
            await am.edit(nick=None, reason=f'Has the Unchanging role.')
            return


@client.event
async def on_message_edit(mb, ma):
    if (ma.channel.name == 'letter_wars' or ma.channel.name == 'letter-wars'
        ) and not len(ma.content.strip()) == 1:
        await ma.delete()


keep_alive()  # Starts a webserver to be pinged.
token = os.environ.get("DISCORD_BOT_TOKEN")
client.run(token)

database.close()
