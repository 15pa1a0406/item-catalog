from sqlalchemy.orm import sessionmaker
from database_setup_catalog import Base, User, Category, PlaceTitle, engine


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# User functions
def create_user(name, email, picture):
    new_user = User(
        name=name,
        email=email,
        picture=picture
        )
    session.add(new_user)
    session.commit()
    return new_user.id


def get_user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# def del_user(user_id):
#     user = session.query(User).filter_by(id=user_id).one()
#     session.delete(user)
#     session.commit()


# Category functions
def create_category(name):
    new_category = Category(name=name)
    session.add(new_category)
    session.commit()
    return new_category.id


def get_cat_id(name):
    cat = session.query(Category).filter_by(name=name).one()
    return cat.id


def get_places_in_category(category_name):
    places_list = session.query(PlaceTitle)
    join(PlaceTitle.category).filter_by(name=category_name)
    return places_list


# PlaceTitle functions
def create_place(name, description, category_id, user_id):
    new_place = PlaceTitle(
        name=name,
        description=description,
        category_id=category_id,
        user_id=user_id
        )
    session.add(new_place)
    session.commit()
    return new_place.id


# set up functions:

def add_users():
    user_list = [
        ['Meher', 'meherattuluri@gmail.com', 'http://picture_url.com']
    ]

    for user in user_list:
        create_user(user[0], user[1], user[2])


def fill_categories():
    cat_list = [
        'Beach',
        'Industries',
        'Temples',
        'Travelling',
    ]

    for cat in cat_list:
        create_category(cat)


def fill_places():

    cities_tuples = [
        (
            'RK Beach: Bay Of Bengal',
            'The Rama Krishna Beach, or RK Beach\
            commonly called, is one of the best\
            known beaches and tourist spots in Vizag,\
            attracting a large number of visitors.'\
            'Beach'
            ),
        (
            'Rushni Konda',\
            'Haritha Beach Resort, Visakahapatnam Located\
            on Bhimli Road, Rushikonda,\
            this beautiful beach resort has a presidential suite.',\
            'Beach'
            ),
        (
            'Steel Plant',\
            'Vizag Steel Plant is the only Indian shore-based\
            steel plant and is situated on 33000 acres\
            (13000 ha), and is poised to expand to\
            produce up to 20 MT in a single campus.',\
            'Industries'
            ),
        (
            'Ship Yard',
            'The shipyard is relatively compact at 46.2 hectares(0.462 km2)\
            It is equipped with the plasma cutting machines, steel processing\
            welding facilities, material handling equipment, cranes,\
            logistics and storage facilities.',\
            'Industries'
            ),
        (
            'Kailasa Giri',
            'As the search operations conducted for six days to\
            spot the leopard at Kailasgiri Hills yielded no result\
            the forest department authorities\
            reopened Kailasagiri Hills .',\
            'Temples'
            ),
        (
            'Simhachalam',
            'Simhachalam temple resembles a fortress from\
            outside with three outer courtyards and five\
            gateways. The architecture is a mixture of the\
            styles of the Orissan, Chalukyas and the Cholas..',\
            'Temples'
            ),
        (
            'Visakhapatnam airport',
            'In 1981, the airport commenced civilian operations\
            with one flight per day. The original runway was 6000\
            ft(1800m)long and a new 10007 ft(3050m)\
            long and 45 m(148ft) wide runway .',\
            'Travelling'
            ),
        (
            'Harbour',
            'Visakhapatnam Port has three harbours - the outer\
            harbour, inner harbour andthe fishing harbour.\
            The outer harbour has 6 berths capable of handling vessels\
            with a draft up to 17 meter.',\
            'Travelling'
            ),
    ]

    for tup in cities_tuples:
        create_place(
            tup[0],
            tup[1],
            get_cat_id(tup[2]),
            1
            )


if __name__ == '__main__':
    add_users()
    fill_categories()
    fill_places()
