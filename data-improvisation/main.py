"""
NOTE: All prices here are weekly

"""

import json
import random
import pandas

with open("./b64img.txt", "r") as f:
    b64img = f.read()
with open("./exported_testing.json", "r") as file:
    data_read = json.load(file)
    data_read = pandas.DataFrame(data_read)

all_unique_models = data_read["model"].unique()
all_unique_brands = data_read["brand"].unique()
all_unique_car_types = data_read["type"].unique()
all_unique_colors = data_read["color"].unique()
output = []
class_tarifs = {"A": 34 * 7, "B": 49 * 7, "C": 69 * 7}  # Week tariffs for class


for _ in range(0, 100):
    random_car = {
        "brand": random.choice(all_unique_brands),
        "model": random.choice(all_unique_models),
        "type": random.choice(all_unique_car_types),
        "age": random.randint(1, 8),
        "seats": 5,  # Assuming that every car has 5 seats (even big ones)
        "towbar": random.choice([True, False]),
        "color": random.choice(all_unique_colors),
        "winter_tires": random.choice([True, False]),
        "roofbox_option": random.choice([True, False]),
        "class": random.choice(["A", "B", "C"]),
        "base64_img_url": b64img,
        "available": True,
    }
    price: float = class_tarifs[random_car["class"]]
    if random_car["towbar"] is True:
        price += 105  # ADDITIONAL TOWBAR PRICE
    if random_car["winter_tires"] is True:
        price += 140
    if random_car["roofbox_option"] is True:
        price += 105
    random_car["price"] = price - 0.01
    output.append(random_car)


with open("./output.json", "w") as file:
    json.dump(output, file, indent=2)
