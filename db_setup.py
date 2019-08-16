from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login_name = Column(String(200))
    access_token = Column(String(200))


class ProductCategory(Base):

    __tablename__ = 'product_category'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250))
    items = relationship("ProductItem")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'id': self.id,
            'category_title': self.title,
            'description': self.description,
            'items': [item.serialize for item in self.items]
        }


class ProductItem(Base):

    __tablename__ = 'product_item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('product_category.id'))
    product_category = relationship(ProductCategory, back_populates='items')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {

            'id': self.id,
            'product_title': self.title,
            'description': self.description,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///shoppingcatalog.db')
Base.metadata.create_all(engine)
