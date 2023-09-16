#-------------------All Imports---------------------------#


from flask import Flask,jsonify,render_template,request,redirect, url_for
from models import *  #importing models from models.py
import pandas as pd   #to make graph   
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import os 
import io  


# ------------connections and initialisations--------------#


app=Flask(__name__)  #app object

#connection of flask to sqlite3
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///grocery_db.sqlite3" #name of database

db.init_app(app)  #db=SQLAlchemy(app)

app.app_context().push()


# ------------------controllers------------------------


# choose whether login as user or 
@app.route("/") #base url
def choice():
    return render_template("home_page.html")





# ------------------manager side code ------------------------

#MANAGER LOGIN
@app.route("/manager_login",methods=['GET','POST'])
def manager_login():
    if request.method=="POST":
        #taking these input from form
        manager_name=request.form.get("man_name") 
        password=request.form.get("manager_pass")

        #creating manager obj
        obj = Manager_data.query.filter_by(m_name=manager_name).first()

        # catching  error that no input is given in name and password 
        if obj is None:
            return ("<h1>Please fill the details correctly</h1>")   
         
        man_id=obj.m_id
        
        # checking pass mathing in db
        if obj.m_pass==password:
            return redirect(url_for('man_dashboard',man_id=man_id))
        else:
            return ("<h1>Manager credentials invalid</h1>")
    else:
        return render_template("manager_login.html")
    



# MANAGER DASHBOARD
@app.route("/m_dash/<int:man_id>")
def man_dashboard(man_id):
    
    man_obj=Manager_data.query.filter_by(m_id=man_id).first()
    man_name=man_obj.m_name

    products_by_category = {}
    categories = Category_table.query.all()
    for category in categories:
        products_by_category[category.cat_name] = category.products
    return render_template('manager_dashboard.html', products_by_category=products_by_category,man_name=man_name,man_id=man_id)
    

# category addition by manager
@app.route("/add_category/<int:man_id>",methods=['GET','POST'])
def add_category(man_id):
    

    if request.method=="POST":
        cat_name_form=request.form.get("cat_name")
        to_add=Category_table(cat_name=cat_name_form)
        db.session.add(to_add)
        db.session.commit()
        return redirect(url_for('man_dashboard',man_id=man_id))
    else:
        man_obj=Manager_data.query.filter_by(m_id=man_id).first()
        man_name=man_obj.m_name
        return render_template("m_add_cat.html",man_name=man_name,man_id=man_id)





# ADD NEW PRODUCT IN CATEGORY
@app.route("/add_new_product/<int:man_id>",methods=['GET','POST'])
def add_product_category(man_id):
    
    man_obj=Manager_data.query.filter_by(m_id=man_id).first()
    man_name=man_obj.m_name
    uom_list=UOM.query.all()
    category_id_list=Category_table.query.all()

    if request.method=="POST":
        category_id_form=request.form.get("cat_id")
        p_name_form=request.form.get("p_name")
        unit_form=request.form.get("unit")
        rate_form=request.form.get("rate")
        quantity_form=request.form.get("quantity")
        expiry_form = request.form.get("expiry")
       
        to_add=Products_table(category_id=category_id_form,product_name=p_name_form,uom_name= unit_form,
                              rate=rate_form, quantity=quantity_form,expiry_date=expiry_form)
        db.session.add(to_add)
        db.session.commit()
        return redirect(url_for('man_dashboard',man_id=man_id))
    else:
        return render_template("m_add_product_in_cat.html",uom_list=uom_list,category_id_list=category_id_list,man_id=man_id,man_name=man_name)



# feature to remove category from db
@app.route('/delete_category/<int:man_id>', methods=['GET','POST'])
def delete_category(man_id):
    man_obj=Manager_data.query.filter_by(m_id=man_id).first()
    man_name=man_obj.m_name
    
    category_id_list=Category_table.query.all()
    if request.method=="POST":
        category_id_form=request.form.get("cat_id")
        # Delete the corresponding product
        to_delete=Products_table.query.filter(Products_table.category_id==category_id_form).delete()
        db.session.commit()
        # Delete the category
        del_cat=Category_table.query.filter(Category_table.cat_id==category_id_form).delete()
        db.session.commit()
        return redirect(url_for('man_dashboard',man_id=man_id))

    else:
        return render_template("m_delete_cat.html",category_id_list=category_id_list,
                               man_id=man_id,man_name=man_name)



# RENAME SECTION 
@app.route('/rename_category/<int:man_id>', methods=['GET','POST'])
def rename_category(man_id):
    man_obj=Manager_data.query.filter_by(m_id=man_id).first()
    man_name=man_obj.m_name



    category_id_list=Category_table.query.all()
    if request.method=="POST":
        category_id_form=request.form.get("cat_id")
        new_name_form=request.form.get("new_cat_name")
        cat_to_rename = Category_table.query.get(category_id_form)
        cat_to_rename.cat_name=new_name_form
        db.session.commit()
        return redirect(url_for('man_dashboard',man_id=man_id))

    else:
        return render_template("m_rename_cat.html",category_id_list=category_id_list,
                               man_name=man_name,man_id=man_id)





# EDIT PRODUCT 
@app.route('/edit_product/<int:man_id>/<int:product_id>', methods=['GET', 'POST'])
def edit_product(man_id,product_id):
    man_obj=Manager_data.query.filter_by(m_id=man_id).first()
    man_name=man_obj.m_name
    product = Products_table.query.get(product_id)
    if request.method == 'POST':
        new_name=request.form.get("new_name")
        new_rate= float(request.form.get("new_rate"))
        new_quantitiy=request.form.get("new_quantity")
        product.product_name=new_name
        product.rate=new_rate
        product.quantitiy =new_quantitiy
        db.session.commit()
        return redirect(url_for('man_dashboard',man_id=man_id))

    return render_template('edit_product.html', product=product,man_id=man_id,man_name=man_name)




# Remove a product by ID
@app.route('/remove_product/<int:man_id>/<int:product_id>')
def remove_product(man_id,product_id):
    
    # remove product from the database
    product = Products_table.query.get(product_id)
    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('man_dashboard',man_id=man_id))






# ---------------------------------------------------------------
# USER SIDE LOGIC


# user login
@app.route("/user_login",methods=['GET','POST'])
def user_login():
    if request.method=="POST":
        uname_form=request.form.get("username")
        upass_form=request.form.get("pass")
        user_obj = User_data.query.filter_by(u_name=uname_form).first()
        if user_obj is None:
            return ("<h1>New User deteted please signup first</h1>")
        user_id=user_obj.u_id
        if user_obj.u_pass==upass_form:
            return redirect(url_for('user_dashboard', user_id=user_id))
        else:
            return ("<h1>User credential invalid</h1>")
    else:
        return render_template("user_login.html")




# user signup
@app.route("/user_signup",methods=['GET','POST'])
def add_user():
    if request.method=="POST":
        uname_form=request.form.get("username")
        upass_form=request.form.get("pass")
        to_add=User_data(u_name=uname_form,u_pass=upass_form)
        db.session.add(to_add)
        db.session.commit()
        return redirect('/user_login')
    
    else:
        return render_template("user_signup.html")






# USER DASHBOARD
@app.route('/user_dashboard/<int:user_id>')
# @login_required
def user_dashboard(user_id):
    products_by_category = {}
    categories = Category_table.query.all()
    user_obj = User_data.query.filter_by(u_id=user_id).first()
    user_name=user_obj.u_name
    for category in categories:
        products_by_category[category.cat_name] = category.products



    return render_template('user_dashboard.html', products_by_category=products_by_category,user_name=user_name,
                           user_id=user_id)




@app.route('/products/search/<int:user_id>', methods=['GET'])
def search_products(user_id):
    user_obj = User_data.query.filter_by(u_id=user_id).first()
    user_name=user_obj.u_name

    search_query = request.args.get('q', '')
    
    if not search_query:
        return jsonify(error='Search query is empty.')

    # Perform the search by using the search_query to filter the products
    products = Products_table.query.filter(Products_table.product_name.ilike(f'%{search_query}%')).all()

    return render_template('search_results.html', products=products,user_id=user_id,user_name=user_name)




@app.route('/products/category/<int:user_id>', methods=['GET'])
def search_products_by_category(user_id):
    user_obj = User_data.query.filter_by(u_id=user_id).first()
    user_name=user_obj.u_name


    category_name = request.args.get('category_name', None)

    if category_name:
        # Find the category by name
        category = Category_table.query.filter(Category_table.cat_name.ilike(f'%{category_name}%')).first()

        if category:
            products = Products_table.query.filter(Products_table.category_id == category.cat_id)
        else:
            products = []

    return render_template('search_cat.html', products=products,user_id=user_id,user_name=user_name)





@app.route('/logout')
# @login_required
def logout():
    return redirect("/")






# add product to cart
@app.route('/add_to_cart/<int:user_id>/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(user_id,product_id):
    user_obj = User_data.query.filter_by(u_id=user_id).first()
    user_name=user_obj.u_name
    obj=Products_table.query.filter_by(product_id=product_id).first()
    product_name=obj.product_name
    quan=obj.quantity
    rate=obj.rate
    category=obj.category_id
    expiry=obj.expiry_date
    
    if request.method=="POST":
        buy_quantity=request.form.get("buy_quantity")
        # subtract quantity from products table
        obj.quantity=(int)(obj.quantity)-(int)(buy_quantity)
        price=(float)(rate)*(float)(buy_quantity)

        

        # adding details in order_details table
        to_add=Order_details(product_id=product_id,product_name=product_name,
                             category_id=category,rate=rate,
                             quantity=buy_quantity,price=price)
       
       
        db.session.add(to_add)
        db.session.commit()
        return redirect(url_for('user_dashboard',user_id=user_id))

    else:
        if quan == 0:
            return ("Sorry the product is out of stock")

        return render_template("product_buy_info.html",product_name=product_name,
                               product_id=product_id,quan=quan,
                               rate=rate,category=category,expiry=expiry,
                               user_name=user_name,user_id=user_id)


    

# Cart
@app.route('/cart/<int:user_id>')
# @login_required
def user_cart(user_id):
    # user info
    user_obj = User_data.query.filter_by(u_id=user_id).first()
    user_name=user_obj.u_name


    user_orders = Order_details.query.all()
    grand_total = sum(order.price for order in user_orders)

    return render_template('user_cart.html', user_orders=user_orders,user_id=user_id,user_name=user_name,grand_total=grand_total)

                           


@app.route('/Thanks_For_Shopping/<int:user_id>/<float:grand_total>')
def thanks(user_id,grand_total):


    # add the bill details in orders
    to_add=All_Orders(customer_id=user_id,grand_total=grand_total)
    db.session.add(to_add)
    db.session.commit()


   # adding data in summary table  
    bills = Order_details.query.all()

    for bill in bills:
        product_id = bill.product_id
        category_id = bill.category_id
        quantity = bill.quantity

        summary_entry = Summary.query.filter_by(product_id=product_id).first()

        if summary_entry:
            # If Summary entry exists, update the quantity
            summary_entry.quantity += quantity
        else:
            # If Summary entry does not exist, create a new entry
            summary_entry = Summary(product_id=product_id, category_id=category_id, quantity=quantity)
            db.session.add(summary_entry)

        

    db.session.commit()

    # deleting the data from order_detail table
    db.session.query(Order_details).delete()
    db.session.commit()
    return "Thank you for shpping with DMart. Do Visit Again !"









# Graph for manager functionality
@app.route('/summary', methods=['GET'])
def summary():
    products=Products_table.query.all()
    summary_entries = Summary.query.all()

    data = {
        'product_id': [],
        'quantity': []
    }

    for entry in summary_entries:
        data['product_id'].append(entry.product_id)
        data['quantity'].append(entry.quantity)

    df = pd.DataFrame(data)

    plt.bar(df['product_id'], df['quantity'])
    plt.xlabel('Product ID')
    plt.ylabel('Quantity')
    plt.title('Product ID vs. Quantity')
    plt.xticks(df['product_id'])

    graph_filename = 'product_quantity_graph.png'
    graph_path = os.path.join('static', graph_filename)
    plt.savefig(graph_path)
      

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plt.clf()


    buffer_base64 = base64.b64encode(buffer.getvalue()).decode()

    plt.close()
    return render_template('summary.html', graph=buffer_base64, summary_entries=summary_entries,products=products)




@app.route('/product_and_categorywise_summary', methods=['GET'])
def display_summary():
    return render_template("graphs_button.html")





# Making category graph
@app.route('/summary_cat', methods=['GET'])
def summary_cat():
    categories=Category_table.query.all()
    summary_entries = Summary.query.all()

    # Calculate total quantity per category_id
    category_totals = {}
    for entry in summary_entries:
        category_id = entry.category_id
        quantity = entry.quantity
        if category_id in category_totals:
            category_totals[category_id] += quantity
        else:
            category_totals[category_id] = quantity

    # Sort the category_ids and total quantities for plotting
    sorted_categories = sorted(category_totals.keys())
    total_quantities = [category_totals[category_id] for category_id in sorted_categories]

    plt.bar(sorted_categories, total_quantities)
    plt.xlabel('Category ID')
    plt.ylabel('Total Quantity')
    plt.title('Category ID vs. Total Quantity')
    plt.xticks(sorted_categories)

   
    # Save the plot as a byte buffer instead of a file
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Clear the plot
    plt.clf()

    # Convert the buffer to a base64-encoded string
    buffer_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Close the plot
    plt.close()

    return render_template('sum_cat.html', graph=buffer_base64, summary_entries=summary_entries,categories=categories)







#--------------running the app -----------------------------    

app.run(debug=True)