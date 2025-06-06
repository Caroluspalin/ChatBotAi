from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import together
from products import products

load_dotenv()

app = Flask(__name__)


api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    raise ValueError("TOGETHER_API_KEY not found in environment variables")


os.environ["TOGETHER_API_KEY"] = api_key


def find_products_by_color(color):
    results = []
    for category, items in products.items():
        for product in items:
            if color.lower() in [c.lower() for c in product["colors"]]:
                results.append(product)
    return results

def find_products_by_size(size):
    results = []
    for category, items in products.items():
        for product in items:
            if size.upper() in [s.upper() for s in product["sizes"]]:
                results.append(product)
    return results

def find_products_by_category_and_color(category, color):
    if category not in products:
        return []
    return [product for product in products[category] 
            if color.lower() in [c.lower() for c in product["colors"]]]

def format_product_info(product):
    return f"{product['name']} ({', '.join(product['colors'])}), koot: {', '.join(product['sizes'])}, hinta: {product['price']}€"

def get_stock_info(product, size=None):
    if size:
        if size in product["stock"]:
            return f"Kokoa {size} on varastossa {product['stock'][size]} kpl"
        return f"Kokoa {size} ei ole saatavilla"
    
    stock_info = []
    for size, quantity in product["stock"].items():
        stock_info.append(f"{size}: {quantity} kpl")
    return ", ".join(stock_info)

@app.route('/')
def home():
    return render_template('index.html', products=products)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    try:
        prompt = f"""Human: Olet avulias asiakaspalvelija verkkokaupassa. Vastaa asiakkaan kysymykseen ystävällisesti ja ammattimaisesti. Voit kertoa tuotteista seuraavat tiedot:

Hupparit:
- Classic Black Hoodie (musta, koot S-XL, hinta 89.99€)
- Urban Gray Hoodie (harmaa, koot S-L, hinta 79.99€)
- Navy Blue Hoodie (sininen, koot M-XL, hinta 94.99€)

Kengät:
- Urban Sneakers (musta/valkoinen, koot 40-44, hinta 129.99€)
- Running Pro (sininen/punainen, koot 39-43, hinta 159.99€)
- Casual Comfort (ruskea/musta, koot 41-44, hinta 89.99€)

T-paidat:
- Basic White Tee (valkoinen, koot S-XL, hinta 29.99€)
- Black Essential (musta, koot S-L, hinta 34.99€)
- Striped Tee (sininen/valkoinen, koot M-XL, hinta 39.99€)

Asusteet:
- Classic Cap (musta/harmaa, one-size, hinta 24.99€)
- Winter Beanie (harmaa/musta/sininen, one-size, hinta 19.99€)
- Sport Socks (musta/valkoinen, koot 39-42 ja 43-46, hinta 12.99€)

Asiakas: {user_message}
"""
        response = together.Complete.create(
            prompt=prompt + "\n\nAssistant: ",
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            max_tokens=1024,
            temperature=0.7,
            top_k=50,
            top_p=0.7,
            repetition_penalty=1.1,
            stop=['Human:', 'Assistant:']
        )
        return jsonify({"response": response['output']['choices'][0]['text'].strip()})
    except Exception as e:
        print(f"Error with Together AI: {str(e)}")
        return jsonify({"response": "Pahoittelen, mutta en pysty juuri nyt vastaamaan. Kokeile hetken kuluttua uudelleen."})

if __name__ == '__main__':
    app.run(debug=True) 