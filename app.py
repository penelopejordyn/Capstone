from flask import Flask, jsonify, session, flash
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from models import db, user, connect_db
from flask_debugtoolbar import DebugToolbarExtension
from secret import Authorization
from forms import RegisterForm, LoginForm
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
    while len(all_businesses) < 500:  # Keep making requests until we have 500 businesses
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
  
@app.route('/register', methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        nuser = user.register(name, pwd)
        db.session.add(nuser)
        db.session.commit()

        session["user_id"] = user.id

        # on successful login, redirect to secret page
        return redirect("/")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        nuser = user.authenticate(name, pwd)

        if user:
            session["user_id"] = user.id  # keep logged in
            return redirect("/secret")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)
# end-login


@app.route("/secret")
def secret():
    """Example hidden page for logged-in users only."""

    if "user_id" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

        # alternatively, can return HTTP Unauthorized status:
        #
        # from werkzeug.exceptions import Unauthorized
        # raise Unauthorized()

    else:
        return render_template("secret.html")


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("user_id")

    return redirect("/")
