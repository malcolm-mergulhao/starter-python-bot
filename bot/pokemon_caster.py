import json
import requests
import re

URL =  'http://pokeapi.co/api/v2/pokemon/{}/'

class PokemonCaster(object):
                 
    def i_choose_you(self, pkmn):
        token = re.split('choose you ', msg)
        link = URL
        target = link.format(token[1])
        try:
            response = requests.get(target)
        except requests.exceptions.RequestException as e:
            return 'nope, something went wrong there pal'
        else:
            pokemon = response.json()
            return pokemon['sprites']['front_default']