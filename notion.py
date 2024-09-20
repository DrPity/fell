import csv
import configparser
import os
from notion_client import Client

def get_notion_config():
    config = configparser.ConfigParser()
    
    # Determine the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to config.ini
    config_path = os.path.join(script_dir, 'config.ini')
    
    # Read the configuration file
    config.read(config_path)
    
    # Get the Notion configuration
    notion_token = config.get('Notion', 'NOTION_TOKEN')
    database_id = config.get('Notion', 'DATABASE_ID')
    
    return notion_token, database_id

# Use the function to get your Notion configuration
NOTION_TOKEN, DATABASE_ID = get_notion_config()

# Initialize the Notion client
notion = Client(auth=NOTION_TOKEN)

def read_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def get_database_properties():
    database = notion.databases.retrieve(database_id=DATABASE_ID)
    return database['properties']

def create_property(property_name):
    notion.databases.update(
        database_id=DATABASE_ID,
        properties={
            property_name: {"rich_text": {}}
        }
    )
    print(f"Created new property: {property_name}")

def ensure_properties_exist(csv_headers):
    db_properties = get_database_properties()
    for header in csv_headers:
        if header not in db_properties and header != 'Image':
            create_property(header)
    return get_database_properties()  # Refresh properties after creation

def find_page_by_identifier(identifier, identifier_property):
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": identifier_property,
            "rich_text" if identifier_property != "Title" else "title": {
                "equals": identifier
            }
        }
    )
    return response['results'][0] if response['results'] else None

def create_notion_properties(row, db_properties):
    properties = {}
    for prop_name, prop_info in db_properties.items():
        if prop_name in row:
            if prop_info['type'] == 'rich_text':
                properties[prop_name] = {"rich_text": [{"text": {"content": row[prop_name]}}]}
            elif prop_info['type'] == 'title':
                properties[prop_name] = {"title": [{"text": {"content": row[prop_name]}}]}
    return properties

def update_or_create_page(row, identifier_property, db_properties):
    existing_page = find_page_by_identifier(row[identifier_property], identifier_property)
    properties = create_notion_properties(row, db_properties)
    
    try:
        if existing_page:
            notion.pages.update(page_id=existing_page['id'], properties=properties)
            print(f"Updated existing page: {row[identifier_property]}")
            page_id = existing_page['id']
        else:
            new_page = {
                "parent": {"database_id": DATABASE_ID},
                "properties": properties
            }
            created_page = notion.pages.create(**new_page)
            print(f"Created new page: {row[identifier_property]}")
            page_id = created_page['id']
        
        # Add or update image
        if 'Image' in row:
            add_or_update_image(page_id, row['Image'])
    except Exception as e:
        print(f"Error processing row {row[identifier_property]}: {str(e)}")

def add_or_update_image(page_id, image_url):
    blocks = notion.blocks.children.list(block_id=page_id)
    image_block = next((block for block in blocks['results'] if block['type'] == 'image'), None)
    
    image_block_data = {
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": image_url
            }
        }
    }
    
    if image_block:
        notion.blocks.update(block_id=image_block['id'], **image_block_data)
    else:
        notion.blocks.children.append(block_id=page_id, children=[image_block_data])

def delete_pages_not_in_csv(csv_identifiers, identifier_property):
    query = notion.databases.query(database_id=DATABASE_ID)
    for page in query['results']:
        page_identifier = page['properties'][identifier_property]['rich_text'][0]['plain_text'] if identifier_property != 'Title' else page['properties'][identifier_property]['title'][0]['plain_text']
        if page_identifier not in csv_identifiers:
            notion.pages.update(page_id=page['id'], archived=True)
            print(f"Archived page: {page_identifier}")

def main():
    csv_path = 'product_template.csv'  # Replace with your CSV file path
    try:
        rows = read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return
    except csv.Error as e:
        print(f"Error reading CSV file: {str(e)}")
        return
    
    if not rows:
        print("CSV file is empty.")
        return

    csv_headers = rows[0].keys()
    db_properties = ensure_properties_exist(csv_headers)
    
    identifier_property = 'Handle' if 'Handle' in db_properties else 'Title'
    if identifier_property not in db_properties:
        print(f"Error: Neither 'Handle' nor 'Title' property found in the database or CSV.")
        return
    
    csv_identifiers = set()
    for row in rows:
        update_or_create_page(row, identifier_property, db_properties)
        csv_identifiers.add(row[identifier_property])
    
    delete_pages_not_in_csv(csv_identifiers, identifier_property)
    
    print(f"Processed {len(rows)} items in the Notion database.")

if __name__ == "__main__":
    main()