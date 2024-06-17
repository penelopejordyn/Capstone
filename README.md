

        README

## Project Title: Local Business Finder

This is a Flask web application that helps users find local businesses in their area. It uses the Yelp API to fetch data about businesses and categorizes them for easy browsing. Users can also search for specific businesses. The application also includes user authentication and allows users to bookmark their favorite businesses.

## Features

1. **Home Page**: Displays a list of businesses in the user's location, categorized by type. The location is determined based on the user's IP address.

2. **Search Results Page**: Allows users to search for businesses in a specific location.

3. **User Registration**: New users can register by providing a username and password.

4. **User Login**: Registered users can log in to access more features.

5. **Bookmarking**: Logged-in users can bookmark their favorite businesses. The bookmarked businesses can be viewed on a separate page.

6. **Logout**: Logged-in users can log out of their account.

## Installation

1. Clone the repository to your local machine.
2. Install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the database:

    ```bash
    createdb user
    ```

4. Run the application:

    ```bash
    FLASK_DEBUG=1 flask run
    ```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`.
2. Use the application to browse local businesses or search for specific ones.
3. Register a new account or log in to bookmark businesses.


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)