from bs4 import BeautifulSoup
from dataclasses import dataclass
import json
import dataclasses
import requests
import time
import random

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0'}
default_beer_picture_link = "https://assets.untappd.com/site/assets/images/temp/badge-beer-default.png"


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
    #print(f"Downloading: {beer_picture_link}")
    filename = filename.replace(" ", "")
    img_data = requests.get(beer_picture_link).content
    with open(filename, 'wb') as f:
        #print(f"Writing {filename}")
        f.write(img_data)
    f.close()


def write_data_file(beers=[]):
    path_to_data_file = "data/data.json"
    with open(path_to_data_file, "w") as f:
        json_obj = json.dumps(beers, cls=EnhancedJSONEncoder)
        f.write(json_obj)
    f.close()


def get_beers(soup: BeautifulSoup):
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
        if beer_picture_link != default_beer_picture_link:
            if ":" in beer_name:
                beer_name = beer_name.replace(":", "")
            if "/" in beer_name:
                beer_name = beer_name.replace("/", "")
            filename = f"images/{beer_name}.jpeg"
            get_beer_picture(beer_picture_link, filename)
        else:
            filename = "images/default_beer_picture.jpeg"

        beers.append(
                Beer(beer_name, beer_style, beer_brewery, beer_abv, beer_ibu, beer_raters, beer_desc, filename))
    return beers


def read_beer_urls():
    with open("urls.json", "r") as f:
        json_obj = json.load(f)
    f.close()
    return json_obj


def main():
    urls = read_beer_urls()
    random.shuffle(urls)
    for url in urls:
        print(f"Visiting: {url}")
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        beers = get_beers(soup)
        write_data_file(beers)
        time_to_wait = random.randint(3, 10)
        print(f"waiting {time_to_wait} seconds...")
        time.sleep(time_to_wait)


main()
