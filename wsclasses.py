from discord import Embed


class msgclass:

  def __init__(self):
    
    self.message = ''
    self.author = ''
    self.embed = Embed()
    self.results = []
    self.select = []
    self.limit = 0
    self.index = 0


class resultclass:

  def __init__(self):

    self.name = 'Default'
    self.aka = ''
    self.link = ''
    self.breeder = ''
    self.type = ''
    self.growcond = ''
    self.flowertime = ''
    self.female = ''
    self.buy = ''
    self.rating = ''


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


class settingclass:

  def __init__(self):
    
    self.whitelist = []
