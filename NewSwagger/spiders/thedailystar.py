""" Aggregate The Daily Star for seuptitious purposes"""
# -*- coding: utf-8 -*-
import datetime
import logging

import scrapy
from scrapy import Request


class ThedailystarSpider(scrapy.Spider):
    """ Right now:
            Parse only the /newspaper path with current date.
    """
    name = 'thedailystar'
    allowed_domains = ['thedailystar.net']
    start_urls = []

    def start_requests(self):
        filename = 'lastdate.txt'
        lastdate = datetime.date.today()
        try:
            with open(filename) as datefile:
                lastdate = datetime.datetime.\
                        strptime(datefile.read().strip(), '%Y-%m-%d').\
                        date()
        except FileNotFoundError:
            self.log(f'File <{filename}> was not found', logging.WARNING)

        # TODO: Make lastdate more accurate by
        # updating it only after parsing whole day.
        try:
            while lastdate <= datetime.date.today():
                yield Request(
                    'http://thedailystar.net/newspaper?date='+str(lastdate),
                    self.parse,
                )
                lastdate += datetime.timedelta(days=1)
        finally:
            with open(filename, 'w') as datefile:
                print(str(lastdate), file=datefile)

    def parse(self, response):
        for pane in response.css('.pane-news-col'):
            page = pane.css('h2::text').extract_first()
            for anchor in pane.css('h5 > a'):
                yield response.follow(
                    anchor.attrib['href'],
                    callback=self.parseArticle
                    if page != 'In Focus'
                    else self.parseInFocusArticle,
                    cb_kwargs={
                        'parentPage': page,
                        'title': anchor.css('::text').get(),
                        'parentURL': response.request.url,
                    }
                )

    def parseArticle(self, response, parentURL, title, parentPage):
        smallText = response.\
                css('.small-text > meta[itemprop]::attr(content)').\
                extract()

        try:
            yield {
                'title': title,
                'paperPage': parentPage,
                'published': datetime.datetime.fromisoformat(smallText[0]),
                'modified': datetime.datetime.fromisoformat(smallText[1]),
            }
        except IndexError:  # TODO: Handle articles of `In Focus' section
            self.log(response.request.url+' >>>> '+parentURL, logging.WARNING)

    def parseInFocusArticle(self, response, title, parentURL, parentPage):
        meta = response.css('meta[property^=article]::attr(content)').extract()
        self.log('In Focus', logging.INFO)
        yield {
            'title': title,
            'paperPage': parentPage,
            'published': datetime.datetime.fromisoformat(meta[0]),
            'modified': datetime.datetime.fromisoformat(meta[1]),
        }
