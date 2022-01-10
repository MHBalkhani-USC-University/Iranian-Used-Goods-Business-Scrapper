import scrapy
from urllib.parse import urljoin

# database
from database.models.city import City as CityModel
from database.models.ad import Ad as AdModel
from database.main import connect

# requests
import requests
import datetime

connect('xxxdb')

def convertPersianToEnglishNumber(number):

    numbersTranslations = {

        '۰':'0',
        '۱':'1',
        '۲':'2',
        '۳':'3',
        '۴':'4',
        '۵':'5',
        '۶':'6',
        '۷':'7',
        '۸':'8',
        '۹':'9'

    }

    numberNew = ""

    number = number.replace(',','')

    for i in range(0,len(number)):
        numberNew+=numbersTranslations[number[i]]

    return numberNew

class SheypoorSpider(scrapy.Spider):
    name = 'Sheypoor Spider'
    start_urls = ['http://www.sheypoor.com']

    MAIN_URLS = [
        "https://www.sheypoor.com/"
    ]

    def getStates(self,response):

        states = []

        state_urls = response.css('#provinces-list>ul>li>ul>li>a ::attr(href)').extract()
        state_names_fa = response.css('#provinces-list>ul>li>ul>li>a ::text').extract()

        # state_urls = list(map(lambda item : urljoin(response.url,item),state_urls))

        for index in range(0,len(state_urls)):

            state = {'name':{}}

            state['url'] = state_urls[index]
            state['name']['fa'] = state_names_fa[index]

            states.append(state)

        return states

    def getNextPageUrl(self,response):
        path = response.css("#pagination>ul>li>a ::attr(href)")
        path = path[len(path)-1:].extract_first()
        return urljoin(self.MAIN_URLS[0],path)

    def getAdsUrl(self,response):
        paths = response.css("#serp>div>article>div.image>a ::attr(href)").extract()
        return list(map(lambda path : urljoin(self.MAIN_URLS[0],path),paths))

    def parse(self, response):

        states = self.getStates(response)
        
        for state in states:
            
            cm = CityModel(name=state['name'],url=state['url'])
            if CityModel.objects(name=state['name'],url=state['url']):
                cm = CityModel.objects(name=state['name'],url=state['url'])[0]
            cm.save()

        yield response.follow(states[0]['url'], callback=self.adPageParser)
        
    def adPageParser(self,response):
        
        self.logger.info("Ad Page "+response.url)

        nextPageUrl = self.getNextPageUrl(response)
        self.logger.info("Next Page "+nextPageUrl)

        adsUrls = self.getAdsUrl(response)

        for adUrl in adsUrls:
            yield response.follow(adUrl,self.adParser)
        
        yield response.follow(nextPageUrl,self.adPageParser)

    def adParser(self,response):

        images = response.css("#item-images>.slides-wrapper>.slides>figure>img ::attr(data-src)").extract()
        images.append(response.css("#item-images>.slides-wrapper>.slides>figure>img ::attr(src)").extract())

        title = response.css("#item-details>h1 ::text").extract_first()

        description = response.css("#item-details>.description ::text").extract()
        del description[len(description)-1]
        del description[len(description)-1]
        del description[len(description)-1]
        ''.join(description).replace('\n','<br>')

        number_revealer_id = response.css("#item-details>.description ::attr(data-reveal-description)").extract_first()
        number = requests.get('https://www.sheypoor.com/api/web/listings/%s/number'%(number_revealer_id), allow_redirects=True).json()['data']['mobileNumber']

        timestamp = response.css("#item-details>p>time ::attr(datetime)").extract_first()
        dateformatted = datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S.%f')

        price = response.css("#item-details>p>span>strong ::text").extract_first()
        price = convertPersianToEnglishNumber(price)

        categorization = response.css('#breadcrumbs>ul>li')
        categories = list(map(lambda x:x.strip(),categorization.css('a::text').extract()))[2:]

        state_url = categorization.css('a::attr(href)')[1].extract()
        state_name = categorization.css('a::text')[0].extract().strip()

        city_url = categorization.css('a::attr(href)')[2].extract()
        city_name = categorization.css('a::text')[1].extract().strip()

        #Proccessing Each Ad
        self.logger.info("Title : \t"+title.__str__())
        self.logger.info("Description : \t"+description.__str__())
        self.logger.info("Images ( how many ? ) : \t"+len(images).__str__())
        self.logger.info("Number : \t",number.__str__())
        self.logger.info("Dateformatted : \t"+dateformatted.__str__())
        self.logger.info("Price : \t"+price.__str__())
        self.logger.info("State ("+state_name+") : \t"+state_url)
        self.logger.info("City ("+city_name+") : \t"+city_url)
        self.logger.info("Categories : \t"+categories.__str__())