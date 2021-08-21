from config import SIZE_IMAGE
from logging import error
from types import MethodType
from flask import Flask, session, render_template, render_template, flash, redirect, request, url_for, session, logging, flash
from flask.signals import message_flashed
from werkzeug.datastructures import MIMEAccept
from wtforms import Form, StringField, PasswordField, validators
from data import Projects
from flaskext.mysql import MySQL
import mysql.connector
from passlib.hash import sha256_crypt
from functools import wraps
import datetime
import os
import numpy as np
from func_project1 import yolotiny
from cv2 import cv2
#from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/client_image"
app.config['RESULT_FOLDER'] = "static/result_image"

# Config cho database Mysql
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ngoccuong1812'
app.config['MYSQL_DATABASE_DB'] = 'FlaskApp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

Projects = Projects()

class RegisterForm(Form):
    name = StringField(u'Name', [validators.Length(min=1, max=50)])
    username = StringField(u'Username', [validators.Length(min= 4, max= 25)])
    email = StringField(u'Email', [validators.Length(min= 6, max= 50)])
    password = PasswordField(u'Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message= u'Password không trùng khớp')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        connection = mysql.connect()
        mycursor = connection.cursor()
        
        mycursor.execute("INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)", (name, username, email, password))
        connection.commit()
        flash('Đã đăng nhập thành công.')
        return redirect(url_for('projects'))
    return render_template('register.html', form = form)


@app.route('/login', methods= ['GET', 'POST'])
def login():
    error=""
    if request.method =='POST':
        username = request.form['username']
        password_user = request.form['password']
        #print(username, password_user)
        cursor= mysql.connect().cursor()
        result= cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        #print('result', result)
        if result == 1:
            data = cursor.fetchall()
            #print('data', data)
            password = data[0][4]

            #Compare password
            if sha256_crypt.verify(password_user, password):
                app.logger.info('Đúng Password')
                session['logged_in'] = True
                session['username'] = username

                flash('Bạn đã loggin thành công')
                return redirect(url_for('index')) 
            else:
                error = 'Sai mật khẩu'
                app.logger.info('Sai Password')
                return render_template('login.html', error= error)
            cursor.close()
        else:
            error = 'Lỗi tài khoản'    
            app.logger.info('Không tìm thấy user')
            return render_template('login.html', error= error)

    return render_template('login.html')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Bạn đang logout, tạm biệt')
    return redirect(url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Vui lòng login trước khi sử dụng chức năng này.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/projects', methods= ['GET', "POST"])
@login_required
def projects():
    return render_template('projects.html', projects= Projects)

@app.route('/project/1', methods = ['POST', 'GET'])
def project_1():
    name_project = "projects/project{id}.html".format(id= 1)
    #print(name_project)
    if request.method == 'POST':
        image = request.files['formFile'] 
        """ x= np.fromstring(image.read(), np.uint8)
        print("convert",type(x))
        print(len(x))
        x_2= cv2.imdecode(x, cv2.IMREAD_UNCHANGED)
        print(x_2) """
        if image:
            # Lưu file
            #print(image.filename)
            #print(app.config['UPLOAD_FOLDER'])
            path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            print("Save = ", path_to_save)
            image.save(path_to_save)
            
            path_to_result = os.path.join(app.config['RESULT_FOLDER'], image.filename)

            img_arr= cv2.imread(path_to_save)
            img_resize = cv2.resize(img_arr, SIZE_IMAGE)
            process= yolotiny(img_resize)
            licenses, result_arr = process.cut_plate()
            cv2.imwrite(path_to_result, result_arr)

            client_image = "client_image/{}".format(image.filename)
            result_image = "result_image/{}".format(image.filename)
            print(client_image, result_image)
            return render_template(name_project, id = 1, licenses = licenses, client_image= client_image, result_image= result_image)
            
    return render_template(name_project, id= 1)

@app.route('/articles', methods=['GET', 'POST'])
@login_required
def articles():
    connection = mysql.connect()
    mycursor = connection.cursor()

    result_search = mycursor.execute("SELECT * FROM articles ORDER BY daytime DESC LIMIT 3;")
    articles = mycursor.fetchall()
    mycursor.close()
    if result_search >0:
        for i in articles:
            print(i)
        render_template('articles.html', articles= articles, result_search= result_search)

    if request.method == 'POST':
        if 'add_article' in request.form:
            return redirect(url_for('add_articles'))
        elif 'show_more' in request.form and result_search >=3:
            return redirect(url_for('dashboard'))    
    return render_template('articles.html', articles= articles, result_search= result_search)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    connection = mysql.connect()
    mycursor = connection.cursor()

    result = mycursor.execute("SELECT * FROM articles")
    articles = mycursor.fetchall()
    mycursor.close()
    return render_template('dashboard.html', articles = articles)

class ArticlesForm(Form):
    title = StringField(u'title', [validators.Length(min=1, max=100)])
    body = StringField(u'body', [validators.Length(min=1, max=800)])

@app.route('/articles/add_articles', methods= ['GET', 'POST'])
def add_articles():
    form = ArticlesForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        connection = mysql.connect()
        mycursor = connection.cursor()

        mycursor.execute("INSERT INTO articles (username, daytime, title, body) VALUE (%s, %s, %s, %s)", (session['username'], datetime.datetime.now() ,title, body))
        connection.commit()
        mycursor.close()
        flash('Đã public comment thành công')
        return redirect(url_for('articles'))
    return render_template('add_articles.html', form=form)
if __name__ == '__main__':
    app.secret_key = b'phamcuong1812'
    app.run(debug= True)