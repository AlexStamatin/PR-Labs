
import asyncio
import requests
import csv
import pandas as pd
import sys

headers = {'Accept': 'text/csv',
           'X-API-Key': '55193451-1409-4729-9cd4-7c65d63b8e76'}

category = 'https://evil-legacy-service.herokuapp.com/api/v101/categories/'

order = 'https://evil-legacy-service.herokuapp.com/api/v101/orders/'




data = {'start': '2018-01-01', 'end': '2018-03-03'}


async def getData(loop):
    def categ():
        try:
            return requests.get('https://evil-legacy-service.herokuapp.com/api/v101/categories/', headers=headers)
        except:
            print("Cannot connect to server.Showing cached data")
            print(pd.read_pickle('localcache'))
            sys.exit(1)
    def ord():
        try:
            return requests.get(order,headers=headers, params=data)
        except:
            pass
    future1 = loop.run_in_executor(None, categ)
    future2 = loop.run_in_executor(None, ord)
    response1 = await future1
    response2 = await future2
    return response1, response2


async def AggregateData(loop):
    def Agreg():

        DecoCateg = ReceiveCateg.content.decode('utf-8')
        DecoOrd = ReceiveOrd.content.decode('utf-8')
        Categs = csv.reader(DecoCateg.splitlines(), delimiter=',')
        Ords = csv.reader(DecoOrd.splitlines(), delimiter=',')
        first = ['id', 'total', 'category_id', 'created']
        second = ['id', 'name', 'category_id']

        ListCateg = list(Categs)
        ListOrd = list(Ords)

        ListOrd.remove(first)
        ListCateg.remove(second)

        CategDict = {}  # string -> string dictionary ; category_id -> category_name
        cats = {}  # string -> string dictionary; category_id -> parent_category_id

#       Build category -> parent_category dictionary

        for cat in ListCateg:
            catid = cat[0]
            cats[catid] = cat[2:][0]

#       Build category_id -> category_name dictionary

        for element in ListCateg:
            elementid = element[0]
            CategDict[elementid] = element[1:2][0]

#       Create Orders and Categories DataFrames

        Orders = pd.DataFrame(ListOrd, columns=['id', 'total', 'id_cat', 'created'])
        Categs = pd.DataFrame(ListCateg, columns=['id_cat', 'Category', 'Parent_Category'])

#       Set type of id_cat column to integer

        Categs['id_cat'] = Categs['id_cat'].astype(int)
        Orders['id_cat'] = Orders['id_cat'].astype(int)

#       Merge Orders and Categs tables. Orders grouped by Category

        merged = Categs.merge(Orders,how='left')
        merged = pd.to_numeric(merged.total).groupby([merged.id_cat, merged.Category, merged.Parent_Category]).sum()
        merged = merged.to_frame()
        merged['total'] = merged['total'].astype(float)
        toadd = {} # integer -> integer dictionary ; categ_id -> number of orders from child categories
        parent = {} # integer -> integer dictionary ; categ_id -> number of parent categories

#       Create list of Categories ID's present

        PresentCategories = []
        for tup in Categs.itertuples():
            PresentCategories.append(tup[1])

#       Initialize toadd and parent dictionaries with Categories and 0 value for each one

        toadd = toadd.fromkeys(PresentCategories,0)
        parent = parent.fromkeys(PresentCategories,0)

#       Calculate the number of parents for each Category

        for cat in cats:
            val = cats[cat]
            while val != '':
                parent[int(cat)] += 1
                val = cats[val]

#       Determine maximum number of parents

        maxparent = max(parent,key=parent.get)
        maxparents = parent[maxparent]


#       Aggregate data. Orders from child categories are added to parent categories

        for i in range(maxparents,0,-1):
            for tup in merged.itertuples():
                toadd[int(tup[0][0])] += float(tup[1])
                if (tup[0][2] != '') and (parent[tup[0][0]] == i):
                    toadd[int(tup[0][2])] += float(tup[1])

            for tup in merged.itertuples():
                merged.loc[int(tup[0][0]), 'total'] = toadd[int(tup[0][0])]
            toadd.update((k, 0) for k in toadd)

        return merged

    future = loop.run_in_executor(None, Agreg)
    merge = await future
    return merge

async def CacheDisplay(loop):
    def Savefile():
        merged.to_pickle('localcache')
    def File():
        print(merged)
    future = loop.run_in_executor(None, File)
    future1 = loop.run_in_executor(None, Savefile)
    response1 = await future1
    response = await future
    return response, response1





loop = asyncio.get_event_loop()
ReceiveCateg, ReceiveOrd = loop.run_until_complete(getData(loop))
merged = loop.run_until_complete(AggregateData(loop))
loop.run_until_complete(CacheDisplay(loop))
loop.close()







