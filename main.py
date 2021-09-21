import discord
import os
import asyncio
import re

from urllib.request import urlopen, Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs

 
# runninggames = {0 : None}
class strainclass:

  def __init__(self):
    
    self.name = 'Unknown'
    self.desc = 'Unknown'
    self.image = 'https://thereef.ca/wp-content/uploads/2019/03/Cannabis-Sessions-questions.jpg'
    self.variety = 'Unknown'
    self.percent = 0
    self.thc = 'Unknown'
    self.cbd = 'Unknown'
    self.terps = 'Unknown'
    self.flavors = 'Unknown'
    self.effects = 'Unknown'
    self.neg = 'Unknown'
    self.uses = 'Unknown'

async def getstraininfo(query):  # Gets variables to plug into the DM
  link = Request("https://www.leafly.com/search?q=" + query + "&searchCategory=strain", headers={'User-Agent': 'Mozilla/5.0'})
  
  print(link)

  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  if "Internal Server Error" in bssearch.body.get_text():
    return None

  result = str(bssearch.body.find_next('div', {'class':'relative flex flex-col justify-between bg-white h-full elevation-low'})[0].find('a',href=re.compile("/strains/"))['href'])
  print(result)
  link = Request('https://www.leafly.com' + result, headers={'User-Agent': 'Mozilla/5.0'})


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

 
 
 
class WikiBluff(discord.Client):
  def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      

  async def on_ready(self):
      print('Logged in as')
      print(self.user.name)
      print(self.user.id)
      print('------')
      print(str(self.loop.is_running()))

      
  async def on_message(self, message):
    global runninggames
    if message.author == client.user:
      await asyncio.sleep(1)
      return
    message.content = message.content.lower()
    if message.content.startswith('$strain '):
      strain = (message.content.replace('$strain ','').strip().replace(' ', '%20'))
      
      
      straininfo = await getstraininfo(strain)
      await makemessage(message.channel, straininfo, strain)
    else:
      return



def isint(string):
  try:
    int(string)
  except ValueError:
    return False
  else:
    return True

async def makemessage(channel, straininfo, strain):
  global runninggames
  if straininfo == None:
    await channel.send('Strain \'**' + strain.replace('%20', ' ') + '**\' not found.')
    return
  newEmbed = discord.Embed(title=straininfo.name, description=straininfo.desc)
  print(straininfo.image)
  newEmbed.set_image(url=straininfo.image)
  newEmbed.set_footer(text='Strain info provided (unwillingly) by Leafly.com')
  
  bar = '['
  for x in range(straininfo.percent):
    bar = bar + '█'
  for x in range(20 - straininfo.percent):
    bar = bar + '_'
  bar = bar + ']'

  #newEmbed.add_field(name = 'Variety', value = straininfo.variety + '\nRelaxing ' + bar + ' Energizing', inline = True)
  #newEmbed.add_field(name = 'Cannabinoids', value = 'THC: ' + straininfo.thc + '\nCBD: ' + straininfo.cbd, inline = True)
  #newEmbed.add_field(name = 'Terpenes', value = straininfo.terps, inline = True)

  #newEmbed.add_field(name = 'Flavors', value = straininfo.flavors, inline = True)
  #newEmbed.add_field(name = 'Effects', value = straininfo.effects, inline = True)
  #newEmbed.add_field(name = 'Negatives', value = straininfo.neg, inline = True)
  #newEmbed.add_field(name = 'Uses', value = straininfo.uses, inline = True)

  await channel.send(embed=newEmbed)
  return



client = WikiBluff()

token = os.environ.get("TOKEN")
client.run(token)

