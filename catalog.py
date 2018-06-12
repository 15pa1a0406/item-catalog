from flask import Flask, render_template
from flask import request, redirect
from flask import jsonify, url_for, flash
from flask import session as login_session
from functools import wraps
import random
import string

from sqlalchemy import asc, desc
from sqlalchemy.orm import sessionmaker

from database_setup_catalog import Base, User
from database_setup_catalog import Category, PlaceTitle, engine
import database_setup_catalog as db

import time

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 
                            'r').read())['web']['client_id']
APPLICATION_NAME = 'Item Catalog'


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('show_login'))
        return function(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/category')
def main_page():
    """Main page. Show place genres and most recently added Titles."""
    categories = db.get_all_categories()
    place = session.query(PlaceTitle).order_by(desc(PlaceTitle.id)).limit(10)

    return render_template(
        'latest_places.html',
        categories=categories,
        places=places
        )

# JSON APIs.
@app.route('/category/JSON')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(Categories=[cat.serialize for cat in categories])


@app.route('/category/<int:category_id>/JSON')
def category_places_json(category_id):
    place_list = db.get_places_in_category(category_id)
    category = db.get_cat(category_id)
    return jsonify(Category=category.name,
                   Places=[place.serialize for place in place_list])


@app.route('/category/<int:category_id>/<int:place_id>/JSON')
def place_json(category_id, place_id):
    place = db.get_place(place_id)
    return jsonify(Place=place.serialize)


@app.route('/category/<int:category_id>/')
def show_category(category_id):
    """Specific category page.  Shows all titles."""
    categories = db.get_all_categories()
    cat = db.get_cat(category_id)
    places = session.query(PlaceTitle).filter_by(category_id=cat.id)\
    .order_by(asc(PlaceTitle.name))
    return render_template(
        'category.html',
        categories=categories,
        category=cat,
        places=places
        )


@app.route('/category/<int:category_id>/<int:place_id>/')
def show_place(category_id, place_id):
    """Specific place page. Shows desc."""
    categories = db.get_all_categories()
    cat = db.get_cat(category_id)
    place = db.get_place(place_id)
    return render_template(
        'place.html',
        categories=categories,
        category=cat,
        place=place
        )


@app.route(
    '/category/new/',
    defaults={'category_id': None},
    methods=['GET', 'POST']
    )
@app.route(
    '/category/new/<int:category_id>/',
    methods=['GET', 'POST']
    )
@login_required
def new_place(category_id):
    """Add new place page.  Requires logged in status."""

    categories = db.get_all_categories()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        field_vals = {}

        user_id = login_session['user_id']

        if name and description and category != "None":
            print 'received inputs'
            flash('New place added!')
            cat_id = db.get_cat_id(category)
            new_place = db.create_place(
                name,
                description,
                cat_id,
                user_id
                )
            return redirect(url_for(
                'show_place',
                category_id=cat_id,
                place_id=new_place.id
                )
            )
        elif category == "None":
            flash('Must enter a category.')
        else:
            field_vals['default_cat'] = category
            flash('Invalid input! Must enter values.')

        field_vals['input_name'] = name
        field_vals['input_description'] = description
        return render_template('new_place.html',
                               categories=categories, **field_vals)
    else:
        if category_id:
            cat_name = db.get_cat(category_id).name
            return render_template('new_place.html',
                                   categories=categories,
                                   default_cat=cat_name)
        else:
            return render_template('new_place.html', categories=categories)


@app.route(
    '/category/<int:category_id>/<int:item_id>/edit/',
    methods=['GET', 'POST']
    )
@login_required
def edit_place(category_id, place_id):
    """Edit place page. User must have created the place to edit."""

    categories = db.get_all_categories()
    cat = db.get_cat(category_id)
    place = db.get_place(place_id)
    user_id = login_session['user_id']

    if place.user_id != user_id:
        return redirect(url_for('main_page'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']

        field_vals = {}

        if name and description:
            flash('place edited!')
            db.edit_place(place, name, description, db.get_cat_id(category))

            time.sleep(1)
            return redirect(url_for(
                'show_place',
                category_id=category_id,
                place_id=place_id
                )
            )
        else:
            field_vals['default_cat'] = category
            flash('Invalid input! Must enter values.')

        field_vals['input_name'] = name
        field_vals['input_description'] = description
        return render_template('new_place.html',
                               categories=categories,
                               **field_vals)
    else:
        return render_template(
            'edit_place.html',
            category_id=category_id,
            place_id=place_id,
            categories=categories,
            input_name=place.name,
            input_description=place.description,
            default_cat=cat.name
            )


@app.route(
    '/category/<int:category_id>/<int:place_id>/delete/',
    methods=['GET', 'POST']
    )
@login_required
def delete_place(category_id, place_id):
    """Delete place page.  User must have created place to delete."""

    cat = db.get_cat(category_id)
    place = db.get_place(place_id)

    user_id = login_session['user_id']

    if place.user_id != user_id:
        return redirect(url_for('main_page'))

    if request.method == 'POST':
        delete_confirmation = request.form['delete']

        if delete_confirmation == 'yes':
            db.delete_place(place)
            flash('place entry deleted.')
        return redirect(url_for('show_category', category_id=cat.id))
    else:
        return render_template(
            'delete_item.html',
            category=cat,
            place=place
            )


# Login functions and handling
@app.route('/')
@app.route('/login')
def show_login():
    """Login page"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    """Google Plus sign in."""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data  # one-time code from server

    try:
        # Upgrades auth code into credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token

    # Checking validity of access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}'\
        .format(token=access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    gplus_id = credentials.id_token['sub']

    # Verifies access_token is for intended user
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('Not matched.'), 401)
        response.heads['Content-Type'] = 'application/json'
        return response

    # Verifies access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('Not Matched.'), 401)
        print 'Token\'s client ID does not match app\'s.'
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(' connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {
        'access_token': credentials.access_token,
        'alt': 'json'
        }
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = db.get_user_id(login_session['email'])

    if user_id is None:
        user_id = db.create_user(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
     -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('You are logged in as {name}'.format(name=login_session['username']))
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Google logout.  Pairs with universal disconnect function."""
    access_token = login_session.get('access_token')
    print 'In gdisconnect, access token is {token}'.format(token=access_token)
    print 'User name is: '
    print login_session.get('username')

    if access_token is None:
        print 'Access token is None'
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = \
        'https://accounts.google.com/o/oauth2/revoke?token={token}'\
        .format(token=access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps('Failed.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Universal disconnect
@app.route('/disconnect')
def disconnect():
    """Disconnects either FB or G+ login"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['user_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']

        flash('You have been successfully logged out.')
    else:
        flash('You were not logged in.')

    return redirect(url_for('main_page'))




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5010)
