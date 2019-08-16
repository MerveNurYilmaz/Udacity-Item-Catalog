from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import ProductCategory, Base, ProductItem

engine = create_engine('sqlite:///shoppingcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# add category 1 items
category_description1 = "For those who likes to wear layers on layers"
category1 = ProductCategory(title="Outerwear",
                            description=category_description1)

db_session.add(category1)
db_session.commit()

item_description1 = "From denims to biker jackets, whole lot " \
                    "of options to choose the one for your style"
productItem1 = ProductItem(title="Jackets", description=item_description1,
                           product_category=category1)

db_session.add(productItem1)
db_session.commit()

item_description2 = "Coats to warm you up on the coldest days"
productItem2 = ProductItem(title="Coats", description=item_description2,
                           product_category=category1)

db_session.add(productItem2)
db_session.commit()

item_description3 = "Stylish blazers to complete your outfits"
productItem3 = ProductItem(title="Blazers", description=item_description3,
                           product_category=category1)

db_session.add(productItem3)
db_session.commit()


# add category 2 items
category_description2 = "Unique designs for your taste"
category2 = ProductCategory(title="Clothes", description=category_description2)

db_session.add(category2)
db_session.commit()

item_description1 = "No wardrobe is complete without a beautiful dress"
productItem1 = ProductItem(title="Dresses", description=item_description1,
                           product_category=category2)

db_session.add(productItem1)
db_session.commit()

item_description2 = "Whether for an office look or " \
                    "a more casual one, many shirts for any style"
productItem2 = ProductItem(title="Shirts", description=item_description2,
                           product_category=category2)

db_session.add(productItem2)
db_session.commit()

item_description3 = "Blouses can make any outfit more " \
                    "stylish and extraordinary"
productItem3 = ProductItem(title="Blouses", description=item_description3,
                           product_category=category2)

db_session.add(productItem3)
db_session.commit()


# add category 3 items
category_description3 = "Yes we are obsessed with shoes"
category3 = ProductCategory(title="Shoes", description=category_description3)

db_session.add(category3)
db_session.commit()

item_description1 = "Elegant models designed to make you feel outstanding"
productItem1 = ProductItem(title="High Heels", description=item_description1,
                           product_category=category3)

db_session.add(productItem1)
db_session.commit()

item_description2 = "Most comfortable sneakers for everyday use"
productItem2 = ProductItem(title="Sneakers", description=item_description2,
                           product_category=category3)

db_session.add(productItem2)
db_session.commit()

item_description3 = "When the weather gets cold, all other " \
                    "types turns into boots"
productItem3 = ProductItem(title="Boots", description=item_description3,
                           product_category=category3)

db_session.add(productItem3)
db_session.commit()

# add category 4 items
category_description4 = "Bags are what differs your style from all others"
category4 = ProductCategory(title="Bags", description=category_description4)

db_session.add(category4)
db_session.commit()

item_description1 = "Because why would you have to carry your bag on your hand"
productItem1 = ProductItem(title="Crossbody Bags",
                           description=item_description1,
                           product_category=category4)

db_session.add(productItem1)
db_session.commit()

item_description2 = "Large models for when you feel like you'll need " \
                    "everything you own when you go outside"
productItem2 = ProductItem(title="Shoppers", description=item_description2,
                           product_category=category4)

db_session.add(productItem2)
db_session.commit()

item_description3 = "How about a trip for weekend"
productItem3 = ProductItem(title="Backpacks", description=item_description3,
                           product_category=category4)

db_session.add(productItem3)
db_session.commit()
