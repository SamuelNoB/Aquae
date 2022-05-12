import requests
from datetime import date
from lxml import html
import json


ESTADOS_BR = (
    ("Acre (AC)", "AC"),
    ("Alagoas (AL)", "AL"),
    ("Amapá (AP)", "AP"),
    ("Amazonas (AM)", "AM"),
    ("Bahia (BA)", "BA"),
    ("Ceará (CE)", "CE"),
    ("Distrito Federal (DF)", "DF"),
    ("Espírito Santo (ES)", "ES"),
    ("Goiás (GO)", "GO"),
    ("Maranhão (MA)", "MA"),
    ("Mato Grosso (MT)", "MT"),
    ("Mato Grosso do Sul (MS)", "MS"),
    ("Minas Gerais (MG)", "MG"),
    ("Pará (PA)", "PA"),
    ("Paraíba (PB)", "PB"),
    ("Paraná (PR)", "PR"),
    ("Pernambuco (PE)", "PE"),
    ("Piauí (PI)", "PI"),
    ("Rio de Janeiro (RJ)", "RJ"),
    ("Rio Grande do Norte (RN)", "RN"),
    ("Rio Grande do Sul (RS)", "RS"),
    ("Rondônia (RO) ", "RO"),
    ("Roraima (RR)", "RR"),
    ("Santa Catarina (SC)", "SC"),
    ("São Paulo (SP)", "SP"),
    ("Sergipe (SE)", "SE"),
    ("Tocantins (TO)", "TO"),
)


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
    ano = hoje.year
    mes = hoje.month
    mes_mm = str(mes - 1).zfill(2)

    url = "https://sidra.ibge.gov.br/Ajax/JSon/Valores/1/1737"
    payload = {
        "params": f"t/1737/f/c/h/n/n1/all/V/2266/P/{ano}{mes_mm}/d/v2266 13",
        "versao": "-1",
        "desidentifica": "false",
    }

    response = requests.post(url, data=payload)
    response__list__ = json.loads(response.content.decode())
    ni = float(response__list__[0]["V"])
    return ni


def get_tarifa_caesb():
    response = requests.get("https://www.caesb.df.gov.br/tarifas-e-precos.html")
    doc = html.fromstring(response.content)

    # O site da CAESB tem uma incosistencia na estrutura
    aliquota = '//*[@id="conceitual"]/div[3]/center/table[1]/tbody/tr[3]/td[4]/div'
    vol_faixa = '//*[@id="conceitual"]/div[3]/center/table[1]/tbody/tr[3]/td[3]/div'

    tarifa = doc.xpath(aliquota)[0].text.lstrip()
    vol_faixa = int(doc.xpath(vol_faixa)[0].text.lstrip())

    vol0 = 0
    tarifas = [
        {
            "min": vol0,
            "max": vol0 + vol_faixa,
            "tarifa": float(tarifa.replace(",", ".")),
        }
    ]
    vol0 += vol_faixa + 1

    for i in range(4, 9):
        aliquota = (
            f'//*[@id="conceitual"]/div[3]/center/table[1]/tbody/tr[{i}]/td[4]/div/span'
        )
        vol_faixa = (
            f'//*[@id="conceitual"]/div[3]/center/table[1]/tbody/tr[{i}]/td[3]/div'
        )
        tarifa = doc.xpath(aliquota)[0].text.lstrip()

        vol_faixa = doc.xpath(vol_faixa)
        if not vol_faixa:
            vol_faixa = 9999999
        else:
            vol_faixa = int(vol_faixa[0].text.lstrip())

        tarifas.append(
            {
                "min": vol0,
                "max": vol0 + vol_faixa - 1,
                "tarifa": float(tarifa.replace(",", ".")),
            }
        )
        vol0 += vol_faixa

    return tarifas
