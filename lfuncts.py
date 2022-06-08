import discord
from discord_slash.utils.manage_components import *
from wsclasses import *
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup as bs
from googlesearch import search

feelingslist = ['Aroused', 'Creative', 'Energetic', 'Euphoric', 'Focused', 'Giggly', 'Happy', 'Hungry', 'Relaxed', 'Sleepy', 'Talkative', 'Tingly', 'Uplifted']
neglist = ['Anxious', 'Dizzy', 'Dry eyes', 'Dry mouth', 'Headache', 'Paranoid']
helplist = ['ADD/ADHD', 'Alzheimer\'s', 'Anorexia', 'Anxiety', 'Arthritis', 'Asthma', 'Bipolar disorder', 'Cachexia', 'Cancer', 'Cramps', 'Crohn\'s disease', 'Depression', 'Epilepsy', 'Eye pressure', 'Fatigue', 'Fibromyalgia', 'Gastrointestinal disorder', 'Glaucoma', 'Headaches', 'HIV/AIDS', 'Hypertension', 'Inflammation', 'Insomnia', 'Lack of appetite', 'Migraines', 'Multiple sclerosis', 'Muscle spasms', 'Muscular dystrophy', 'Nausea', 'Pain', 'Parkinson\'s', 'Phantom limb pain', 'PMS', 'PTSD', 'Seizures', 'Spasticity', 'Spinal cord injury', 'Stress', 'Tinnitus', 'Tourette\'s syndrome']


async def leaflyinfo(query):  # Gets search results and returns message embed
  #link = Request("https://www.leafly.com/search?q=" + quote_plus(query) + "&searchCategory=strain", headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.64'})
  #print(quote_plus(query))
  #try:
  #  info = urlopen(link)  # Grab html
  #except HTTPError as e:
  #  info = e.read()
  
  #bssearch = bs(info, 'html.parser')  # Converts to BeautifulSoup object
  #print(bssearch)
  #if bssearch.head.title.get_text() == '500: Internal Server Error':
  #  return None

  # results = bssearch.find_all(class_='relative flex flex-col justify-between bg-white h-full elevation-low rounded')
  # Grabs each 'box''s div element
  results = search(term=f'{query.lower()} site:leafly.com/strains', num_results=2, advanced=True)
  isset = False
  for result in results:
    print(result.title)
    if not isset:
      isset=True
      rslt = result.url
    if query.lower() in result.title:
      
      return result.url
      # If the strain name matches the query exactly (except case)
  
  return rslt
  # If the above three fail, just return the first result

  

async def leaflyresultmessage(ctx, link):

  url = link
  link = Request(url=link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.50'})
  try:
    info = urlopen(link)  # Grab html
  except HTTPError as e:
    info = e.read()
  bssearch = bs(info, 'html.parser') # Converts to BeautifulSoup object
  print(bssearch)
  name = bssearch.find('h1', attrs={'itemprop':'name'}).get_text()
  aka = bssearch.find('h2', attrs={'itemprop':'name'})
  try:
    aka = aka.get_text().replace('aka','').strip()
    desc = '*(aka:* ***' + aka + '*** *)*\n\n' + '__**Description:**__\n\n' + bssearch.find('div', itemprop='description').get_text()
  except AttributeError:
    desc = '__**Description:**__\n' + bssearch.find('div', itemprop='description').get_text()
  weedpic = bssearch.find('picture', attrs={'data-testid':'image-picture-element'}).img['srcset'].split('?', 1)[0]


  newEmbed = discord.Embed(title=name, url=url)
  newEmbed.description = desc[:2048]
  # newEmbed.add_field(name='Description:', value=desc)
  newEmbed.set_thumbnail(url=weedpic)
  newEmbed.set_footer(text='(Strain information courtesy Leafly.com)')
  
  # if bssearch.find(string='ve smoked, dabbed, or otherwise enjoyed this strain') != None:
  try:
    indicapercent = int(bssearch.find(class_='bg-default rounded-full')['style'].split('width:')[1].split('.')[0])

    # bar = '`'
    # for x in range(int(indicapercent * 38 / 100)):
    #   bar = bar + '█'
    # for x in range(int((100 - indicapercent) * 38 / 100)):
    #   bar = bar + '∙'
    # bar = bar + '`'
    # newEmbed.add_field(name='Indica <━━━━━━━━━━━━━━━> Sativa', value=bar, inline=False)
    newEmbed.add_field(name='__Type__', value=str(indicapercent)+'% Indica')
  except Exception as e:
    print(e)
    pass
  cannabinoids = [] 
  cannabinoids = bssearch.find_all('span', class_='text-xs rounded flex items-center mr-xl')

  if len(cannabinoids) >= 1:
    newEmbed.add_field(name='__'+cannabinoids[0].get_text().split()[0].strip('Loading...')+'__', value=cannabinoids[0].get_text().split()[1])
  if len(cannabinoids) >= 2:
    newEmbed.add_field(name='__'+cannabinoids[1].get_text().split()[0].strip('Loading...')+'__', value=cannabinoids[1].get_text().split()[1])
  if len(cannabinoids) >= 3:
    newEmbed.add_field(name='__'+cannabinoids[2].get_text().split()[0].strip('Loading...')+'__', value=cannabinoids[2].get_text().split()[1])
  if len(cannabinoids) >= 4:
    newEmbed.add_field(name='__'+cannabinoids[3].get_text().split()[0].strip('Loading...')+'__', value=cannabinoids[3].get_text().split()[1])

  try:
    domterp = bssearch.find('a', attrs={'aria-label':'Terpene Information'}).get_text()
    newEmbed.add_field(name='__Dominant Terp__', value=domterp)
  except Exception as e:
    print(e)
    pass
  possibleflavs=['Ammonia', 'Apple', 'Apricot', 'Berry', 'Blueberry', 'Blue Cheese', 'Butter', 'Cheese', 'Chemical', 'Chestnut', 'Citrus', 'Coffee', 'Diesel',
                 'Earthy', 'Flowery', 'Grape', 'Grapefruit', 'Honey', 'Lavender', 'Lemon', 'Lime', 'Mango', 'Menthol', 'Mint', 'Nutty', 'Orange', 'Peach',
                 'Pear', 'Pepper', 'Pine', 'Pineapple', 'Plum', 'Pungent', 'Rose', 'Sage', 'Skunk', 'Spicy/Herbal', 'Strawberry', 'Sweet', 'Tar', 'Tea',
                 'Tobacco', 'Tree fruit', 'Tropical', 'Vanilla', 'Violet', 'Woody']
  flavs = ''
  for res in bssearch.find_all('a', href='/strains/lists/effect/'):
    if res.get_text() in possibleflavs:
      flavs += f'{res.get_text()}\n'

  if flavs != '':
    flavs.strip('\n')
    newEmbed.add_field(name='__Flavors__', value=flavs)


  try:
    feelings = bssearch.find(id='Feelings-tab').find_all(p)
    effects = ''
    for feeling in feelings:
      effects += feeling.get_text() + '\n'
    effects.strip('\n')
    newEmbed.add_field(name='__Feelings__', value=effects)
  except Exception as e:
    print(e)
    pass
  try:
    negatives = bssearch.find(id='Negatives-tab').find_all(p)
    effects = ''
    for neg in negatives:
      effects += neg.get_text() + '\n'
    effects.strip('\n')
    newEmbed.add_field(name='__Negatives__', value=effects)
  except Exception as e:
    print(e)
    pass
  return newEmbed


