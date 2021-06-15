import os
from keep_alive import keep_alive # repl.it keep_alive function

print('Starting Potato Overlord!')

import potatoscript
import art
import asyncio
import discord
import discord.ext.commands
import requests
import datetime
import sqlite3 as sqlite

database                = sqlite.Connection('data.db')    # Database
user_code_file          = 'luacode/'                      # Location of user code
dbcursor                = database.cursor()               # Cursor to edit the database with
prefix                  = 'p!'                            # Prefix
version                 = 'V121 - Wrath'                  # Version
potatoid                = 185421198094499840              # My discord ID
intents                 = discord.Intents.default()       # Default intents
intents.members         = True                            # So that bot can access members
intents.presences       = True                            # So that the bot can access statusses
defment                 = discord.AllowedMentions(everyone=False, roles=False, users=True)
client                  = discord.ext.commands.Bot(prefix, None, intents=intents) # Create client
client.allowed_mentions = defment                         # Sets who can be mentioned

onreadyonce = False # Stops on_ready from firing multiple times
commandsDict = {} # Globalization
reactionDict = {} # My reaction API
storageDict = {} # Global storage for commands
spamDict = {} # Preventing spam/bot abuse

class Command():
    """
    A wrapper around a python function.
    """
    from typing import Coroutine as coro
    def __init__(func : coro, /):
        pass

def add_command(alias=None, timeout=5, emoji=False, *args, **kwargs):
    def wrapper(function):
        comdict = {
            'function': function,
            'timeout': timeout,
            'emoji': emoji,
            'args': args,
            **kwargs
        }
        if alias == None:
            commandsDict[function.__name__] = comdict
        else:
            for name in alias:
                commandsDict[name] = comdict

    return wrapper

def save_sort_to_db(t, m_id, c_id, a, l):
    li = ' '.join(str(i) for i in l)
    dbcursor.execute('SELECT message FROM sorts WHERE message = ?', (m_id, ))

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

        return '\n' + '\n'.join(out[::-1])
    except ZeroDivisionError:
        return '\n' + (symbol + '\n') * 10


# This will definitely not go horribly wrong eventually
def clean_filename(s : str):
    """
    A really bad function to clean a filename
    from messing with the filesystem.
    """
    return s.replace('/', '_').replace('.', '_').replace('*', '_')


# Why do I keep this here???
# I have no plans of making it anytime soon, so why . _.
def boardgen(lin, symbol='#', symbolv='@', height=10):
    pass


@add_command(['quote'])
async def _(m : discord.Message):
    """
    `{prefix}quote id`

    Retrieves a quote from the entered id.
    """
    if len(m.content.split()) < 2:
        await m.channel.send("ID is required")
        return

    try:
        # Cannot use variable id
        # because of builtin
        quoteid = int(m.content.split()[1])
    except ValueError:
        await m.channel.send("Invalid ID!")
        return

    if quoteid < 0:
        await m.channel.send("ID must be an integer higher or equal to 0")
        return

    dbcursor.execute("SELECT quote FROM quotes WHERE id = ?", (quoteid, ))
    quote = dbcursor.fetchone()
    if quote == None:
        await m.channel.send("No such quote exists!")
    else:
        await m.channel.send(quote[0])

@add_command(['addquote'])
async def _(m : discord.Message):
    """
    `{prefix}addquote id quote`

    Adds a quote to the database at the entered id,
    adding or overwriting the quote
    that is already at that id.
    """
    if len(m.content.split()) < 3:
        await m.channel.send("Not enough arguments!")
        return

    try:
        # Cannot use variable id
        # because of builtin
        quoteid = int(m.content.split()[1])
    except ValueError:
        await m.channel.send("Invalid ID!")
        return

    if quoteid < 0:
        await m.channel.send("ID must be an integer higher or equal to 0")
        return

    quote = m.content.split(None, 2)[2]

    dbcursor.execute("REPLACE INTO quotes(id, quote) VALUES(?, ?)", (quoteid, quote))
    database.commit()

@add_command(['execute'])
async def _(m):
    """
    `{prefix}execute ?`

    ???
    """
    from inspect import cleandoc
    order = {
        1 : "We are number one!",
        5 : "A new potato is summoned!",
        7 : "Couldn't hold me back",
        10 : "On harder mode!",
        13 : "You won't live past tonight.",
        42 : "Shiva Gautama Christ-chan",
        45 : "II",
        64 : "Stack",
        66 : "Disabled devil",
        68 : "So close",
        69 : "Nice",
        70 : "Just missed it",
        420 : "( ͡ʘ ͜ʖ ͡ʘ)",
        475 : "It's a biiiiiiiiiinge compilation",
        666 : "]:->",
        1337 : "Did you install Kali Linux?",
        1945 : cleandoc("""
                        ⠄⠄⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡄⠄⠄⠄⠄⠄⠄⠄⠄⠄
                        ⠄⠄⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⠄⠄⠄⠄⠄⠄⠄⠄
                        ⠄⢾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠄⠄⠄⠄⠄⠄
                        ⣀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠄⠄⠄⠄⠄⠄
                        ⢻⣿⣿⣿⣿⣿⣿⣿⡟⢿⠿⠿⠢⡈⠻⠿⢿⡿⣿⣿⣿⣿⣿⣿⡆⠄⠄⠄⠄⠄
                        ⢨⣿⣿⣿⣿⣿⣿⣿⣷⡆⠄⠄⠄⠄⠙⠳⣦⣌⣉⡛⠻⠿⠿⢏⡀⠄⠄⠄⠄⠄
                        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣁⠄⢀⠄⠄⠄⠄⠄⠙⣻⣿⣿⣧⡀⠄⠈⠑⠢⢀⠄⠄
                        ⠄⠄⠈⠉⠋⠙⣿⣿⠉⠠⡲⣶⠢⠄⠄⠄⡄⢾⢛⣿⣯⢽⣿⣷⣄⠄⠄⠄⠈⠒
                        ⠄⠄⠄⠄⠄⢀⣿⣿⠄⠄⠄⠄⠄⠄⠄⠈⣕⠘⠋⢸⡇⠈⠛⠿⢿⣷⣦⡀⠄⢀
                        ⠄⠄⠄⠄⠄⠘⣿⣿⣆⡀⠄⠄⠄⠄⠄⣀⡍⣀⣀⡰⠄⠄⠄⠄⠄⠙⢯⣿⣿⣿
                        ⠄⠄⠄⠄⠄⠄⠹⣿⣿⣧⠗⡚⠚⠄⠄⠙⢿⢟⡿⠁⠄⠄⠄⠄⠄⠄⠄⠈⠁⠄
                        ⠄⠄⠄⠄⠄⠄⠄⠉⢿⣿⡀⠄⠄⠄⠄⠄⢼⡞⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
                        ⠄⠄⠄⠄⠄⠄⠄⠄⠈⢻⣇⠄⠄⠤⠤⠴⡿⠁⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
                        ⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠙⠳⣤⡤⠤⠶⠃⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄
                        """),
        2004 : "Terrible tragedy",
        2012 : "The end of the world?",
        2020 : "We don't have enough toilet paper",
        2021 : "We still don't have enough toilet paper",
        2077 : "Delayed",
        6666 : "Woah, too evil!",
        7470 : "Tato hath cometh",
        80082 : "( ͡° ͜ʖ ͡°)",
        177013 : "No, stop, don't, please, don't *cries*",
        345431 : "WAY AWAY AWAY FROM HERE I'LL BE, WAY AWAY AWAY SO YOU CAN SEE",
    }

    try:
        await m.channel.send(order[int(m.content.split()[1])])
        return
    except:
        raise KeyError()

    raise KeyError()


@add_command(['help'], 12)
async def _(m):
    """
    `{prefix}help (commandname)`

    Shows help of any command.
    """
    try:
        name = m.content.split()[1]
        cdict = commandsDict[name]
    except IndexError:
        name = 'help'
        cdict = commandsDict[name]
    except KeyError:
        await m.channel.send('Cannot find this command!')
        return

    doc = cdict['function'].__doc__
    if doc:
        from inspect import cleandoc
        await m.channel.send(f"Showing documentation for {name}:\n{cleandoc(doc.format(prefix=prefix))}")
    else:
        await m.channel.send('Can\'t find any documentation, sorry!')


@add_command()
async def nonamechange(m):
    """
    `{prefix}nonamechange (user)`

    Moderators only. Requires the **Unchanging** role in this server.
    Makes the user unable to rename themselves.
    """
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


@add_command(['emojipurge'], 30)
async def _(m):
    """
    `{prefix}emojipurge`
    `{prefix}emojipurge true`

    Server owner only.
    Deletes all emojis from the server,
    *except* those whose names start with `_`.
    To also delete animated emojis, add true.
    May take a while to finish.

    __**THIS ACTION CANNOT BE TAKEN BACK.**__
    """
    if m.guild.owner.id == m.author.id:
        await m.channel.send("Purging.")
        animated = False

        if len(m.content.split()) >= 2:
            if m.content.split()[1] == "true":
                animated = True

        for emoji in m.guild.emojis:
            if not emoji.name.startswith('_'):
                if (not emoji.animated) or (emoji.animated and animated):
                    await emoji.delete(reason=f"Command executed by {m.author.name}#{m.author.discriminator}")
    else:
        await m.channel.send("You're not the owner!", delete_after=3)


@add_command(['spam'])
async def _(m):
    """
    `{prefix}spam`

    :)
    """
    if m.author.id != 185421198094499840:
        raise KeyError("Not allowed m8")

    i = 0
    while i < int(m.content.split()[1]):
        await m.channel.send(' '.join(m.content.split(' ')[2:]))
        i += 1


@add_command()
async def joinchannel(m):
    """
    `{prefix}joinchannel`

    Server owner only.
    Makes the specified channel the welcome channel.
    """
    if m.guild.owner == m.author:
        dbcursor.execute('UPDATE servers SET join_chat = ? WHERE server = ?', (m.channel.id, m.guild.id))
        database.commit()
    else:
        await m.delete()
        await m.channel.send('You do not have the permission!', delete_after=5)


@add_command(['potatoscript', 'script', 'ps'])
async def _(m):
    """
    `{prefix}potatoscript`
    ```

    code

    ```

    Runs your message in Potatoscript,
    a custom assembly-like scripting language.

    Discontinued.
    """

    await m.channel.send('This is a discontinued feature, go away >:[')
    return

    try:
        ps = potatoscript.potatoscript('\n'.join(m.content.split('\n')[1:]))
        out = ps()
        await m.channel.send(f"__Output:__\n{ps.output}\n__Return:__\n{out}")
    except Exception as e:
        await m.channel.send(e)


@add_command(['lua'], 8)
async def _(m):
    """
    __**WIP**__

    `{prefix}lua`
    ```
    code
    ```

    `{prefix}lua save name`
    ```
    code
    ```

    `{prefix}lua run name`
    input

    Runs a safe Lua interpreter with
    limited capabilities.

    When saving and running code, the global value "input"
    will be set by the user input.

    You don't wanna see the source code for this,
    it's a total mess.
    """
    from re import search, DOTALL
    from time import time as unix_time
    from os import remove as removefile
    from asyncio import create_subprocess_exec as subexec
    from asyncio.subprocess import PIPE

    code_file = f'{user_code_file}__process-{unix_time()}__'

    inp = m.content.split(None, 1)
    if len(inp) == 1:
        inp = ''
    else:
        inp = inp[1]
        match = search(r"```lua(\n.*)```", inp, DOTALL)
        if match:
            inp = match.group(1)
        else:
            match = search(r"```(\n.*)```", inp, DOTALL)
            if match:
                inp = match.group(1)
            else:
                inp = ''

    first_line = m.content.split('\n', 1)[0].split()

    if len(first_line) >= 3:
        user_code_save = user_code_file + clean_filename(' '.join(first_line[2:]))
        if first_line[1] == 'save':
            if not inp:
                await m.channel.send('No codeblock found!')
                return
            with open(code_file, 'w') as luacodefile:
                luacodefile.write(inp)
            cor = await subexec('./luac', '-o', user_code_save, code_file, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            await cor.wait()
            removefile(code_file)
            return
        if first_line[1] == 'run':
            split = m.content.split('\n', 1)
            if len(split) == 1:
                inp = ''
            else:
                inp = split[1]
            cor = await subexec('./luap', user_code_save, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout, stderr = await cor.communicate(bytes(inp, 'utf-8'))
            await m.channel.send(f'Output:\n{stdout.decode()}\nErrors:\n{stderr.decode()}', allowed_mentions=discord.AllowedMentions.none())
            return
        await m.channel.send('No known action')
        return
    else:
        if inp:
            with open(code_file, 'w') as luacodefile:
                luacodefile.write(inp)
            cor = await subexec('./luap', code_file, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            stdout, stderr = await cor.communicate(bytes())
            removefile(code_file)
            await m.channel.send(f'Output:\n{stdout.decode()}\nErrors:\n{stderr.decode()}', allowed_mentions=discord.AllowedMentions.none())
            return
        else:
            await m.channel.send('No codeblock found!')
            return

    await m.channel.send('Found nothing to do!')



@add_command()
async def linecount(m):
    """
    `{prefix}linecount`

    Sends the bot's source code line count.
    """
    await m.channel.send(len(open(__file__, 'r').read().split('\n')) - 1)


@add_command()
async def tictactoe(m):
    """
    `{prefix}tictactoe`

    Undefined.
    """
    pass


@add_command(['timeouts'], 120)
async def _(m):
    """
    `{prefix}timeouts`

    Shows the timeouts of every command in seconds.
    """
    await m.channel.send('{}'.format(', '.join([f"{x} : {commandsDict[x]['timeout']}" for x in commandsDict])))


@add_command(('version', 'ver'), 30)
async def _(m):
    """
    `{prefix}ver`
    `{prefix}version`

    Shows the bot's version number and name.
    Shows the version of potatoscript being run.
    """
    await m.channel.send(f'Potato Overlord version: {version}\nPotatoscript Version: {potatoscript.version}')


@add_command()
async def ping(m):
    """
    `{prefix}ping`

    Shows the bot's response time in seconds.
    """
    await m.channel.send(
        f'Pong! `{(datetime.datetime.utcnow() - m.created_at).total_seconds()}`'
    )


@add_command()
async def pong(m):
    """
    `{prefix}pong`

    Shows the bot's response time in seconds.
    """
    await m.channel.send(
        f'Ping! `{(datetime.datetime.utcnow() - m.created_at).total_seconds()}`'
    )


@add_command(timeout=180)
async def tmp(m):
    """
    `{prefix}tmp (channel name)`

    Creates a temporary channel in the '/tmp' category.
    This chat will automatically delete itself when unused
    for a certain amount of time.

    Will not function if no /tmp category exists.
    Grants special permissions to the command's author in the created channel.
    """
    if m.channel.category.name == '/tmp':
        await m.channel.edit(name='_'.join(m.content.split()[1:]))
    else:
        categ = None
        for category in m.guild.categories:
            if category.name == '/tmp':
                categ = category
                break
        if categ:
            ch = await categ.create_text_channel('_'.join(m.content.split()[1:]), reason=f'{m.author.name}#{m.author.discriminator} used the tmp command!',)
            await ch.set_permissions(m.author, manage_channels=True, manage_messages=True)
            while True:
                await asyncio.sleep(300)
                try:
                    lm = await ch.fetch_message(ch.last_message_id)
                    if (datetime.datetime.utcnow() - lm.created_at).total_seconds() > 300:
                        await ch.delete()
                        break
                except:
                    await ch.delete()
                    break


        else:
            await m.channel.send('This server doesn\'t have a /tmp category!')



@add_command()
async def figlet(m):
    """
    `{prefix}figlet [font] (text)`

    Creates ascii art of the entered text.
    If the font is invalid, the first word
    is treated as text.
    """
    if len(m.content.split()) < 2:
        return
    if (m.content.split()[1] in art.FONT_NAMES) and (len(m.content.split()) > 2):
        await m.channel.send(f"```{discord.utils.escape_markdown(art.text2art(' '.join(m.content.split()[2:]), m.content.split()[1]))}```")
    else:
        await m.channel.send(f"```{discord.utils.escape_markdown(art.text2art(' '.join(m.content.split()[1:]), 'random'))}```")


@add_command(['art'])
async def _(m):
    """
    `{prefix}art (art_name) [art_name2] ... [art_namen]`

    Sends ascii art based on the name.
    The full list can be found here:
    https://www.4r7.ir/ArtList.html
    Spaces in names should be replaced with underscores (_).
    """
    message = ''
    for i in range(len(m.content.split()) - 1):
        try:
            message += f"`{discord.utils.escape_markdown(art.art(m.content.split()[i + 1].replace('_', ' ')))}`" + '\n'
        except art.artError:
            pass

    if message:
        await m.channel.send(message)



@add_command(['arts'], 10)
async def _(m):
    """
    `{prefix}arts`

    Sends a link to the full list of arts and art names.
    May be replaced in the future to send all arts and their respective names.
    """
    await m.channel.send('Full list can be found here: https://www.4r7.ir/ArtList.html')



@add_command(timeout=40)
async def tatohost(m):
    """
    `{prefix}tatohost`

    Shows if the bot is currently being hosted by the bot's creator,
    Jagaimo no Shikan a.k.a. The Potato Chronicler.
    """
    if os.getenv('USER') == 'potato':
        await m.channel.send('Potato is hosting!')
    else:
        await m.channel.send('Nope, not potato!')


@add_command()
async def lockdown(m):
    """
    `{prefix}lockdown`

    Moderator only.
    Prevents the default role from sending messages in this chat.
    Won't work if the chats are set improperly.
    """
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
    """
    `{prefix}unlockdown`

    Moderator only.
    Allows the default role from sending messages in this chat.
    Won't work if the chats are set improperly.
    """
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

@add_command(timeout=300)
async def commands(m):
    """
    `{prefix}commands`

    Shows all the bot's commands in an alphabetical order.
    """
    await m.channel.send(
        f'List of commands: `{", ".join(sorted(list(commandsDict.keys())))}`'
    )


@add_command()
async def xkcd(m):
    """
    `{prefix}xkcd [number]`

    Shows a random xkcd comic.
    If the number is specified, it shows the specified comic.
    """
    if len(m.content.split()) == 1:
        from random import randint
        await m.channel.send(f'https://xkcd.com/{randint(1, 2441)}/')
        return
    elif len(m.content.split()) == 2:
        try:
            await m.channel.send(
                f'https://xkcd.com/{int(m.content.split()[1])}/')
            return
        except ValueError:
            await m.channel.send(
                f'``{m.content.split()[1]}`` isn\'t an integer!')


@add_command(["potato"])
async def _(m):
    """
    `{prefix}potato`

    Sends contact info about Potato, my father <3
    """

    # Gets me :)
    p = client.get_guild(752177122998747199).get_member(potatoid)
    info = f"""
    Discord: {p.name}#{p.discriminator}
    [Github](https://github.com/ThePotatoChronicler)
    [Reddit](https://www.reddit.com/user/Potato-of-All-Trades)
    [Discord Server](https://discord.gg/EWQPNfddmz)
    """
    from inspect import cleandoc
    embed = discord.Embed(title="Contact Information",
                          url="https://github.com/ThePotatoChronicler",
                          description=cleandoc(info))
    embed.set_image(url=str(p.avatar_url))

    footer = "Hello world!"

    for activity in p.activities:
        if isinstance(activity, discord.CustomActivity):
            footer = activity
            break
    embed.set_footer(text=footer, icon_url=str(client.user.avatar_url))

    await m.channel.send(embed=embed)


@add_command()
async def cat(m):
    """
    `{prefix}cat`

    Shows a random picture of a cat.
    """
    await m.channel.send(
        requests.get('https://api.thecatapi.com/v1/images/search').json()[0]
        ['url'])


@add_command()
async def dog(m):
    """
    `{prefix}dog`

    Shows a random picture of a dog.
    """
    await m.channel.send(
        requests.get('https://api.thedogapi.com/v1/images/search').json()[0]
        ['url'])


@add_command(timeout=600)
async def ownermail(m):
    """
    `{prefix}ownermail (message)`

    DMs the owner of the server.
    Should not be used for conversations.
    """
    await m.delete()
    if len(m.content.split()) > 1:
        await m.guild.owner.send(
            f'Channel: {m.channel.mention} in {m.guild.name}\nMember: {m.author.mention} ({m.author.name}#{m.author.discriminator})\nMessage: {" ".join(m.content.split()[1:])}'
        )
    else:
        await m.channel.send(
            f'Usage: `{prefix}ownermail [message]`', delete_after=2)


@add_command(timeout=600)
async def modmail(m):
    """
    `{prefix}modmail (message)`

    DMs the moderators of the server.
    Should not be used for conversations.
    """
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


@add_command(('bogosort', 'bogo'), 45)
async def bogosort(m):
    """
    `{prefix}bogo (numbers)`
    `{prefix}bogosort (numbers)`

    Sorts the inputted list of numbers using the
    bogosort algorithm.
    """
    from random import shuffle
    amount = 0
    if len(m.content.split()) < 2:
        return
    message = await m.author.send('Starting bogosort!')
    sort = [
        int(x) if float(x) % 1 == 0 else float(x)
        for x in m.content.split()[1:]
    ]

    while not all(x <= y for x, y in zip(sort, sort[1:])):
        await message.edit(content=f'```{board(sort)}```Shuffles: ``{amount}``')

        shuffle(sort)
        amount += 1

        if amount % 20 == 0:
            save_sort_to_db(0, message.id, m.channel.id, amount, sort)

    await message.edit(
        content=
        f"```{board(sort)}```Sorted in {amount} shuffle{'' if amount == 1 else 's'}! {sort}"
    )
    remove_sort_from_db(message.id)


@add_command(('bubblesort', 'bubble'), 30)
async def bubblesort(m):
    """
    `{prefix}bubble (numbers)`
    `{prefix}bubblesort (numbers)`

    Sorts the inputted list of numbers using the
    bubblesort algorithm.
    """
    amount = 0
    if len(m.content.split()) < 2:
        return
    message = await m.author.send('Starting bubblesort!')
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


@add_command(('insertionsort', 'insertion'), 30)
async def insertionsort(m):
    """
    `{prefix}insertion (numbers)`
    `{prefix}insertionsort (numbers)`

    Sorts the inputted list of numbers using the
    insertion sort algorithm.
    """
    amount = 0
    if len(m.content.split()) < 2:
        return
    message = await m.author.send('Starting insertionsort!')
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

    global onreadyonce
    if onreadyonce:
        return

    onreadyonce = True

    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name=f'{prefix} >w>'))
    print('Potato Overlord is ready!')

    # Checks for new guilds, adds them to database
    async def managenewguilds():
        while True:
            for guild in client.guilds:
                dbcursor.execute('SELECT server FROM servers WHERE server = ?', [guild.id])
                if not dbcursor.fetchone():
                    dbcursor.execute('INSERT INTO servers(server) VALUES(?)', [guild.id])

            database.commit()
            await asyncio.sleep(600)

    # Temporary channel management after crash or reboot
    async def managetmp():
        async def managetmpch(ch):
            while True:
                await asyncio.sleep(300)
                try:
                    lm = await ch.fetch_message(ch.last_message_id)
                    if (datetime.datetime.utcnow() - lm.created_at).total_seconds() > 300:
                        await ch.delete()
                        break
                except:
                    await ch.delete()
                    break

        lst = []
        for guild in client.guilds:
            for category in guild.categories:
                if category.name == '/tmp':
                    for ch in category.text_channels:
                        lst.append(managetmpch(ch))
                    break

        await asyncio.gather(*lst)

    # Manage sorts that were saved and left unfinished before crash or reboot
    async def managesorts():
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
        lst = []
        dbcursor.execute('SELECT * FROM sorts')
        for fetched in dbcursor.fetchall():
            t, *args = fetched
            lst.append(funcs[t](*args))

        await asyncio.gather(*lst)

    # Begin
    await asyncio.gather(managetmp(),
                         managesorts(),
                         managenewguilds())


@client.event
async def on_disconnect():  # Executes when bot loses connection
    print('Disconnected!')


@client.event
async def on_message(m):  # Executes on every message

    # Exit if message was sent by the bot
    if m.author == client.user or m.author.bot:
        return

    nomentions = discord.AllowedMentions.none()

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
                ).replace(':', r'\:'),
                allowed_mentions=nomentions
            )
            return

        if m.channel.name == 'binary-wars' or m.channel.name == 'binary_wars':
            await m.delete()
            await m.channel.send(
                f'{m.author.display_name} : {"".join(bin(ord(x))[2:] for x in m.content)}',
                allowed_mentions=nomentions
            )
            return

        if m.content.startswith(prefix):
            if spamDict.setdefault(m.author.id, 0) >= 3:
                return

            try:
                comdict = commandsDict[m.content.split()[0][len(prefix):]]
            except KeyError:
                await m.channel.send('Command doesn\'t exist!')
                return

            spamDict[m.author.id] += 1

            try:
                message = await comdict['function'](m)
                if comdict['emoji']:
                    reactionDict[message.id] = comdict['function']

            except KeyError:
                await m.channel.send('Command doesn\'t exist!')

            await asyncio.sleep(comdict['timeout'])

            spamDict[m.author.id] -= 1


    else:
        if m.author.id == 185421198094499840 and m.content == 'close':
            m.channel.send('Closing.')
            await client.close()


@client.event
async def on_reaction_add(r, u):
    if u == client.user:
        return

    if r.message.id in reactionDict:
        delete = reactionDict[r.message.id](r.message, r, u)

        if delete:
            del reactionDict[r.message.id]


@client.event
async def on_member_join(m):
    dbcursor.execute('SELECT join_chat FROM servers WHERE server = ?', [m.guild.id])
    chat = m.guild.get_channel(dbcursor.fetchone()[0])
    if chat:
        await chat.send(f'{m.name} has joined **{m.guild.name}**! We\'re now **{m.guild.member_count}** strong!',
                        allowed_mentions = discord.AllowedMentions.none())


@client.event
async def on_member_remove(m):
    dbcursor.execute('SELECT join_chat FROM servers WHERE server = ?', [m.guild.id])
    chat = m.guild.get_channel(dbcursor.fetchone()[0])
    if chat:
        await chat.send(f'{m.name} has deserted **{m.guild.name}**! We\'re now **{m.guild.member_count}** strong!',
                        allowed_mentions = discord.AllowedMentions.none())


@client.event
async def on_member_ban(g, u):
    dbcursor.execute('SELECT join_chat FROM servers WHERE server = ?', [g.id])
    chat = g.get_channel(dbcursor.fetchone()[0])
    if chat:
        await chat.send(f'{u.name} has been executed.',
                        allowed_mentions = discord.AllowedMentions.none())


@client.event
async def on_member_unban(g, u):
    dbcursor.execute('SELECT join_chat FROM servers WHERE server = ?', [g.id])
    chat = g.get_channel(dbcursor.fetchone()[0])
    if chat:
        await chat.send(f'{u.name} has been pardoned by the gods.',
                        allowed_mentions = discord.AllowedMentions.none())


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
client.run(os.environ.get("DISCORD_BOT_TOKEN"))

database.close()
