import requests
import datetime
import json


def now():
    now = datetime.datetime.now()

    return now


def urlGeneretor(var, date):
    if var == 1:
        # Brasil.io --- Dados Brasil
        url = ('https://brasil.io/api/dataset/covid19/caso/data/?date<{}'
               .format(date))
    elif var == 2:
        # Brasil.io --- Dados Cartórios
        url = ('https://brasil.io/api/dataset/covid19/obito_cartorio/data/?date<{}'
               .format(date))
    elif var == 3:
        # Brasil.api
        pass
    elif var == 4:
        # Brasil.api
        pass
    else:
        # ERROR
        pass

    return url


def getApi(url):
    res = requests.request("GET", url)
    if res.status_code == 200:
        res = json.loads(res.content)
    else:
        return False

    return res
