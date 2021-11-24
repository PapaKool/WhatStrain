import discord
from discord_slash.utils.manage_components import *
from wsclasses import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup as bs

def isint(string):
  try:
    int(string)
  except ValueError:
    return False
  else:
    return True

async def sfsearchmessage(ctx, searchinfo, strain):

  newEmbed = discord.Embed(title='Search Results for ' + strain)
  if searchinfo == None:
    await ctx.send('Strain \'**' + strain.replace('%20', ' ') + '**\' not found.')
    return

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
  for s in searchinfo:
    # body = '`Breeder:` ' + s.breeder + '  `Type:` ' + s.type + '  `Growspace:` ' + \
    # s.growcond + '  `Flower time:` ' + s.flowertime + ' days  `Fem seeds?:` ' + s.female
    #name = str(loop) + '. ' + s.name
    # newEmbed.add_field(name=name, value=body, inline=False)

    ## name = name + new
    ## breeder = breeder + s.breeder + '\n'
    ## kind = kind + s.type + '\n'
    ## #growcond = growcond + s.growcond + '\n'
    ## flowertime = flowertime + s.flowertime + '\n'
    ## fem = fem + s.female + '\n'
    bname = s.name + '               '
    bbreeder = s.breeder + '               '
    
    body = body + str(loop) + '. ' + bname[:20] 
    if loop < 10:
      body = body + ' ' # Adds an extra space for numbers 1-9 bc single digit throws row length off
    body = body + '` ` ' + bbreeder[:15] + '  \n'
    options.append(create_select_option(str(loop) + '. ' + s.name, s.link))
    count = count + 1
    loop = loop + 1
    if count == 26 or loop == len(searchinfo) + 1:
      body = body + '`'
      if loop == len(searchinfo) + 1:
        body = body + '\n**End of results**'
      count = 1
      
    ##   newEmbed.add_field(name='Strain name', value=name, inline=True)
    ##   newEmbed.add_field(name='Breeder', value=breeder, inline=True)
    ##   newEmbed.add_field(name='Type', value=kind, inline=True)
    ##   newEmbed.add_field(name='Growcond', value=growcond, inline=True)
    ##   newEmbed.add_field(name='Flower time', value=flowertime, inline=True)
    ##   newEmbed.add_field(name='Fem seeds?', value=fem, inline=True)
      select = create_select(options=options, placeholder='Select a strain option from the list above', custom_id='sfselect', min_values=1, max_values=1)
      newEmbed.description = body
      await ctx.send(embed=newEmbed, components=[create_actionrow(select)])
      newEmbed.clear_fields()
      options = []
      body = '`         Name                 Breeder       \n         ‾‾‾‾‾                ‾‾‾‾‾‾‾‾      \n'
  return



async def sfresultmessage(ctx):
  link = ctx.selected_options[0]
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
  newEmbed.set_footer(text='Info provided by SeedFinder.com')
  newEmbed.add_field(name='Overview', value=sfdescription, inline=False)
  newEmbed.add_field(name='Breeder\'s description:', value=breederdescription, inline=False)

  await ctx.send(embed=newEmbed)
  return



 
async def sfinfo(query):  # Gets variables to plug into the DM
  link = Request(url="https://en.seedfinder.eu/search/results/", data = urlencode({'SSUCHW': query,'save':'🔎','welchesform':'klein'}).encode('utf-8'), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.50'}, method='POST')
  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object

  result = bssearch.body.find('table').find_all('tr', class_='hell alternate') #.find('a',href=re.compile("/strains/"))['href'])
  
  if len(result) > 250:
    result = result[:250]

  slist = []
  for key in result:
    newstrain = resultclass()
    newstrain.name = key.find('th').get_text()
    print(newstrain.name)
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
    slist.append(newstrain)
  
  return slist
