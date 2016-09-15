import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
import re
from datetime import date
expire = re.compile(r'\(scad\.\s+(?P<dd>\d{1,2})\s+(?P<mm>\w+)\s+(?P<yyyy>\d{4})\)')


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

class OutItem:
    def __init__(self,rubrica=None,emettitore=None,dt=None,data=None,url=None, header=None):
        self.rubrica = rubrica
        self.emettitore = emettitore
        self.dt = dt
        self.data = data
        self.url = url
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

outitems = []

for item in v.findAll('span'):
    i = res_map.get(item['class'][0])
    # cls = i()
    if i:
        obj = i()
        dt = None
        # print(item.string)
        if isinstance(obj, Rubrica):
            rubrica = obj
            rubrica.name = item.string
            emettitore = None
        elif isinstance(obj, Emettitore):
            emettitore = obj
            emettitore.name = item.string
        elif isinstance(obj, Item):
            if not rubrica:
                print('WARNING! rubrica unknown')
            if not emettitore:
                print('WARNING! emettitore unknown')
            # print(item['class'])
            # data = item.findChildren()
            # data = []
            # print(item.find("a"))
            data = item.findChildren()
            for d in data:
                if d.span and d.span['class'][0] == 'data':
                    data_content = d.span.string
                    # print(data_content)
                    if data_content:
                        data_string = data_content.replace('\n','').replace('\t','')
                        print('>>datastr  ', data_string)
                        # print('data ==> ',data_content.replace('\n','').replace('\t',''))
                    else:
                        # print('#'*5)
                        # print(d.span.contents)
                        data_string = d.span.contents[0].replace('\n','').replace('\t','')
                        for chunk in d.span.contents:
                            # print(type(chunk))
                            # print('!!!!! ',d.span.contents[0])
                            if isinstance(chunk, Tag) and expire.search(chunk.string):
                                date_search = expire.search(chunk.string)
                                dd = date_search.group('dd')
                                mm = date_search.group('mm')
                                yyyy = date_search.group('yyyy')
                                dt = date(year=int(yyyy),month=int(months_map.get(mm)),day=int(dd))
                                # print('yeaaahh  {}     dd: {}  mm:{}   yyyy: {}'.format(chunk.string, dd, months_map.get(mm), yyyy))
                        # print('#'*5)
                else:
                    if d.span and d.name == "a":
                        # print('>>> ',d.contents)
                        header = d.contents[0].replace('\n','').replace('\t','')
                        # for i,r in enumerate(d.contents):
                        #     print('{}>> {}'.format(i,r))
                        # print('>>> ',d.text)
                # if d.span['class'] == 'data':
            # print('data ==> ',item.find('span',{'class' : 'data'}))
            url = obj.content(item)
            # print('         ',obj.content(item))
            outitem = OutItem(rubrica=rubrica.name,
                              emettitore=emettitore.name,
                              dt=dt,
                              data=data_string,
                              header=header,
                              url=url)
            outitems.append(outitem)
    # print(i['contents'])
    # link = i.find('a')


print('#'*20)
for i in outitems:
    print('rubrica: ',i.rubrica)
    print('emettitore: ',i.emettitore)
    print('type: ',i.data)
    print('dt: ',i.dt)
    print('header: ',i.header)
print('#'*20)
    # print('http://www.gazzettaufficiale.it'+link.get('href'))
    # o = urlparse('http://www.gazzettaufficiale.it'+link.get('href'))
    # print(o)
    # exit()


