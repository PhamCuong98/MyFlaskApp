import os
from cv2 import cv2
from flask import Flask, session, render_template, render_template, flash, redirect, request, url_for, session, logging, flash
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import datetime
from sqlalchemy import desc

from init import create_app
from models import db, users, data_articles
from data import Projects
from project1.func_project1 import yolotiny
from project1.config_project1 import SIZE_IMAGE

ENV = "DEV"
app = create_app(ENV=ENV)

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

        infor = users(name, username, email, password)
        db.session.add(infor)
        db.session.commit()
        flash('Đã đăng ký thành công.')
        return redirect(url_for('projects'))
    return render_template('register.html', form = form)


@app.route('/login', methods= ['GET', 'POST'])
def login():
    error=""
    if request.method =='POST':
        username = request.form['username']
        password_user = request.form['password']
        load_db = db.session.query(users.username ,users.password).filter_by(username = username).all()
        #print("case: {}, {}".format(username, password_user))

        """ for row in db.session.query(users, users.username).all():
            print(row.users, row.username) """

        if len(load_db) == 1:
            password_db= load_db[0][1]           
            #Compare password
            if sha256_crypt.verify(password_user,password_db):
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
            filename= image.filename
            name_split = filename.split(".")

            file_temp= "image_temp.{}".format(name_split[-1])
            print("test", file_temp)
            path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], file_temp)
            print("Save = ", path_to_save)
            image.save(path_to_save)
            
            path_to_result = os.path.join(app.config['RESULT_FOLDER'], file_temp)

            img_arr= cv2.imread(path_to_save)
            img_resize = cv2.resize(img_arr, SIZE_IMAGE)
            process= yolotiny(img_resize)
            licenses, result_arr = process.cut_plate()
            print("bien so", licenses)
            cv2.imwrite(path_to_result, result_arr)

            client_image = "client_image/{}".format(file_temp)
            result_image = "result_image/{}".format(file_temp)
            print(client_image, result_image)
            return render_template(name_project, id = 1, licenses = licenses, client_image= client_image, result_image= result_image)
            
    return render_template(name_project, id= 1)

@app.route('/articles', methods=['GET', 'POST'])
@login_required
def articles():
    load_db = db.session.query(data_articles.id, data_articles.username, data_articles.daytime, data_articles.title, data_articles.body).order_by(desc(data_articles.id)).limit(3).all()
    num_article= len(load_db)
    if num_article <=3:
        print("vao case")
        for i in load_db:
            print("test", i)
        render_template('articles.html', articles= load_db, result_search= num_article)

    if request.method == 'POST':
        if 'add_article' in request.form:
            return redirect(url_for('add_articles'))
        elif 'show_more' in request.form and num_article >=3:
            return redirect(url_for('dashboard'))    
    return render_template('articles.html', articles= load_db, result_search= num_article)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    load_db = db.session.query(data_articles.id, data_articles.username, data_articles.daytime, data_articles.title, data_articles.body).all()

    return render_template('dashboard.html', articles = load_db)

class ArticlesForm(Form):
    title = StringField(u'title', [validators.Length(min=1, max=100)])
    body = StringField(u'body', [validators.Length(min=1, max=800)])

@app.route('/articles/add_articles', methods= ['GET', 'POST']) 
def add_articles():
    form = ArticlesForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        article = data_articles(session['username'], datetime.datetime.now(), title, body)
        db.session.add(article)
        db.session.commit()
        
        flash('Đã public comment thành công')
        return redirect(url_for('articles'))
    return render_template('add_articles.html', form=form)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug= True)