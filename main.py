from discord import Client, Intents, Embed, Activity, ActivityType
import discord_interactions as interactions
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import *
import os
import asyncio
import re
import pickle
import psycopg2

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
  settings = await getsettings()
  for guild in WhatStrain.guilds:
    try:
      settings[guild.id]
    except KeyError:
      settings[guild.id] = settingclass()
  print('ready')
  await WhatStrain.change_presence(activity=Activity(type=ActivityType.watching, name="/help"))
  await setsettings(settings)
  return

@WhatStrain.event
async def on_guild_join(guild):
  settings = await getsettings()
  try:
    settings[guild.id]
  except KeyError:
    settings[guild.id] = settingclass()
  await setsettings(settings)

@slash.slash(
  name='seedfinder',
  description='Search for a strain in the SeedFinder database',
  # guild_ids=[913857013577043968],
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
  await ctx.defer()
  perms = await permscheck(ctx, False)
  if perms == False:
    return

  strain = strain.strip()
  print(strain)
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
  await ctx.defer()
  perms = await permscheck(ctx, False)
  if perms == False:
    return
  strain = strain.strip()
  print(strain)
  try:
    searchresult = await leaflyinfo(strain)
  except HTTPError:
    await ctx.send('Oops, it looks like Google\'s stupid servers are overloaded. Guck Foogle.')
    return
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
  await ctx.defer()
  perms = await permscheck(ctx, False)
  if perms == False:
    return
  strain = strain.strip()
  print(strain)
  searchinfo = await leafsearch(strain)
  if searchinfo is None:
    await ctx.send('Sorry, I couldn\'t find any strains matching *\"'+strain+'\"*')
  newEmbed = await leaflysearchmessage(ctx, searchinfo, strain)

@slash.slash(
  name='invite',
  # guild_ids=[913857013577043968],
  description='Sends a link allowing you to invite WhatStrain to your server')

async def invite(ctx: ComponentContext):
  await ctx.defer()
  perms = await permscheck(ctx, False)
  if perms == False:
    return
  await ctx.send('Use this link to invite <@889784843116879902> to your server:\n\nhttps://discord.com/api/oauth2/authorize?client_id=889784843116879902&permissions=2048&scope=bot%20applications.commands')
  return

@slash.slash(
  name='help',
  # guild_ids=[913857013577043968],
  description='Provides an overview of available commands')

async def _help(ctx):
  await ctx.defer()
  perms = await permscheck(ctx, False)
  if perms == False:
    return
  newEmbed = discord.Embed(title='WhatStrain Help')
  newEmbed.add_field(name='/seedfinder `strain` `breeder(optional)`', value='Searches SeedFinder.eu for a strain. Can optionally be narrowed by breeder name. Note that SeedFinder limits the max number of results to 420.', inline=False)
  newEmbed.add_field(name='/leafly `strain`', value='Searches Leafly.com for a strain and returns the best result it can find.\nUse /searchleafly for the top 12 results.', inline=False)
  newEmbed.add_field(name='/leaflysearch `strain`', value='Displays the top 12 results from Leafly and allows you to choose.', inline=False)
  # newEmbed.add_field(name='/feedback `message`', value='Submit a suggestion or bug.', inline=False)
  newEmbed.add_field(name='/invite', value='Sends a link allowing you to invite the bot to your server', inline=False)
  newEmbed.add_field(name='__Credits__', value=f'Author: <@253339557355978752>\nOfficial discord: <https://discord.gg/uABbNVk89y>\nGitHub: <https://github.com/PapaKool/WhatStrain>', inline=False)
  newEmbed.description='*Note: This bot is still in beta, and you may experience bugs.*'
  await ctx.send(embed=newEmbed)


@slash.subcommand(
  base='settings',
  # guild_ids=[913857013577043968],
  name='botchannel',
  description='Restricts the bot to one (or more) channel(s). Use reset:true to enable in all channels',
  options=[create_option(
    name='channel',
    description='Which channel would you like to whitelist?',
    option_type=7,
    required=False,
    )]
  )

async def settings_botchannel(ctx: ComponentContext, channel=None):
  await ctx.defer()
  perms = await permscheck(ctx, True)
  if perms == False:
    return
  if ctx.channel.permissions_for(ctx.author).administrator != True:
    await ctx.send(f'Sorry, {ctx.author.mention}, only administrators can use this command.')

  if channel == None:
    newEmbed = Embed(title='Channel Whitelist', description='The bot will currently function in the following channels:\n\n')
    if settings[ctx.guild.id].whitelist == []:
      newEmbed.description += '(**all** channels)'
    else:
      for chan in settings[ctx.guild.id].whitelist:
        newEmbed.description += WhatStrain.get_channel(chan).mention + '\n'
    await ctx.send(embed=newEmbed)
    return
  elif type(channel).__name__ != 'TextChannel':
    await ctx.send(f'Cannot add {channel.mention} to whitelist, because it is not a text channel.')
    return
  elif channel.id in settings[ctx.guild.id].whitelist:
    settings[ctx.guild.id].whitelist.remove(channel.id)
    if settings[ctx.guild.id].whitelist == []:
      await ctx.send(f'{channel.mention} removed from the whitelist. Because the whitelist is empty, commands will now work in **__all__** channels')
    else:
      await ctx.send(f'Removed from whitelist. You may no longer use commands in {channel.mention}')
  else:
    settings[ctx.guild.id].whitelist.append(channel.id)
    await ctx.send(f'Added to whitelist. You may now use commands in {channel.mention}')
  await setsettings(settings)


@slash.subcommand(
  base='settings',
  # guild_ids=[913857013577043968],
  name='botchannelreset',
  description='Restricts the bot to one (or more) channel(s). Use reset:true to enable in all channels'
  )

async def settings_botchannelreset(ctx: ComponentContext):
  
  await ctx.defer()
  perms = await permscheck(ctx, True)
  if perms == False:
    return
  
  if ctx.channel.permissions_for(ctx.author).administrator != True:
    await ctx.send(f'Sorry, {ctx.author.mention}, only administrators can use this command.')
    return
  settings[ctx.guild.id].whitelist = []
  await ctx.send('Botchannel list reset. The bot will now operate in all channels')
  await setsettings(settings)

@slash.subcommand(
  base='settings',
  name='bugreport',
  # guild_ids=[913857013577043968],
  description='Use this to report a bug (this will be posted publically on the offical server)',
  options=[create_option(
    name='bug',
    description='Describe the bug you experienced',
    option_type=3,
    required=True
    )])

async def settings_bugreport(ctx: ComponentContext, bug=None):
  await ctx.defer()
  perms = await permscheck(ctx, True)
  if perms == False:
    return
  if bug == None:
    await ctx.send('You must describe the bug you want to report.')
    return
  else:
    newEmbed = Embed()
    newEmbed.add_field(name='Bug', value=bug, inline=False)
    newEmbed.add_field(name='Details', value=f'Reported by: {ctx.author.mention}\nServer: {ctx.guild.name}\nIs admin: {ctx.channel.permissions_for(ctx.author).administrator}', inline=False)
    await WhatStrain.get_channel(913989528396628058).send(embed=newEmbed)
    await ctx.send(f'Thanks, {ctx.author.mention}, your bug report has been sent.\nYou may follow up with this bug report at the official WhatStrain server: <https://discord.gg/uABbNVk89y>')
# choices = [create_choice(name='Disable threading', value=0)]  {WhatStrain.get_user(id=253339557355978752).mention}
# for count in range(1,16):
#   choices.append(create_choice(name=str(count), value=count))

# ========================================================
#   if ctx.channel not in settings[ctx.guild.id].whitelist and ctx.channel.permissions_for(ctx.author) != True:
# ========================================================


# @slash.slash(
#   name='gettable',
#   guild_ids=[913857013577043968],
#   description='make table',
#  )

async def getsettings():
  conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
  cur = conn.cursor()
  cur.execute('SELECT * FROM settingstable;')
  unpickled = pickle.loads(cur.fetchone()[0])
  print(unpickled)
  conn.commit()
  cur.close()
  conn.close()
  print('done')
  return unpickled

async def setsettings(localsettings):
  global settings
  conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
  cur = conn.cursor()
  pickled = pickle.dumps(localsettings)
  cur.execute('UPDATE settingstable SET settings=%s;', [pickled])
  cur.execute('SELECT * FROM settingstable;')
  settings = pickle.loads(cur.fetchone()[0])
  print(settings)
  conn.commit()
  cur.close()
  conn.close()
  print('done')
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
async def permscheck(ctx, ismodcommand):
  if ctx.channel.permissions_for(ctx.author).administrator != True and ismodcommand == True:
    ctx.send(content=f'Sorry {ctx.author.mention}, this command requires administrator permission.')
    return False
  if settings[ctx.guild.id].whitelist != [] and ctx.channel.id not in settings[ctx.guild.id].whitelist:
    channels = ''
    for chan in settings[ctx.guild.id].whitelist:
      channels += '\n' + WhatStrain.get_channel(chan).mention
    await ctx.send(content=f'Sorry {ctx.author.mention}, commands are not allowed in this channel. Please use: \n{channels}')
    return False
  else:
    return True

WhatStrain.run(os.environ.get('TOKEN'))
