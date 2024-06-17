from flask import Flask, jsonify, session, flash, url_for
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from models import db, User, connect_db, Bookmark
from flask_debugtoolbar import DebugToolbarExtension
from secret import Authorization
from forms import RegisterForm, LoginForm
import requests
import random
from werkzeug.security import generate_password_hash, check_password_hash

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
    """
    Renders the home page of the web application.

    Retrieves the user's IP address, determines the location based on the IP address,
    and fetches a list of businesses in that location. The businesses are categorized
    and a random selection of categories is chosen. For each selected category, a list
    of businesses belonging to that category is created. The information of each business
    includes its ID, name, city, zip code, state, and image URL.

    Returns:
        A rendered template of the home page with the categorized businesses and the user's
        zip code.
    """
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
                    'id': business['id'],
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
    """
    Handle the search results page.

    This function is responsible for handling the '/Search_results' route. It retrieves the user's IP address,
    uses it to get the corresponding zip code, and performs a search based on the user's input. The search results
    are then rendered in the 'Search_results.html' template.

    Returns:
        The rendered 'Search_results.html' template with the search results, search parameters, and location.
    """
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
  
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission.

    This function is responsible for rendering the registration form and handling the form submission.
    It creates an instance of the RegisterForm class, validates the form data, and if the form is valid,
    it registers the user by creating a new User object and adding it to the database. It also sets the
    user_id in the session and redirects the user to the secret page upon successful registration.

    Returns:
        If the form submission is successful, it redirects the user to the secret page.
        If the form submission fails, it renders the register.html template with the form.

    """
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        user = User.register(name, pwd)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id

        # on successful login, redirect to secret page
        return redirect("/secret")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login.

    This function is responsible for rendering the login form or handling the login process.
    If the form is submitted and valid, it will attempt to authenticate the user using the provided
    username and password. If the authentication is successful, the user will be redirected to the
    "/secret" page. Otherwise, an error message will be displayed on the login form.

    Returns:
        If the user is authenticated, it redirects to "/secret" page.
        If the user is not authenticated, it renders the login form with an error message.

    """

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["user_id"] = user.id  # keep logged in
            return redirect("/secret")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)
# end-login

@app.route('/bookmark/<restaurant_id>', methods=['POST'])
def bookmark(restaurant_id):
    """
    Bookmark a restaurant for the logged-in user.

    Args:
        restaurant_id (str): The ID of the restaurant to be bookmarked.

    Returns:
        redirect: Redirects the user to the login page if not logged in.
                  Redirects the user to the secret page after bookmarking the restaurant.

    Raises:
        None
    """
    if 'user_id' not in session:
        flash('You need to be logged in to bookmark a restaurant.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    restaurant_id = request.form.get('restaurant_id')
    restaurant_name = request.form.get('restaurant_name')
    restaurant_image = request.form.get('restaurant_image')
    restaurant_address = request.form.get('restaurant_address')
    restaurant_phone = request.form.get('restaurant_phone')

    new_bookmark = Bookmark(user_id=user_id, restaurant_id=restaurant_id, restaurant_name=restaurant_name,
                            restaurant_image=restaurant_image, restaurant_address=restaurant_address,
                            restaurant_phone=restaurant_phone)

    db.session.add(new_bookmark)
    db.session.commit()

    flash('Restaurant bookmarked successfully!', 'success')
    return redirect(url_for('secret'))




@app.route('/secret')
def secret():
    if 'user_id' not in session:
        flash('You need to be logged in to view bookmarks.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    return render_template('secret.html', bookmarks=bookmarks)


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("user_id")

    return redirect("/")