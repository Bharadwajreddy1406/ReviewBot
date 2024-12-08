import requests
import os
from dotenv import load_dotenv
from app.Helpers.embeddingAndFormat import transform_data, add_review
from app.DB.session import dbconnection
# import app.Model.LlamaModel as Model
# import app.Helpers.RagHelper as rh
import app.Model.NLPModel as Model
load_dotenv()
api_key = os.getenv('SCRAPER_API_KEY')
if not api_key:
    raise Exception("SCRAPER_API_KEY environment variable not set")

db = dbconnection()
products_collection = db['products']

def scrape_data(asin_no, domain="in"):
    print(f"Scraping data for ASIN: {asin_no}, domain: {domain}")
    payload = {
        "api_key": api_key,
        "asin": asin_no,
        "domain": domain,
    }
    product_url = "https://api.scrapingdog.com/amazon/product"
    review_url = "https://api.scrapingdog.com/amazon/reviews"
    try:
        formatted_data = {}
        r = requests.get(product_url, params=payload)
        print("Received product response from ScraperAPI")
        if r.status_code == 200:
            product_data = r.json()
            formatted_data = transform_data(product_data, asin_no)
        else:
            print(f"failed, response status code of product scrape is {r.status_code}")
            raise Exception(f"Failed to get product data: {r.status_code}")
            
        print(f"trying to get reviews response from ScraperAPI")
        for i in range(2,5):
            payload["page"] = str(i)
            r = requests.get(review_url, params=payload)
            
            if r.status_code == 200:
                
                review_data = r.json()
                if(review_data["customer_reviews"] == []):
                    break
                formatted_data = add_review(formatted_data, review_data)
                
            else:
                print(f"response status code of review scrape is {r.status_code}")  
                if("reviews" not in formatted_data):
                    break
                raise Exception(f"Failed to get review data: {r.status_code}")                  
        # print(f"added {len(formatted_data["reviews"])} reviews")

        print(f"added {len(formatted_data['reviews'])} reviews")
        print("creating review summary")
        results = ""
        for doc in formatted_data["reviews"]:
            results = results + "\n" + doc["review"]
        # formatted_data["review_summary"] = lm.summarise_text(results, formatted_data["title"])
        formatted_data["review_summary"] = Model.summarise_text(results, formatted_data["title"])
        print("review summary created")
                
        if isinstance(formatted_data, dict):
            # print("updating data to MongoDB")
            
            # products_collection.update_one(
            #     {"product_asin_no": asin_no},
            #     {"$set": formatted_data},
            #     upsert=True
            # )
            # print("Data successfully saved to MongoDB")
            return formatted_data
        else:
            return {"success": "false", "error": "Unexpected formatted data format"}
    except Exception as e: 
        print("Exception occurred while scraping data " + str(e))
        return {"success": "false", "error": str(e)}
# scrape_data("B0CYGYCRH8")