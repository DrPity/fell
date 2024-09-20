import json
import csv
import re

def expand_range(range_str):
    if '-' not in range_str:
        return [range_str]
    
    start, end = range_str.split('-')
    
    # For articleNumber (e.g., 240512140001-0005)
    if len(start) > len(end):
        prefix = start[:-len(end)]
        start_num = int(start[-len(end):])
        end_num = int(end)
        return [f"{prefix}{str(num).zfill(len(end))}" for num in range(start_num, end_num + 1)]
    
    # For articleNumberHeino (e.g., 1372251-55)
    else:
        start_num = int(start)
        end_num = int(end)
        return [str(num).zfill(len(start)) for num in range(start_num, end_num + 1)]

def process_subarticles(subarticles, main_article):
    rows = []
    for subarticle in subarticles:
        try:
            if subarticle['type'] == 'individual':
                row = main_article.copy()
                row.update(subarticle)
                row['imageUrl'] = f"https://heterogondesign.com/assets/fell/{subarticle['articleNumberHeino']}.png"
                rows.append(row)
            elif subarticle['type'] == 'range':
                heino_numbers = expand_range(subarticle['articleNumberHeino'])
                art_numbers = expand_range(subarticle['articleNumber'])
                
                # Ensure both ranges have the same length
                if len(heino_numbers) != len(art_numbers):
                    print(f"Warning: Mismatch in range lengths for {subarticle['articleNumberHeino']}")
                    max_length = max(len(heino_numbers), len(art_numbers))
                    heino_numbers = heino_numbers + [heino_numbers[-1]] * (max_length - len(heino_numbers))
                    art_numbers = art_numbers + [art_numbers[-1]] * (max_length - len(art_numbers))
                
                for heino_num, art_num in zip(heino_numbers, art_numbers):
                    row = main_article.copy()
                    row.update(subarticle)
                    row['articleNumberHeino'] = heino_num
                    row['articleNumber'] = art_num
                    row['imageUrl'] = f"https://heterogondesign.com/assets/fell/{heino_num}.png"
                    rows.append(row)
            else:
                print(f"Warning: Unknown subarticle type: {subarticle['type']}")
        except Exception as e:
            print(f"Error processing subarticle: {subarticle}")
            print(f"Error message: {str(e)}")
    return rows

def json_to_csv(json_data, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['mainArticleNumberHeino', 'mainArticleNumber', 'description', 'price', 'amount', 'notes',
                      'articleNumberHeino', 'type', 'articleNumber', 'imageUrl']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for article in json_data['articles']:
            main_article = {
                'mainArticleNumberHeino': article['mainArticleNumberHeino'],
                'mainArticleNumber': article['mainArticleNumber'],
                'description': article['description'],
                'price': article['price'],
                'amount': article['amount'],
                'notes': article['notes']
            }

            if article['subArticles']:
                rows = process_subarticles(article['subArticles'], main_article)
                writer.writerows(rows)
            else:
                writer.writerow(main_article)

# Load JSON data
with open('corrected_articles.json', 'r') as json_file:
    data = json.load(json_file)

# Convert JSON to CSV
json_to_csv(data, 'articles.csv')

print("CSV file has been created successfully.")