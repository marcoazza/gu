import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
import re

expire = re.compile(r'\(scad\.\s+(?P<dd>\d{1,2})\s+(\w+)\s+(?P<yyyy>\d{4})\)')


def get_content(item):
    return item.string

def get_em(item):
    return item.string

def get_res(item):
    return item.a['href']



# url = 'http://www.gazzettaufficiale.it/gazzetta/concorsi/caricaDettaglio/home?dataPubblicazioneGazzetta=2016-08-09&numeroGazzetta=63'
url = 'http://www.gazzettaufficiale.it/gazzetta/concorsi/caricaDettaglio/home?dataPubblicazioneGazzetta=2016-09-06&numeroGazzetta=71'
headers = {
    'User-Agent': 'Chrome'
}


class Rubrica:
    def __init__(self):
        pass

class Item:
    def __init__(self):
        pass

    def content(self, item):
        return item.a['href']

class Emettitore:
    def __init__(self):
        pass

    def content(self, item):
        return item

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



resp = requests.get(url,headers=headers)
htmlparsed = BeautifulSoup(resp.text,"html.parser")

v = htmlparsed.find("div", {"id": "elenco_hp"})
# print(v)
# r = v.findAll('span', {"class": 'risultato'})
# r = v.findAll('span')
rubrica = None
emettitore = None
for item in v.findAll('span'):
    i = res_map.get(item['class'][0])
    # cls = i()
    if i:
        obj = i()
        print(obj)
        if isinstance(obj, Rubrica):
            rubrica = obj
            emettitore = None
        elif isinstance(obj, Emettitore):
            emettitore = obj
        elif isinstance(obj, Item):
            if not rubrica:
                print('WARNING! rubrica unknown')
            if not emettitore:
                print('WARNING! emettitore unknown')
            print(item['class'])
            data = item.findChildren()
            for d in data:
                if d.span and d.span['class'][0] == 'data':
                    data_content = d.span.string
                    if data_content:
                        print('data ==> ',data_content.replace('\n',''))
                    else:
                        print('#'*5)
                        print(d.span.contents)
                        for chunk in d.span.contents:
                            print(type(chunk))
                            if isinstance(chunk, Tag) and expire.search(chunk.string):
                                date_search = expire.search(chunk.string)
                                dd = date_search.group('dd')
                                yyyy = date_search.group('yyyy')
                                print('yeaaahh  {}     dd: {}     yyyy: {}'.format(chunk.string, dd, yyyy))
                        print('#'*5)
                # if d.span['class'] == 'data':
            # print('data ==> ',item.find('span',{'class' : 'data'}))
            print('         ',obj.content(item))
    # print(i['contents'])
    # link = i.find('a')

    # print('http://www.gazzettaufficiale.it'+link.get('href'))
    # o = urlparse('http://www.gazzettaufficiale.it'+link.get('href'))
    # print(o)
    # exit()


