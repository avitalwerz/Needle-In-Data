import requests
from bs4 import BeautifulSoup
import io
import json


def recipe_spider(max_pages):
    page = 1
    page_counter = 1
    while page <= max_pages:
        # url = 'https://www.allrecipes.com/recipes/156/bread/'
        url = 'https://www.allrecipes.com/recipes/156/bread/?page=' + str(page_counter)
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, 'html.parser')
        for link in soup.findAll('div', {'class': 'fixed-recipe-card__info'}):
            href = link.select_one('a').get('href')
            print(href)
            if href is not None:
                get_single_item_data(href)
                page += 1
                if page > max_pages:
                    break
        page_counter += 1
        print(page)


def get_single_item_data(item_url):
    data_dict = dict()
    source_code = requests.get(item_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)

    # extracting data from html file
    directions = list()
    ingredients = list()
    data_dict['title'] = soup.findAll('h1', {'class': 'recipe-summary__h1'})[0].string
    data_dict['creator'] = soup.findAll('span', {'class': 'submitter__name'})[0].string
    data_dict['rating'] = soup.findAll('div', {'class': 'rating-stars'})[0].get('data-ratingstars')
    data_dict['num_made_it'] = soup.findAll('span', {'class': 'made-it-count'})[0].string
    data_dict['num_reviews'] = soup.findAll('span', {'class': 'review-count'})[0].string
    data_dict['num_photos'] = soup.findAll('span', {'class': 'picture-count-link'})[0].string
    for ingredient in soup.findAll('span', {'class': 'recipe-ingred_txt added'}):
        ingredients.append(ingredient.string)
    data_dict['ingredients'] = ingredients
    for direction in soup.findAll('span', {'class': 'recipe-directions__list--item'}):
        directions.append(direction.string)
    data_dict['directions'] = directions

    prep_items = soup.find('ul', class_='prepTime').find_all('li', class_='prepTime__item')
    if len(prep_items) > 3:
        prep_time = prep_items[1].get('aria-label')[11:]
        cook_time = prep_items[2].get('aria-label')[11:]
        ready_in = prep_items[3].get('aria-label')[9:]
    else:
        prep_time = cook_time = ready_in = "None"
    data_dict['PrepTime'] = prep_time
    data_dict['CookTime'] = cook_time
    data_dict['ReadyIn'] = ready_in

    write_json_file(data_dict)
    # counter = 0
    # for time in soup.findAll('li', {'class': 'prepTime__item'}):
    #     time = time.get('aria-label')
    #     if counter == 0:
    #         data_dict['prep_time'] = time
    #     elif counter == 1:
    #         data_dict['cook_time'] = time
    #     elif counter == 2:
    #         data_dict['ready_in'] = time
    #     else:
    #         break
    #     counter += 1

    print(data_dict)
    # data_dict['prep_time'] = soup.find('li', 'class': 'prepTime__item').get('aria-label')
    # data_dict['cook_time'] = soup.findAll('li', {'class': 'prepTime__item--time'})[1].string
    # data_dict['ready_in'] = soup.findAll('li', {'class': 'prepTime__item--time'})[2].string



def write_json_file(data_dict):
    with io.open('data.json', 'w') as data_file:
        data = json.dump(data_dict, data_file, indent=4)


recipe_spider(51)

# Title, Creator, Rating, NumMadeIt, NumReviews, NumPhotos, Ingredients (array of strings),
# Directions (array of strings), PrepTime, CookTime, ReadyIn
