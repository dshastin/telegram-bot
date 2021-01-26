import pandas as pd
import sqlite3

photo_urls = pd.read_excel('photo_links.xlsx')
conn = sqlite3.connect('KFC.db')

for i, row in photo_urls.iterrows():
    product_id, url = row.values
    print(product_id, url)
    query = f'INSERT INTO product_photos (product_id, url) VALUES ({product_id}, "{url}");'
    conn.execute(query)
    conn.commit()
