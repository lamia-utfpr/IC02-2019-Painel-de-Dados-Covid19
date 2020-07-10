from scripts.functions import now
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
        try:
            dfs[col] = dfs[col].str.replace(".", "").astype(int)
            dfs.loc['Total', col] = dfs[col].sum()
        except:
            pass 
        
    dfs.loc['Total', 'REGIONAL'] = ''
    dfs.loc['Total', 'MUNICIPIO'] = ''

    return dfs

def cleanner(df):
    
    if len(df.columns) > 8:
        df.drop(columns=[3], inplace=True)
        df.columns = range(df.shape[1])

    return df

def insert(session):
    print("Inserindo get_sesa_pr.")

    page_list = list(range(17, 27))
    data_check = False
    complements = ['_atualizado', '_1', '_0', '']
    texto = 'informe_epidemiologico'
    base_url = 'http://www.saude.pr.gov.br/sites/default/arquivos_restritos/files/documento/{}/{}_{}{}.pdf'

    # hoje = datetime(2020, 7, 7, 14, 0, 0).date()
    
    hoje = now().date()
    
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

    if data_check:
        df = pd.DataFrame()
        df = tabula.read_pdf(url, pages=page_list, pandas_options={'header': None, 'dtype': str})
        dfs = pd.DataFrame()

        for d in range(len(df)):
            if len(df[d].keys()) > 5:
                df[d] = cleanner(df[d])
                # print(df[d])
                dfs = pd.concat([dfs, df[d]], ignore_index=True)
        

        dfs.drop(columns=[0], inplace=True)
        dfs.columns = mcroaa_columns
        dfs = dfs[1:]
        
        # print("Criando SESA Clean = ", hoje.strftime("%d-%m"))
        # with pd.ExcelWriter('SESA_Clean.xlsx') as writer:
        #     dfs.to_excel(writer, index=False, engine='xlsxwriter', encoding='UTF-8', sheet_name='SESA_FULL')

        dfs = transform(dfs)
        dfs.reset_index(drop=True, inplace=True)
        dfs['DATA'] = hoje
        # print(dfs)

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
    return print("sesa_pr inserido com sucesso!")