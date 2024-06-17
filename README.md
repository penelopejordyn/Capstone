# Capstone
FLASK_DEBUG=1 flask run

def add(username, email, password):
    with app.app_context():
        steven = user(username=username, email=email, password=password)
        db.session.add(steven)
        db.session.commit()