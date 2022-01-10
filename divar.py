import scrapy
from urllib.parse import urljoin

# from database.main import *

from mongoengine import *
connection = connect('xdb')

class DivarSpider(scrapy.Spider):
    name = 'Divar Spider'
    start_urls = ['http://www.divar.ir']

    MAIN_URLS = [
        "https://divar.ir/",
        "http://divar.ir/"
    ]

    def getStates(self,response):

        states = []

        state_urls = response.css('.city ::attr(href)').extract()
        state_names_fa = response.css('.city ::text').extract()


        state_urls = list(map(lambda item : urljoin(response.url,item),state_urls))

        for index in range(0,len(state_urls)):

            state = {'name':{}}

            state['url'] = state_urls[index]
            state['name']['fa'] = state_names_fa[index]

            states.append(state)

        return states

    def parse(self, response):

        if response.url in self.MAIN_URLS:

            states = self.getStates(response)
            
            for state in states:
                cm = City(state)
                cm.save()

            print(states)

        

        # for title in response.css('.post-header>h2'):
        #     print({'title': title.css('a ::text').extract_first()})

        # for next_page in response.css('div.prev-post > a'):
        #     yield response.follow(next_page, self.parse)