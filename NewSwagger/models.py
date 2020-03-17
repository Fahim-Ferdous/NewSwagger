""" Generic models are defined here. """
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class PaperPage(Base):
    """ Equivalent of a physical newspaper's page."""
    __tablename__ = 'paperpages'

    paperPage = Column(String, primary_key=True)  # PaperPageTitle
    articles = relationship('Article')

    def __repr__(self):
        return f"<PaperPage(pageTitle={self.title})>"


class Article(Base):
    """ The article on a page. """
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    parentPage = Column(String, ForeignKey('paperpages.paperPage'))

    def __repr__(self):
        return f"<Article(title={self.title})>"
