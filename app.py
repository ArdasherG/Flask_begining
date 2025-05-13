from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

# ? При помощи класса можно созлать таблицы в БД
class Article(db.Model):
    # ? Column - нужен для создаания опрерделенного поля в таблице
    # ? в поле (только цифры, присваивается уникальность с помощью "primary_key")
    id = db.Column(db.Integer, primary_key=True)
    
    # ? в поле (только буквы(кол-во символов), nullable - означает, что нельзя будет оставялть пустое значение)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)

    # ? в поле (DateTime - тип данных. В defualt записывается время создания статьи или чего то ещё)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # ? Нужен для индексирования объектов класса 'Article' из БД (выдает ID объекта)
    def __repr__(self):
        return '<Article %r>' % self.id
    
with app.app_context():
    db.create_all()

@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/posts")
def posts():
    # ? Объект через котрый мы получаем все данные из БД и передаем в шаблон
    # ? query() - позволяет через класс обращаться к БД и выбирать ту таблицу которая соответствует данному классу
    # ? first() - позволяет обратиться к первой записи в БД и забрать её, а all() ко всем.
    # ? order_by() - позволяет сортировать все полученные данные по определенному полю
    # ? desc - позволяет сортировать по новизне
    articles = Article.query.order_by(Article.date.desc()).all()
    # ? Передаем шаблон articles(список всех записей). И в шаблоне мы сможем работать со списком по ключевому назв. articles 
    return render_template('posts.html', articles=articles)


@app.route("/posts/<int:id>")
def posts_detail(id):
    # ? get() - позволяет выбрать определенный объект по его ID
    article = Article.query.get(id)
    return render_template('posts_detail.html', article=article)


@app.route("/posts/<int:id>/delete")
def posts_delete(id):
    # ? get_or_404() - работает как get(), но если не находит функцию по ID выдает ошибку
    article = Article.query.get_or_404(id)

    # ? redirect() - нужна для переадресации
    # ? Мы пытаемся удалить запись, если получается мы возвращаемся на страницу со всеми постами, если нет получаем ошибку
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'An error occurred when deleting the article!'


# ? POST() - когда мы отправляем данные с страницы через форму(html)
# ? GET() - когда мы переходим на страницу
@app.route("/posts/<int:id>/update", methods=['POST', 'GET'])
def posts_update(id):
    article = Article.query.get(id)
    if request.method == 'POST':
       article.title = request.form['title']
       article.intro = request.form['intro']
       article.text = request.form['text']

        
       try:
        # ? commti() - позволяет обновлять БД
           db.session.commit()
           return redirect('/posts')
       except:
           return 'An error occurred when edit the article!'
    else:
        return render_template('post_update.html', article=article)


@app.route("/create-article", methods=['POST', 'GET'])
def create_article():
    if request.method == 'POST':
       title = request.form['title']
       intro = request.form['intro']
       text = request.form['text']

        # ? Для работы с БД создается объект на основе этого класса 
       article = Article(title=title, intro=intro, text=text)
        
        # ? Сохраняем объект через другой объект который принадлежит БД(db)
       try:
           db.session.add(article)
           db.session.commit()
           return redirect('/posts')
       except:
           return 'An error occurred when adding the article!'
    else:
        return render_template('create-article.html')


# @app.route("/user/<string:name>/<int:id>")
# def user(name, id):
#     return f"Username: {name}, user ID: {id}"


if __name__ == "__main__":
    app.run(debug=True)