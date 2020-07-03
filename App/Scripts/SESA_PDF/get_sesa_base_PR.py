from Scripts.functions import now, urlGenerator, getApi, getNextDate, formatDate
from DataBase import sqlCreator
from sqlalchemy.types import String, Date, Integer, Float
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import tabula

mcroaa_columns = [
    'REGIONAL',
    'MUNICIPIO',
    'POPULACAO',
    'CONFIRMADOS',
    'RECUPERADOS',
    'OBITOS',
    'INVESTIGACAO'
]

def transform(dfs):

    dfs.dropna(inplace=True)
    dfs.loc['Total' ] = '0'
    for col in mcroaa_columns:
        print(dfs[col])
        try:
            dfs[col] = dfs[col].str.replace(".", "").astype(int)
            dfs.loc['Total', col] = dfs[col].sum()
        except:
            pass 
        
    
    dfs.loc['Total', 'REGIONAL'] = ''
    dfs.loc['Total', 'MUNICIPIO'] = ''

    return dfs

def cleanner(df):
        

    return df

def get_data(session, page_list):
    

    complements = ['_atualizado', '_1', '_0', '']
    texto = 'informe_epidemiologico'
    base_url = 'http://www.saude.pr.gov.br/sites/default/arquivos_restritos/files/documento/{}/{}_{}{}.pdf'

    hoje = datetime(2020, 7, 2, 14, 0, 0).date()

    # hoje = now().date() # HOJE

    for com in complements:
        url = base_url.format(hoje.strftime('%Y-%m'), texto, hoje.strftime('%d_%m_%Y'), com)
        response = requests.get(url)
        if response.ok:
            print("COMPLEMENTO = ", com)
            print("link do dia ", hoje.strftime("%d-%m"))
            print(url)
            data_check = True
            break
        else:
            url =  url = base_url.format(hoje.strftime('%Y-%m'), texto.upper(), hoje.strftime('%d_%m_%Y'), com)
            response = requests.get(url)
            if response.ok:
                print("COMPLEMENTO = ", com)
                print("link do dia ", hoje.strftime("%d-%m"))
                print(url)
                data_check = True
                break
        
    if not response.ok: # end of the days
        if not data_check:
            print("Sem Dados")
    
    print(data_check)

    if data_check:
    
        df = pd.DataFrame()
        df = tabula.read_pdf(url, pages=page_list, pandas_options={'header': None, 'dtype': str})

        dfs = pd.DataFrame()

        for d in range(len(df)):
            if len(df[d].keys()) > 5:
                dfs = pd.concat([dfs, df[d]])
        
        dfs = dfs[1:]
        dfs.drop(columns=[0], inplace=True)
        dfs.columns = mcroaa_columns
        
        dfs = transform(dfs)
        
        print(dfs)
        
        dfs['DATA'] = hoje
        # Full data
        print("CRIANDO Clean DIA = ", hoje.strftime("%d-%m"))
        with pd.ExcelWriter('SESA_FULL-Clean.xlsx') as writer:
            dfs.to_excel(writer, index=False, engine='xlsxwriter', encoding='UTF-8', sheet_name='SESA_FULL')

        dfs.to_sql('SESA_base_PR', con=session.get_bind(), if_exists='replace', method='multi',
        dtype={
            'REGIONAL': String(),
            'MUNICIPIO': String(),
            'POPULACAO': Integer(),
            'CONFIRMADOS': Integer(),
            'RECUPERADOS': Integer(),
            'OBITOS': Integer(),
            'INVESTIGACAO': Integer(),
            'DATA': Date()
        })
    
    return ''