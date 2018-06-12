# item-catalog-project
Udacity project.  Item catalog website with db CRUD and oauth  Google login.

## Setup:


* Install (if necessary): 
  * [Flask](http://flask.pocoo.org/docs/0.11/installation/)
  * [SQLAlchemy](http://docs.sqlalchemy.org/en/latest/intro.html)

## Testing:

1. Open terminal to folder location of cloned repo.
2. Run database_setup_catalog.py: `python database_setup_catalog.py`
3. Run database_management.py: `python database_management.py`
4. Run catalog.py to start web app: `python catalog.py`
5. Open browser to [http://localhost:5010/category/](http://localhost:5010/category/)


## Expected functionality:
* Users can login / logout with Google Plus sign in.
* Users cannot Get or Post New, Edit, or Delete pages without being signed in.
* Users cannot Get or Post Edit or Delete place without being the original creators of the place.
* Logged in users can create new place.
* Can access JSON data at the following pages:
  * Category list: [http://localhost:5000/category/JSON](http://localhost:5010/category/JSON)
  * Specific category's place: [http://localhost:5010/category/\<category_id\>/JSON](http://localhost:5000/category/1/JSON)
  * Specific place information: [http://localhost:5010/category/\<category_id\>/\<item_id\>/JSON](http://localhost:5000/category/1/1/JSON)
