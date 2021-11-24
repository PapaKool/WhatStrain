import discord
from discord_slash.utils.manage_components import *
from wsclasses import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup as bs

async def leafsearch(query):  # Gets variables to plug into the DM
  link = Request("https://www.leafly.com/search?q=" + quote_plus(query) + "&searchCategory=strain", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.231'})
  

  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  if "Internal Server Error" in bssearch.body.get_text():
    return None

  results = bssearch.find_all(class_='relative flex flex-col justify-between bg-white h-full elevation-low')
  resultlist = []
  for result in results:
    newstrain = resultclass()
    newstrain.name = result.find(itemprop='name').get_text()
    if result.find(class_='text-xs truncate text-grey').get_text().strip() is not '':
      newstrain.name += ' (' + result.find(class_='text-xs truncate text-grey').get_text().strip() + ')'
    while len(newstrain.name) < 60:
      newstrain.name += ' '
    newstrain.link = 'https://www.leafly.com' + result.a['href']
    resultlist.append(newstrain)
 
  return resultlist

  


async def leaflysearchmessage(ctx, searchinfo, strain):

  newEmbed = discord.Embed(title='Search Results for ' + strain)
  
  name = ''
  body = '`'
  count = 1
  loop = 1
  options = []
  for s in searchinfo:
    if loop < 10:
      body = body + ' ' # Adds an extra space for numbers 1-9 bc single digit throws row length off
    body = body + str(loop) + '. ' + s.name[:60] + '\n' 
    options.append(create_select_option(str(loop) + '. ' + s.name, s.link))
    count = count + 1
    loop = loop + 1
    if  loop == len(searchinfo) + 1:
      body = body + '`'
      if loop == len(searchinfo) + 1:
        body = body + '\n**End of results**'
      count = 1
      select = create_select(options=options, placeholder='Select a strain option from the list above', custom_id='sfselect', min_values=1, max_values=1)
      newEmbed.description = body
      await ctx.send(embed=newEmbed, components=[create_actionrow(select)])
      newEmbed.clear_fields()
      options = []
      body = '`'
  return