import discord
import logging
import datetime
import time
import json
import schedule
import asyncio
import random
from discord import utils
from discord.utils import get
from discord.ext import tasks

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Токен бота
TOKEN = "***"

# Цвета для рамок
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

class YLBotClient(discord.Client):
    pass


intents = discord.Intents.default()
intents.members = True
client = YLBotClient(intents=intents)

# Очищаем все варны бота в 00:00
def job():
    all = []
    with open("data.json") as file:
        data = json.load(file)
    for i in client.guilds:
        for j in data[str(i.id)]["warns"]:
            all.append(j)
        for j in all:
            del data[str(i.id)]["warns"][j]
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

schedule.every().day.at("00:00").do(job)

async def clearallwarns():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

#Каждые 10 секунд проверяем не закончились ли баны/муты,
#не вышел ли бот с сервера, а если вышел,
#то удаление сервера из json-а
@tasks.loop(seconds=10)
async def rest():
    try:
        all = []
        all0 = []
        all1 = []
        with open("data.json") as file:
            data = json.load(file)
        for i in client.guilds:
            all0.append(i.id)
        for i in data:
            if not(int(i) in all0):
                all1.append(i)
        for i in all1:
            del data[i]
        for i in client.guilds:
            for j in data[str(i.id)]["bans"]:
                if data[str(i.id)]["bans"][j]["timer"] < time.time():
                    guild = client.get_guild(i.id)
                    member = await client.fetch_user(int(data[str(i.id)]["bans"][j]['name']))
                    await guild.unban(member)
                    all.append(j)
            for j in all:
                print(data[str(i.id)]["bans"][j])
                del data[str(i.id)]["bans"][j]
            all = []
    except:
        pass

    for i in client.guilds:
        for j in data[str(i.id)]["mutes"]:
            if data[str(i.id)]["mutes"][j]["timer"] < time.time():
                guild = client.get_guild(i.id)
                member = guild.get_member(int(data[str(i.id)]["mutes"][j]['name']))
                Role = data[str(i.id)]["settings"]["mute_role"]
                role = discord.utils.get(guild.roles, id=Role)
                await member.remove_roles(role)
                all.append(j)
        for j in all:
            del data[str(i.id)]["mutes"][j]
        all = []

    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@rest.before_loop
async def zerox():
    await client.wait_until_ready()

rest.start()

# Если аудит работает на сервере и включены все сообщения
#для него, то они будут высвечиваться
# в выбранном канале
@client.event
async def on_message(message):
    if message.author.bot:
        return
    with open("data.json") as file:
        data = json.load(file)
    if data[str(message.guild.id)]["settings"]["audit_settings"]["on"] and data[str(
        message.guild.id)]["settings"]["audit_settings"]["all_msgs"] == "on":
        channel0 = data[str(message.guild.id)]["settings"]["channels"]["audit_channel"]
        channel = client.get_channel(channel0)
        times_start = datetime.datetime.today()
        emb = discord.Embed(title = '**Логи - Сообщение**', color = 0x3498db)
        emb.add_field(name = '**Ник:**', value = message.author, inline = False)
        emb.add_field(name = '**Соодержание:**', value = message.content, inline = False)
        emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
        await channel.send(embed = emb)

# Логирование изменения каналов
@client.event
async def on_guild_channel_create(channelx : discord.channel):
    with open("data.json") as file:
        data = json.load(file)
    if data[str(channelx.guild.id)]["settings"]["audit_settings"]["on"] and data[str(
        channelx.guild.id)]["settings"]["audit_settings"]["edit_channels"] == "on":
        channel0 = data[str(channelx.guild.id)]["settings"]["channels"]["audit_channel"]
        channel = client.get_channel(channel0)
        times_start = datetime.datetime.today()
        emb = discord.Embed(title = '**Логи - Канал создан**', color = 0x9b59b6)
        emb.add_field(name = '**Название канала:**', value = channelx.name, inline = False)
        emb.add_field(name = '**Название категории:**', value = channelx.category, inline = False)
        emb.add_field(name = '**ID канала:**', value = channelx.id, inline = False)
        emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
        await channel.send(embed = emb)

#Логирование изменения названия сервера
@client.event
async def on_guild_update(before, after):
    with open("data.json") as file:
        data = json.load(file)
    if data[str(after.id)]["settings"]["audit_settings"]["on"] and data[str(
        after.id)]["settings"]["audit_settings"]["edit_servname"] == "on":
        channel0 = data[str(after.id)]["settings"]["channels"]["audit_channel"]
        channel = client.get_channel(channel0)
        times_start = datetime.datetime.today()
        emb = discord.Embed(title = '**Логи - Название сервера изменено**', color = 0x2ecc71)
        emb.add_field(name = '**Прошлое название:**', value = before, inline = False)
        emb.add_field(name = '**Новое название:**', value = after, inline = False)
        emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
        await channel.send(embed = emb)

'''
@client.event
async def on_guild_role_deleted(role):
    with open("data.json") as file:
        data = json.load(file)
    #if data[str(message.guild.id)]["settings"]["audit_settings"]["on"] and data[str(
        message.guild.id)]["settings"]["audit_settings"]["edit_roles"] == "on":
        print('Role name:', role.name)#имя роли
        print('Role color:', role.color)#цвет роли
        print('Role id:', role.id)#айди роли
        print('Role permissions:', role.permissions)#разрешения роли
        print('Role created_at:', role.created_at)#когда роль была создана
'''

# Логирование удалённых сообщений
@client.event
async def on_message_delete(message):
    with open("data.json") as file:
        data = json.load(file)
    if data[str(message.guild.id)]["settings"]["audit_settings"]["on"] and data[str(
        message.guild.id)]["settings"]["audit_settings"]["del_msgs"] == "on":
        times_start = datetime.datetime.today()
        channel0 = data[str(message.guild.id)]["settings"]["channels"]["audit_channel"]
        channel = client.get_channel(channel0)
        emb = discord.Embed(title = '**Логи - Сообщение удалено**', color = 0xa84300)
        emb.add_field(name = '**Ник:**', value = message.author, inline = False)
        emb.add_field(name = '**Соодержание:**', value = message.content, inline = False)
        emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
        await channel.send(embed = emb)

# Логирование изменённых сообщений
@client.event
async def on_message_edit(message0, message1):
    with open("data.json") as file:
        data = json.load(file)
    if data[str(message0.guild.id)]["settings"]["audit_settings"]["on"] and data[
        str(message0.guild.id)]["settings"]["audit_settings"]["edit_msgs"] == "on":
        times_start = datetime.datetime.today()
        channel0 = data[str(message0.guild.id)]["settings"]["channels"]["audit_channel"]
        channel = client.get_channel(channel0)
        emb = discord.Embed(title = '**Логи - Сообщение изменено**', color = 0x1f8b4c)
        emb.add_field(name = '**Ник:**', value = message0.author, inline = False)
        emb.add_field(name = '**Соодержание до:**', value = message0.content, inline = False)
        emb.add_field(name = '**Соодержание после:**', value = message1.content, inline = False)
        emb.set_footer(text = f'Дата: {times_start.strftime("%Y-%m-%d, %H:%M:%S")}')
        await channel.send(embed = emb)

# Запуск работы проверки
@client.event
async def on_ready():
    await rest()
    client.loop.create_task(clearallwarns())

# Добавление сервера в БД после захода
@client.event
async def on_guild_join(guild):
    zero = {
        "name": guild.name,
        "id": guild.id,
        "warn_max": 3,
        "greetings": [],
        "mutes": {},
        "bans": {},
        "warns": {},
        "settings": {
            "channels": {
                "audit_channel": None,
                "hello_channel": None,
                "bot_channel": None
            },
            "audit_settings": {
                "on": False,
                "all_msgs": "off",
                "del_msgs": "on",
                "edit_msgs": "on",
                "edit_roles": "on",
                "edit_servname": "on",
                "edit_channels": "on"
            },
            "mute_role": None
        }
    }
    with open("data.json") as file:
        data = json.load(file)
    data[guild.id] = zero
    with open("data.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    await guild.text_channels[0].send(
    "Бот Olimp теперь с Вами!\nПропишите ,help что-бы увидеть список комманд")


#Приветствие новых пользователей на сервере
@client.event
async def on_member_join(member):
    with open("data.json") as file:
        data = json.load(file)
    channel = member.guild.text_channels[0]
    if data[str(member.guild.id)]["settings"]["channels"]["hello_channel"] != None:
        channel = data[str(member.guild.id)]["settings"]["channels"]["hello_channel"]
        channel = client.get_channel(int(channel))
    if data[str(member.guild.id)]["greetings"] == []:
        await channel.send(embed=discord.Embed(title=
            f"Добро пожаловать на сервер, {member.name}!", color = all_colors["green"]))
    else:
        greet = random.choice(data[str(member.guild.id)]["greetings"]).replace("{member}",
            member.name)
        await channel.send(embed=discord.Embed(title=greet, color=all_colors["green"]))

#Запуск бота
client.run(TOKEN)
