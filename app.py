from flask import Flask, render_template, request, redirect, url_for, session 
from flask_mysqldb import MySQL 
import MySQLdb.cursors 
import re 
  
app = Flask(__name__) 

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tejas'
app.config['MYSQL_DB'] = 'farm1_db'
app.config["CACHE_TYPE"] = "null"
  
mysql = MySQL(app) 
  
@app.route('/')
@app.route('/login', methods =['GET', 'POST']) 
def login(): 
    msg = '' 
    if request.method == 'POST': 
        username = request.form['username'] 
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT * FROM farmer WHERE User_id = %s AND Password = %s ',(username,password))
        account = cursor.fetchone()
        #print(account)
        if account: 
            session['loggedin'] = True
            session['id'] = account['User_id'] 
            msg = 'Logged in successfully!!!'
            if account['F_Firstname'] == '' and account['F_Lastname'] == '':
                msg = "complete your profile"
                return render_template("complete.html")
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
            cursor.execute('SELECT * FROM farmer WHERE User_id = %s ', (session['id'],)) 
            info=cursor.fetchone()
            return render_template('index.html', msg=info, user=account['User_id'])
        else: 
            msg = 'Incorrect username / password!!!'
    return render_template('login.html', msg = msg) 
  
@app.route('/logout') 
def logout(): 
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('username', None) 
    return redirect(url_for('login')) 
  
@app.route('/signup', methods =['GET', 'POST']) 
def signup(): 
    msg = '' 
    if request.method == 'POST': 
        user_id = request.form['username'] 
        password = request.form['password'] 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute('SELECT * FROM farmer WHERE User_id = % s', (user_id, )) 
        account = cursor.fetchone() 
        if account: 
            msg = 'Account already exists!!!'
        else: 
            cursor.execute('INSERT INTO farmer VALUES (0, "", "", "", "", 0, %s, %s)', (user_id, password)) 
            mysql.connection.commit() 
            msg = 'You have successfully registered!!!'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST': 
        msg = 'Please fill out the form!!!'
    return render_template('signup.html', msg = msg)

@app.route('/complete', methods =['GET', 'POST'])
def complete():
    msg = "Please first create user!!!" 
    if request.method == 'POST':
        first = request.form['first']
        last = request.form['last']
        town = request.form['town']
        gender = request.form['gender']
        district = request.form['district']
        state = request.form['state']
        contact = request.form['contact']
        user_id = request.form['user_id']
        address =  town+", "+district+", "+state
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE farmer SET F_Firstname=%s, F_Lastname=%s, F_Gender=%s, F_Address = %s, F_ContactNo=%s WHERE User_id=%s', (first, last, gender, address, contact, user_id))
        mysql.connection.commit()
        msg="successfully completed profile!!!"
    return render_template('login.html',msg=msg)

@app.route('/home')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM farmer WHERE User_id = %s ', (session['id'],)) 
    info = cursor.fetchone()
    return render_template('index.html', msg=info, user=session['id'])

@app.route('/farm')
def farm():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM farm WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    if len(info)==0:
        return render_template('no_data.html', user=session['id'])
    return render_template('farm.html',msg=info, user=session['id'])

@app.route('/crop_allocation')
def crop_allocation():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM crop_allocation WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    if len(info)==0:
        return render_template('no_data.html', user=session['id'])
    return render_template('crop_allocation.html',msg=info, user=session['id'])

@app.route('/labour')
def labour():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM labour WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    if len(info)==0:
        return render_template('no_data.html', user=session['id'])
    return render_template('labour.html',msg=info, user=session['id'])

@app.route('/warehouse')
def warehouse():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM warehouse WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    if len(info)==0:
        return render_template('no_data.html', user=session['id'])
    return render_template('warehouse.html',msg=info, user=session['id'])

@app.route('/crop_market')
def crop_market():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM crop_market WHERE User_id = %s ', (session['id'],))
    info = cursor.fetchall()
    if len(info)==0:
        return render_template('no_data.html', user=session['id'])
    return render_template('crop_market.html',msg=info, user=session['id'])

@app.route("/delete", methods =['GET', 'POST'])
def delete():
    msg = ''
    if request.method == 'POST':
        name = list(request.form)[0]
        value = request.form[name]
        column, table = name.split("+")
        #print("\n------",name,"-----\n")
        #print("\n------",column," ",table,"-----\n")
        #print("\n------",value,"-----\n")
        sql="DELETE FROM "+table+" WHERE "+column+" = "+value
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        info = cursor.fetchall()
        mysql.connection.commit()
        #print(info)
        return redirect(table)
    return render_template('login.html', msg = msg) 

@app.route("/update", methods =['GET', 'POST'])
def update():
    msg = ''
    if request.method == 'POST':
        name = list(request.form.to_dict())[0]
        value = request.form[name]
        column, table = name.split("+")
        #print("\n------",name,"-----\n")
        #print("\n------",column," ",table,"-----\n")
        #print("\n------",value,"-----\n")
        sql="SELECT * FROM "+table+" WHERE "+column+" = "+value
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        info = cursor.fetchall()[0]
        temp=list(info.items())
        info=dict(temp[1:-1])
        #print(info)
        return render_template('update.html', msg=info, user=session['id'], table=table)
    return render_template('login.html', msg = msg) 

@app.route("/update_confirm", methods=['GET', 'post'])
def update_confirm():
    msg = ''
    if request.method == 'POST':
        name = request.form.to_dict()
        table = list(name.keys())[-1]
        temp = list(name.items())[:-1]
        columns = dict(temp)
        #print(table)
        #print(columns)

        q1="UPDATE "+table
        q2=" SET "
        for key, value in columns.items():
            try:
                temp=float(value)
                if int(temp)/temp==1 or temp/int(temp)>1:
                    pass
            except ValueError:
                value = "'"+value+"'"
            q2 = q2 + key+" = "+value+", "
        q2=q2[:-2]
        q3=" WHERE User_id = '"+session['id']+"' "

        sql=q1+q2+q3
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        mysql.connection.commit()
        return redirect(table)
    return render_template('login.html', msg = msg) 
        
@app.route("/add", methods =['GET', 'POST'])
def add():
    msg = ''
    if request.method == 'POST':
        table = list(request.form.to_dict().keys())[0]
        #print(table)
        #print("\n------",name,"-----\n")
        #print("\n------",column," ",table,"-----\n")
        #print("\n------",value,"-----\n")
        sql="SELECT column_name FROM information_schema.columns WHERE table_schema = '"+app.config['MYSQL_DB']+"' AND table_name = '"+table+"' "
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        info = list(cursor.fetchall())
        columns=[]
        for value in info[1:-1]:
            columns.append(value["COLUMN_NAME"])
        #print(columns)
        return render_template('add.html', msg=columns, user=session['id'], table=table)
    return render_template('login.html', msg = msg)

@app.route("/add_confirm", methods=['GET', 'post'])
def add_confirm():
    msg = ''
    if request.method == 'POST':
        name = request.form.to_dict()
        table = list(name.keys())[-1]
        temp = list(name.items())[:-1]
        columns = dict(temp)
        #print(table)
        #print(columns)

        q1="INSERT INTO "+table
        q2=" VALUES (0, "
        for key, value in columns.items():
            try:
                temp=float(value)
                if int(temp)/temp==1 or temp/int(temp)>1:
                    pass
            except ValueError:
                value = "'"+value+"'"
            q2=q2+value+", "
        q2=q2+"'"+session['id']+"' )"

        sql=q1+q2
        #print(sql)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute(sql)
        mysql.connection.commit()
        return redirect(table)
    return render_template('login.html', msg = msg) 