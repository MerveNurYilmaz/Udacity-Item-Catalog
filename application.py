from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session as flask_session
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, ProductItem, ProductCategory, User
from requests_oauthlib import OAuth2Session
from config import config_dict
import os
# to let http
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__, static_url_path='', static_folder='static',
            template_folder='templates')
app.secret_key = config_dict['secret_key']

client_id = config_dict['client_id']
client_secret = config_dict['client_secret']
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'

engine = create_engine('sqlite:///shoppingcatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


@app.route('/login')
def login():
    """
    Login via github
    """
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)
    flask_session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/logout')
def logout():
    flask_session.pop('user_id', None)
    flask_session.pop('user_token', None)
    flask_session.pop('oauth_state', None)
    return redirect(url_for('catalog'))


@app.route('/github-callback', methods=['GET'])
def callback():
    github = OAuth2Session(client_id, state=flask_session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)
    if token is None:
        return redirect('catalog')

    login_name = get_profile_detail(token)['login']
    # check if the user is already logged in
    user = db_session.query(User).\
        filter_by(access_token=token['access_token']).first()
    if user is None:
        # check if the user logged in before
        user = db_session.query(User).filter_by(login_name=login_name).first()
        if user is None:
            user = User(access_token=token['access_token'])
            db_session.add(user)
    user.access_token = token['access_token']
    user.login_name = login_name
    db_session.commit()
    flask_session['user_id'] = user.id
    flask_session['user_token'] = token['access_token']
    return redirect(url_for('catalog'))


def get_profile_detail(token):
    """
    Get user information from github api
    """
    github = OAuth2Session(client_id, token=token)
    return github.get('https://api.github.com/user').json()


def is_user_authenticated():
    """
    Return if user is authenticated by github
    """
    if 'user_id' in flask_session.keys() and \
            'user_token' in flask_session.keys():
        user = db_session.query(User).\
            filter_by(id=flask_session['user_id']).first()
        if user:
            return user.access_token == flask_session['user_token']
    return False


def is_user_authorized(element_type, element_id):
    """
    Return if user is authorized by checking if the user
    created the given element
    Element could either be a category or category item
    """
    if element_type == 'category':
        user_id = db_session.query(ProductCategory).\
            filter_by(id=element_id).one().user_id
    else:
        user_id = db_session.query(ProductItem).\
            filter_by(id=element_id).one().user_id
    if user_id:
        return 'user_id' in flask_session.keys() and \
               user_id == flask_session['user_id']
    else:
        return False


@app.route('/catalog_json')
def catalog_json():
    """
    API of catalog data
    """
    categories = db_session.query(ProductCategory).all()
    return jsonify(categories=[category.serialize for category in categories])


@app.route('/items_json')
def items_json():
    """
    API of item data
    """
    items = db_session.query(ProductItem).all()
    return jsonify(items=[item.serialize for item in items])


@app.route('/')
@app.route('/catalog')
def catalog():
    """
    Renders main page
    """
    categories = db_session.query(ProductCategory).all()
    latest_items = db_session.query(ProductItem).\
        join(ProductItem.product_category).order_by(desc(ProductItem.id))[0:5]
    is_authenticated = is_user_authenticated()
    return render_template('catalog.html', categories=categories,
                           latest_items=latest_items,
                           is_authenticated=is_authenticated)


@app.route('/catalog/category/<int:category_id>/items')
def items(category_id):
    """
    Render items page that shows items belongs to the given category
    """
    categories = db_session.query(ProductCategory).all()
    category_items = db_session.query(ProductItem).\
        filter_by(category_id=category_id).all()
    item_count = len(category_items)
    category_title = db_session.query(ProductCategory).\
        filter_by(id=category_id).one()
    category_info = {'id': category_id, 'title': category_title.title,
                     'item_count': item_count}
    is_authenticated = is_user_authenticated()
    is_authorized = is_user_authorized(element_type='category',
                                       element_id=category_id)
    return render_template('items.html', categories=categories,
                           category_info=category_info,
                           category_items=category_items,
                           is_authenticated=is_authenticated,
                           is_authorized=is_authorized)


@app.route('/catalog/detail/<element_type>/<int:element_id>')
def detail(element_type, element_id):
    """
    Render detail page with either a category element or category item
    """
    if element_type == 'category':
        element = db_session.query(ProductCategory)\
            .filter_by(id=element_id).one()
    else:
        element = db_session.query(ProductItem).filter_by(id=element_id).one()
    is_authenticated = is_user_authenticated()
    # edit and delete elements are only visible if user is authorized
    is_authorized = is_user_authorized(element_type=element_type,
                                       element_id=element_id)
    return render_template('detail.html', element_type=element_type,
                           element=element, is_authenticated=is_authenticated,
                           is_authorized=is_authorized)


@app.route('/catalog/add/<element_type>',
           defaults={'selected_category_id': None},
           methods=['GET', 'POST'])
@app.route('/catalog/add/<element_type>/<int:selected_category_id>',
           methods=['GET', 'POST'])
def add(element_type, selected_category_id):
    """
    Render add page with get method or add an element
    in the database with post method
    Element to add to database could be either category or item of a category
    """
    # Redirect users who aren't logged in or aren't the owner of the element,
    # to main page
    # This control is added to prevent unauthorized access by url
    # If element type is item, check if the user is the owner of the
    # category that item belongs to
    if not is_user_authenticated() or \
            (element_type == 'item' and
             not is_user_authorized('category', selected_category_id)):
        return redirect(url_for('catalog'))
    # users may add items only to categories which they created
    categories = db_session.query(ProductCategory).\
        filter_by(user_id=flask_session['user_id']).all()
    if request.method == 'POST':
        if element_type == 'item':
            category = db_session.query(ProductCategory).\
                filter_by(id=selected_category_id).one()
            new_item = ProductItem(title=request.form['title'],
                                   description=request.form['description'],
                                   product_category=category,
                                   user_id=flask_session['user_id'])
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('items', category_id=selected_category_id))
        else:
            category_description = request.form['description']
            new_category = ProductCategory(title=request.form['title'],
                                           description=category_description,
                                           user_id=flask_session['user_id'])
            db_session.add(new_category)
            db_session.commit()
            return redirect(url_for('catalog'))
    else:
        return render_template('add.html', categories=categories,
                               selected_category_id=selected_category_id,
                               element_type=element_type)


@app.route('/catalog/edit/<element_type>/<int:element_id>',
           methods=['GET', 'POST'])
def edit(element_type, element_id):
    """
    Render edit page with get method or alter the given element
    in the database with post method
    Given element could be either category or item of a category
    """
    # Redirect users who aren't logged in or aren't the owner of the element,
    # to main page
    # This control is added to prevent unauthorized access by url
    if not is_user_authenticated() or \
            not is_user_authorized(element_type, element_id):
        return redirect(url_for('catalog'))
    if element_type == 'category':
        element_to_edit = db_session.query(ProductCategory).\
            filter_by(id=element_id).one()
    else:
        element_to_edit = db_session.query(ProductItem).\
            filter_by(id=element_id).one()
    # users may change the category of items only to the
    # categories which they created
    categories = db_session.query(ProductCategory).\
        filter_by(user_id=flask_session['user_id']).all()
    if request.method == 'POST':
        if request.form['title']:
            element_to_edit.title = request.form['title']
        if request.form['description']:
            element_to_edit.description = request.form['description']
        if element_type == 'item' and request.form['category']:
            element_to_edit.category_id = request.form['category']
        db_session.add(element_to_edit)
        db_session.commit()
        return redirect(url_for('detail', element_type=element_type,
                                element_id=element_to_edit.id))
    else:
        return render_template('edit.html', element_type=element_type,
                               element=element_to_edit, categories=categories)


@app.route('/catalog/delete/<element_type>/<int:element_id>',
           methods=['GET', 'POST'])
def delete(element_type, element_id):
    """
    Render delete page with get method or delete the given element
    from database with post method
    Given element could be either category or item of a category
    """
    # Redirect users who aren't logged in or aren't the owner of the element,
    # to main page
    # This control is added to prevent unauthorized access by url
    if not is_user_authenticated() or \
            not is_user_authorized(element_type, element_id):
        return redirect(url_for('catalog'))
    if request.method == 'POST':
        if element_type == 'category':
            items_to_delete = db_session.query(ProductItem).\
                filter_by(category_id=element_id).all()
            for item in items_to_delete:
                db_session.delete(item)
            category_to_delete = db_session.query(ProductCategory).\
                filter_by(id=element_id).one()
            db_session.delete(category_to_delete)
            db_session.commit()
            return redirect(url_for('catalog'))
        else:
            item_to_delete = db_session.query(ProductItem).\
                filter_by(id=element_id).one()
            category_id = item_to_delete.category_id
            db_session.delete(item_to_delete)
            db_session.commit()
            return redirect(url_for('items', category_id=category_id))
    else:
        return render_template('delete.html')


if __name__ == "__main__":
    app.run(debug=True)
