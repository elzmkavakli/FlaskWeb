
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,ValidationError
from passlib.hash import sha256_crypt
from functools import wraps
#Kullanıcı giriş decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ("logged_in" in session):
            return f(*args, **kwargs)
        else:
            flash("Bu sayfası görmeye yetkiniz yok","danger")
            return redirect(url_for("login"))
    return decorated_function
#Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name=StringField("İsim Soyisim:",validators=[validators.length(min=10,max=50)])
    email=StringField("E_Mail:",validators=[validators.Email(message="Geçerli Değil")])#pip install email-validator
    username=StringField("Kullanıcı Adı:",validators=[validators.length(min=5,max=35)])
    password=PasswordField("Parola:",validators=[
        validators.DataRequired(message="Lütfen Email Adresi Giriniz"),
        validators.EqualTo(fieldname="confirm",message="Parola Uyuşmuyor")
    ])
    confirm=PasswordField("Parola Doğrula:")
#Login Formu Oluşturma
class LoginForm(Form):
    username=StringField("Kullanıcı Adı:")
    password=PasswordField("Parola:")
app=Flask(__name__)
app.secret_key="mkblog"#Flash mesajları için
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="mkblog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"
mysql=MySQL(app)
@app.route('/')
def home():
    ogretmen_listesi=[
        {"id":"1","adi":"Mehmet KAVAKLI","gorevi":"Alan Şefi"},
        {"id":"2","adi":"Selman UZUN","gorevi":"Atölye Şefi"},
        {"id":"3","adi":"A. Alper KARAGÖZOĞLU","gorevi":"Atölye Şefi"},
        {"id":"4","adi":"Recep ŞAHİN","gorevi":"Atölye Şefi"},
        {"id":"5","adi":"Ü. Yaşar ERTAŞ","gorevi":"Atölye Şefi"},
        {"id":"6","adi":"Hikmet ERDOĞAN","gorevi":"Alan Öğretmeni"},
      
        ]
    """ad_soyad="Mehmet KAVAKLI"
    telefon_numarası=5530533224"""
    """article=dict()
    article["title"]="Gazi MTAL Bilişim Teknolojileri Alanı"
    article["body"]="Bilişim Teknolojileri Alanı"
    article["author"]='Mehmet KAVAKLI'
    """

    #return render_template('index.html',article=article)
    return render_template('index.html',ogretmen=ogretmen_listesi,answer=2)
@app.route('/about')
def about():
    return render_template('about.html')
    """
@app.route("/articles/<string:id>")
def detail(id):
    return "Makale numarası:"+id
    """
#Veri tabanına kayıt iş ve işlmeleri

@app.route('/register',methods=["GET","POST"])
def register():
    form=RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(form.password.data)
        cursor=mysql.connection.cursor()
        sorgu="Insert into users (name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("Başarıyla Kayıt Oldunuz...","success")
        return redirect(url_for("login"))
    else:
        return render_template('register.html',form=form)
#Login işlemleri
@app.route('/login',methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        username=form.username.data
        password_entered=form.password.data
        cursor=mysql.connection.cursor()
        sorgu="Select * From users where username = %s "
        result = cursor.execute(sorgu,(username,))
        if result>0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla Giriş Yaptınız...","success")
                session["logged_in"]=True
                session["username"]=username
                return redirect(url_for("home"))
            else:
                flash("Parolayı yanlış girdiniz...","danger")
                return redirect(url_for("login"))

        else:
            flash("Böyle Bir Kullanıcı Yok...","danger")
            return redirect(url_for("login"))

    else:
        return render_template('login.html',form=form)
#Logout Çıkış yap
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))


    #KontrolPaneli
@app.route('/dashboard')
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    sorgu="Select * From articles where author = %s"
    result=cursor.execute(sorgu,(session["username"],))
    if result>0:
        articles=cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:
        return render_template("dashboard.html")



#Makale oluşturma paneli
@app.route('/addarticle',methods=["GET","POST"])
def addarticle():
    form =ArticleForm(request.form)
    if request.method=="POST" and form.validate():
        title=form.title.data
        content=form.content.data
        cursor=mysql.connection.cursor()
        sorgu="insert into articles(title,author,content) Values(%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username"],content))
        mysql.connection.commit()
        cursor.close()
        flash("Makale Başarıyla Eklendi...","success")
        return redirect(url_for("dashboard"))
    
    
    return render_template("addarticle.html",form=form)
#Makale Form oluşturuma
class ArticleForm(Form):
    title=StringField("Makale Başlığı:",validators=[validators.Length(min=5,max=100)])
    content=TextAreaField("Makale İçeriği:",validators=[validators.Length(min=10)])
#Makale Sayfası
@app.route('/articles')
def articles():
    cursor=mysql.connection.cursor()
    sorgu ="Select * From articles"
    result=cursor.execute(sorgu)
    if result>0:
        articles=cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")
@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()
    
    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")
#Makale Silme İş ve İşlemleri
@app.route('/delete/<string:id>')
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    
    sorgu = "Select * from articles where author = %s and id = %s"

    result = cursor.execute(sorgu,(session["username"],id))
    if result > 0:
        sorgu2 = "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
        return redirect(url_for("home"))
#Makale Güncellme
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
    if request.method=="GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where id = %s and author = %s"
        result = cursor.execute(sorgu,(id,session["username"]))
        if result == 0:
           flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
           return redirect(url_for("home"))
        else:
           article = cursor.fetchone()
           form = ArticleForm()
           form.title.data = article["title"]
           form.content.data = article["content"]
           return render_template("update.html",form = form)
    else:
        # POST REQUEST
       form = ArticleForm(request.form)
       newTitle = form.title.data
       newContent = form.content.data
       sorgu2 = "Update articles Set title = %s,content = %s where id = %s "
       cursor = mysql.connection.cursor()
       cursor.execute(sorgu2,(newTitle,newContent,id))
       mysql.connection.commit()
       flash("Makale başarıyla güncellendi","success")
       return redirect(url_for("dashboard"))
# Arama URL
@app.route("/search",methods = ["GET","POST"])
def search():
   if request.method == "GET":
       return redirect(url_for("home"))
   else:
       keyword = request.form.get("keyword")
       cursor = mysql.connection.cursor()
       sorgu = "Select * from articles where title like '%" + str(keyword)+"%'"
       result = cursor.execute(sorgu)
       if result == 0:
           flash("Aranan kelimeye uygun makale bulunamadı...","warning")
           return redirect(url_for("articles"))
       else:
           articles = cursor.fetchall()
           return render_template("articles.html",articles = articles)
if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)



