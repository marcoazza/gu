import requests
from bs4 import BeautifulSoup, Tag
# from urllib.parse import urlparse
import re
from datetime import date, datetime
expire = re.compile(r'\(scad\.\s+(?P<dd>\d{1,2})\s+(?P<mm>\w+)\s+(?P<yyyy>\d{4})\)')
codeid_re = re.compile(r'codiceRedazionale=(?P<code>\w+)')
pubdate_re = re.compile(r'dataPubblicazioneGazzetta=(?P<pubdate>\d{4}-\d{2}-\d{2})')


class OutItem:
    def __init__(self, category=None, publisher=None,expiry_date=None,comp_type=None,url=None, header=None):
        self.category = category
        self.publisher = publisher
        self.expiry_date = expiry_date
        self.comp_type = comp_type
        self.url = url
        pubdate = pubdate_re.search(self.url)
        if pubdate:
            self.pub_date = datetime.strptime(pubdate.group('pubdate'), "%Y-%m-%d").date().isoformat()
        codeid = codeid_re.search(self.url)
        if codeid:
            self.code = codeid.group('code')
        self.header = header


class Rubrica:
    def __init__(self):
        self.name = None

    def content(self):
        return self.string


class Item:
    def __init__(self):
        pass

    def content(self, item):
        return item.a['href']



class Emettitore:
    def __init__(self):
        self.name = None

    def content(self, item):
        return item


class ScrapingError(Exception):
  pass

res_map = {'rubrica' : Rubrica,
           'emettitore': Emettitore,
           'risultato': Item,}

months_map = {'gennaio': 1,
              'febbraio': 2,
              'marzo': 3,
              'aprile': 4,
              'maggio': 5,
              'giugno': 6,
              'luglio': 7,
              'agosto': 8,
              'settembre': 9,
              'ottobre': 10,
              'novembre': 11,
              'dicembre': 12,
              }




def parse(url,headers=None):
    resp = requests.get(url,headers=headers)
    htmlparsed = BeautifulSoup(resp.text,"html.parser")
    v = htmlparsed.find("div", {"id": "elenco_hp"})
    category = None
    publisher = None
    outitems = []

    try:
      for item in v.findAll('span'):
        i = res_map.get(item['class'][0])
        if i:
            obj = i()
            dt = None
            if isinstance(obj, Rubrica):
                category = obj
                category.name = item.string.replace('\n','').replace('\t','').rstrip(' ')
                publisher = None
            elif isinstance(obj, Emettitore):
                publisher = obj
                publisher.name = item.string
            elif isinstance(obj, Item):
                if not category:
                    print('WARNING! rubrica unknown')
                if not publisher:
                    print('WARNING! emettitore unknown')
                data = item.findChildren()
                for d in data:
                    if d.span and d.span['class'][0] == 'data':
                        data_content = d.span.string
                        if data_content:
                            comp_type = data_content.replace('\n','').replace('\t','')
                        else:
                            comp_type = d.span.contents[0].replace('\n','').replace('\t','')
                            for chunk in d.span.contents:
                                if isinstance(chunk, Tag) and expire.search(chunk.string):
                                    date_search = expire.search(chunk.string)
                                    dd = date_search.group('dd')
                                    mm = date_search.group('mm')
                                    yyyy = date_search.group('yyyy')
                                    dt = date(year=int(yyyy),month=int(months_map.get(mm)),day=int(dd)).isoformat()
                    else:
                        if d.span and d.name == "a":
                            header = d.contents[0].replace('\n','').replace('\t','')

                url = obj.content(item)
                outitem = OutItem(category=category.name,
                                  publisher=publisher.name,
                                  expiry_date=dt,
                                  comp_type=comp_type,
                                  header=header,
                                  url=url)
                outitems.append(outitem)
    except AttributeError:
      # print('ERROR parsing URL')
      raise ScrapingError()
    return outitems

def print_out(items):
  for i in items:
    print('i.category   ' ,i.category.rstrip(' '))
    print('i.publisher   ' ,i.publisher)
    print('i.dt   ' ,i.expiry_date)
    print('i.data   ' ,i.comp_type)
    print('i.url   ' ,i.url)
    print('i.pubdate   ' ,i.pubdate)
    print('i.codeid   ' ,i.codeid)
    print('i.header   ' ,i.header)

if __name__ == '__main__':
  testurl = 'http://www.gazzettaufficiale.it/gazzetta/concorsi/caricaDettaglio/home?dataPubblicazioneGazzetta=2016-09-06&numeroGazzetta=71'
  print('Parsing: ',testurl)
  out = parse(testurl)
  print_out(out)
