""" Aggregate The Daily Star for seuptitious purposes"""
# -*- coding: utf-8 -*-
import scrapy


class ThedailystarSpider(scrapy.Spider):
    """ Right now:
            Parse only the /newspaper path with current date.
    """
    name = 'thedailystar'
    allowed_domains = ['thedailystar.net']
    start_urls = ['http://thedailystar.net/newspaper?date=2020-03-14']

    def parse(self, response):
        for pane in response.css('.pane-news-col'):
            page = pane.css('h2::text').extract_first()
            yield {
                'paperPage': page,
            }

            for title in pane.css('h5 > a::text'):
                yield {
                    'title': title.extract(),
                    'parentPage': page,
                }
