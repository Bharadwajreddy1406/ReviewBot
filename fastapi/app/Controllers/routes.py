import random
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from pydantic import BaseModel
from pymongo import MongoClient
from app.Schemas.models import User, TextInput, responses, Url, QueryInput  # Assuming you have a User model defined in models.py
from app.DB.session import dbconnection  # Import the dbConnection function
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from tqdm import tqdm
import time
from app.Helpers.scrapeAndStore import scrape_data
from urllib.parse import urlparse, parse_qs
import re
from app.Model.NLPModel import answer_query
from app.Helpers.RagHelper import getContext

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if not token or token.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Not Received",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        token = token.split(" ")[1]  # Remove 'Bearer' prefix
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # You can also return user information if needed
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

# Route to handle the generation
@router.post("/generate")
async def generate_text(query: QueryInput, token: dict = Depends(verify_token)):
    try:
        username = token.get("username")
        print("I came here bruh !!" + username)
        
        response = answer_query(query.query)
        
        return {"response": response} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.get("/users", response_model=List[User])
async def get_all_users(db: MongoClient = Depends(dbconnection)):
    users_collection = db["users"]  # Assuming the collection name is "users"
    users = list(users_collection.find({}))

    # Map MongoDB _id to id
    for user in users:
        user["id"] = str(user.pop("_id"))

    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

    
@router.post("/scrape_url")
async def scraping(input: Url):
    print(f"Received scraping request with asin: {input.asin}")

    asin = input.asin
    print(f"Extracted ASIN: {asin}")

    try:
        data = scrape_data(asin)
        productCollection = dbconnection()["products"]
        print("updating data to MongoDB")
        productCollection.insert_one(data)
        print("Data successfully saved to MongoDB")
        return {"isScraped": True }
    except Exception as e:
        print("Error occurred during scraping")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

class Test(BaseModel):
    query :str
    asin:str

@router.post("/get_LLM_response")
def get_LLM_response(input : Test ):
    query = input.query
    context = getContext(input.asin, query)
    response = answer_query(query, context=context)
    
    print(f"Response: {response}")
    return {"response": response}

    
