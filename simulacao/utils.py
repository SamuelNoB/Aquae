import requests
from datetime import date, timedelta
from lxml import html
import json
from tabula import read_pdf


ESTADOS_BR = (
    ("AC", "AC"),
    ("AL", "AL"),
    ("AP", "AP"),
    ("AM", "AM"),
    ("BA", "BA"),
    ("CE", "CE"),
    ("DF", "DF"),
    ("ES", "ES"),
    ("GO", "GO"),
    ("MA", "MA"),
    ("MT", "MT"),
    ("MS", "MS"),
    ("MG", "MG"),
    ("PA", "PA"),
    ("PB", "PB"),
    ("PR", "PR"),
    ("PE", "PE"),
    ("PI", "PI"),
    ("RJ", "RJ"),
    ("RN", "RN"),
    ("RS", "RS"),
    ("RO", "RO"),
    ("RR", "RR"),
    ("SC", "SC"),
    ("SP", "SP"),
    ("SE", "SE"),
    ("TO", "TO"),
)

Estado_Sigla = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
    "Distrito Federal": "DF",
}

meses = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def chunk_list(lst, n=3):
    """
    Divide a lista em grupos de tamanho n
    """
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def get_dollar():
    res = requests.get("https://economia.awesomeapi.com.br/json/all/USD-BRL")
    dollar_data = res.json()
    dollar = float(dollar_data["USD"]["low"])
    return round(dollar, 2)


def get_ni_ipca():
    """
    Coleta o IPCA do mês anterior fazendo um post request
    para a tabela 1737 do SIDRA (IBGE) e
    retorna o número índice respectivo ao mês anterior
    """
    hoje = date.today()
    primeiro = hoje.replace(day=1)
    mes_passado = primeiro - timedelta(days=1)
    ano = mes_passado.year
    mes = str(mes_passado.month).zfill(2)

    url = "https://sidra.ibge.gov.br/Ajax/JSon/Valores/1/1737"
    payload = {
        "params": f"t/1737/f/c/h/n/n1/all/V/2266/P/{ano}{mes}/d/v2266 13",
        "versao": "-1",
        "desidentifica": "false",
    }

    response = requests.post(url, data=payload, verify="simulacao/CAs/ibge.pem")
    response__list__ = json.loads(response.content.decode())
    ni = float(response__list__[0]["V"])
    return ni


def get_tarifa():
    ano = date.today().year - 4
    snis = f"http://www.snis.gov.br/downloads/diagnosticos/ae/{ano}/Diagnostico-SNIS-AE-{ano}-Capitulo-12.pdf"
    df = read_pdf(
        input_path=snis,
        pages=4,
        area=[290, 80, 800, 600],
    )[0]

    df = df.iloc[:, 0:2]
    df.set_axis(["UF", "Tarifa"], axis=1, inplace=True)
    df["Tarifa"] = df["Tarifa"].apply(lambda tarifa: float(tarifa.replace(",", ".")))
    df.query(
        "UF not in ['Brasil', 'Sul', 'Sudeste', 'Centro-Oeste', 'Norte', 'Nordeste']",
        inplace=True,
    )
    df["UF"] = df["UF"].apply(lambda uf: Estado_Sigla[uf])

    return df
