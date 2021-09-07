import requests
from argparse import ArgumentParser

parser = ArgumentParser(description="Small script to check bondi's schedule. Some useful Paradas 3048 (L), 2664 (C)")
parser.add_argument('-p','--parada',action='store',dest='parada',default='2664')
parser.add_argument('-b','--bondi',action='store',dest='bondi')
args = parser.parse_args()



def obtenerBondi(bondi,parada=3048):
        url = 'http://api.montevideo.gub.uy/transporteRest/siguientesParada/' + str(parada)
        cabezales = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-J320M Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.64 Mobile Safari/537.36'}
        r = requests.get(url,headers=cabezales)
        for i in r.json():
            if i['linea']==bondi:
                return ("El %s está a punto de pasar en %s minutos" % (i['linea'],i['minutos']))
            elif i['linea']==bondi and i['real']==False:
                return ("El %s no está en camino pero se estima que pasa en %s minutos" % (i['linea'],i['minutos']))

if args.bondi:
    print(obtenerBondi(args.bondi, args.parada))
