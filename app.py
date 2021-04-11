from flask import Flask, render_template, request, redirect, url_for, session 
from flask_mysqldb import MySQL 
import MySQLdb.cursors 
import re 
from decimal import *
  
app = Flask(__name__) 

app.secret_key = 'your secret key'

# connecting to mysql database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tejas'
app.config['MYSQL_DB'] = 'farm1_db'
app.config["CACHE_TYPE"] = "null"
  
mysql = MySQL(app) 
  
# routes  
# login route
@app.route('/')
@app.route('/login', methods =['GET', 'POST']) 
def login(): 
    msg = '' 
    if request.method == 'POST':
        
        # getting id and password
        username = request.form['username'] 
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        
        # getting farmer where id and password matches
        cursor.execute('SELECT * FROM farmer WHERE User_id = %s AND Password = %s ',(username,password))
        account = cursor.fetchone()

        if account:

            # if account found then log in successful
            session['loggedin'] = True
            session['id'] = account['User_id'] 
            msg = 'Logged in successfully!!!'
        
            if account['F_Firstname'] == '' and account['F_Lastname'] == '':
                
                # if firstname and lastname is none or empty and then complete profile
                msg = "complete your profile"
                return render_template("complete.html")
            
            # getting farmer info where id and password matches
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM farmer WHERE User_id = %s ', (session['id'],)) 
            info = cursor.fetchone()
            data = {'user_id': session['id'], 'msg': msg, 'info': info}

            # displaying farmer basic info 
            return render_template('index.html', **data)
        else:
            
            # if username/password not matching with our database or not present in database then displaying error 
            msg = 'Incorrect username / password!!!'
    return render_template('login.html', msg = msg) 

# logout route
@app.route('/logout') 
def logout():
    
    # removing data of current logged in farmer from sessions  
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('username', None) 
    return redirect(url_for('login')) 

# signup route
@app.route('/signup', methods =['GET', 'POST']) 
def signup(): 
    msg = ''
    if request.method == 'POST':

        # getting new id and new password
        user_id = request.form['username'] 
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # getting farmer where id and password matches
        cursor.execute('SELECT * FROM farmer WHERE User_id = %s', (user_id, )) 
        account = cursor.fetchone() 
        
        if account:

            # if user already exists then displaying error
            msg = 'Account already exists!!!'
        else: 

            # if user don't exists then create new user
            cursor.execute('INSERT INTO farmer VALUES (0, "", "", "", "", 0, %s, %s)', (user_id, password)) 
            mysql.connection.commit() 
            msg = 'You have successfully registered!!!'
            return render_template('login.html', msg=msg) 
    return render_template('signup.html', msg = msg)

# complete route
@app.route('/complete', methods =['GET', 'POST'])
def complete():
    msg = "Please first create user!!!" 
    if request.method == 'POST':

        # getting other info of new user and adding it in our database and going to home page
        first = request.form['first']
        last = request.form['last']
        gender = request.form['gender']
        address = request.form['address']
        contact = request.form['contact']
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE farmer SET F_Firstname=%s, F_Lastname=%s, F_Gender=%s, F_Address = %s, F_ContactNo=%s WHERE User_id=%s', (first, last, gender, address, contact, user_id))
        mysql.connection.commit()
        cursor.execute('SELECT * FROM farmer WHERE User_id = %s ', (session['id'],))
        info=cursor.fetchone()
        msg="successfully completed profile!!!"
        data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('index.html', **data)

# from now 9 routes are used for displaying respected data and if no data found then display error
# 1 - home route - to main user page
@app.route('/home')
def home():
    msg = ""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM farmer WHERE User_id = %s ', (session['id'],)) 
    info = cursor.fetchone()
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('index.html', **data)

# 2 - farm route - to display farm data
@app.route('/farm')
def farm():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM farm WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('farm.html', **data)

# 3 - crop_allocation route - to display all currently allocated crop data
@app.route('/crop_allocation')
def crop_allocation():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM crop_allocation WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('crop_allocation.html', **data)

# 4 - seed route - to display all seeds data 
@app.route('/seed')
def seed():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM seed WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('seed.html', **data)

# 5 - pesticide route - to display all pesticides data
@app.route('/pesticide')
def pesticide():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM pesticide WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('pesticide.html', **data)

# 6 - fertilizers route - to display all fertilizers data
@app.route('/fertilizer')
def fertilizer():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM fertilizer WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('fertilizer.html', **data)

# 7 - labour route - to display all labours data
@app.route('/labour')
def labour():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM labour WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('labour.html', **data)

# 8 - warehouse route - to display all warehouses data where crops are stored
@app.route('/warehouse')
def warehouse():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM warehouse WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('warehouse.html', **data)

# 9 - crop_market route - to display all markets data where crops are sold
@app.route('/crop_market')
def crop_market():
    msg=""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM crop_market WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    for d in info:
	    _ = d.popitem()
    if len(info)==0:
        msg="Sorry, no data found!!!"
    data = {'user_id': session['id'], 'msg': msg, 'info': info}
    return render_template('crop_market.html', **data)

# delete route - to delete any entry or account
@app.route("/delete", methods = ['GET', 'POST'])
def delete():
    msg = ''
    if request.method == "POST":

        # getting value that will be deleted
        name = list(request.form)[0]
        value = request.form[name]
        column, table = name.split('+')

        # deleting value from respected table
        sql = "DELETE FROM " + table + " WHERE " + column + " = '" + value + "'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        mysql.connection.commit()

        if (table != 'farmer'):
            return redirect(table)

        # only user is deleted not data
        msg = 'User Deleted!!!'
    return render_template('login.html', msg = msg)

# update route - to get old data for update
@app.route("/update", methods = ['GET', 'POST'])
def update():
    msg = ''
    if request.method == 'POST':

        # getting all old values to update them with new values 
        name = list(request.form.to_dict())[0]
        column_id = request.form[name]
        column, table = name.split('+')
        sql = "SELECT * FROM " + table + " WHERE " + column + " = '" + column_id + "'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        temp = list(cursor.fetchone().items())[1:-1]
        info = dict(temp)
        data = {'info':info, 'user_id': session['id'], 'table': table, 'id': column_id, 'column':column}
        return render_template('update.html', **data)
    return render_template('login.html', msg = msg) 

# update_confirm - to update with new data
@app.route("/update_confirm", methods = ["GET", "post"])
def update_confirm():
    msg = ""
    if request.method == "POST":

        # getting new data to update
        name = request.form.to_dict()
        table, column = list(name.keys())[-1].split('+')
        column_id = list(name.values())[-1]
        info = dict(list(name.items())[:-1])

        q1 = "UPDATE " + table
        q2 = " SET "
        for key, value in info.items():
            
            # to solve conversion error
            try:
                temp = float(value)
                if int(temp) / temp == 1 or temp / int(temp) > 1:
                    pass
            except ValueError:
                value = "'" + value + "'"
            q2 = q2 + key +" = " + value + ", "
        q2 = q2[:-2]
        q3 = " WHERE " + column + " = '" + column_id + "'"
        sql = q1 + q2 + q3

        # update old data with new data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        mysql.connection.commit()
        return redirect(table)
    return render_template("login.html", msg = msg) 

# add route - to get table, column names to add
@app.route("/add", methods = ['GET', 'POST'])
def add():
    msg = ''
    if request.method == 'POST':

        # getting table, column name to add
        id_column = list(request.form.to_dict())[0]
        table = request.form[id_column]
        sql = "SELECT column_name FROM information_schema.columns WHERE table_schema = '" + app.config['MYSQL_DB'] + "' AND table_name = '" + table + "' "
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        all_columns = list(cursor.fetchall())
        data_columns = []

        # removing unwanted columns
        for column in all_columns:
            if column["COLUMN_NAME"] not in [id_column, 'User_id']:
                data_columns.append(column["COLUMN_NAME"])
        data = {"columns": data_columns, "table": table, "user_id": session['id']}
        return render_template('add.html', **data)
    return render_template('login.html', msg = msg)

# add_confirm - to add new data
@app.route("/add_confirm", methods = ['GET', 'POST'])
def add_confirm():
    msg = ''
    if request.method == 'POST':

        # getting new data
        name = request.form.to_dict()
        table = list(name.keys())[-1]
        temp = list(name.items())[:-1]
        columns = dict(temp)

        q1 = "INSERT INTO " + table + "("
        q2 = " VALUES ("
        for key, value in columns.items():

            # to solve conversion error
            try:
                temp = float(value)
                if int(temp)/temp == 1 or temp/int(temp) > 1:
                    pass
            except ValueError:
                value = "'" + value + "'"
            q1 = q1 + key + ", "
            q2 = q2 + value + ", "
        q1 = q1 + "User_id )"
        q2 = q2 + "'" + session['id'] + "' )"

        # add new data in our database
        sql = q1 + q2
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        mysql.connection.commit()
        return redirect(table)
    return render_template('login.html', msg = msg)

# to calulate sum
def calculate_total(d):
    total = 0
    for v in d:
        total += list(v.values())[0]
    return(total)

# profit_loss_overall route - to caluculate overall profit-loss
@app.route('/profit_loss_overall', methods=['GET', 'post'])
def profit_loss_overall():
    msg=''

    # getting selling prices of every crop and all expences and calculating its sum
    sql1 = "SELECT selling_price FROM crop_market WHERE User_id = '" + session['id'] + "' "
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute(sql1)
    total_sp = cursor.fetchall()
    total_sp = calculate_total(total_sp)
    
    q1 = "SELECT seed_price FROM seed WHERE User_id = '" + session['id'] + "' "  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute(q1)
    exp1 = cursor.fetchall()
    exp1 = calculate_total(exp1)
    
    q2 = "SELECT pesticide_price FROM pesticide WHERE User_id = '" + session['id'] + "' "
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute(q2)
    exp2 = cursor.fetchall()
    exp2 = calculate_total(exp2)

    q3 = "SELECT fertilizer_price FROM fertilizer WHERE User_id = '" + session['id'] + "' "
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute(q3)
    exp3 = cursor.fetchall()
    exp3 = calculate_total(exp3)

    q4 = "SELECT salary FROM labour WHERE User_id = '" + session['id'] + "' "
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute(q4)
    exp4 = cursor.fetchall()
    exp4 = calculate_total(exp4)

    total_exp = exp1 + exp2 + exp3 + exp4
    values = [exp1, exp2, exp3, exp4]
    data = {'user_id': session['id'], 'msg': msg, 'values': values, 'total_exp': total_exp, 'sp': total_sp, 'color': 'primary'}

    if (total_sp - total_exp) > 0:
        data['color'] = 'success'
    elif (total_sp - total_exp) < 0:
        data['color'] = 'danger'

    return render_template('profit.html', **data)

# cropwise route - give crop name to calculate profit-loss
@app.route('/cropwise', methods = ['GET', 'post'])
def cropwise():
    return render_template("cropwise.html", user_id = session['id'])

# profit_loss_cropwise - to calculate cropwise profit-loss 
@app.route('/profit_loss_cropwise', methods = ['GET', 'post'])
def profit_loss_cropwise():
    msg = ''
    if request.method == 'POST':
        crop_name = request.form['crop_name']

        # getting selling prices of every crop and all expences and calculating its sum
        sql1 = "SELECT selling_price FROM crop_market WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' "
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql1)
        sp = cursor.fetchall()
        sp = calculate_total(sp)

        q1 = "SELECT seed_price FROM seed WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' " 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(q1)
        exp1 = cursor.fetchall()
        exp1 = calculate_total(exp1)
        
        
        q2 = "SELECT pesticide_price FROM pesticide WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' "
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(q2)
        exp2 = cursor.fetchall()
        exp2 = calculate_total(exp2)
        

        q3 = "SELECT fertilizer_price FROM fertilizer WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' "
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(q3)
        exp3 = cursor.fetchall()
        exp3 = calculate_total(exp3)
        
        total_exp = exp1 + exp2 + exp3
        values = [exp1, exp2, exp3]
        data = {'user_id': session['id'], 'msg': msg, 'values': values, 'total_exp': total_exp, 'sp': sp, 'color': 'primary'}

        if (sp - total_exp) > 0:
            data['color'] = 'success'
        elif (sp - total_exp) < 0:
            data['color'] = 'danger'
        return render_template('profit.html', **data)
    return render_template('login.html', msg = msg)