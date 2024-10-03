from bs4 import BeautifulSoup
from dataclasses import dataclass
import re
import json
import string
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

    def toJSON(self):
        return json.dumps(
                self,
                default=lambda o: o.__dict__,
                sort_keys=True,
                indent=4)

    def toStr(self):
        return f"Beer[name: {self.beer_name}, style: {self.beer_style}]"


""" Correct format
    {
        "beer_style" : {
            "beer_id": {
                "beer_desc": "..",
                "beer_brewery" : ".."
                ...
            }
        },
        "beer_style" : {
            "beer_id": {
                "beer_style": ".."
                "beer_brewery" : ".."
            }
        }
    }
"""
def write_data_file(beers: dict):
    path_to_data_file = f"data/data.json"
    with open(path_to_data_file, "w") as f:
        f.write("{\n")
        y = 0
        for beer_style in beers.keys():
            y += 1
            f.write(f'"{beer_style}" :')
            f.write("{\n")
            beer_list = beers.get(beer_style)

            for i in range(0, len(beer_list)):
                beer_id_key = ''.join(random.choice(string.ascii_letters) for i in range(32))
                beer_json = beers[beer_style][i].toJSON()
                f.write(f'"{beer_id_key}": ')
                f.write(beer_json)

                if i < len(beers[beer_style])-1:
                    f.write(",")
                else: f.write("\n")

            if y < len(beer_style):
                f.write("\n},")
            else: f.write("}")

        f.write("\n}")
    f.close()


def get_printable_str(s: str):
    printable_chars = set(string.printable)
    return ''.join(filter(lambda x: x in printable_chars, s))


def get_beers(soup: BeautifulSoup):
    beer_container = soup.find("div", {"class": "beer-container beer-list pad"})
    beer_items = beer_container.findAll("div", {"class": "beer-item"})
    beers = []

    printable_chars = set(string.printable)

    for beer in beer_items:
        # beer picture
        beer_label = beer.find("a", {"class": "label"})
        beer_picture_link = beer_label.find("img")["src"].strip()

        # beer data
        beer_data_bid = beer["data-bid"]
        beer_name = beer.find("p", {"class": "name"}).text.strip()
        printable_name = get_printable_str(beer_name) 

        beer_styles = beer.findAll("p", {"class": "style"})
        beer_brewery = beer_styles[0].text.strip()
        printable_brewery = get_printable_str(beer_brewery)
        beer_style = beer_styles[1].text.strip()
        printable_style = get_printable_str(beer_style)

        full_desc = beer.find("p", {"class": f"desc-full-{beer_data_bid}"}).text.strip()

        if "Read Less" in full_desc:
            t = full_desc.replace("Read Less", "")
            beer_desc =  ''.join(filter(lambda x: x in printable_chars, t))
        elif " Read Less" in full_desc:
            t = full_desc.replace(" Read Less", "")
            beer_desc = ''.join(filter(lambda x: x in printable_chars, t))
        else:
            beer_desc = ""

        printable_desc = ''.join(filter(lambda x: x in string.punctuation, beer_desc))

        # beer details
        beer_abv = beer.find("p", {"class": "abv"}).text.strip()
        beer_ibu = beer.find("p", {"class": "ibu"}).text.strip()
        beer_raters = beer.find("p", {"class": "raters"}).text.strip()

        beers.append(
                Beer(printable_name, printable_style, printable_brewery, 
                     beer_abv, beer_ibu, beer_raters, beer_desc, beer_picture_link))
    return beers


def read_beer_urls():
    with open("urls.json", "r") as f:
        json_obj = json.load(f)
    f.close()
    return json_obj

def get_match(url: str):
    pattern = r"type=([^&]+)"
    match = re.search(pattern, url) 
    return match.group(1)


def main():
    urls = read_beer_urls()
    pattern = r"type=([^&]+)"
    number_of_urls_left = len(urls)
    random.shuffle(urls)
    beer_dict = {}
    for url in urls:
        number_of_urls_left -= 1
        print(f"Visiting: {url}")
        print(f"Number of urls left: {number_of_urls_left}")
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        beers = get_beers(soup)
        beer_style = get_match(url)
        beer_dict[beer_style] = beers
        #print(beer_dict)
        write_data_file(beer_dict)
        time_to_wait = random.randint(3, 5)
        print(f"waiting {time_to_wait} seconds...")
        time.sleep(time_to_wait)


main()
