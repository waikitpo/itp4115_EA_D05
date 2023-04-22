from app import db, app
from app.models import Location, Category


app_context = app.app_context()
app_context.push()


def insert_default_categories():
    categories = ['Information Technology','Engineering', 'Education','Management','Finance','Healthcare','Transportation']
    for category_name in categories:
        category = Category.query.filter_by(category=category_name).first()
        if not category:
            category = Category(category=category_name)
            db.session.add(category)
    db.session.commit()

def insert_default_locations():
    locations = ['Hong Kong Island', 'Kowloon Peninsula', 'New Territory', 'Oversea']
    for location_name in locations:
        location = Location.query.filter_by(location=location_name).first()
        if not location:
            location = Location(location=location_name)
            db.session.add(location)
    db.session.commit()


insert_default_categories()
insert_default_locations()