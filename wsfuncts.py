import discord
from discord_slash.utils.manage_components import *
from wsclasses import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs

def isint(string):
  try:
    int(string)
  except ValueError:
    return False
  else:
    return True

async def sfmessage(ctx, searchinfo, strain):

  newEmbed = discord.Embed(title='Search Results for ' + strain)
  if searchinfo == None:
    await ctx.channel.send('Strain \'**' + strain.replace('%20', ' ') + '**\' not found.')
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
      body = body + ' '
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




async def searchmessage(channel, searchinfo, strain):

  
  


  if searchinfo == None:
    await channel.send('Strain \'**' + strain.replace('%20', ' ') + '**\' not found.')
    return
  
  newEmbed = discord.Embed(title='Search Results', description=searchinfo.desc)
  print(searchinfo.image)
  newEmbed.set_image(url=searchinfo.image)
  newEmbed.set_footer(text='Strain info provided (unwillingly) by Leafly.com')
  
  bar = '['
  for x in range(searchinfo.percent):
    bar = bar + '█'
  for x in range(20 - searchinfo.percent):
    bar = bar + '_'
  bar = bar + ']'

  #newEmbed.add_field(name = 'Variety', value = searchinfo.variety + '\nRelaxing ' + bar + ' Energizing', inline = True)
  #newEmbed.add_field(name = 'Cannabinoids', value = 'THC: ' + searchinfo.thc + '\nCBD: ' + searchinfo.cbd, inline = True)
  #newEmbed.add_field(name = 'Terpenes', value = searchinfo.terps, inline = True)

  #newEmbed.add_field(name = 'Flavors', value = searchinfo.flavors, inline = True)
  #newEmbed.add_field(name = 'Effects', value = searchinfo.effects, inline = True)
  #newEmbed.add_field(name = 'Negatives', value = searchinfo.neg, inline = True)
  #newEmbed.add_field(name = 'Uses', value = searchinfo.uses, inline = True)

  msg = await channel.send(embed=newEmbed)
  
  return msg


async def leaflyinfo(query):  # Gets variables to plug into the DM
  link = Request("https://www.leafly.com/search?q=" + query.replace(' ', '%20') + "&searchCategory=strain", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.231'})
  
  print(link)

  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  # print(bssearch)
  if "Internal Server Error" in bssearch.body.get_text():
    return None

  results = bssearch.find_all(class_='hell')
  processed = []
  for res in results:
    name = res.find(class_='xs1').get_text
    link = res.find(class_='xs1').a.href

  print(results)

  return

  
async def leaflyresult(linklonk):
  result = str(bssearch.body.find_next('div', {'class':'relative flex flex-col justify-between bg-white h-full elevation-low'}).find('a',href=re.compile("/strains/"))['href'])
  # print(bssearch.body.find_all('div', {'class':'relative flex flex-col justify-between bg-white h-full elevation-low'}))
  link = Request('https://www.leafly.com' + result, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.231'})


  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bsinfo = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  
  

  thisstrain = strainclass()

  thisstrain.name = str(bsinfo.body.find('h1', itemprop='name').get_text())  
  print(thisstrain.name)
  image = str(bsinfo.body.find('img',srcset=re.compile("flower-images"))['srcset'])
  img = re.search('http(.+?)png', image)

  if img == None:
    img = re.search('http(.+?)jpg', image)
    thisstrain.image = 'http' + img[1] + 'jpg'
  else:
    thisstrain.image = 'http' + img[1] + 'png'

  thisstrain.desc = str(bsinfo.body.find('div', itemprop='description').get_text()) 
  #thisstrain.variety = str(bsinfo.body.find('div', {"class":'flex-1 py-sm text-center text-sm rounded-l-full font-bold border-green text-grey'})) 
  #thisstrain.thc = str(bsinfo.body.find(string=re.compile("THC"))) 
  # cbd = str(bsinfo.body.find(string=re.compile("CBD")))
  # cbg =  str(bsinfo.body.find(string=re.compile("CBG")))
  # thisstrain.terps = str(bsinfo.body.find(string=re.compile("The most abundant terpene")))
  # flavorelements = bsinfo.body.find('div', {"class":"jsx-2865998862 flavor-list pt-md mt-md inline-block lg:flex"}).find_all('a',href=re.compile('strains/lists/flavor'))
  flavs = ''
  # for ele in flavorelements:
  #   flavs = flavs + ele.get_text() + '\n'

  thisstrain.flavors = flavs
  #print(thisstrain.flavors)
  #thisstrain.effects = bsinfo.body.find_all(string=re.compile('strains/lists/effect'))
  #thisstrain.uses = bsinfo.body.find_all(string=re.compile('strains/lists/condition'))
  
  print(thisstrain)
  return thisstrain

 
async def sfinfo(query):  # Gets variables to plug into the DM
  link = Request(url="https://en.seedfinder.eu/search/results/", data = urlencode({'SSUCHW': str(query),'save':'🔎','welchesform':'klein'}).encode('utf-8'), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.50'}, method='POST')
  

  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  # print(str(bssearch) + '\n\n\n\n\n\n\n\n\n')
  # if "No search hits" in bssearch.body.get_text():
  #   return None
  
  result = bssearch.body.find('table').find_all('tr', class_='hell') #.find('a',href=re.compile("/strains/"))['href'])
  # print(bssearch.body.find_all('div', {'class':'relative flex flex-col justify-between bg-white h-full elevation-low'}))
  slist = []
  for key in result:
    # print(key.find_all('th').get_text())
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
    slist.append(newstrain)
  
  return slist
  link = Request('https://www.leafly.com' + result, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.231'})


  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bsinfo = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  
  

  thisstrain = searchclass()

  thisstrain.name = str(bsinfo.body.find('h1', itemprop='name').get_text())  
  print(thisstrain.name)
  image = str(bsinfo.body.find('img',srcset=re.compile("flower-images"))['srcset'])
  img = re.search('http(.+?)png', image)

  if img == None:
    img = re.search('http(.+?)jpg', image)
    thisstrain.image = 'http' + img[1] + 'jpg'
  else:
    thisstrain.image = 'http' + img[1] + 'png'

  thisstrain.desc = str(bsinfo.body.find('div', itemprop='description').get_text()) 
  #thisstrain.variety = str(bsinfo.body.find('div', {"class":'flex-1 py-sm text-center text-sm rounded-l-full font-bold border-green text-grey'})) 
  #thisstrain.thc = str(bsinfo.body.find(string=re.compile("THC"))) 
  # cbd = str(bsinfo.body.find(string=re.compile("CBD")))
  # cbg =  str(bsinfo.body.find(string=re.compile("CBG")))
  # thisstrain.terps = str(bsinfo.body.find(string=re.compile("The most abundant terpene")))
  # flavorelements = bsinfo.body.find('div', {"class":"jsx-2865998862 flavor-list pt-md mt-md inline-block lg:flex"}).find_all('a',href=re.compile('strains/lists/flavor'))
  flavs = ''
  # for ele in flavorelements:
  #   flavs = flavs + ele.get_text() + '\n'

  thisstrain.flavors = flavs
  #print(thisstrain.flavors)
  #thisstrain.effects = bsinfo.body.find_all(string=re.compile('strains/lists/effect'))
  #thisstrain.uses = bsinfo.body.find_all(string=re.compile('strains/lists/condition'))
  
  print(thisstrain)
  return thisstrain