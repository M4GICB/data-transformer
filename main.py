import json
import re


with open('test.json', 'r') as file:
    data = json.load(file)

def transform_drinks(data):
    transformed_data = []

    for drink in data["drinks"]:
        name_id = re.sub(r'\s+', '-', drink["strDrink"].strip().lower())

        ingredients = []
        for i in range(1, 16):
            ingredient = drink.get(f"strIngredient{i}")
            measure = drink.get(f"strMeasure{i}")

            if ingredient:
                # if measure or not measure.isalnum():
                #     measure = "null"
                ingredients.append({"name": ingredient, "measure": measure})

        transformed_drink = {
            "name_id": name_id,
            "name": drink["strDrink"],
            "category": drink["strCategory"],
            "classification": drink["strAlcoholic"],
            "glass": drink["strGlass"],
            "instructions": drink["strInstructions"],
            "image": drink["strDrinkThumb"],
            "ingredients": ingredients,
        }
        transformed_data.append(transformed_drink)

    return transformed_data

transformed_drinks = transform_drinks(data)

print(json.dumps(transformed_drinks, indent=2))