from Scripts.functions import now, urlGenerator, getApi, getNextDate, formatDate
from DataBase import sqlCreator
from sqlalchemy.types import String, Date, Integer, Float
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import tabula

list_sheets = [
    'ocupacaoLeitos', #PG 5
    'leitosMacrorregiao', #PG 5
]

data_types = {
    'ocupacaoLeitos':{
        'tipo_de_leito': String(),
        'sus_suspeitos': Integer(),
        'sus_confirmados': Integer(),
        'particular_suspeitos': Integer(),
        'particular_confirmados': Integer()
    },
    'leitosMacrorregiao':{
        'leitos': String(),
        'uti adulto exist': Integer(),
        'uti adulto ocup': Integer(),
        'uti adulto tx ocup': Float(),
        'enf adulto exist': Integer(),
        'enf adulto ocup': Integer(),
        'enf adulto tx ocup': Float(),
        'uti infantil exist': Integer(),
        'uti infantil ocup': Integer(),
        'uti infantil tx ocup': Float(),
        'enf infantil exist': Float(),
        'enf infantil ocup': Integer(),
        'enf infantil tx ocup': Float()
    }
}

ocupacao_columns = [
    'tipo de leito',
    'sus susp',
    'sus conf',
    'sus total',
    'priv susp',
    'priv conf',
    'priv total',
    'total susp',
    'total conf',
    'total total'
]

leitos_columns = [
    'leitos',
    'uti adulto exist',
    'uti adulto ocup',
    'uti adulto tx ocup',
    'enf adulto exist',
    'enf adulto ocup',
    'enf adulto tx ocup',
    'uti infantil exist',
    'uti infantil ocup',
    'uti infantil tx ocup',
    'enf infantil exist',
    'enf infantil ocup',
    'enf infantil tx ocup'
]

# complements = ['atualizado', 
#     '_1', 
#     '_0', 
#     '']


def transform(dfs):


    for df in dfs:
        for d in df:
            try:              
                df[d] = df[d].str.replace(".", "").str.replace("%", "").astype(int)
            except:
                pass
        
    return dfs
        
def cleanner(dfs):

    if len(dfs) == 2:
        ocupacao = dfs[0]

        if len(ocupacao.dropna()) == 3:
            ocupacao.dropna(inplace=True)
            ocupacao[0] = ''
            ocupacao = ocupacao.astype(str).values.tolist()

            new_ocupacao = [] # stack de new lines
            for ocup in ocupacao:
                new_line = [] # stack line
                for oo in ocup:
                    if len(oo) > 5:
                        oo = oo.split(' ')
                        for o in oo:
                            new_line.append(o)
                    else:
                        new_line.append(oo)
                new_ocupacao.append(new_line)

            ocupacao = pd.DataFrame(new_ocupacao)
            ocupacao.iloc[0][0] = "UTI"
            ocupacao.iloc[1][0] = "CLINICO"
            ocupacao.iloc[-1][0] = "UTI E CLINICO"
            
            # ocupacao.columns = ocupacao_columns
            # ocupacao.drop(columns=['sus total', 'priv total', 'total susp', 'total conf', 'total total'], inplace=True)
        else:
            ocupacao = pd.concat([ocupacao[4:6], ocupacao[7:8]]).astype(str).values.tolist()
            new_ocupacao = [] # stack de new lines

            for ocup in ocupacao:
                new_line = [] # stack line
                for oo in ocup:
                    if len(oo) > 5:
                        oo = oo.split(' ')
                        for o in oo:
                            new_line.append(o)
                    else:
                        new_line.append(oo)
                new_ocupacao.append(new_line)

            ocupacao = pd.DataFrame(new_ocupacao)
            ocupacao.iloc[-1][0] = "UTI E CLINICO"

        ocupacao.columns = ocupacao_columns
        ocupacao.drop(columns=['sus total', 'priv total', 'total susp', 'total conf', 'total total'], inplace=True)
        #TRATANDO DF LEITOS
        leitos = dfs[1].dropna().astype(str).values.tolist()
        new_leitos = []
        # print(type(leitos))
        for lei in leitos:
            new_line = [] 
            for ll in lei:
                #QUEBRA
                if len(ll.split(' ')) > 1: # MINIMO PARA QUEBRA len(0% 0 0 0%) = 9 ou > que (len("NOROESTE"))
                    ll = ll.split(' ')
                    for l in ll:
                        new_line.append(l) 
                else: 
                    new_line.append(ll) 
            new_leitos.append(new_line) 

        leitos = pd.DataFrame(new_leitos)

        if len(leitos.columns) > 13:
            leitos.drop(columns=[4, 8, 12, 16], inplace=True)

        leitos.columns = leitos_columns 
        # print(leitos)

        porcentagem = lambda x,y: ((x/y)*100)
        leitos['uti adulto tx ocup'] = porcentagem(leitos['uti adulto ocup'].str.replace(".", "").astype(int), leitos['uti adulto exist'].str.replace(".", "").astype(int))
        leitos['enf adulto tx ocup'] = porcentagem(leitos['enf adulto ocup'].str.replace(".", "").astype(int), leitos['enf adulto exist'].str.replace(".", "").astype(int))
        leitos['uti infantil tx ocup'] = porcentagem(leitos['uti infantil ocup'].str.replace(".", "").astype(int), leitos['uti infantil exist'].str.replace(".", "").astype(int))
        leitos['enf infantil tx ocup'] = porcentagem(leitos['enf infantil ocup'].str.replace(".", "").astype(int), leitos['enf infantil exist'].str.replace(".", "").astype(int))

        # reset dfs
        dfs[0] = ocupacao
        dfs[1] = leitos

    else:
        leitos = dfs[0].dropna().astype(str).values.tolist()
        new_leitos = []

        # print(type(leitos))
        for lei in leitos:
            new_line = [] 
            for ll in lei:
    
                #QUEBRA
                if len(ll.split(' ')) > 1: # MINIMO PARA QUEBRA len(0% 0 0 0%) = 9 ou > que (len("NOROESTE"))
                    ll = ll.split(' ')
                    for l in ll:
                        new_line.append(l) 
                else: 
                    new_line.append(ll) 
            new_leitos.append(new_line) 

        leitos = pd.DataFrame(new_leitos) 
        leitos.columns = leitos_columns 
        porcentagem = lambda x,y: ((x/y)*100)
        leitos['uti adulto tx ocup'] = porcentagem(leitos['uti adulto ocup'].str.replace(".", "").str.replace("%", "").astype(int), leitos['uti adulto exist'].str.replace(".", "").str.replace("%", "").astype(int))
        leitos['enf adulto tx ocup'] = porcentagem(leitos['enf adulto ocup'].str.replace(".", "").str.replace("%", "").astype(int), leitos['enf adulto exist'].str.replace(".", "").str.replace("%", "").astype(int))
        leitos['uti infantil tx ocup'] = porcentagem(leitos['uti infantil ocup'].str.replace(".", "").str.replace("%", "").astype(int), leitos['uti infantil exist'].str.replace(".", "").str.replace("%", "").astype(int))
        leitos['enf infantil tx ocup'] = porcentagem(leitos['enf infantil ocup'].str.replace(".", "").str.replace("%", "").astype(int), leitos['enf infantil exist'].str.replace(".", "").str.replace("%", "").astype(int))
    
        dfs[0] = leitos
        
    dfs = transform(dfs)

    return dfs

complements = ['_atualizado', '_1', '_0', '']


texto = 'informe_epidemiologico'
base_url = 'http://www.saude.pr.gov.br/sites/default/arquivos_restritos/files/documento/{}/{}_{}{}.pdf'

start_date = datetime(2020, 5, 6, 14, 0, 0)
# start_date = datetime(2020, 6, 17, 14, 0, 0)

hoje = datetime(2020, 6, 24, 19, 0, 0)

links = []
while start_date <= hoje:
    
    for com in complements:
        url = base_url.format(start_date.strftime('%Y-%m'), texto, start_date.strftime('%d_%m_%Y'), com)
        response = requests.get(url)        
        if response.ok:
            print("COMPLEMENTO = ", com)
            print("link do dia ", start_date.strftime("%d-%m"))
            links.append(url)
            print(url)
            break
        else:
            url =  url = base_url.format(start_date.strftime('%Y-%m'), texto.upper(), start_date.strftime('%d_%m_%Y'), com)
            response = requests.get(url)
            if response.ok:
                print("link do dia ", start_date.strftime("%d-%m"))
                print(url)
                links.append(url)
                break

    page = 5 if start_date > datetime(2020, 5, 18, 14, 0, 0) else 4 # set page
    
    df = tabula.read_pdf(url, pages=[page], pandas_options={'header': None, 'dtype': str})
    
    # with pd.ExcelWriter('../../SESA_MESS_{}.xlsx'.format(start_date.strftime('%d-%m'))) as writer:
    #     for i in range(len(df)):
    #         df[i].to_excel(writer, index=False, engine='xlsxwriter', encoding=' UTF-8', sheet_name='SESA_{}'.format(i))


    df = cleanner(df)

    #PRINT CLEAN
    for i in range(len(df)):
        # print("O CARALHOOO")
        print(df[i])

    # with pd.ExcelWriter('SESA_{}.xlsx'.format(start_date.strftime('%d-%m'))) as writer:
    #     for i in range(len(df)):
    #         df[i].to_excel(writer, index=False, engine='xlsxwriter', encoding=' UTF-8', sheet_name='SESA_{}'.format(i))

    start_date += timedelta(days=1)

# printei tudo, falta só arrumar maiúsculo e mineirar


# print(links)

# /2020-05/informe_epidemiologico_06_05_2020_0.pdf start pg 4 - 1Table
# /2020-05/informe_epidemiologico_19_05_2020_0.pdf start pg 5 - 1Table
# /2020-06/informe_epidemiologico_10_06_2020_1.pdf start pg 5 - 2 Table
# /2020-06/INFORME_EPIDEMIOLOGICO_23_06_2020.pdf start pg 5 - 2Table