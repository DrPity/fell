import json
import re

def get_description_code(description):
    description_codes = {
        "devoree metallic Ecoleder": "01",
        "bedruckt Zebra auf weiß": "02",
        "bedruckt Zebra auf braun": "03",
        "khaki grün gefärbt": "04",
        "dunkelrot gefärbt": "05",
        "petrol gefärbt": "06",
        "pink gefärbt": "07",
        "gemischte Farben": "08",
        "exoten dunkel weiße Flanken": "09",
        "exoten Tricolor": "10",
        "exoten dunkel": "11",
        "exoten hell": "12",
        "Salz und Pfeffer": "13",
        "rotbraun": "14",
        "Allgäuer": "15",
        "Gries/gräulich": "16",
        "braun uni natur": "17",
        "weiß uni natur": "18",
        "schwarz uni natur": "19",
        "braun/weiß": "20",
        "schwarz/weiß": "21",
        "beige/weiß": "22"
    }
    
    for key, value in description_codes.items():
        if key in description:
            return value
    return "00"  # Default if no match found

def get_square_meter_code(description):
    if "1-2m²" in description:
        return "1"
    elif "2-3m²" in description:
        return "2"
    elif "3-4m²" in description:
        return "3"
    elif "4-5m²" in description:
        return "4"
    else:
        return "0"  # Default if no match found

def correct_article_number(article):
    if 'subArticles' in article:
        description = article['description']
        desc_code = get_description_code(description)
        sqm_code = get_square_meter_code(description)
        
        for sub_article in article['subArticles']:
            old_number = sub_article['articleNumber']
            new_number = f"{old_number[:4]}1{desc_code}{sqm_code}{old_number[-4:]}"
            sub_article['articleNumber'] = new_number

    return article

# Load the JSON data
with open('articles.json', 'r') as file:
    data = json.load(file)

# Correct the article numbers
corrected_articles = [correct_article_number(article) for article in data['articles']]

# Update the original data
data['articles'] = corrected_articles

# Save the corrected JSON data
with open('corrected_articles.json', 'w') as file:
    json.dump(data, file, indent=2)

print("Article numbers have been corrected and saved to 'corrected_articles.json'")