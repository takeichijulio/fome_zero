import pandas as pd
import numpy as np
import inflection

def limpar_dataframe(df, *, dropna_mode=None, subset=None, lowercase=False):
    """
    dropna_mode: None | 'any' | 'all'
    subset: lista de colunas para considerar no dropna (opcional)
    lowercase: True para padronizar texto em minúsculas
    """
    # 1) tira espaços de texto
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip()
        if lowercase:
            df[col] = df[col].str.lower()
    # 2) normaliza "nulos de texto"
    df = df.replace(["NaN", "nan", "NULL", ""], np.nan)

    # 3) regra de remoção de nulos
    if dropna_mode in ("any", "all"):
        df = df.dropna(how=dropna_mode, subset=subset).copy()

    # 4) reindexa
    return df.reset_index(drop=True)

def remover_duplicatas(df, *, subset=None, keep='first', report=False):
    """
    Remove duplicatas de forma simples.
    - subset: coluna ou lista de colunas para definir duplicidade (ex.: 'id' ou ['id','data'])
    - keep: 'first', 'last' ou False (False remove TODAS as ocorrências duplicadas)
    - report: se True, retorna também um dicionário com estatísticas
    """
    antes = len(df)
    out = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
    if not report:
        return out

    stats = {
        "rows_before": antes,
        "rows_after": len(out),
        "removed": antes - len(out),
        "pct_removed": (antes - len(out)) / antes if antes else 0.0,
        "subset": [subset] if isinstance(subset, str) else (subset or list(df.columns)),
        "keep": keep,
    }
    return out, stats

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

def country_name(country_id):
    ''' Função recebe o código do páis dentro do dicionário 
        indicado e retorna o nome do país correspondente. '''

    COUNTRIES = {
     1: "India",
     14: "Australia",
     30: "Brazil",
     37: "Canada",
     94: "Indonesia",
     148: "New Zeland",
     162: "Philippines",
     166: "Qatar",
     184: "Singapure",
     189: "South Africa",
     191: "Sri Lanka",
     208: "Turkey",
     214: "United Arab Emirates",
     215: "England",
     216: "USA",
     }
    return COUNTRIES[country_id]

def create_price_type(price_range):
    ''' Função cria uma categoria de preço
        dado um valor relacionado no dataframe'''
    if price_range == 1:
        return "Cheap"
    elif price_range == 2:
        return "Normal"
    elif price_range == 3:
        return "Expensive"
    else:
        return "Gourmet"

def color_name(color_code):
    ''' Função pega o codigo do dataframe informado e 
        retorna uma cor correspondente dentro da chave informada
    '''
    COLORS = {
         "3F7E00": "Darkgreen",
         "5BA829": "Green",
         "9ACD32": "Lightgreen",
         "CDD614": "Orange",
         "FFBA00": "Red",
         "CBCBC8": "Darkred",
         "FF7800": "Darkred",
         }
    return COLORS[color_code]

def mudar_coluna(df:pd.DataFrame,coluna:str,i:int):
    cols = list(df.columns)
    cols.insert(i, cols.pop(cols.index(coluna)))  
    df = df[cols]
    return df

def converter_usd(df, coluna_valor='average_cost_for_two', coluna_moeda='currency'):
    """
    Converte valores monetários de diferentes moedas para USD com base em um dicionário fixo de taxas.
    """

    # Dicionário de taxas (1 unidade da moeda local = X USD)
    rates_to_usd = {
        'Dollar($)':               1.00,     # USD
        'NewZealand($)':           0.60,     # NZD
        'Brazilian Real(R$)':      0.18,     # BRL
        'Indian Rupees(Rs.)':      0.012,    # INR
        'Indonesian Rupiah(IDR)':  0.000061, # IDR
        'Pounds(£)':               1.27,     # GBP
        'Euro(€)':                 1.09,     # caso apareça futuramente
        'Rand(R)':                 0.055,    # ZAR
        'Qatari Rial(QR)':         0.274,    # QAR
        'Emirati Diram(AED)':      0.272,    # AED
        'Botswana Pula(P)':        0.074,    # BWP
        'Sri Lankan Rupee(LKR)':   0.0033,   # LKR
        'Turkish Lira(TL)':        0.030     # TRY
    }

    # Padroniza texto da coluna
    df[coluna_moeda] = df[coluna_moeda].str.strip()

    # Mapeia o fator de conversão
    df['rate_to_usd'] = df[coluna_moeda].map(rates_to_usd)

    # Identifica moedas não mapeadas
    moedas_faltantes = df.loc[df['rate_to_usd'].isna(), coluna_moeda].unique()
    if len(moedas_faltantes) > 0:
        print("⚠️ Moedas sem taxa definida:", moedas_faltantes)

    # Cria coluna convertida
    df['valor_usd'] = (df[coluna_valor] * df['rate_to_usd']).round(2)

    return df