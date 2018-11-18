import io
import json
import requests
from bs4 import BeautifulSoup


def recipe_spider(max_pages):
    """
    the main function that enters the site, moves between pages and send each recipe to be extracted.
    :param max_pages: max number of pages (recipes in our case) to crawl
    :return: None
    """
    total_dict = list()
    recipe_counter = 1
    page_counter = 1
    while recipe_counter <= max_pages:
        url = 'https://www.allrecipes.com/recipes/156/bread/?page=' + str(page_counter)
        # get the content
        source_code = requests.get(url)
        # turn the content into readable text
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'html.parser')
        for link in soup.findAll('div', {'class': 'fixed-recipe-card__info'}):
            link_to_recipe = link.select_one('a').get('href')
            if link_to_recipe is not None:
                recipe_dict = dict()
                recipe_dict['id'] = recipe_counter
                recipe_dict['Url'] = link_to_recipe
                # we dont want our program to crash if there is a problem in some recipe, e.g there is a missing
                # field that will be resulted in NUll etc.
                try:
                    recipe_dict = get_single_item_data(link_to_recipe, recipe_dict)
                except AttributeError:
                    break
                recipe_counter += 1
                total_dict.append(recipe_dict)
                if recipe_counter > max_pages:
                    break
        page_counter += 1
    write_json_file(total_dict)


def get_single_item_data(item_url, item_dict):
    """
    extract data from one recipe.
    :param item_url: the url of the recipe
    :param item_dict: the dictionary for the recipe
    :return: list of all the data extracted & needed about this recipe
    """
    source_code = requests.get(item_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    # extracting data from html file
    data_dict = extract_data(soup, item_dict)
    return data_dict


def extract_data(soup, data_dict):
    """
    A method that extracting data from a url into a dictionary by categories
    :param soup: html parser
    :param data_dict: the dictionary for one item
    :return: dictionary of the data
    """
    directions = list()
    ingredients = list()
    data_dict['Title'] = soup.title.string.split('-')[0]
    num_list = soup.find('div', class_='total-made-it').text.split('|')
    data_dict['Creator'] = soup.find('span', class_='submitter__name').string
    data_dict['Rating'] = soup.find('div', class_='rating-stars').get('data-ratingstars')
    data_dict['Num_made_it'] = num_list[0].split('m')[0].replace('\xa0', "").strip()
    data_dict['Num_reviews'] = num_list[1].split('r')[0].strip()
    data_dict['Num_photos'] = num_list[2].split('p')[0].strip()

    prep_list = soup.find('ul', class_='prepTime').findAll('li', {'class': 'prepTime__item'})
    # if times are mentioned so the list size is exactly 4, else there is no times mentioned.
    if len(prep_list) < 4:
        data_dict['PrepTime'] = data_dict['CookTime'] = data_dict['ReadyIn'] = None
    else:
        data_dict['PrepTime'] = prep_list[1].get('aria-label').split(':')[1].strip()
        data_dict['CookTime'] = prep_list[2].get('aria-label').split(':')[1].strip()
        data_dict['ReadyIn'] = prep_list[3].get('aria-label').split('in')[1].strip()

    for ingredient in soup.findAll('span', {'class': 'recipe-ingred_txt added'}):
        ingredients.append(ingredient.string)

    data_dict['Ingredients'] = ingredients

    for direction in soup.findAll('span', {'class': 'recipe-directions__list--item'}):
        if direction is not None:
            directions.append(direction.text.strip())
    data_dict['Directions'] = directions
    return  data_dict


def write_json_file(data_dict):
    """
    simple function that turnes the dictionary into json file
    :param data_dict:
    :return:
    """
    json_dict = {'recipes': data_dict}
    with io.open('data.json', 'w') as data_file:
        json.dump(json_dict, data_file, indent=4)


recipe_spider(300)

