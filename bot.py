import discord
from discord.ext import commands
import random, logging
import asyncio
import datetime
import re
import json
import time as time_zero

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# Цвета для рамок и ролей
all_colors = {
    "teal": 0x1abc9c,
    "dark_teal": 0x11806a,
    "green": 0x2ecc71,
    "dark_green": 0x1f8b4c,
    "blue": 0x3498db,
    "dark_blue": 0x206694,
    "purple": 0x9b59b6,
    "dark_purple": 0x71368a,
    "magenta": 0xe91e63,
    "dark_magenta": 0xad1457,
    "gold": 0xf1c40f,
    "dark_gold": 0xc27c0e,
    "orange": 0xe67e22,
    "dark_orange": 0xa84300,
    "red": 0xe74c3c,
    "dark_red": 0x992d22,
    "lighter_grey": 0x95a5a6,
    "dark_grey": 0x607d8b,
    "light_grey": 0x979c9f,
    "darker_grey": 0x546e7a,
    "blurple": 0x7289da,
    "greyple": 0x99aab5
}
rainbow_colors = [0x32a852, 0x3296a8, 0xb700ff, 0x9232a8, 0xa8326f, 0xf25207, 0x3efa00, 0xfa0000]

TOKEN = "***"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=",", intents=intents)
bot.remove_command("help")


# Преобразование различных велечин в секунды
def convert(number):
    number = str(number)
    try:
        if "s" in number:
            number = number.replace("s", "")
        elif "min" in number or "m" in number:
            number = number.replace("min", "")
            number = number.replace("m", "")
            number = str(int(number) * 60)
        elif "h" in number:
            number = number.replace("h", "")
            number = str(int(number) * 3600)
        elif "d" in number:
            number = number.replace("d", "")
            number = str(int(number) * (3600 * 24))
        elif "w" in number:
            number = number.replace("w", "")
            number = str(int(number) * (3600 * 24 * 7))
        elif "mon" in number or "month" in number:
            number = number.replace("month", "")
            number = number.replace("mon", "")
            number = str(int(number) * (3600 * 24 * 30))
        elif "y" in number:
            number = number.replace("y", "")
            number = str(int(number) * (3600 * 24 * 365))
        else:
            int(number)
    except:
        return None
    return int(number)


@bot.command(name='randint')
async def my_randint(ctx, min_int, max_int):
    num = random.randint(int(min_int), int(max_int))
    await ctx.send(num)

# Команда для бана участника
@commands.has_guild_permissions(administrator=True)
@bot.command(name="ban")
async def ban(ctx, member_name=None, time="7d", *, reason="no reason"):
    try:
        member_name = member_name.replace("<@", "")
        member_name = member_name.replace(">", "")
        member_name = ctx.guild.get_member(int(member_name))
    except:
        member_name = None
    if member_name == None:
        await ctx.send(embed = discord.Embed(title = "**Не существующее имя пользователя!**", 
            color = all_colors["red"]))
        return
    times_start = datetime.datetime.today()
    emb = discord.Embed(title = '**Уведомление - Ban**', color = 0xe74c3c)
    emb.add_field(name = '**Выдал:**', value = ctx.author.mention, inline = False)
    emb.add_field(name = '**Причина:**', value = reason, inline = False)
    emb.add_field(name = '**Длительность:**', value = time, inline = False)
    emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    time = convert(time)
    if time == None:
        await ctx.send(embed = discord.Embed(title = "Не верно задано время!",
            color = all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["bans"][member_name.name] = {}
    data[str(ctx.guild.id)]["bans"][member_name.name]["name"] = member_name.id
    data[str(ctx.guild.id)]["bans"][member_name.name]["reason"] = reason
    data[str(ctx.guild.id)]["bans"][member_name.name]["timer"] = time_zero.time() + time
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = emb)
    await ctx.guild.ban(member_name)

# Команда для мута участника
@commands.has_guild_permissions(administrator=True)
@bot.command(name="mute")
async def mute(ctx, member_name=None, time="300", *, reason="no reason"):
    try:
        member_name = member_name.replace("<@", "")
        member_name = member_name.replace(">", "")
        member_name = ctx.guild.get_member(int(member_name))
    except:
        member_name = None
    if member_name == None:
        await ctx.send(embed = discord.Embed(title =
            "**Не существующее имя пользователя!**", color = all_colors["red"]))
        return
    times_start = datetime.datetime.today()
    with open("data.json") as file:
        data = json.load(file)
    Role = data[str(ctx.guild.id)]["settings"]["mute_role"]
    if Role == None:
        await ctx.send(embed = discord.Embed(title =
            '**Назначте роль для мута перед использованием.**', color = 0xe74c3c))
        return
    role = discord.utils.get(ctx.guild.roles, id=int(Role))
    emb = discord.Embed(title = '**Уведомление - Mute**', color = 0xe74c3c)
    emb.add_field(name = '**Выдал:**', value = ctx.author.mention, inline = False)
    emb.add_field(name = '**Причина:**', value = reason, inline = False)
    emb.add_field(name = '**Длительность:**', value = time, inline = False)
    emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    time = convert(time)
    if time == None:
        await ctx.send(embed = discord.Embed(title = "Не верно задано время!",
            color = all_colors["red"]))
        return
    data[str(ctx.guild.id)]["mutes"][member_name.name] = {}
    data[str(ctx.guild.id)]["mutes"][member_name.name]["name"] = member_name.id
    data[str(ctx.guild.id)]["mutes"][member_name.name]["reason"] = reason
    data[str(ctx.guild.id)]["mutes"][member_name.name]["timer"] = time_zero.time() + time
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    try:
        await member_name.add_roles(role)
    except:
        await ctx.send(embed = discord.Embed(title =
            '**Установите роль бота выше роли мута!**', color = 0xe74c3c))
        return
    await ctx.send(embed = emb)

# Команда для изгнания участника
@commands.has_guild_permissions(administrator=True)
@bot.command(name="kick")
async def kick(ctx, member_name=None, *, reason="no reason"):
    try:
        member_name = member_name.replace("<@", "")
        member_name = member_name.replace(">", "")
        member_name = ctx.guild.get_member(int(member_name))
    except:
        member_name = None
    if member_name == None:
        await ctx.send(embed = discord.Embed(title = "**Не существующее имя пользователя!**",
            color = all_colors["red"]))
        return
    times_start = datetime.datetime.today()
    emb = discord.Embed(title = '**Уведомление - Kick**', color = 0xe74c3c)
    emb.add_field(name = '**Кикнул:**', value = ctx.author.mention, inline = False)
    emb.add_field(name = '**Причина:**', value = reason, inline = False)
    emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    await ctx.send(embed = emb)
    await member_name.kick()

# Команда для предупреждения участника
@commands.has_guild_permissions(administrator=True)
@bot.command(name="warn")
async def warn(ctx, member_name=None, *, reason="no reason"):
    try:
        member_name = member_name.replace("<@", "")
        member_name = member_name.replace(">", "")
        member_name = ctx.guild.get_member(int(member_name))
    except:
        member_name = None
    if member_name == None:
        await ctx.send(embed = discord.Embed(title = "**Не существующее имя пользователя!**",
            color = all_colors["red"]))
        return
    times_start = datetime.datetime.today()
    emb = discord.Embed(title = '**Уведомление - Warn**', color = 0xe74c3c)
    emb.add_field(name = '**Выдал:**', value = ctx.author.mention, inline = False)
    emb.add_field(name = '**Причина:**', value = reason, inline = False)
    emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    with open("data.json") as file:
        data = json.load(file)
    try:
        data[str(ctx.guild.id)]["warns"][member_name.name]["name"] = member_name.id
        data[str(ctx.guild.id)]["warns"][member_name.name]["count"] = int(data[str(
            ctx.guild.id)]["warns"][member_name.name]["count"]) + 1
    except:
        data[str(ctx.guild.id)]["warns"][member_name.name] = {}
        data[str(ctx.guild.id)]["warns"][member_name.name]["name"] = member_name.id
        data[str(ctx.guild.id)]["warns"][member_name.name]["count"] = 1
    await ctx.send(embed = emb)
    maximum = data[str(ctx.guild.id)]["warn_max"]
    if int(data[str(ctx.guild.id)]["warns"][member_name.name]["count"]) >= maximum:
        Role = data[str(ctx.guild.id)]["settings"]["mute_role"]
        if Role == None:
            await ctx.send(embed = discord.Embed(title =
                '**Бот не может замутить участника, так как вы не указали роль.**',
                color = 0xe74c3c))
            return
        role = discord.utils.get(ctx.guild.roles, id=int(Role))
        embz = discord.Embed(title = '**Уведомление - Mute**', color = 0xe74c3c)
        embz.add_field(name = '**Выдал:**', value = ctx.author.mention, inline = False)
        embz.add_field(name = '**Причина:**', value = "Слишком много нарушений!", inline = False)
        embz.add_field(name = '**Длительность:**', value = "5m", inline = False)
        embz.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
        data[str(ctx.guild.id)]["mutes"][member_name.name] = {}
        data[str(ctx.guild.id)]["mutes"][member_name.name]["name"] = member_name.id
        data[str(ctx.guild.id)]["mutes"][member_name.name]["reason"] = reason
        data[str(ctx.guild.id)]["mutes"][member_name.name]["timer"] = time_zero.time() + 300
        del data[str(ctx.guild.id)]["warns"][member_name.name]
        with open("data.json", "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        await ctx.send(embed = embz)
        await member_name.add_roles(role)
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Команда для создания категории, канала
@commands.has_guild_permissions(administrator=True)
@bot.command(name="newchannel")
async def newchannel(ctx, cat=None, name="", type0="text", private=None, *, roles=None):
    all = []
    if cat == None:
        await ctx.send(embed = discord.Embed(title=f"**Введите имя категории!**",
            color=all_colors["red"]))
        return
    #roles = roles.split(", ")
    for category in ctx.message.guild.categories:
        all.append(category.name)
    if cat in all:
        catyg = discord.utils.get(ctx.message.guild.categories, name=cat)
    else:
        catyg = await ctx.guild.create_category(cat)
    if name != "":
        if type0 == "text":
            chl = await ctx.guild.create_text_channel(name, category = catyg)
            type0 = "Текстовый"
        elif type0 == "voice":
            chl = await ctx.guild.create_voice_channel(name, category = catyg)
            type0 = "Голосовой"
    if private == "private":
        #admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            #admin_role: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await ctx.guild.create_text_channel('secret', overwrites=overwrites)
    if name == "":
        await ctx.send(embed = discord.Embed(title=f"**Категория {cat} успешно создана**",
            color=all_colors["green"]))
    else:
        await ctx.send(embed = discord.Embed(title=
            f"**{type0} канал {name} создан в категории {cat}**", color=all_colors["green"]))

# Команда для добавления ролей участнику сервера
@commands.has_guild_permissions(administrator=True)
@bot.command(name="addrolemember")
async def addrolemember(ctx, member=None, *, role0=None):
    try:
        member = member.replace("<@", "")
        member = member.replace(">", "")
        member = ctx.guild.get_member(int(member))
    except:
        member = None
    if member == None:
        await ctx.send(embed = discord.Embed(title = "**Не существующее имя пользователя!**",
            color = all_colors["red"]))
        return
    if role0 == None:
        await ctx.send(embed = discord.Embed(title =
            "**Пожалуйста, введите роли для добавления!**", color = all_colors["red"]))
        return
    role0 = role0.split("; ")
    for b in role0:
        role = discord.utils.get(ctx.guild.roles, name=b)
        if role == None:
            await ctx.send(embed = discord.Embed(title = f'**Роли {b} не существует!**',
                color = all_colors["red"]))
            return
        await member.add_roles(role)
    emb = discord.Embed(title = f'**Пользователю {member} добавлены следующие роли:**',
        color = 0x2ecc71)
    for i in range(len(role0)):
        emb.add_field(name = f'**Роль {i + 1}:**', value = role0[i], inline = False)
    await ctx.send(embed = emb)


# Команда для удаления ролей у участника сервера
@commands.has_guild_permissions(administrator=True)
@bot.command(name="removerolemember")
async def removerolemember(ctx, member=None, *, role0=None):
    try:
        member = member.replace("<@", "")
        member = member.replace(">", "")
        member = ctx.guild.get_member(int(member))
    except:
        member = None
    if member == None:
        await ctx.send(embed = discord.Embed(title =
            "**Не существующее имя пользователя!**", color = all_colors["red"]))
        return
    if role0 == None:
        await ctx.send(embed = discord.Embed(title =
            "**Пожалуйста, введите роли для добавления!**", color = all_colors["red"]))
        return
    role0 = role0.split("; ")
    for d in role0:
        role = discord.utils.get(ctx.guild.roles, name=d)
        if role == None:
            await ctx.send(embed = discord.Embed(title = f'**Роли {b} не существует!**',
                color = all_colors["red"]))
            return
        await member.remove_roles(role)
    emb = discord.Embed(title = f'**У пользователя {member} були удалены следующие роли:**',
        color = 0x2ecc71)
    for i in range(len(role0)):
        emb.add_field(name = f'**Роль {i + 1}:**', value = role0[i], inline = False)
    await ctx.send(embed = emb)

# Команда для очистки чата
@commands.has_guild_permissions(administrator=True)
@bot.command(name="clear")
async def clear(ctx, count="1"):
    if count.isdigit():
        count = int(count)
        await ctx.channel.purge(limit=count + 1)
    else:
        await ctx.send(embed = discord.Embed(title="Неверное значение для очистки чата!",
            color=all_colors["red"]))

# Команда для создания вложения по шаблону
@bot.command(name="specmsg")
async def specmsg(ctx, *, msg = None, color=0xe74c3c):
    if msg == None:
        await ctx.send(embed = discord.Embed(title=
            "Пожалуйста, введите сообщение, которое будет выведено в рамку согласно синтаксису.",
            color=all_colors["red"]))
        return
    if not("<title>:" in msg):
        embf = discord.Embed(title="**Ошибка синтаксиса:**", color=all_colors["red"])
        embf.add_field(name="Пропущен обязательный элемент встраивания:", value="<title>")
        await ctx.send(embed = embf)
        return
    rain = False
    nmsg = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+', msg)
    nmsg0 = []
    col, start = "", False
    for i in range(len(nmsg)):
        if nmsg[i] in ("<title>:", "<element>:", "<subelement>:", "<footer>:",):
            nmsg0.append(nmsg[i] + nmsg[i + 1])
    for i in nmsg:
        if "{" in i or start == True:
            col += " " + i
            start = True
        if "}" in i:
            start = False
    if col == "":
        col = 0xe74c3c
    else:
        col = col.replace("{", "")
        col = col.replace("}", "")
        col = col[1:]

        if col == "rainbow":
            rain = True
            col = 0xe74c3c
        elif col[0:2] == "0x":
            col = int(col, 16)
        else:
            col = all_colors[col]

    emb = await spec(nmsg0, col)

    msg = await ctx.send(embed = emb)
    if rain:
        while True:
            for j in rainbow_colors:
                emb = await spec(nmsg0, j)
                await asyncio.sleep(0.8)
                await msg.edit(embed = emb)

# Функция для сокращения кода (относится к вложениям, specmsg)
async def spec(nmsg0, col):
    for element in nmsg0:
        if "<title>" in element:
            element = element.replace("<title>:(", "")
            element = element.replace(")", "")
            emb = discord.Embed(title = element, color = col)
        if "<element>" in element:
            ind = nmsg0.index(element)
            element = element.replace("<element>:(", "")
            element = element.replace(")", "")
            try:
                if "<subelement>" in nmsg0[ind + 1]:
                    subelement = nmsg0[ind + 1].replace("<subelement>:(", "")
                    subelement = subelement.replace(")", "")
                else:
                    subelement = "**No information**"
            except:
                subelement = "**No information**"
            emb.add_field(name = element, value = subelement, inline = False)
        if "<footer>" in element:
            element = element.replace("<footer>:(", "")
            element = element.replace(")", "")
            emb.set_footer(text = element)
    return emb

# Функция для создания радужной роли (Отключается через несколько
# секунд в связи с ограничениями API)
@bot.command(name="set_rainbow_role")
async def set_rainbow_role(ctx, *, role : discord.Role):
    for i in range(10):
        for j in rainbow_colors:
            await role.edit(color=j)
            await asyncio.sleep(2)

# Команда для очистки предупреждений всем участникам сервера
@commands.has_guild_permissions(administrator=True)
@bot.command(name="clearwarns")
async def clearwarns(ctx):
    times_start = datetime.datetime.today()
    emb = discord.Embed(title = "**Уведомление**", color = 0xe74c3c)
    emb.add_field(name = "**Внимание!**", value = "Все варны были сброшены.", inline=False)
    emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    await ctx.send(embed = emb)
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["warns"] = {}
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Команда для вывода всех команд бота
@bot.command(name="help")
async def help(ctx):
    times_start = datetime.datetime.today()
    with open("data.json") as file:
        data = json.load(file)
    warns_max = data[str(ctx.guild.id)]["warn_max"]
    emb = discord.Embed(title = '**Администрирование**', color = 0xe74c3c)
    emb.add_field(name = f'**,ban**', value =
        "Забанить участника сервера.\n,ban <member> <time> <reason>\n Пример: !ban @User 6h",
        inline = True)
    emb.add_field(name = f'**,mute**', value =
        "Замутить участника сервера.\n,mute <member> <time> <reason>\n Примечание: Чтобы команда работала создайте роль для мута и привяжите её к боту командой ,set_mute_role", inline = False)
    emb.add_field(name = f'**,kick**', value =
        "Кикнуть участника с сервера.\n,kick <member> <reason>", inline = True)
    emb.add_field(name = f'**,warn**', value =
        f"Дать предупреждение участнику сервера.\n,warn <member> <reason>\nПосле {warns_max} предупреждений участник получит мут.",
        inline = False)
    emb.add_field(name = f'**,newchannel**', value =
        "Создать новый канал в существующей или новой категории.\n,newchannel <category> <channel> <text/voice>",
        inline = False)
    emb.add_field(name = f'**,addrolemember**', value =
        "Добавить роли участнику сервера.\n,addrolemember <member> <role1>; <role2> ...\nПримечание: роли писать через ;",
        inline = False)
    emb.add_field(name = f'**,removerolemember**', value =
        "Удалить роли у участника сервера.\n,removerolemember <member> <role1>; <role2> ...\nПримечание: роли писать через ;",
        inline = False)
    emb.add_field(name = f'**,clear**', value =
        "Очистить чат на n-ное количество сообщений\n,clear <count>", inline = False)
    emb.add_field(name = f'**,clearwarns**', value =
        "Очистить все предупреждения у всех участников сервера\n,clearwarns", inline = False)
    emb.add_field(name = f'**,specmsg**', value =
        "Создать сообщение в рамке\n,specmsg <title>: (Заголовок) <element>: (Подзаголовок) <subelement>: (Содержание данного подзаголовка) <element>: (Подзаголовок2) <subelement>: (Содержание данного подзаголовка2) <footer>: (Нижний колонтитул) {color}\nПримечание: Угловые скобки неизменяемы, параметров <element> может быть сколько угодно, после него обязателен параметр <subelement>, параметр <title> и <footer> только один. В круглых скобках - нужный вам текст", inline = False)
    emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    embz = discord.Embed(title = '**Каналы и побочные команды**',
        color = 0xe74c3c)
    embz.add_field(name = f'**,set_audit_channel <channel_name>**',
        value='Задать канал для аудита', inline = True)
    embz.add_field(name = f'**,set_bot_channel <channel_name>**',
        value='Задать канал для бота', inline = True)
    embz.add_field(name = f'**,set_salute_channel <channel_name>**',
        value='Задать канал для приветствий', inline = True)
    embz.add_field(name = f'**,set_salute <greeting1>; <greeting2> ...**', value=
        'Задать возможные приветствия новых участников.\nПримечание:{member}-участник, который зашёл на сервер',
        inline = True)
    embz.add_field(name = f'**,set_count_warns <count>**', value=
        'Задать количество предупреждений до мута', inline = True)
    embz.add_field(name = f'**,set_mute_role <role>**', value = "Задать роль для мута",
        inline = False)
    embz.add_field(name = f'**,help_audit_settings**', value='Показать настройки аудита',
        inline = True)

    emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    await ctx.send(embed = emb)
    await ctx.send(embed = embz)

# Команда для вывода команд для настройки аудита
@commands.has_guild_permissions(administrator=True)
@bot.command(name="help_audit_settings")
async def help_audit_settings(ctx):
    times_start = datetime.datetime.today()
    embz = discord.Embed(title = '**Настройки аудита:**', color = 0xe74c3c)
    embz.add_field(name = f'**,audit <on/off>**', value=
        'Включить/выключить аудит', inline = True)
    embz.add_field(name = f'**,audit_all_msgs <on/off>**', value=
        'Логировать/не логировать все сообщения', inline = True)
    embz.add_field(name = f'**,audit_deleted_msgs <on/off>**', value=
        'Логировать/не логировать удалённые сообщения', inline = True)
    embz.add_field(name = f'**,audit_edited_msgs <on/off>**', value=
        'Логировать/не логировать изменённые сообщения', inline = True)
    #embz.add_field(name = f'**,audit_roles_edit <on/off>**', value=
        #'Логировать/не логировать создание/удаление ролей', inline = True)
    embz.add_field(name = f'**,audit_channel_edit <on/off>**', value=
        'Логировать/не логировать добавление каналов', inline = True)
    embz.add_field(name = f'**,audit_servname_edit\n<on/off>**', value=
        'Логировать/не\nлогировать изменение\nназвания сервера', inline = True)
    embz.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
    await ctx.send(embed = embz)

# Команда для отправки сообщения от имени бота
@bot.command(name="send")
async def send(ctx, *, msg=None):
    if msg == None:
        ctx.send(embed = discord.Embed(title="Введите сообщение для отправки ботом!",
            color = all_colors["red"]))
    await ctx.send(msg)

# Команда для установки канала аудита
@commands.has_guild_permissions(administrator=True)
@bot.command(name="set_audit_channel")
async def set_audit_channel(ctx, *, msg=None):
    with open("data.json") as file:
        data = json.load(file)
    channel = discord.utils.get(ctx.guild.channels, name=msg)
    if channel == None:
        await ctx.send(embed = discord.Embed(title = f'**Такого канала не существует!**',
            color = all_colors["red"]))
        return
    data[str(ctx.guild.id)]["settings"]["channels"]["audit_channel"] = channel.id
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = discord.Embed(title = f'**Канал аудита установлен: {msg}**',
        color = 0x2ecc71))

# Команда для установки канала бота
@commands.has_guild_permissions(administrator=True)
@bot.command(name="set_bot_channel")
async def set_bot_channel(ctx, msg=None):
    with open("data.json") as file:
        data = json.load(file)
    channel = discord.utils.get(ctx.guild.channels, name=msg)
    if channel == None:
        await ctx.send(embed = discord.Embed(title = f'**Такого канала не существует!**',
            color = all_colors["red"]))
        return
    data[str(ctx.guild.id)]["settings"]["channels"]["bot_channel"] = channel.id
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = discord.Embed(title = f'**Канал для бота установлен: {msg}**',
        color = 0x2ecc71))

# Команда для установки канала приветствий
@commands.has_guild_permissions(administrator=True)
@bot.command(name="set_salute_channel")
async def set_salute_channel(ctx, msg=None):
    with open("data.json") as file:
        data = json.load(file)
    channel = discord.utils.get(ctx.guild.channels, name=msg)
    if channel == None:
        await ctx.send(embed = discord.Embed(title = f'**Такого канала не существует!**',
            color = all_colors["red"]))
        return
    data[str(ctx.guild.id)]["settings"]["channels"]["hello_channel"] = channel.id
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = discord.Embed(title = f'**Канал для приветствий установлен: {msg}**',
        color = 0x2ecc71))

# Команда для установки роли мута
@commands.has_guild_permissions(administrator=True)
@bot.command(name="set_mute_role")
async def set_mute_role(ctx, *, msg0=None):
    with open("data.json") as file:
        data = json.load(file)
    msg = discord.utils.get(ctx.guild.roles, name=msg0)
    if msg == None:
        await ctx.send(embed = discord.Embed(title = f"Роли {msg0} не существует!",
            color = all_colors["red"]))
        return
    data[str(ctx.guild.id)]["settings"]["mute_role"] = msg.id
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = discord.Embed(title =
        f'**Роль для мута установоена: {msg}**', color = 0x2ecc71))

# Команда для включения/отключения аудита
@commands.has_guild_permissions(administrator=True)
@bot.command(name="audit")
async def audit(ctx, msg=None):
    if msg not in ("on", "off"):
        await ctx.send(embed = discord.Embed(title =
            "Некорректно введено значение. Оно должно быть равно off или on",
            color = all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    if data[str(ctx.guild.id)]["settings"]["channels"]["audit_channel"] == None:
        await ctx.send(embed = discord.Embed(title =
            f'**Прежде чем включить аудит - установите для него канал командой ,set_audit_channel**\nПодробности - ,help',
            color = 0x2ecc71))
        return
    if msg == "on":
        data[str(ctx.guild.id)]["settings"]["audit_settings"]["on"] = True
        await ctx.send(embed = discord.Embed(title = f'**Аудит включён**', color = 0x2ecc71))
    if msg == "off":
        data[str(ctx.guild.id)]["settings"]["audit_settings"]["on"] = False
        await ctx.send(embed = discord.Embed(title = f'**Аудит отключён**', color = 0x2ecc71))
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Команда для включения/отключения логирования всех сообщений
@commands.has_guild_permissions(administrator=True)
@bot.command(name="audit_all_msgs")
async def audit_all_msgs(ctx, msg=None):
    if msg not in ("on", "off"):
        await ctx.send(embed = discord.Embed(title =
            "Некорректно введено значение. Оно должно быть равно off или on",
            color = all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["settings"]["audit_settings"]["all_msgs"] = msg
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    if msg == "on":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование сообщений включено**', color = 0x2ecc71))
    elif msg == "off":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование сообщений отключено**', color = 0x2ecc71))

# Команда для включения/отключения логирования добавления новых каналов
@commands.has_guild_permissions(administrator=True)
@bot.command(name="audit_channel_edit")
async def audit_channel_edit(ctx, msg=None):
    if msg not in ("on", "off"):
        await ctx.send(embed = discord.Embed(title =
            "Некорректно введено значение. Оно должно быть равно off или on",
            color = all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["settings"]["audit_settings"]["edit_channels"] = msg
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    if msg == "on":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование каналов включено**', color = 0x2ecc71))
    elif msg == "off":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование каналов отключено**', color = 0x2ecc71))

# Команда для включения/отключения логирования удалённых сообщений
@commands.has_guild_permissions(administrator=True)
@bot.command(name="audit_deleted_msgs")
async def audit_deleted_msgs(ctx, msg=None):
    if msg not in ("on", "off"):
        await ctx.send(embed = discord.Embed(title =
            "Некорректно введено значение. Оно должно быть равно off или on",
            color = all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["settings"]["audit_settings"]["del_msgs"] = msg
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    if msg == "on":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование удалённых сообщений включено**', color = 0x2ecc71))
    elif msg == "off":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование удалённых сообщений отключено**', color = 0x2ecc71))

# Команда для включения/отключения логирования изменённых сообщений
@commands.has_guild_permissions(administrator=True)
@bot.command(name="audit_edited_msgs")
async def audit_edited_msgs(ctx, msg=None):
    if msg not in ("on", "off"):
        await ctx.send(embed = discord.Embed(title =
            "Некорректно введено значение. Оно должно быть равно off или on",
            color = all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["settings"]["audit_settings"]["edit_msgs"] = msg
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    if msg == "on":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование изменённых сообщений включено**', color = 0x2ecc71))
    elif msg == "off":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование изменённых сообщений отключено**', color = 0x2ecc71))

# Команда для включения/отключения логирования изменения ролей (временно не работает)
@commands.has_guild_permissions(administrator=True)
@bot.command(name="audit_edit_roles")
async def audit_edit_roles(ctx, msg=None):
    if msg not in ("on", "off"):
        await ctx.send(embed = discord.Embed(title =
            "Некорректно введено значение. Оно должно быть равно off или on", color =
            all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["settings"]["audit_settings"]["edit_msgs"] = msg
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    if msg == "on":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование изменения сообщений включено**', color = 0x2ecc71))
    elif msg == "off":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование изменения сообщений отключено**', color = 0x2ecc71))

# Команда для включения/отключения логирования изменения названия сервера
@commands.has_guild_permissions(administrator=True)
@bot.command(name="audit_servname_edit")
async def audit_servname_edit(ctx, msg=None):
    if msg not in ("on", "off"):
        await ctx.send(embed = discord.Embed(title =
            "Некорректно введено значение. Оно должно быть равно off или on",
            color = all_colors["red"]))
        return
    with open("data.json") as file:
        data = json.load(file)
    data[str(ctx.guild.id)]["settings"]["audit_settings"]["edit_servname"] = msg
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    if msg == "on":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование изменения названия сервера включено**', color = 0x2ecc71))
    elif msg == "off":
        await ctx.send(embed = discord.Embed(title =
            f'**Логирование изменения названия сервера отключено**', color = 0x2ecc71))

# Команда для установки максимального количества варнов перед мутом
@commands.has_guild_permissions(administrator=True)
@bot.command(name="set_count_warns")
async def set_count_warns(ctx, count=None):
    with open("data.json") as file:
        data = json.load(file)
    if not(count.isdigit()):
        await ctx.send(embed = discord.Embed(title =
            "Введено неверное значение для максимального количества предупреждений!",
            color = all_colors["red"]))
        return
    data[str(ctx.guild.id)]["warn_max"] = int(count)
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = discord.Embed(title =
        f'**После {int(count)} предупреждений участник будет замучен.**', color = 0x2ecc71))

# Команда для добавления новых приветствий
@commands.has_guild_permissions(administrator=True)
@bot.command(name="set_salute")
async def set_salute(ctx, *, greetings):
    greetings = greetings.split("; ")
    with open("data.json") as file:
        data = json.load(file)
    for i in greetings:
        data[str(ctx.guild.id)]["greetings"].append(i)
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = discord.Embed(title = "Приветствия добавлены.",
        color=all_colors["green"]))

# Команда для удаления приветствий по их содержанию
@commands.has_guild_permissions(administrator=True)
@bot.command(name="clear_salute")
async def clear_salute(ctx, *, greetings=None):
    with open("data.json") as file:
        data = json.load(file)
    if greetings != None:
        greetings = greetings.split("; ")
        for i in greetings:
            data[str(ctx.guild.id)]["greetings"].remove(i)
    else:
        data[str(ctx.guild.id)]["greetings"] = []
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await ctx.send(embed = discord.Embed(title = "Приветствия были очищены",
        color=all_colors["green"]))

# Проверка, хватает ли участнику прав для взаимодействия с командой
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingPermissions):
        await ctx.send(embed = discord.Embed(title=
            'Недостаточно прав для выполнения команды!', color=all_colors["red"]))



bot.run(TOKEN)














#
