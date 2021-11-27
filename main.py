from discord import Client, Intents, Embed, Activity, ActivityType
import discord_interactions as interactions
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import *
import os
import asyncio
import re
import pickle

from wsclasses import *
from sffuncts import *
from lfuncts import *
from lsfuncts import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs

settings = {}
searches = {}
WhatStrain = Client()
slash = SlashCommand(WhatStrain, sync_commands=True)

# breeders = getbreeders()

@WhatStrain.event
async def on_ready():
  print('ready')
  await WhatStrain.change_presence(activity=Activity(type=ActivityType.watching, name="/help"))
  return


@slash.slash(
  name='seedfinder',
  description='Search for a strain in the SeedFinder database',
  guild_ids=[885339477160124416],
  options=[
    create_option(
      name='strain',
      description='The name of the strain you want to search for',
      option_type=3,
      required=True),
    create_option(
      name='breeder',
      description='Optional: Narrow your results by breeder',
      option_type=3,
      required=False)],)

async def _seedfinder(ctx, strain:str, breeder=None):
  global searches
  strain = strain.strip()
  print(strain)
  await ctx.defer()
  searchinfo = await sfinfo(strain, breeder)
  # await ctx.send('')
  searches = await sfsearchmessage(ctx, searchinfo, strain, breeder, searches)
  # msglst[mid.id].author = message.author.id
  # msglst[mid.id].results

@slash.slash(
  name='leafly',
  description='Search for a strain in the Leafly database',
  options=[
    create_option(
      name='strain',
      description='The name of the strain you want to search for',
      option_type=3,
      required=True)],)

async def _leafly(ctx, strain:str):
  strain = strain.strip()
  print(strain)
  await ctx.defer()
  searchresult = await leaflyinfo(strain)
  if searchresult is None:
    await ctx.send('Sorry, I couldn\'t find any strains matching *\"'+strain+'\"*')
    return
  newEmbed = await leaflyresultmessage(ctx, searchresult)
  await ctx.send('*Best result for \'' + strain + '\':*', embed=newEmbed)

@slash.slash(
  name='leaflysearch',
  description='Allows you to choose from a list of possible strain matches',
  options=[
    create_option(
      name='strain',
      description='The name of the strain you want to search for',
      option_type=3,
      required=True)],)

async def _leaflysearch(ctx, strain:str):
  strain = strain.strip()
  print(strain)
  await ctx.defer()
  searchinfo = await leafsearch(strain)
  if searchinfo is None:
    await ctx.send('Sorry, I couldn\'t find any strains matching *\"'+strain+'\"*')
  newEmbed = await leaflysearchmessage(ctx, searchinfo, strain)

@slash.slash(
  name='invite',
  guild_ids=[885339477160124416],
  description='Sends a link allowing you to invite WhatStrain to your server')

async def invite(ctx: ComponentContext):
  await ctx.send('Use this link to invite <@889784843116879902> to your server:\n\nhttps://discord.com/api/oauth2/authorize?client_id=889784843116879902&permissions=2048&scope=bot%20applications.commands')
  return

@slash.slash(
  name='help',
  guild_ids=[885339477160124416, 765254440717385759, 913857013577043968],
  description='Provides an overview of available commands')

async def _help(ctx):
  newEmbed = discord.Embed(title='WhatStrain Help')
  newEmbed.add_field(name='/seedfinder `strain` `breeder*(optional)*`', value='Searches SeedFinder.eu for a strain. Can optionally be narrowed by breeder name. Note that SeedFinder limits the max number of results to 420.', inline=False)
  newEmbed.add_field(name='/leafly `strain`', value='Searches Leafly.com for a strain and returns the best result it can find.\nUse /searchleafly for the top 12 results.', inline=False)
  newEmbed.add_field(name='/leaflysearch `strain`', value='Displays the top 12 results from Leafly and allows you to choose.', inline=False)
  # newEmbed.add_field(name='/feedback `message`', value='Submit a suggestion or bug.', inline=False)
  newEmbed.add_field(name='/invite', value='Sends a link allowing you to invite the bot to your server', inline=False)
  newEmbed.add_field(name='__Credits__', value=f'Author: <@253339557355978752>\nOfficial discord: <https://discord.gg/uABbNVk89y>\nGitHub: <https://github.com/PapaKool/WhatStrain>', inline=False)
  newEmbed.description='*Note: This bot is still in beta, and you may experience bugs.*'
  await ctx.send(embed=newEmbed)


# @slash.slash(
#   name='settings',
#   guild_ids=[885339477160124416, 913857013577043968],
#   description='Allows moderators to set various permissions',

#   )
# choices = [create_choice(name='Disable threading', value=0)]  {WhatStrain.get_user(id=253339557355978752).mention}
# for count in range(1,16):
#   choices.append(create_choice(name=str(count), value=count))

# @slash.slash(
#   name='threadresponses',
#   guild_ids=[885339477160124416],
#   description='Allows you to set when the bot will respond in a thread (/help for more info)',
#   options=[create_option(
#     name='messagecount',
#     description='Number of msgs to thread at',
#     option_type=4,
#     choices=choices,
#     required=True)])

# async def threadresponses(ctx, messagecount: int):
#   print(1)
#   if ctx.channel.permissions_for(ctx.author).administrator != True:
#     await ctx.send(f'Sorry, {ctx.author}, you don\'t have permission to use this command.')
#   else:
#     print(2)
#     if ctx.guild.id not in settings:
#       settings[ctx.guild.id] = settingclass()
#     settings[ctx.guild.id].threadat = messagecount
#     with open('settings.pk1', 'wb') as file:
#       pickle.dump(settings, file)
#     await ctx.send(f'Roger that, I will now thread responses longer than **{str(settings[ctx.guild.id].threadat)}** messages.')

@slash.component_callback()
async def sfselect(ctx: ComponentContext):
    await sfresultmessage(ctx)
    return

@slash.component_callback()
async def lsselect(ctx: ComponentContext):
  newEmbed = await leaflyresultmessage(ctx, ctx.selected_options[0])
  await ctx.send(embed=newEmbed)
  return

@slash.component_callback()
async def left(ctx: ComponentContext):
  global searches
  searches[ctx.origin_message_id].index -= 1
  searches[ctx.origin_message_id].embed.description = searches[ctx.origin_message_id].results[searches[ctx.origin_message_id].index]
  await ctx.edit_origin(embed=searches[ctx.origin_message_id].embed, components=searches[ctx.origin_message_id].select[searches[ctx.origin_message_id].index])
  return

@slash.component_callback()
async def right(ctx: ComponentContext):
  global searches
  searches[ctx.origin_message_id].index += 1
  searches[ctx.origin_message_id].embed.description = searches[ctx.origin_message_id].results[searches[ctx.origin_message_id].index]
  await ctx.edit_origin(embed=searches[ctx.origin_message_id].embed, components=searches[ctx.origin_message_id].select[searches[ctx.origin_message_id].index])
  return

# @slash.component_callback()
# async def sfpagenav(ctx: ComponentContext):
#   global searches
#   searches[ctx.origin_message_id].index = ctx.selected_options[0] - 1
#   searches[ctx.origin_message_id].embed.description = searches[ctx.origin_message_id].results[searches[ctx.origin_message_id].index]
#   await ctx.edit_origin(embed=searches[ctx.origin_message_id].embed, components=searches[ctx.origin_message_id].select[searches[ctx.origin_message_id].index])


token = 'ODg5Nzg0ODQzMTE2ODc5OTAy.YUmStg.JEO7d1C43ttzc8vzzqHHcSXwERA'
WhatStrain.run(token)