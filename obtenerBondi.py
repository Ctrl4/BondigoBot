import requests
from argparse import ArgumentParser
import os

parser = ArgumentParser(description="Small script to check bondi's schedule. Some useful Paradas 3048 (L), 2664 (C)")
parser.add_argument('-p', '--parada', action='store', dest='parada', default='2664')
parser.add_argument('-b', '--bondi', action='store', dest='bondi')
parser.add_argument('-i', '--chat_id', action='store', dest='chat_id')
args = parser.parse_args()

API_KEY = os.environ['TELEGRAM']


def obtenerbondi(bondi, parada=3048):
    url = f"http://api.montevideo.gub.uy/transporteRest/siguientesParada/{str(parada)}"
    cabezales = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-J320M Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.64 Mobile Safari/537.36'}
    r = requests.get(url, headers=cabezales)
    for i in r.json():
        if i['linea'] == bondi:
            return f"El {i['linea']} está a punto de pasar en {i['minutos']} minutos"
        elif i['linea'] == bondi and i['real'] is False:
            return "El {i['linea']} no está en camino pero se estima que pasa en {i['minutos']} minutos"


if args.bondi:
    result = obtenerbondi(args.bondi, args.parada)
    result = requests.utils.quote(result)
    telegram_url = f'https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={args.chat_id}&text={result}'
    print(telegram_url)
    requests.get(telegram_url)
