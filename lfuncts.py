import discord
from discord_slash.utils.manage_components import *
from wsclasses import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup as bs

feelingslist = ['Aroused', 'Creative', 'Energetic', 'Euphoric', 'Focused', 'Giggly', 'Happy', 'Hungry', 'Relaxed', 'Sleepy', 'Talkative', 'Tingly', 'Uplifted']
neglist = ['Anxious', 'Dizzy', 'Dry eyes', 'Dry mouth', 'Headache', 'Paranoid']
helplist = ['ADD/ADHD', 'Alzheimer\'s', 'Anorexia', 'Anxiety', 'Arthritis', 'Asthma', 'Bipolar disorder', 'Cachexia', 'Cancer', 'Cramps', 'Crohn\'s disease', 'Depression', 'Epilepsy', 'Eye pressure', 'Fatigue', 'Fibromyalgia', 'Gastrointestinal disorder', 'Glaucoma', 'Headaches', 'HIV/AIDS', 'Hypertension', 'Inflammation', 'Insomnia', 'Lack of appetite', 'Migraines', 'Multiple sclerosis', 'Muscle spasms', 'Muscular dystrophy', 'Nausea', 'Pain', 'Parkinson\'s', 'Phantom limb pain', 'PMS', 'PTSD', 'Seizures', 'Spasticity', 'Spinal cord injury', 'Stress', 'Tinnitus', 'Tourette\'s syndrome']


async def leaflyinfo(query):  # Gets search results and returns message embed
  link = Request("https://www.leafly.com/search?q=" + quote_plus(query) + "&searchCategory=strain", headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.64'})
  print(quote_plus(query))
  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  
  bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  
  if bssearch.head.title.get_text() == '500: Internal Server Error':
    return None

  results = bssearch.find_all(class_='relative flex flex-col justify-between bg-white h-full elevation-low rounded')
  # Grabs each 'box''s div element
  print(results)
  for result in results:
    
    
    if query.lower() == result.find(itemprop='name').get_text().lower():
      return 'https://www.leafly.com' + result.a['href']
      # If the strain name matches the query exactly (except case)
    elif query.lower() in result.find(class_='text-xs truncate text-grey').get_text().lower():
      return 'https://www.leafly.com' + result.a['href']
      # If the query is in the alternate names for a strain
    elif query.lower() in result.find(itemprop='name').get_text().lower():
      return 'https://www.leafly.com' + result.a['href']
      # If the query is part of a strain name
  return 'https://www.leafly.com' + results[0].a['href']
  # If the above three fail, just return the first result

  

async def leaflyresultmessage(ctx, link):

  url = link
  link = Request(url=link, headers={'Accept': 'text/html','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.50'})
  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser') # Converts to BeautifulSoup object

  name = bssearch.find('h1', itemprop='name').get_text()
  aka = bssearch.find('h2', itemprop='name')
  
  try:
    aka = aka.get_text().replace('aka','').strip()
    desc = '*(aka:* ***' + aka + '*** *)*\n\n' + '__**Description:**__\n\n' + bssearch.find('div', itemprop='description').get_text()
  except AttributeError:
    desc = '__**Description:**__\n' + bssearch.find('div', itemprop='description').get_text()
  weedpic = bssearch.find('div', class_='jsx-1012626707 h-full w-full').img['srcset'].split('?', 1)[0]


  newEmbed = discord.Embed(title=name, url=url)
  newEmbed.description = desc[:2048]
  # newEmbed.add_field(name='Description:', value=desc)
  newEmbed.set_thumbnail(url=weedpic)
  newEmbed.set_footer(text='(Strain information courtesy Leafly.com)')

  if not bssearch.find(class_='text-xs font-bold py-sm'):
    indicapercent = int(bssearch.find(class_='bg-default rounded-full')['style'].split('width:')[1].split('.')[0])
 
    # bar = '`'
    # for x in range(int(indicapercent * 38 / 100)):
    #   bar = bar + '█'
    # for x in range(int((100 - indicapercent) * 38 / 100)):
    #   bar = bar + '∙'
    # bar = bar + '`'
    # newEmbed.add_field(name='Indica <━━━━━━━━━━━━━━━> Sativa', value=bar, inline=False)
    newEmbed.add_field(name='__Type__', value=str(indicapercent)+'% Indica')

    cannabinoids = bssearch.find_all(class_='jsx-1012626707 text-xs rounded flex items-center mr-xl')
    if len(cannabinoids) >= 1:
      newEmbed.add_field(name='__'+cannabinoids[0].get_text().split()[0]+'__', value=cannabinoids[0].get_text().split()[1])
    if len(cannabinoids) >= 2:
      newEmbed.add_field(name='__'+cannabinoids[1].get_text().split()[0]+'__', value=cannabinoids[1].get_text().split()[1])
    if len(cannabinoids) >= 3:
      newEmbed.add_field(name='__'+cannabinoids[2].get_text().split()[0]+'__', value=cannabinoids[2].get_text().split()[1])
    if len(cannabinoids) >= 4:
      newEmbed.add_field(name='__'+cannabinoids[3].get_text().split()[0]+'__', value=cannabinoids[3].get_text().split()[1])


    domterp = bssearch.find(class_='jsx-221743974 text-sm font-bold') 
    domterptype = bssearch.find(class_='jsx-221743974 text-sm font-bold text-grey')
    terps = bssearch.find_all(class_='jsx-221743974 flex items-center')
    try:
      terpenes = '**' + domterp.get_text() + ' ' + domterptype.get_text() + '**'
      for terp in terps:
        terpenes = terpenes + '\n' + terp.get_text().replace('(', ' (')
    except AttributeError:
      pass
    if domterp != None:
      newEmbed.add_field(name='__Terpenes__', value=terpenes)


    flavs = bssearch.find_all(class_='jsx-1497574014 font-bold font-headers text-sm')
    flavors = ''
    if flavs != None:
      for flav in flavs:
        flavors = flavors + flav.get_text() + '\n'
    else:
      flavs = '(Unknown)'
    newEmbed.add_field(name='__Flavors__', value=flavors)

    effecttitles = bssearch.find(class_='jsx-3739643243 strain-effects-new').find(class_='react-tabs__tab-list')
    if effecttitles != None:
      effecttitles = effecttitles.find_all(class_='react-tabs__tab')
      effects = bssearch.find(class_='jsx-3739643243 react-tabs__tab-panel-container mt-md react-tabs-padding').find_all(class_='react-tabs__tab-panel')
      for effect in effects:
        thiseffect = effect.find_all(class_='jsx-2869020097 font-bold font-headers text-sm')
        effectnames = ''
        for e in thiseffect:
          effectnames+= e.get_text() + '\n'
        newEmbed.add_field(name='__'+effecttitles[effects.index(effect)].get_text()+'__', value=effectnames)
    # feelraw = None
    # negraw = None
    # useraw = None
    # if bssearch.find(id='react-tabs-149265') != None:
    #   feelraw = bssearch.find(id='react-tabs-149265').find_all(class_='jsx-2869020097 font-bold font-headers text-sm')
    # if bssearch.find(id='react-tabs-149267') != None:
    #   negraw = bssearch.find(id='react-tabs-149267').find_all(class_='jsx-2869020097 font-bold font-headers text-sm')
    # if bssearch.find(id='react-tabs-149269') != None:
    #   useraw = bssearch.find(id='react-tabs-149269').find_all(class_='jsx-2869020097 font-bold font-headers text-sm')
    # feelings = ''
    # negs = ''
    # uses = ''
    # if feelraw != None:
    #   for feeling in feelraw:
    #     feelings = feelings + feeling.get_text() + '\n'
    # else:
    #   feelings = '(Unknown)'
    # if negraw != None:
    #   for neg in negraw:
    #     negs = negs + neg.get_text() + '\n'
    # else:
    #   negs = '(Unknown)'
    # if useraw != None:
    #   for use in useraw:
    #     uses = uses + use.get_text() + '\n'
    # else:
    #   uses = '(Unknown)'

    # newEmbed.add_field(name='__Feelings__', value=feelings)
    # newEmbed.add_field(name='__Helps with__', value=uses)
    # newEmbed.add_field(name='__Negatives__', value=negs)
    
    # genetics = bssearch.find_all(class_='jsx-1789851897 flex flex-col md:flex-row pt-xl')
    # parents = ''
    # for gen in genetics:
    #   parents = parents + gen.div.div.get_text() + '\n'
    # newEmbed.add_field(name='__Parents__', value=parents)

  return newEmbed


