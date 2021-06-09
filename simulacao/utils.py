import requests as req


def get_dollar():
    res = req.get('https://economia.awesomeapi.com.br/json/all/USD-BRL')
    dollar_data = res.json()
    dollar = float(dollar_data['USD']['low'])
    return round(dollar, 2)
