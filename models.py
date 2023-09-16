# all files related to sql alchemy (all models ) are here
from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy() #db object


class User_data(db.Model):
    u_id=db.Column(db.Integer,primary_key=True)
    u_name=db.Column(db.String(30),nullable=False)
    u_pass=db.Column(db.String(30),nullable=False)
    
class Manager_data(db.Model):
    m_id=db.Column(db.Integer,primary_key=True)
    m_name=db.Column(db.String(30),nullable=False)
    m_pass=db.Column(db.String(30),nullable=False)


class Category_table(db.Model):
    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name = db.Column(db.String, nullable=False)


class Products_table(db.Model):
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id=db.Column(db.Integer, db.ForeignKey("category_table.cat_id") ,nullable=False)
    product_name= db.Column(db.String(30), nullable=False)
    uom_name= db.Column(db.String, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.String(7), nullable=True)
    category = db.relationship('Category_table', backref='products')
    

class UOM(db.Model):
    uom_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uom_name = db.Column(db.String, nullable=False)


# all orders major details
class All_Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    grand_total=db.Column(db.Float, nullable=False)
    
    
# only one order details 
class Order_details(db.Model):
    index=db.Column(db.Integer,primary_key=True,autoincrement=True)
    category_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name= db.Column(db.String(30), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    

class Summary(db.Model):
    index=db.Column(db.Integer,primary_key=True,autoincrement=True)
    product_id = db.Column(db.Integer,nullable=False )
    category_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
