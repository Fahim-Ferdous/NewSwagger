""" Aggregate The Daily Star for seuptitious purposes"""
# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy


class ThedailystarSpider(scrapy.Spider):
    """ Right now:
            Parse only the /newspaper path with current date.
    """
    name = 'thedailystar'
    allowed_domains = ['thedailystar.net']
    start_urls = ['http://thedailystar.net/newspaper?date=2020-03-14']

    def parse(self, response):
        for href in response.css('h5 > a::attr(href)').extract():
            yield response.follow(href, callback=self.parseArticle)

    def parseArticle(self, response):
        smallText = response.\
                css('.small-text > meta[itemprop]::attr(content)').\
                extract()

        yield {
            'title': response.css('h1::text').extract_first(),
            'paperPage':
                response.
                css('.breadcrumb span[itemprop=name]::text').
            extract()[-1],
            'published': datetime.fromisoformat(smallText[0]),
            'modified': datetime.fromisoformat(smallText[0]),
        }
