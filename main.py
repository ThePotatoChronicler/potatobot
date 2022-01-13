import os
from keep_alive import keep_alive # repl.it keep_alive function

print('Starting Potato Overlord!')

from cryptography.fernet import Fernet
import potatoscript
import art
import asyncio
import nextcord as discord
import requests
import datetime
import bitstring
import sqlite3 as sqlite

database                = sqlite.Connection('data.db')    # Database
user_code_file          = 'luacode/'                      # Location of user code
dbcursor                = database.cursor()               # Cursor to edit the database with
prefix                  = 'p!'                            # Prefix
version                 = (1, 7, 1, "Resurrection")       # Version
intents                 = discord.Intents.default()       # Default intents
intents.members         = True                            # So that bot can access members
intents.presences       = True                            # So that the bot can access statusses
defment                 = discord.AllowedMentions(everyone=False, roles=False, users=False)
client : discord.Client = discord.Client(                 # Create client
                                intents=intents,
                                allowed_mentions=defment) # Sets who can be mentioned

christmas = Fernet(os.environ.get("CHRISTMAS_KEY"))

developer_mode : bool = os.path.isfile('developer.lock')
onreadyonce = False # Stops on_ready from firing multiple times
unchanginglist = [] # Used by the Unchanging role to check
                    # if the bot forced a rename, so the event is ignored next
serverDebug = [] # List of servers with enabled debug mode
commandsDict = {} # Globalization
reactionDict = {} # My reaction API
storageDict = {} # Global storage for commands
spamDict = {} # Preventing spam/bot abuse
christmasDict = {} # Compiled christmas commands

# renameall globals
renameList = [] # Stops renameall stacking
engdict_database = sqlite.Connection(':memory:')
engdict_db_cursor = engdict_database.cursor()
engdict_db_cursor.execute("PRAGMA synchronous = OFF")
engdict_db_cursor.execute("CREATE TABLE words (word TEXT)")
with open('english_dict_a.txt') as engdict:
    engdict_db_cursor.executemany("INSERT INTO words (word) VALUES (?)", ((line[:-1],) for line in engdict.readlines()))
engdict_db_cursor.close()

class Command():
    """
    A wrapper around a python function.
    """
    from typing import Coroutine as coro
    def __init__(func : coro, /):
        pass

class DoesNotExist(Exception):
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


def remove_first_word(s : str):
    """
    Removes first word and the first whitespace after it
    """
    return s[len(s.split()[0]) + 1:]

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


@add_command(['debug'])
async def _(m : discord.Message):
    """
    `{prefix}debug`

    The debug command is a frontend to user debugging.
    It can only be used by people with the `View Audit Log` permission.

    With no arguments, enables debug mode for entire server,
    which might lead to extra output by commands.

    Debug commands:
        timeout userID - returns the member's timeout stack
    """

    if not m.author.guild_permissions.view_audit_log:
        await m.channel.send("You do not have the permissions to use debug!")
        return

    if len(m.content.split(None, 1)) == 1:
        if m.guild.id in serverDebug:
            serverDebug.remove(m.guild.id)
            await m.channel.send("Turned off debug")
        else:
            serverDebug.append(m.guild.id)
            await m.channel.send("Turned on debug")
        return

    args = m.content.split(None, 1)[1]
    argss = args.split()

    if argss[0] == 'timeout':
        if len(argss) == 1:
            await m.channel.send("Missing userID")
            return
        else:
            member : discord.Member = m.guild.get_member(int(argss[1]))
            if member == None:
                await m.channel.send("No such member found")
            else:
                await m.channel.send(f"{member} timeout stack: {spamDict.get(member.id, 'Untracked')}")
    else:
        await m.channel.send("No such command found")


@add_command(['christmas1'])
async def _(m : discord.Message):
    g = { 'input' : remove_first_word(m.content) }
    exec(christmasDict['christmas1'], g)

    # If we send an empty message, react with an emoji
    try:
        await m.channel.send(g['output'])
    except discord.errors.HTTPException as ex:
        if ex.code == 50006:
            await m.add_reaction('❌')
        else:
            raise ex from None

@add_command(['christmas2'])
async def _(m : discord.Message):
    g = { 'input' : remove_first_word(m.content) }
    exec(christmasDict['christmas2'], g)

    # If we send an empty message, react with an emoji
    try:
        await m.channel.send(g['output'])
    except discord.errors.HTTPException as ex:
        if ex.code == 50006:
            await m.add_reaction('❌')
        else:
            raise ex from None

@add_command(['christmas3'])
async def _(m : discord.Message):
    g = { 'm' : m }
    exec(christmasDict['christmas3'], g)

    # If we send an empty message, react with an emoji
    try:
        await m.channel.send(g['output'])
    except discord.errors.HTTPException as ex:
        if ex.code == 50006:
            await m.add_reaction('❌')
        else:
            raise ex from None

@add_command(['christmas4'])
async def _(m : discord.Message):
    g = { 'm' : m }
    exec(christmasDict['christmas4'], g)

    # If we send an empty message, react with an emoji
    try:
        await m.channel.send(g['output'])
    except discord.errors.HTTPException as ex:
        if ex.code == 50006:
            await m.add_reaction('❌')
        else:
            raise ex from None

@add_command(['christmas2021'])
async def _(m : discord.Message):
    g = { 'input' : remove_first_word(m.content) }
    exec(christmasDict['christmas2021'], g)

    # If we send an empty message, react with an emoji
    try:
        await m.channel.send(g['output'])
    except discord.errors.HTTPException as ex:
        if ex.code == 50006:
            await m.add_reaction('❌')
        else:
            raise ex from None

# There are probably a few edge cases in this function,
# let's hope I am not bitten in the ass by them
@add_command(['fillemoji'])
async def _(m : discord.Message):
    """
    `{prefix}fillemoji`

    Useable by anyone wit the \"Manage Emoji\" permission

    Fills up the rest of the emoji slots with emojis from other
    servers that the bot is in.
    """

    if not m.author.guild_permissions.manage_emojis:
        await m.channel.send("You lack the permissions to use this command")
        return

    used_emoji = []
    guilds = client.guilds.copy()
    guilds.remove(m.guild)
    guilds_len = len(guilds) - 1
    reason = f"{m.author} used the fillemoji command"

    from random import randint

    await m.channel.send("Filling all remaining emoji slots, this might take a while!")

    async with m.channel.typing():

        for _ in range(len(m.guild.emojis), m.guild.emoji_limit):
            e : discord.Emoji = None
            while e == None or e.id in used_emoji or e.animated:
                g : discord.Guild = guilds[randint(0, guilds_len)]
                e : discord.Emoji = g.emojis[randint(0, len(g.emojis) - 1)]
            used_emoji.append(e.id)
            b = await e.url.read()
            await m.guild.create_custom_emoji(name=e.name, image=b, reason=reason)

    await m.channel.send("Finished filling up all the emoji slots")

@add_command(['renameall'])
async def _(m : discord.Message):
    """
    `{prefix}renameall format`
    `{prefix}renameall %preview% format`

    __**THIS IS A REALLY STUPID COMMAND**__

    Useable by anyone with the \"Manage Nicknames\" permission
    and Nitro Boosters

    If format is exactly '%clear%', clears all nicknames.

    If format has '%preview%' before it, no renaming will be done,
    instead, a single name will be returned.

    Renames everyone in the guild,
    with some optional formatting.

    There is formatting, which can be added using `%` and a character:
        a - Random english word
        A - Random english word, first letter capitalized
        e - Enumerates all users
        E - Enumerates all users with equal number length, adding leading zeroes if needed
        d - Random decimal number (0 - 9)
        l - Random lowercase letter
        L - Random uppercase letter
    To include a literal %, use `%%`
    To escape a formatting sequence, use `%%`, example:
        This is %%a
        Will result in name "This is %a"

    This command will take more time to process with more people
    """

    if (not m.author.guild_permissions.manage_nicknames) and (m.author.premium_since is None):
        await m.channel.send("You lack the permissions to use this command!")
        return

    preview : bool = False
    if (len(m.content.split(None, 1)) == 2) and m.content.split(None, 2)[1] == "%preview%":
        preview = True
        form : str = ' '.join(m.content.split()[2:])
    else:
        form : str = ' '.join(m.content.split()[1:])

    # I can check this part with just "if not",
    # but I'm making this explicit to shit on
    # JS programmers, you're welcome
    if form == '':
        await m.channel.send("No format specified!")
        return

    elif (not preview) and form == '%clear%':
        nameschanged : int = 0
        renameList.append(m.guild.id)
        await m.channel.send("Clearing all nicknames, this might take a while!")

        async with m.channel.typing():
            for member in m.guild.members:
                try:
                    await member.edit(nick=None, reason=f"{m.author} used the renameall command to clear all nicknames")
                except discord.errors.Forbidden:
                    pass
                else:
                    nameschanged += 1

        renameList.remove(m.guild.id)
        await m.channel.send(f"Nickname clearing finished, cleared nicknames of {nameschanged} out of {len(m.guild.members)} member{'' if len(m.guild.members) == 1 else 's'}")
        return


    if m.guild.id in renameList and (not preview):
        await m.channel.send("A renameall command is already in progress, please wait until it finishes!")
        return

    # Maximum characters in a discord nickname
    maxchars = 32
    import re
    if not preview:
        renameList.append(m.guild.id)

    async with m.channel.typing():
        # Occurence count
        formcdict : dict[str, int] = {}
        for inst in re.findall(r"%[a-zA-Z%]", form):
            formcdict[inst[1]] = formcdict.get(inst[1], 0) + 1

        minchars : int = 0 # Minimum required characters for formatting
        cursor : sqlite.Cursor = engdict_database.cursor()
        engwordsneeded : int = formcdict.get('a', 0) + formcdict.get('A', 0)
        engwords : list[str] = [] # List of random english words for further processing
        enumprogress : int = 0
        enumlength : int = len(str(len(m.guild.members)))

        minchars += formcdict.get('%', 0)
        minchars += engwordsneeded
        minchars += (formcdict.get('e', 0) + formcdict.get('E', 0)) * enumlength
        minchars += formcdict.get('d', 0)
        minchars += formcdict.get('l', 0) + formcdict.get('L', 0)

        if (minchars + len(re.sub(r"%[a-zA-Z%]", '', form))) > maxchars:
            if not preview:
                renameList.remove(m.guild.id)
            await m.channel.send(f"Name would be longer than Discord allows ({maxchars})")
            return

        if not preview:
            await m.channel.send("Starting the rename, this might take a while!")


        engquery : str = ""
        if engwordsneeded > 0:
            engquery = f"SELECT word FROM words WHERE LENGTH(word) <= {((maxchars - (len(form) - engwordsneeded)) // engwordsneeded) + 1} ORDER BY RANDOM() LIMIT {engwordsneeded}"

        nameschanged : int = 0

        # Used for the %d formatting
        from random import randint

        for i, member in enumerate(m.guild.members):

            engwords = cursor.execute(engquery).fetchall()
            usedwords = 0

            def subfunc(match : re.Match):
                nonlocal usedwords

                let : str = match.group(1)
                sd : dict = {
                    '%' : '%',
                    'a' : engwords[usedwords][0] if usedwords < len(engwords) else "",
                    'A' : engwords[usedwords][0].capitalize() if usedwords < len(engwords) else "",
                    'e' : str(enumprogress),
                    'E' : str(enumprogress).zfill(enumlength),
                    'd' : str(randint(0, 9)),
                    'l' : chr(randint(ord('a'), ord('z'))),
                    'L' : chr(randint(ord('A'), ord('Z')))
                }
                if let == 'a' or let == 'A':
                    usedwords += 1

                return sd.get(let, match.group(0))

            nick = re.sub("%([a-zA-Z%])", subfunc, form)

            try:
                if preview:
                    await m.channel.send(nick)
                    break
                else:
                    await member.edit(nick=nick, reason=f"{m.author} used the renameall command")
            except discord.errors.Forbidden:
                pass
            else:
                enumprogress += 1
                nameschanged += 1

    if not preview:
        renameList.remove(m.guild.id)
    if not preview:
        await m.channel.send(f"Renaming finished, changed nicknames of {nameschanged} out of {len(m.guild.members)} member{'' if len(m.guild.members) == 1 else 's'}")


@add_command(['quote'])
async def _(m : discord.Message):
    """
    `{prefix}quote [id]`

    Retrieves a quote from the entered id.
    If no id is entered, it finds a quote at random.
    """

    argin = (len(m.content.split()) > 1)

    if argin:
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

    else: # Selects a random quote
        dbcursor.execute("SELECT quote FROM quotes ORDER BY RANDOM() LIMIT 1")

    quote = dbcursor.fetchone()
    if quote == None:
        await m.channel.send("No such quote exists!")
    else:
        await m.channel.send(quote[0])


@add_command(['quotes'], 15)
async def _(m : discord.Message):
    """
    `{prefix}quotes [id]`

    Returns N quotes, close to the entered id.
    Returns N random quotes if no id is entered.
        (These won't be close to eachother)

    N is a static value set by hand,
    who knows what it's set to right now ;-;
    """
    argin = (len(m.content.split()) > 1)
    returnamount = 10
    if argin:
        try:
            # Cannot use variable id
            # because of builtin
            quoteid = int(m.content.split()[1])
        except ValueError:
            await m.channel.send("Invalid ID!")
            return

        dbcursor.execute(f"SELECT quote FROM quotes WHERE id <  {quoteid} LIMIT {returnamount // 2}")
        retquotes = dbcursor.fetchall()
        returnamount -= len(retquotes)
        dbcursor.execute(f"SELECT quote FROM quotes WHERE id >= {quoteid} LIMIT {returnamount}")
        retquotes += dbcursor.fetchall()

    else:
        dbcursor.execute(f"SELECT quote FROM quotes ORDER BY RANDOM() LIMIT {returnamount}")
        retquotes = dbcursor.fetchall()

    success = False
    retmes = ""
    for quote in retquotes:
        if (len(retmes) + len(quote[0])) > 2000:
            break
        retmes = retmes + quote[0] + "\n"
    else:
        success = True

    await m.channel.send(retmes)
    if not success:
        await m.channel.send("⚠️ Only a partial result has been returned, since the quotes were too long for one message")


@add_command(['addquote'])
async def _(m : discord.Message):
    """
    `{prefix}addquote id [quote]`

    Adds a quote to the database at the entered id,
    adding or overwriting the quote
    that is already at that id.

    You can reply to a message with this command,
    in which case it will be added as a quote.
    """

    if m.reference:
        if len(m.content.split()) < 2:
            await m.channel.send("Not enough arguments!")
            return

        cachedm = m.reference.cached_message
        if cachedm != None:
            quote = "\n".join(["> " + line for line in cachedm.clean_content.split('\n')]) + "\n" + f"- {cachedm.author.display_name}"
        else:
            # 'tis a mess
            cachedm = (await (await client.fetch_channel(m.reference.channel_id)).fetch_message(m.reference.message_id))
            if cachedm != None:
                quote = "\n".join(["> " + line for line in cachedm.clean_content.split('\n')]) + "\n" + f"- {cachedm.author.display_name}"
            else:
                await m.channel.send("Couldn't get that message, sorry!")
                return
    else:
        if len(m.content.split()) < 3:
            await m.channel.send("Not enough arguments!")
            return

        quote = m.content.split(None, 2)[2]

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


    try:
        dbcursor.execute("REPLACE INTO quotes(id, quote) VALUES(?, ?)", (quoteid, quote))
    except OverflowError:
        await m.channel.send("That ID is too thicc")
        return
    database.commit()
    await m.add_reaction("👍")

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
        raise DoesNotExist()


@add_command(['help'], 12)
async def _(m : discord.Message):
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


@add_command(['nonamechange'])
async def _(m : discord.Message):
    """
    `{prefix}nonamechange member`

    To use this command, you must have the `Manage Nicknames` permission.

    Requires the **Unchanging** role in this server to work.
    Makes the target user unable to rename themselves, by setting their name
    back whenever they are renamed.

    This is not a guarantee, for example if the bot is offline, it will not know
    of any renames afterwards.
    """
    if not m.author.guild_permissions.manage_nicknames:
        await m.channel.send('You need `Manage Nicknames` permission to do this!')
        return

    unchanging : discord.Role = discord.utils.find(lambda r : r.name == "Unchanging", m.guild.roles)
    if unchanging == None:
        await m.channel.send("This server lacks the 'Unchanging' role!")

    if len(m.content.split()) == 1:
        await m.channel.send('No user specified!')
        return

    member : discord.Member = None

    args = m.content.split(None, 1)[1]

    import re

    if (len(args.split()) == 1) and (len(m.mentions) == 1):
        member = m.mentions[0]

    else:
        if re.fullmatch(r"\d+", args):
            member = m.guild.get_member(int(args))

        if not member:
            member = discord.utils.find(lambda mem : args in mem.display_name, m.guild.members)

    if member == None:
        await m.channel.send("No member found")
    else:
        urole = discord.utils.find(lambda r : r.name == "Unchanging", member.roles)
        if urole == None:
            await member.add_roles(unchanging, reason=f"{m.author} used nonamechange command")
            await m.channel.send(f"{member.display_name} ({member}) received the Unchanging role")
        else:
            await member.remove_roles(urole, reason=f"{m.author} used nonamechange command")
            await m.channel.send(f"{member.display_name} ({member}) lost the Unchanging role")



@add_command(['emojipurge'], 30)
async def _(m):
    """
    `{prefix}emojipurge`
    `{prefix}emojipurge true`

    Requires the \"Manage Emojis\" permission to use

    Deletes all emojis from the server,
    *except* those whose names start with `_`.
    To also delete animated emojis, add true.
    May take a while to finish.

    __**THIS ACTION CANNOT BE TAKEN BACK.**__
    """
    if not m.author.guild_permissions.manage_emojis:
        await m.channel.send("You lack the permissions to use this")
        return

    await m.channel.send("Purging all emojis, it could take a while!")
    animated = False

    if len(m.content.split()) >= 2:
        if m.content.split()[1] == "true":
            animated = True

    async with m.channel.typing():
        for emoji in m.guild.emojis:
            if not emoji.name.startswith('_'):
                if (not emoji.animated) or (emoji.animated and animated):
                    await emoji.delete(reason=f"Command executed by {m.author.name}#{m.author.discriminator}")

    await m.channel.send("Emoji purge finished!")


@add_command(['spam'])
async def _(m):
    """
    `{prefix}spam`

    :)
    """
    if (m.author.id != 185421198094499840) and (m.guild.id != 797066786792538123):
        raise DoesNotExist()

    try:
        i = 0
        while i < int(m.content.split()[1]):
            try:
                await m.channel.send(' '.join(m.content.split(' ')[2:]))
            except discord.errors.NotFound:
                return
            i += 1
    except:
        pass


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
    from inspect import cleandoc

    v = version
    fversion = f"{'.'.join( str(n) for n in v[0:3] )} - {v[3]}"

    await m.channel.send(
        cleandoc(
            f'''
            Potato Overlord: {fversion}
            Potatoscript: {potatoscript.version}
            Discord Wrapper (Nextcord): {discord.__version__}
            '''
        )
    )


@add_command()
async def ping(m):
    """
    `{prefix}ping`

    Shows the bot's response time in seconds.
    """
    await m.channel.send(
        f'Pong! `{(datetime.datetime.utcnow() - m.created_at).total_seconds()}` seconds to respond'
    )


@add_command()
async def pong(m):
    """
    `{prefix}pong`

    Shows the bot's response time in seconds.
    """
    await m.channel.send(
        f'Ping! `{(datetime.datetime.utcnow() - m.created_at).total_seconds()}` seconds to respond'
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
    if m.channel.category != None and m.channel.category.name == '/tmp':
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

    # Gets the bot owner :)
    p = (await client.application_info()).owner
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
    await m.channel.send(requests.get('https://api.thecatapi.com/v1/images/search').json()[0]['url'])


@add_command()
async def dog(m):
    """
    `{prefix}dog`

    Shows a random picture of a dog.
    """
    await m.channel.send(requests.get('https://api.thedogapi.com/v1/images/search').json()[0]['url'])

@add_command(['fox'])
async def _(m):
    """
    `{prefix}fox`

    Shows a random picture of a fox.
    """
    await m.channel.send(requests.get('https://randomfox.ca/floof/').json()['image'])

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

    if developer_mode:
        await client.change_presence(status=discord.Status.dnd,
                                     activity=discord.Activity(type=discord.ActivityType.listening,
                                                               name='Potato'))

    with open('christmas2021/christmas1', 'rb') as f:
        christmasDict['christmas1'] = compile(christmas.decrypt(f.read()), "christmas1.py", 'exec')

    with open('christmas2021/christmas2', 'rb') as f:
        christmasDict['christmas2'] = compile(christmas.decrypt(f.read()), "christmas2.py", 'exec')

    with open('christmas2021/christmas3', 'rb') as f:
        christmasDict['christmas3'] = compile(christmas.decrypt(f.read()), "christmas3.py", 'exec')

    with open('christmas2021/christmas4', 'rb') as f:
        christmasDict['christmas4'] = compile(christmas.decrypt(f.read()), "christmas4.py", 'exec')

    with open('christmas2021/christmas2021', 'rb') as f:
        christmasDict['christmas2021'] = compile(christmas.decrypt(f.read()), "christmas2021.py", 'exec')

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
            try:
                message = client.get_channel(c_id).get_partial_message(m_id)
            except AttributeError:
                return
            from random import shuffle
            amount = a
            sort = [
                int(x) if float(x) % 1 == 0 else float(x)
                for x in l.split(' ')
            ]

            while not all(x <= y for x, y in zip(sort, sort[1:])):
                try:
                    await message.edit(content=f'```{board(sort)}```Shuffles: ``{amount}``')
                except discord.errors.NotFound:
                    remove_sort_from_db(m_id)
                    return
                shuffle(sort)
                amount += 1

                if amount % 20 == 0:
                    save_sort_to_db(0, m_id, c_id, amount, sort)

                await message.edit(content=f"```{board(sort)}```Sorted in {amount} shuffle{'' if amount == 1 else 's'}! {sort}")

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
                    await message.edit(content=f"```{board(sort)}```Comparisons: ``{amount}``")
                    if sort[j] > sort[j + 1]:
                        sort[j], sort[j + 1] = sort[j + 1], sort[j]
                    amount += 1

                    if amount % 20 == 0:
                        save_sort_to_db(1, m_id, c_id, amount, sort)

            await message.edit(content=f"```{board(sort)}```Sorted in {amount} comparison{'' if amount == 1 else 's'}! {sort}")
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
    if isinstance(m.channel, discord.TextChannel):
        if (m.channel.name == 'letter_wars' or m.channel.name == 'letter-wars') and not len(m.content.strip()) == 1:
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
                f"{m.author.display_name} : {bitstring.Bits(bytes(m.content, 'utf-8')).bin}",
                allowed_mentions=nomentions
            )
            return

        if m.content.startswith(prefix):
            if spamDict.setdefault(m.author.id, 0) >= 3:
                return

            try:
                cmdname : str = m.content.split()[0][len(prefix):]
                comdict = commandsDict[cmdname]
            except KeyError:
                await m.channel.send('Command doesn\'t exist!')
                return

            spamDict[m.author.id] += 1

            try:
                message = await comdict['function'](m)
                if comdict['emoji']:
                    reactionDict[message.id] = comdict['function']

            except DoesNotExist:
                await m.channel.send('Command doesn\'t exist!')
            except Exception as err:
                spamDict[m.author.id] -= 1
                print(f"\x1b[1;91mAn exception occured inside '{cmdname}' and is being re-raised:\x1b[22;39m")
                raise err from None
            else:
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
async def on_member_update(bm : discord.Member, am : discord.Member):
    for role in am.roles:
        if (role.name == 'Unchanging') and (bm.display_name != am.display_name):
            if am.id in unchanginglist:
                unchanginglist.remove(am.id)
            else:
                unchanginglist.append(am.id)
                await am.edit(nick=bm.display_name, reason='Has the Unchanging role.')


@client.event
async def on_message_edit(mb, ma):
    if (ma.channel.name == 'letter_wars' or ma.channel.name == 'letter-wars') and not len(ma.content.strip()) == 1:
        await ma.delete()


keep_alive()  # Starts a webserver to be pinged.
client.run(os.environ.get("DISCORD_BOT_TOKEN"))

database.close()
engdict_database.close()
