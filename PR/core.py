
import asyncio
import requests

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
    print(response1.text)
    print(response2.text)

loop = asyncio.get_event_loop()
loop.run_until_complete(getData())

