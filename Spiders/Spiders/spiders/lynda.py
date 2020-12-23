import scrapy
import csv, json
from urllib.parse import quote

class LyndaSpider(scrapy.Spider):
    name = 'lyndaSpider'
    allowed_domains = ['lynda.com']
    start_urls = ['https://www.lynda.com/learning-paths/']
    data = {}
    data['tracks'] = []

    def parse(self, response):
        industries = response.css("div.tab-content > div")
        csIndustries = ['Developer','IT','Web']
        for industry in industries:
            if industry.css("h3::text").extract()[0] in csIndustries:
                cards = industry.css("div.card")
                for i,card in enumerate(cards):
                    title = card.css("h4::text").extract()[0]
                    link = card.css("a::attr(href)").extract()[0]
                    track = {'name':title}
                    self.data['tracks'].append(track)
                    yield response.follow(url=link,callback=self.parse_a_learning_path,meta={'index':i})
                    break
        with open('data.json', 'w') as outfile:
            json.dump(self.data, outfile)
    
    def parse_a_learning_path(self, response):
        courses = response.css("div.title-author-info > h2::text").extract()
        self.data['tracks'][response.meta.get('index')]['courses'] = []
        
        for course in courses:
            self.data['tracks'][response.meta.get('index')]['courses'].append({'name':course})
            yield response.follow(url=f'/search?q={quote(course)}',callback=self.parse_search_result, meta={'key':course})
            break

    def parse_search_result(self,response):
        searchKey = response.meta.get('key')
        searchResult = response.css('li.card-cont')
        link = ''
        for card in searchResult:
            if searchKey.strip()==card.css("img::attr(alt)").extract()[0].strip():
                link = card.css("a::attr(href)").extract()[0]
                #print('Search result:',card.css("img::attr(alt)").extract()[0],searchKey)
                break
        if len(link) > 0:
            yield response.follow(url=link,callback=self.parse_a_course)

    def parse_a_course(self,response):
        skills = response.css('div.subject-tags > a > em::text').extract()
        #print(skills)

