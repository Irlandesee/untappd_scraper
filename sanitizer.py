import json
import hashlib
from dataclasses import dataclass
import time

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
    path_to_data_file = f"data/correct_data.json"
    with open(path_to_data_file, "w") as f:
        f.write("{\n")
        y = 0
        for beer_style in beers.keys():
            y += 1
            f.write(f'"{beer_style}" :')
            f.write("{\n")
            beer_list = beers.get(beer_style)

            for i in range(0, len(beer_list)):
                beer_json = beers[beer_style][i].toJSON()
                f.write(f'"{beers[beer_style][i].beer_name_hex}": ')
                f.write(beer_json)

                if i < len(beers[beer_style])-1:
                    f.write(",")
                else: f.write("\n")

            if y < len(beers.keys()):
                f.write("\n},")
            else: f.write("}")

        f.write("\n}")
    f.close()

@dataclass
class Beer:
    beer_name_hex: str
    beer_cat_hex: str
    beer_name: str
    beer_style: str
    beer_brewery: str
    beer_abv: str
    beer_abv: str
    beer_ibu: str
    beer_raters: str
    beer_desc: str
    beer_picture_link: str

    def toJSON(self):
        return json.dumps(
                self,
                default= lambda o: o.__dict__,
                sort_keys=True,
                indent=4)
    def toStr(self):
        return f"Beer[name: {self.beer_name_hex}, cat: {self.beer_cat_hex}]"


beer_dict = {}
with open("data/mybeer-f68c5-default-rtdb-export.json", "r") as f:
    json_obj = json.load(f)
    
    for category in json_obj.keys():
        beers = json_obj[category]
        category = category.replace(" ", "")
        category = category.replace("-", "")
        cat_hex = hashlib.md5(category.casefold().encode("utf-8")).hexdigest()
        #print(f"{category} -> {cat_hex}")
        beer_list = []
        for beer in beers.values():
            beer_name_to_encode = beer["beer_name"].casefold()
            beer_name_to_encode = beer_name_to_encode.replace(" ", "")
            beer_name_to_encode = beer_name_to_encode.replace("-", "")

            beer_name_hex = hashlib.md5(beer["beer_name"].casefold().encode("utf-8")).hexdigest()
            #print(f"{beer_name_to_encode} -> {beer_name_hex}")
            b = Beer(beer_name_hex, 
                     cat_hex, 
                     beer["beer_name"],
                     beer["beer_style"],
                     beer["beer_brewery"],
                     beer["beer_abv"],
                     beer["beer_ibu"],
                     beer["beer_raters"],
                     beer["beer_desc"],
                     beer["beer_picture_link"])
            beer_list.append(b)
        beer_dict[cat_hex] = beer_list

f.close()

write_data_file(beer_dict)

def get_beer_hex_codes(beer_list: list):
    separator = "|"
    hex_codes = '"'
    i = 0
    for beer in beer_list:
        i+=1
        if i != len(beer_list):
            hex_codes += beer.beer_name_hex + separator
        else:
            hex_codes += beer.beer_name_hex
    hex_codes += '"'
    #print(hex_codes)
    return hex_codes


beer_hex_codes= ""
with open("data/SQLitedb.sql", "w") as f:
    for cat in beer_dict.keys():
        beer_hex_codes = get_beer_hex_codes(beer_dict[cat])
        insert_query = 'values = ContentValues().apply{'\
        + f'\n\tput("id", "{cat}")'\
        + f'\n\tput("beer_style", "{beer_dict[cat].pop().beer_style}")'\
        + f'\n\tput("beer_hex_codes", {beer_hex_codes})'\
        + '}\ndb.insert("beer_categories", null, values)\n'
        f.write(insert_query)
    f.close()

print("done")
