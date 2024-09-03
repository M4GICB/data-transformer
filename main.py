import json
import re
import requests


def validate_filter_input(filter_type, filter, filter_type_map):
    """
    Validate the filter input based on the filter type and filter type map.

    Args:
        filter_type (str): The type of filter to validate.
        filter (str): The filter value to validate.
        filter_type_map (dict): The mapping of filter types to their URLs.

    Raises:
        KeyError: If the filter type is not in the filter type map.
        ValueError: If the filter input does not meet the requirements for the "letter" filter type.
        TypeError: If the filter input is not alphanumeric for the "letter" filter type.
    """
    error_prefix = f"{{Filter Type: '{filter_type}', Filter Input: '{filter}'}} - "

    # Check if the filter type exists in the map
    if filter_type not in filter_type_map:
        raise KeyError(
            error_prefix + "The filter type does not exist in the filter type map."
        )

    # Additional checks for "letter" filter type
    if filter_type == "letter":
        if len(filter) != 1:
            raise ValueError(
                error_prefix
                + "The filter input must be a single character when Filter Type is 'letter'."
            )
        if not filter.isalnum():
            raise TypeError(
                error_prefix
                + "The filter input must be an alphanumeric character when Filter Type is 'letter'."
            )


def construct_url(filter_type, filter):
    """
    Construct the URL for the API request based on filter type and filter input.

    Args:
        filter_type (str): The type of filter to apply.
        filter (str): The filter value to use in the URL.

    Returns:
        str: The constructed URL.

    Raises:
        KeyError: If the filter type does not exist in the filter type map.
        ValueError: If the filter input does not meet the requirements for the "letter" filter type.
    """
    base_url = "https://www.thecocktaildb.com/api/json/v1/1"
    filter_type_map = {
        "name": "/search.php?s=",
        "letter": "/search.php?f=",
        "random": "/random.php",
        "ingredient": "/filter.php?i=",
        "alcoholic": "/filter.php?a=",
        "category": "/filter.php?c=",
        "glass": "/filter.php?g=",
    }

    # Validate the input first
    validate_filter_input(filter_type, filter, filter_type_map)

    # Handle the "random" filter type with early return
    if filter_type == "random":
        return f"{base_url}{filter_type_map[filter_type]}"

    # Construct and return the full URL
    return f"{base_url}{filter_type_map[filter_type]}{filter}"


def fetch_drink_by_id(id):
    """
    Fetch drink details by ID.

    Args:
        id (str): The ID of the drink to fetch.

    Returns:
        dict: The drink details.

    Raises:
        ValueError: If the ID is not a string or not numeric, or if no drinks are found.
        requests.HTTPError: If the request returns a non-200 status code.
    """
    # Ensure ID is a string and numeric
    if not isinstance(id, str):
        raise ValueError(
            f"{{ID: '{id}', Type: {type(id)}}} - The ID must be a string.")

    if not id.isdigit():
        raise ValueError(f"{{ID: '{id}'}} - The ID must be numeric.")

    # Make a GET request to the API endpoint
    url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={id}"
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError for non-200 responses

    # Parse JSON response
    posts = response.json()

    # Check if 'drinks' key is present and contains data
    if not posts.get("drinks"):
        raise ValueError(
            f"{{ID: '{id}'}} - No drinks found for the provided ID.")

    return posts["drinks"][0]


def fetch_data_by_filter(filter_type, filter):
    """
    Fetch data from the API based on the filter type and filter input.

    Args:
        filter_type (str): The type of filter to apply.
        filter (str): The filter value to use in the API call.

    Returns:
        dict: The processed data from the API.

    Raises:
        KeyError: If the filter type does not exist in the filter type map.
        ValueError: If the response is empty or contains invalid data.
        requests.HTTPError: If the request returns a non-200 status code.
    """
    url = construct_url(filter_type, filter)

    # Make the API call
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError for bad responses

    # Check if the response is empty
    if not response.text.strip():
        raise ValueError("Received an empty response from the API call.")

    # Parse JSON response
    fetched_data = response.json()

    # Process the data for specific filter types
    if filter_type in {"ingredient",  "alcoholic", "category", "glass"}:
        print("Filter APIs require extra processing...")
        new_fetched_data = {"drinks": []}
        drinks_list = fetched_data.get("drinks", [])
        total = len(drinks_list)
        interval = max(total // 10, 1)  # Ensure minimum interval of 1

        for index, drink in enumerate(drinks_list, start=1):
            if index == 1 or index % interval == 0 or index == total:
                print(f"Processing entry {index} of {total}...")

            # Fetch additional details for each drink
            drink_data = fetch_drink_by_id(drink["idDrink"])
            if drink_data:
                new_fetched_data["drinks"].append(drink_data)

        fetched_data = new_fetched_data

    return fetched_data


def transform_drinks(data):
    transformed_data = []

    for drink in data["drinks"]:
        name_id = re.sub(r"\s+", "-", drink["strDrink"].strip().lower())

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


try:
    data = fetch_data_by_filter("name", "Margarita")
    transformed_drinks = transform_drinks(data)
    with open("output.json", "w") as file:
        json.dump(transformed_drinks, file, indent=2)

    print("\n\n<<< Printing Transformed Drinks... >>>\n\n")

    for drink in transformed_drinks:
        for key, value in drink.items():
            print(f"{key}: {value}")
        print("\n==========\n")

    print(f"Number Of Entries: {len(transformed_drinks)}")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
