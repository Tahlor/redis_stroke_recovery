from random import choice

import requests

mars_rover_url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'


def get_mars_photo(sol):
    params = { 'sol': sol, 'api_key': 'DEMO_KEY' }
    response = requests.get(mars_rover_url, params).json()
    photos = response['photos']

    image = choice(photos)['img_src']
    print(image)

if __name__=='__main__':
    get_mars_photo(1000)