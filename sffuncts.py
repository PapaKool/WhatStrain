import discord
from discord_slash.utils.manage_components import *
from wsclasses import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode, quote_plus

import pickle
from bs4 import BeautifulSoup as bs
from math import floor




async def sfsearchmessage(ctx, searchinfo, strain, breeder, searches):
  msg = await ctx.send('Loading results...')

  searches[msg.id] = msgclass()
  newEmbed = discord.Embed(title='Search Results for ' + strain)
  searches[msg.id].embed = newEmbed
  if searchinfo == []:
    if breeder == None:
      await msg.edit(content=f'Strain \'**{strain}**\' not found.')
    else:
      await msg.edit(content=f'Strain \'**{strain}**\' by \'*{breeder}*\' not found.')
    
    return
  # with open('settings.pk1', 'rb') as file:
  #   settings = pickle.load(file)
  # threaded = False
  # if len(searchinfo)/25 >= settings[ctx.guild.id].threadat:
  #   thread = await ctx.channel.create_thread(name=f'Search results for {query}', type='public', auto_archive_duration=10)
  #   threaded = True

  name = ''
  breeder = ''
  kind = ''
  #growcond = ''
  flowertime = ''
  fem = ''
  body = '`         Name                 Breeder       \n         ‾‾‾‾‾                ‾‾‾‾‾‾‾‾      \n'
  count = 1
  loop = 1
  options = []
  lbutton = create_button(style=ButtonStyle.blurple, label='⇚', custom_id='left')
  lbuttondisabled = create_button(style=ButtonStyle.blurple, label='⇚', custom_id='left', disabled=True)
  rbutton = create_button(style=ButtonStyle.blurple, label='⇛', custom_id='right')
  rbuttondisabled = create_button(style=ButtonStyle.blurple, label='⇛', custom_id='right', disabled=True)
  # pagenavoptions = []
  # for i in range(floor(len(searchinfo)/25)):
  #   pagenavoptions.append(create_select_option(str(i+1), i+1))
  # pagenav = create_select(options=pagenavoptions, placeholder='Jump to page:', custom_id='sfpagenav', min_values=1, max_values=1)

  for s in searchinfo:
    bname = s.name + '               '
    bbreeder = s.breeder + '               '
    
    body = body + str(loop) + '. ' + bname[:20] 
    if loop < 10:
      body = body + ' ' # Adds an extra space for numbers 1-9 bc single digit throws row length off
    body = body + '` ` ' + bbreeder[:15] + '  \n'
    op = str(loop) + '. ' + s.name
    options.append(create_select_option(op[:99], s.link.replace('https://en.seedfinder.eu/strain-info', '')))
    count = count + 1
    loop = loop + 1
    if count == 26 or loop == len(searchinfo) + 1:
      body = body + '`'
      if loop == len(searchinfo) + 1:
        body = body + '\n**End of results**'
        if len(searchinfo) == 420:
          body += ' (Capped at 420 by SeedFinder)'
      count = 1
      
    ##   newEmbed.add_field(name='Strain name', value=name, inline=True)
    ##   newEmbed.add_field(name='Breeder', value=breeder, inline=True)
    ##   newEmbed.add_field(name='Type', value=kind, inline=True)
    ##   newEmbed.add_field(name='Growcond', value=growcond, inline=True)
    ##   newEmbed.add_field(name='Flower time', value=flowertime, inline=True)
    ##   newEmbed.add_field(name='Fem seeds?', value=fem, inline=True)
      select = create_select(options=options, placeholder='Select a strain option from the list above', custom_id='sfselect', min_values=1, max_values=1)
      newEmbed.description = body
      if len(searchinfo) > 25:
        if loop == 26:
          components = [create_actionrow(select), create_actionrow(lbuttondisabled, rbutton)]
          searches[msg.id].results = [body]
          searches[msg.id].select = [components]
          searches[msg.id].embed.description = searches[msg.id].results[0]
          await msg.edit(content='', embed=searches[msg.id].embed, components=searches[msg.id].select[0])
        elif loop == len(searchinfo) + 1:
          # searches[msg.id].limit = len(searches[msg.id].results) - 1
          components = [create_actionrow(select), create_actionrow(lbutton, rbuttondisabled)]
          searches[msg.id].results.append(body)
          searches[msg.id].select.append(components)
          # searches[msg.id].results.reverse()
          # searches[msg.id].select.reverse()
        else:
          components = [create_actionrow(select), create_actionrow(lbutton, rbutton)]
          searches[msg.id].results.append(body)
          searches[msg.id].select.append(components)
      else:
        components = [create_actionrow(select)]
        searches[msg.id].results = [body]
        searches[msg.id].select = [components]
        searches[msg.id].embed.description = searches[msg.id].results[0]
        await msg.edit(content='', embed=searches[msg.id].embed, components=searches[msg.id].select[0])
  
      newEmbed.clear_fields()
      components = []
      options = []
      body = '`         Name                 Breeder       \n         ‾‾‾‾‾                ‾‾‾‾‾‾‾‾      \n'
      print(len(searches[msg.id].results))
      searches[msg.id].limit = len(searches[msg.id].results) - 1
  return searches



async def sfresultmessage(ctx):
  link = 'https://en.seedfinder.eu/strain-info' + ctx.selected_options[0]
  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser')
  title = bssearch.head.title.get_text().replace(' :: Cannabis Strain Info', '')
  sfdescription = bssearch.body.find(class_='partInnerDiv').find('p').get_text()
  breederdescription = bssearch.body.find('p', itemprop='description').get_text(separator='\n')[:1024]
  thumb = bssearch.body.find('span', class_='breederPic').a.img['src'].replace('../../../','https://en.seedfinder.eu/')
  try:
    weedpic = bssearch.body.find('div',class_='partInnerDiv').find('span', itemprop='thumbnail').a['href']
  except AttributeError:
    weedpic = None
  newEmbed = discord.Embed(title=title, url=link)

  if weedpic != None:
    newEmbed.set_image(url=weedpic)
  newEmbed.set_thumbnail(url=thumb)
  newEmbed.set_footer(text='Info provided by SeedFinder.eu')
  newEmbed.add_field(name='Overview', value=sfdescription, inline=False)
  newEmbed.add_field(name='Breeder\'s description:', value=breederdescription, inline=False)

  await ctx.send(embed=newEmbed)
  return



 
async def sfinfo(query, breeder):  # Gets variables to plug into the DM
  link = Request(url="https://en.seedfinder.eu/search/results/", data = urlencode({'SSUCHW': query,'save':'🔎','welchesform':'klein'}).encode('utf-8'), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.50'}, method='POST')
  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  try:
    result = bssearch.body.find('table').find_all('tr', class_='hell') #.find('a',href=re.compile("/strains/"))['href'])
  except AttributeError:
    return []
  slist = []
  for key in result:
    newstrain = resultclass()
    newstrain.name = key.find('th').get_text()
    newstrain.link = key.find('th').a['href'].replace('../../','https://en.seedfinder.eu/')
    newstrain.breeder, newstrain.type, newstrain.growcond, newstrain.flowertime, newstrain.female, newstrain.buy, newstrain.rating = key.find_all('td')
    newstrain.breeder = newstrain.breeder.get_text()
    newstrain.type = newstrain.type.img['title']
    newstrain.growcond = newstrain.growcond.img['title']
    newstrain.flowertime = newstrain.flowertime.get_text()
    newstrain.female = newstrain.female.img['title']
    if newstrain.buy.img:
      newstrain.buy = 'Yes'
    else:
      newstrain.buy = 'No'
    newstrain.rating = newstrain.rating.img['title']
    if breeder != None:
      if breeder.lower() in newstrain.breeder.lower():
        slist.append(newstrain)
    else:
      slist.append(newstrain)
  
  return slist


def getbreeders():
  link = Request(url='https://en.seedfinder.eu/search/extended/', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.50'})
  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  breeders = ['Unknown or Legendary']
  for breeder in bssearch.find(id='seedbank').find_all('option'):
    breeders.append(create_select_option(breeder.get_text(),breeder.get_text()))
  return breeders
