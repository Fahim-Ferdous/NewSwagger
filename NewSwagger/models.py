""" Generic models are defined here. """
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship

Base = declarative_base()


class PaperPage(Base):
    """ Equivalent of a physical newspaper's page."""
    __tablename__ = 'paperpages'

    id = Column(Integer, primary_key=True)
    paperPage = Column(String, unique=True)  # PaperPageTitle
    articles = relationship('Article')

    def __repr__(self):
        return f"<PaperPage(pageTitle={self.title})>"


author_articles = Table(
    'author_articles',
    Base.metadata,
    Column('author_id', ForeignKey('authors.id'), primary_key=True),
    Column('article_id', ForeignKey('articles.id'), primary_key=True),
)

class Article(Base):
    """ The article on a page. """
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    published = Column(Date)
    title = Column(String)
    body = Column(String)
    url = Column(String)

    paperPage_id = Column(Integer, ForeignKey('paperpages.id'))
    authors = relationship(
        'Author',
        secondary=author_articles,
        back_populates='articles',
    )

    def __repr__(self):
        return f"<Article(title={self.title})>"

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    url = Column(String, index=True)
    articles = relationship('Article',
                            secondary=author_articles,
                            back_populates='authors')

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return f"<Author(name={self.name})>"
