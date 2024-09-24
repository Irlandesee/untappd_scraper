import json
import dataclasses
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0'}
#url = 'https://untappd.com/beer/top_rated?type=bitter-best&country=england'
#req = requests.get(url, headers=headers)
#soup = BeautifulSoup(req.content, 'html.parser')

#print(req.status_code)


@dataclass
class Beer:
    beer_name: str
    beer_style: str
    beer_brewery: str
    beer_abv: str
    beer_ibu: str
    beer_raters: str
    beer_desc: str
    beer_picture_link: str


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def get_beer_picture(beer_picture_link: str, filename: str):
    print(f"Downloading: {beer_picture_link}")
    filename = filename.replace(" ", "")
    img_data = requests.get(beer_picture_link).content
    with open(filename, 'wb') as f:
        print(f"Writing {filename}")
        f.write(img_data)
    f.close()


def write_data_file(beers=[]):
    path_to_data_file = "data/data.json"
    with open(path_to_data_file, "w") as f:
        json_obj = json.dumps(beers, cls=EnhancedJSONEncoder)
        f.write(json_obj)
    f.close()


def get_beers():
    beer_container = soup.find("div", {"class": "beer-container beer-list pad"})
    beer_items = beer_container.findAll("div", {"class": "beer-item"})
    beers = []
    for beer in beer_items:
        # beer picture
        beer_label = beer.find("a", {"class": "label"})
        beer_picture_link = beer_label.find("img")["src"].strip()
        # beer data
        beer_data_bid = beer["data-bid"]
        beer_name = beer.find("p", {"class": "name"}).text.strip()
        beer_styles = beer.findAll("p", {"class": "style"})
        beer_brewery = beer_styles[0].text.strip()
        beer_style = beer_styles[1].text.strip()
        full_desc = beer.find("p", {"class": f"desc-full-{beer_data_bid}"}).text.strip()

        if "Read Less" in full_desc:
            beer_desc = full_desc.replace("Read Less", "")
        elif " Read Less" in full_desc:
            beer_desc = full_desc.replace(" Read Less", "")
        else:
            beer_desc = ""

        # beer details
        beer_abv = beer.find("p", {"class": "abv"}).text.strip()
        beer_ibu = beer.find("p", {"class": "ibu"}).text.strip()
        beer_raters = beer.find("p", {"class": "raters"}).text.strip()

        # retrieve beer picture
        filename = f"images/{beer_name}.jpeg"
        #get_beer_picture(beer_picture_link, filename)

        beers.append(Beer
                     (beer_name, beer_style, beer_brewery, beer_abv, beer_ibu,
                      beer_raters, beer_desc, filename))
    return beers


def get_beer_styles():
    url = "https://untappd.com/beer/top_rated"
    req = requests.get(url, headers=headers)
    print(f"Beer styles status code: {req.status_code}")
    soup = BeautifulSoup(req.content, 'html.parser')
    content_box = soup.find("div", {"class", "content"})
    filters = content_box.find("div", {"class", "filter"})
    print(filters)


def main():
    get_beer_styles()



main()
