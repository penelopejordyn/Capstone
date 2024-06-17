from flask import Flask, jsonify
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from models import db, user, connect_db
from flask_debugtoolbar import DebugToolbarExtension
from secret import Authorization
import requests
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True



with app.app_context():
    connect_db(app)
# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'secret'
url = "https://api.yelp.com/v3/businesses/search"
ipurl = "http://ip-api.com/json"

toolbar = DebugToolbarExtension(app)
headers = {
    "accept": "application/json",
    "Authorization": Authorization,

}
    


@app.route('/', methods=['GET', 'POST'])
def home_page():
    
    user_ip = request.remote_addr
    paramsip = {"query": user_ip}
    respip = requests.get(ipurl, params=paramsip)
    dataip = respip.json()
    zip_code = dataip['zip']
    
    location = zip_code
    
    
    
    all_businesses = []
    offset = 0
    while len(all_businesses) < 200:  # Keep making requests until we have 200 businesses
        params = {"location": location, "limit": 50, "offset": offset}
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        all_businesses.extend(data['businesses'])
        offset += 50
    
    
    all_categories = set()
    for business in data['businesses']:
        for category in business['categories']:
            all_categories.add(category['title'])
            
    selected_categories = random.sample(all_categories, 5)
    
   # Select businesses that belong to the selected categories
    category_businesses = {}
    for category in selected_categories:
        category_businesses[category] = []
        for business in all_businesses:
            if any(cat['title'] == category for cat in business['categories']):
                business_info = {
                    'name': business['name'],
                    'city': business['location']['city'],
                    'zip_code': business['location']['zip_code'],
                    'state': business['location']['state'],
                    'image_url': business['image_url']
                    # Add more business details here
                }
                category_businesses[category].append(business_info)
            if len(category_businesses[category]) >= 20:
                break  # We have enough businesses for this category
    
    return render_template('Home_page.html', category_businesses=category_businesses, zip_code=zip_code)

@app.route('/Search_results', methods=['GET', 'POST'])
def search_results():
    user_ip = request.remote_addr
    paramsip = {"query": user_ip}
    respip = requests.get(ipurl, params=paramsip)
    dataip = respip.json()
    zip_code = dataip['zip']
    location = zip_code
    searchparams = request.form.get('search')
    params = {
        "term":searchparams, 
        "limit": 50, 
        "location": request.form.get('location')}
    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    return render_template('Search_results.html',data=data, searchparams=searchparams,location=location)
  
   