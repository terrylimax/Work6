import requests
from bs4 import BeautifulSoup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bottle import route, run, template
from bottle import redirect
from bottle import request
from collections import defaultdict
from math import log


def get_news(pages):
    def get_news_one_page(text):

        page = BeautifulSoup(text, 'html5lib')

        for i in range(30):
            try:
                title = page.table.findAll('table')[1].findAll('tr')[i * 3]('td')[2].text.split('(')[0]
            except:
                title = None
            try:
                link = page.table.findAll('table')[1].findAll('tr')[i * 3]('td')[2].text.split('(')[1][:-1]
            except:
                link = None
            try:
                points = page.table.findAll('table')[1].findAll('tr')[i * 3 + 1]('td')[1].findAll('span')[0].text[:-7]
            except:
                points = None
            try:
                author = page.table.findAll('table')[1].findAll('tr')[i * 3 + 1]('td')[1].findAll('a')[0].text
            except:
                author = None
            try:
                comments = page.table.findAll('table')[1].findAll('tr')[i * 3 + 1]('td')[1].findAll('a')[4].text[:-9]
            except:
                comments = 0
            new = {'title': title, 'link': link, 'points': points, 'author': author, 'comments': comments}
            news.append(new)
            next = page.table.findAll('table')[1].findAll('tr')[91]('td')[1].findAll('a')[0]['href'].split('?')[1]
        return news, next

    news = []
    next = ''
    for i in range(pages):
        r = requests.get('https://news.ycombinator.com/newest?{}'.format(next))
        news_list, next = get_news_one_page(r.text)
    return news_list


news_list = get_news(1)

Base = declarative_base()


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


engine = create_engine("sqlite:///news.db")
Base.metadata.create_all(bind=engine)

for new in news_list:
    news = News(title=new['title'],
                author=new['author'],
                url=new['link'],
                comments=new['comments'],
                points=new['points'])
    session = sessionmaker(bind=engine)
    s = session()
    s.add(news)
    s.commit()


@route('/')
@route('/news')
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route('/add_label')
def add_label():
    s = session()
    label = request.query.label
    id = request.query.id
    article = s.query(News).filter(News.id == int(id)).first()
    article.label = label
    s.commit()
    redirect('/news')


@route('/update_news')
def update_news():
    s = session()
    newest = get_news(1)
    for new in newest:
        if not s.query(News).filter(News.title == new['title'] and News.author == new['author']).all():
            n = News(title=new['title'],
                     author=new['author'],
                     url=new['link'],
                     comments=new['comments'],
                     points=new['points'])
            s.add(n)
            s.commit()
    redirect('/news')


def train(samples):
    classes, freq = defaultdict(lambda: 0), defaultdict(lambda: 0)
    for feats, label in samples:
        classes[label] += 1
        freq[label, feats] += 1
    for label, feat in freq:
        freq[label, feat] /= classes[label]
    for c in classes:
        classes[c] /= len(samples)
    return classes, freq


def classify(classifier, feats):
    classes, prob = classifier
    return min(classes.keys(),
               key=lambda cl: -log(classes[cl]) +
                              sum(-log(prob.get((cl, feat), 10 ** (-7))) for feat in feats.title.split()))


def get_features(title, label):
    for i in title.split():
        return i, label


samples = s.query(News).filter(News.label != None).all()
features = [get_features(sample.title, sample.label) for sample in samples]
trainer = train(features)
predictions = []
for new in s.query(News).filter(News.label == None).all():
    label = classify(trainer, new)
    predictions.append({
        'title': new.title,
        'author': new.author,
        'label': label,
        'url': new.url
    })


class Rec(Base):
    __tablename__ = "rec"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    label = Column(String)


engine = create_engine("sqlite:///rec.db")
Base.metadata.create_all(bind=engine)

for prediction in predictions:
    rec = Rec(title=prediction['title'],
              author=prediction['author'],
              url=prediction['url'],
              label=prediction['label'])
    session = sessionmaker(bind=engine)
    s = session()
    s.add(rec)
    s.commit()


@route('/recommendations')
def recommendations():
    s = session()
    rows_g = s.query(Rec).filter(Rec.label == 'good').all()
    rows_m = s.query(Rec).filter(Rec.label == 'maybe').all()
    rows_n = s.query(Rec).filter(Rec.label == 'never').all()
    return template('rec_template', rows_g=rows_g, rows_m=rows_m, rows_n=rows_n)


run(host='localhost', port=8080)
