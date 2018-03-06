
import asyncio
import requests
import csv
import pandas as pd

headers = {'Accept': 'text/csv',
           'X-API-Key': '55193451-1409-4729-9cd4-7c65d63b8e76'}

category = 'https://evil-legacy-service.herokuapp.com/api/v101/categories/'

order = 'https://evil-legacy-service.herokuapp.com/api/v101/orders/'

data = {'start': '2018-01-01', 'end': '2018-03-03'}


async def getData():
    def categ():
        return requests.get('https://evil-legacy-service.herokuapp.com/api/v101/categories/', headers=headers)
    def ord():
        return requests.get(order,headers=headers, params=data)
    loop = asyncio.get_event_loop()
    future1 = loop.run_in_executor(None, categ)
    future2 = loop.run_in_executor(None, ord)
    response1 = await future1
    response2 = await future2
    return response1, response2

async def AggregateData():
    

loop = asyncio.get_event_loop()
res1, res2 = loop.run_until_complete(getData())

decoded = res1.content.decode('utf-8')
decoded2 = res2.content.decode('utf-8')

cr = csv.reader(decoded.splitlines(), delimiter = ',')
cr2 = csv.reader(decoded2.splitlines(), delimiter = ',')

first = ['id','total','category_id','created']
second = ['id','name','category_id']

List1 = list(cr)
List2 = list(cr2)

List2.remove(first)
List1.remove(second)

CategDict = {}

for element in List1:
    CategDict[List1[0][0]] = List1[0][1]

print(CategDict)


Orders = pd.DataFrame(List2, columns = ['id','total','id_cat','created'])

Categs = pd.DataFrame(List1, columns = ['id_cat','name','cat_id'])


Categs['id_cat']=Categs['id_cat'].astype(int)
Orders['id_cat']=Orders['id_cat'].astype(int)

merged = Categs.merge(Orders)

merged = pd.to_numeric(merged.total).groupby([merged.id_cat,merged.name,merged.cat_id]).sum()
merged = merged.to_frame()


print(merged)

PresentCategories = []

for tup in merged.itertuples():
    PresentCategories.append(tup[0][0])

for tup in merged.itertuples():
    if (tup[0][2] != '') and tup[0][2] in PresentCategories:
        merged.at[int(tup[0][2]),'total'] =+ float(tup[1])

# for tup in merged.itertuples():
#     if tup[0][2] != '':
#         merged.at[int(tup[0][2]),'cat_id'] = CategDict.get(str(tup[0][2]))


print(merged)

