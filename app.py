
import discord
from discord import utils
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import requests
from bs4 import BeautifulSoup

import os
from random import randint

from const import URL, API_BOT_NAME, API_BOT_PASS




#Задаем константы
# Константа ID Поста с которого будут считываться реакции
POST_ID = 1
# Список ролей в соответсвии с эмоджи  (Эмоджи http://getemoji.com/), эмоджики просто копируем в ключи
ROLES = {
            '💩':724963604583153674,    #role 1
            '👻':724963710367563776,    #role 2
            '🤡':724963754806345798,    #role 3
            'admin':724965035033624597,    # admin
}
# Список исключений - роли которые не считаются при подсчете кол-ва ролей у юзера ( Вроде МОдератора или ВИП юзера)
EXROLES = ()
#Максимальное кол-во ролей которе сможет взять 1 юзер
MAX_ROLES_PER_USER = 2


                            # 2) Получение всех сообщений чатов на сервере и вывод их в консоль

BOT_TOKEN = '...'
# Модель с настроиными ПОЛЬЗОВАТЕЛЕМ коммандами
class MyBot(commands.Cog):

    # Для бота надо задать ввод переменную БОТА, и от неё будет
    def __init__(self, bot):
        self.bot = bot

    # Ответ бота ВАЖНО если бот сам чтото говорит, то произойдет ВЕЧНЫЙ ЦИКЛ, поэтому надо добавлять проверку , не бот ли это сказал!!!
    @commands.command()
    async def hello(self,ctx):
        await ctx.send('Hello')
        # await message.send(f'Hello {message.author}')
        print(f'Model Message from {ctx.message.author}: {ctx.message.content}')


    # Вывод данных о готовности бота
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged on as {self.bot.user.name}')


    # Вывод данных написаных пользователем (echo)
    @commands.Cog.listener()
    async def on_message(self,message):
        print(f'Message from {message.author}: {message.content}')


    # Раздача ролей через эмоджи - СОБЫТИЯ - EVENT
    # Добавление РЕАКЦИЙ на сервере ролей через эмоджи - СОБЫТИЯ - EVENT -
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        channel = self.bot.get_channel(int(payload.channel_id)) #get_channel(payload.channel_id)                  # Получаем объект канала ID
        message = await channel.fetch_message(payload.message_id)       # Получаем объект соощения ID
        member = utils.get(message.guild.members, id=payload.user_id)   # Получаем объект юзера ID, поставившего эмоцию

        try:
            emoji= str(payload.emoji)   # Эмоджи которую выбрал юзер
            role = utils.get(message.guild.roles, id=ROLES[emoji])   # Объект выбраной роли(если есть)

            if (len([i for i in member.roles if i.id not in EXROLES]) <= MAX_ROLES_PER_USER):
                await member.add_roles(role)
                print(f'[SUCCESS] User {member.display_name} has been granted with role {role.name}')
            else:
                await message.remove_reaction(payload.emoji, member)
                print(f'[ERROR] Too many roles for {member.display_name}, can not grant role {role.name}'+emoji)
        except KeyError as e:
            print(f'[ERROR] KeyError, no role found for user {member.display_name}')
        except Exception as e:
            print(repr(e))
    # Удаление Реакций на сервере
    async def on_raw_reaction_remove(self,payload):
        pass


# API Авторизация + получение данных с сайта NKP
def api_f_auth():
    data = requests.get(URL+API_BOT_NAME+API_BOT_PASS)
    soup = BeautifulSoup(data.text, 'html.parser')
    print(soup)
    return f'{soup}'

# Резервные советы, можно и в БД записать, но лучше не перегружать
def offline_api():
    adv_list =[]
    filepath = os.path.abspath(os.path.dirname(__file__)) + '/base.txt'
    baseopen = open(filepath, mode='r', encoding='utf-8-sig')
    for line in baseopen:
        i = line.strip('-').strip()
        if i != '':
            adv_list.append(i)
    baseopen.close()
    generate = randint(0, len(adv_list))
    choice = adv_list[generate - 1]
    return str(choice)


# Задаем переменную Для ОБЪЕКТА нашей МОДЕЛИ
bot = commands.Bot(command_prefix='!')

# Можно задать переменную для ДЕКОРАТОРА
BotDecor = commands.Bot(command_prefix='!')

client = discord.Client(command_prefix='!')


@BotDecor.command()
async def hello(ctx):
    await ctx.send('ЗДАРОВА ЩЕГЛЫ!')
    await ctx.send(f'Здаров по mention - {ctx.message.author.mention}')
    await ctx.send(f'Здаров по id <@{ctx.message.author.id}>')

    #await message.send(f'Hello {message.author}')
    print(f'Decorator Message from {ctx.message.author}: {ctx.message.content}')


#Команда для активации API с сайта
@BotDecor.command()
async def adv(ctx):

    try:
        # Личное сообющение
        await ctx.author.send(f'{api_f_auth()}')
        # Сообщение в чат
        await ctx.send(f'Уважаемы {ctx.message.author.mention} совет отправлен, пожалуйста проверьте личные сообщения ')

        print('online')
    except Exception as e:
        print(e)
        print('offline')
        await ctx.author.send(f'{offline_api()}')
        await ctx.send(f'Уважаемы {ctx.message.author.mention} совет отправлен, пожалуйста проверьте личные сообщения ')


@BotDecor.command()
async def seeya(ctx):
    await ctx.send(f'Бывай кожаный ')



# Выдача РОЛИ ПО КОМАНДЕ
@BotDecor.command()
@commands.has_permissions(administrator =True)
async def add_role_1(ctx, member: discord.Member):
    new_role= discord.utils.get(ctx.message.guild.roles, name='Role 1')
    print(f'Роль {new_role} назначена {member}')
    await member.add_roles(new_role)

# Выдача МУТА
@BotDecor.command()
@commands.has_permissions(administrator =True)
async def mute(ctx, member: discord.Member):
    new_role= discord.utils.get(ctx.message.guild.roles, name='mute')
    await member.add_roles(new_role)



@BotDecor.event
async def on_ready():

    #Приветсиве при активации бота
    #channel = client.get_channel(724942576792240221)
    #await  BotDecor.get_channel(724942576792240221).send('Hi bot activate!')
    print(f'1) {BotDecor.user.name} has connected to Discord!')




@BotDecor.event
async def on_member_join(member):
    print("Recognised that a member called " + member.name + " joined")
    try:
        await BotDecor.send_message(member, 'Hi new member!')
        print("Sent message to " + member.name)
    except:
        print("Couldn't message " + member.name)


BotDecor.run(BOT_TOKEN)
