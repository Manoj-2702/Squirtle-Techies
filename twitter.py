import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import google.generativeai as genai
import folium
from geopy.geocoders import Nominatim
import webbrowser
import pymongo
from flask import Flask, redirect, url_for 
from flask_pymongo import PyMongo
from geopy.geocoders import Nominatim
from flask import Flask


app = Flask(__name__)
app.secret_key = "4"
app.config["MONGO_URI"] = "mongodb+srv://sana:sana1000@cluster0.eybaoqn.mongodb.net/dotslash?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

geolocator=Nominatim(user_agent="my_app")



# Set the API key directly in the script (for testing purposes)
os.environ['GOOGLE_API_KEY'] = 'Your api key'

# Configure the SDK with the API key
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-pro')

def initialize_driver():
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def extract_tweets(driver, search_text):
    search_input = WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='SearchBox_Search_Input']")))
    search_input.send_keys(search_text)
    search_input.send_keys(Keys.ENTER)

    parent_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-175oi2r.r-1igl3o0.r-qklmqi.r-1adg3ll.r-1ny4l3l')))
    extracted_text_list = []
    for parent_div in parent_divs:
        nested_div = parent_div.find_element(By.CLASS_NAME, 'css-175oi2r')
        text = nested_div.text
        extracted_text_list.append(text)
    return '\n\n'.join(extracted_text_list)

def write_to_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)
    print(f"Data has been written to {filename} file.")

def generate_address_and_category(tweet):
    # Generate address
    address = model.generate_content(f"I have a sentence - {tweet}. Extract location name along with apartment name, locality if present using google maps. Give me only the location name. Nothing else. No other text.")

    # Extract location name from address
    location_name = address.text.split('in ')[-1].split(',')[0].strip()

    # Generate category
    category = model.generate_content(f"I have a sentence- {tweet}. Now use the sentence and categorize it into one of the categories- Scarcity, Drainage, Flooding, Leakage, Other. Give me only the category. Nothing else. No other text.")

    return location_name, category.text.split(':')[-1].strip()

def main():
    driver = initialize_driver()
    driver.get('https://twitter.com/login')

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    email_input.send_keys("Prad40790835339")

    next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
)
    next_button.click()

    


    # Wait for the password input element to be present
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )

    # Read the password from the file
    with open("pass.txt", "r") as file:
        password = file.read().strip()

    # Input the password
    password_input.send_keys(password)


    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]'))
    )

    # Click the button
    button.click()




    search_text = "#hydraforbengaluru"
    extracted_text = extract_tweets(driver, search_text)
    write_to_file("extracted_text.txt", extracted_text)

    tweets = extracted_text.split('\n\n')
    tweet_desc_list = [tweet.split('\n')[4] for tweet in tweets if len(tweet.split('\n')) >= 5]
    tweet_desc_text = '\n'.join(tweet_desc_list)
    write_to_file("tweet_desc.txt", tweet_desc_text)

    usernames_text = '\n'.join(tweet.split('\n')[0] for tweet in tweets if tweet.split('\n'))
    write_to_file("username.txt", usernames_text)


    # Process each tweet
    with open("tweet_desc.txt", "r") as file:
        tweets = file.readlines()

    with open("username.txt", "r") as user_file:
        usernames = user_file.readlines()


    
    for tweet, username in zip(tweets, usernames):
        tweet = tweet.strip()
        username = username.strip() 
        if tweet:
            location_name, category = generate_address_and_category(tweet)
            location=geolocator.geocode(location_name)

            # Check for duplicates
            existing_tweet = mongo.db.users.find_one({"description": tweet})
            if existing_tweet:
                print(f"Duplicate tweet found: {tweet}")
                continue  # Skip insertion if the tweet already exists

            # Store data in MongoDB
            tweet_data = {
                "username":username,
                "password":"Sana",
                "description": tweet,
                "location": location_name,
                "category": category,
                "latitude":location.latitude,
                "longitude":location.longitude
            }
            
            # Insert data into MongoDB
            mongo.db.users.insert_one(tweet_data)

    driver.quit()  # Close the WebDriver instance
    return redirect(url_for('admin2'))



if __name__ == "_main_":
    main()
