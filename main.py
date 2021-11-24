from discord import Client, Intents, Embed
import discord_interactions as interactions
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import *
import os
import asyncio
import re

from wsclasses import *
from sffuncts import *
from lfuncts import *
from lsfuncts import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs


WhatStrain = Client()
slash = SlashCommand(WhatStrain, sync_commands=True)


@slash.slash(
  name='seedfinder',
  guild_ids=[885339477160124416],
  description='Search for a strain in the SeedFinder database',
  options=[
    create_option(
      name='strain',
      description='The name of the strain you want to search for',
      option_type=3,
      required=True)],)

async def _seedfinder(ctx, strain:str):
  strain = strain.strip()
  print(strain)
  await ctx.defer()
  searchinfo = await sfinfo(strain)
  # await ctx.send('')
  await sfsearchmessage(ctx, searchinfo, strain)
  # msglst[mid.id].author = message.author.id
  # msglst[mid.id].results

@slash.slash(
  name='leafly',
  guild_ids=[885339477160124416],
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
  guild_ids=[885339477160124416],
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

# @slash.slash(
#   name='help',
#   guild_ids=[885339477160124416],
#   description='Provides an overview of available commands')

# async def _help(ctx):
#   newEmbed = discord.Embed(title='WhatStrain Help')
#   newEmbed.add_field(name='/leafly `strain`', value='Searches Leafly.com for a strain and returns the best result it can find.\nUse /searchleafly for the top)

@slash.component_callback()
async def sfselect(ctx: ComponentContext):
  if 'https://en.seedfinder.eu/strain-info' in ctx.selected_options[0]:
    await sfresultmessage(ctx)
    return
  elif 'https://www.leafly.com/strains' in ctx.selected_options[0]:
    newEmbed = await leaflyresultmessage(ctx, ctx.selected_options[0])
    await ctx.send(embed=newEmbed)


WhatStrain.run(os.environ.get(TOKEN))
