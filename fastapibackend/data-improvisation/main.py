"""
NOTE: All prices here are daily

With this program you can generate/improvise data based off an existing set of mongodb documents

Can be useful to "fake" data :) but the car images are just not realistic

"""

import json, json5
import random
import pandas
import os

tariffs_file = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../tariffs.jsonc")
)

with open("./rons_autoverhuur.autos.json", "r") as file:
    data_read = json.load(file)
    data_read = pandas.DataFrame(data_read)
with open(tariffs_file, "r") as file:
    tariffs: dict[str, int] = json5.load(file)

all_unique_models = data_read["model"].unique()
all_unique_brands = data_read["brand"].unique()
all_unique_car_types = data_read["type"].unique()
all_unique_colors = data_read["color"].unique()
all_unique_images = data_read["car_image_base64"].unique()
output = []


for _ in range(0, 100):
    random_car = {
        "brand": random.choice(all_unique_brands),
        "model": random.choice(all_unique_models),
        "type": random.choice(all_unique_car_types),
        "age": random.randint(1, 8),
        "seats": 5,  # Assuming that every car has 5 seats (even large ones)
        "towbar": random.choice([True, False]),
        "color": random.choice(all_unique_colors),
        "winter_tires": random.choice([True, False]),
        "roofbox_option": random.choice([True, False]),
        "class": random.choice(["Compact", "Economy", "Off-Road", "Sport", "Standard"]),
        "car_image_base64": random.choice(all_unique_images),
        "available": True,
    }
    price: float = tariffs[random_car["class"]]
    if random_car["towbar"] is True:
        price += tariffs["towbar_tariff"]  # ADDITIONAL TOWBAR PRICE
    if random_car["winter_tires"] is True:
        price += tariffs["winter_tires_tariff"]
    if random_car["roofbox_option"] is True:
        price += tariffs["roofbox_tariff"]
    random_car["price"] = price - 0.01
    output.append(random_car)


with open("./output.json", "w") as file:
    json.dump(output, file, indent=2)
