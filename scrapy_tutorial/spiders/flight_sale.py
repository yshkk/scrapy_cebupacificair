import json
import xmltodict
import scrapy
import re,os,stat
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import datetime
class FlightSpider(scrapy.Spider):
    """This spider crawls the CebuPacific website select page."""
    name = "flight-sale"
    allowed_domains = ["cebupacificair.com"]
    start_urls = ['https://beta.cebupacificair.com']
   
    def __init__(self, origins='PEK,MNL', date="2018-07-01,2018-12-31"):
        """:param origins: comma-separated ORIGIN of flights to look for"""
        self.origins = origins.split(',')
        self.date = date.split(',')
        self.currentDate = datetime.datetime.strptime(self.date[0],'%Y-%m-%d')
        self.endDate = datetime.datetime.strptime(self.date[1],'%Y-%m-%d')
        self.delta = (self.endDate - self.currentDate).days
        self.isSearchReturn = False
        with open("./go.csv", 'w') as f:
            pass
        with open("./back.csv", 'w') as f:
            pass
    def start_requests(self):
        yield scrapy.Request(url= self.start_urls[0], callback=self.start_query)

    def start_query(self,response = {}):
        time_str = self.currentDate.strftime('%Y-%m-%d')
        url = 'https://beta.cebupacificair.com/Flight/Select?o1={}&d1={}&o2=&d2=&dd1={}&ADT=1&CHD=0&INF=0&inl=0&pos=cebu.cn&culture=zh-cn'.format(self.origins[0],self.origins[1],time_str)
        yield scrapy.Request(url,callback = self.parse_page)
            
    def parse_page(self, response):
        bs = BeautifulSoup(response.body,"lxml")
        days = bs.select('div.flights-schedule-col')
        # print("\033[36;1m{}\n \033[0m".format(days))
        daylens = len(days)
        for day in days:
            price = day.select('.price')
            realprice = ''
            if len(price) == 2:
                unit = price[0].text.split(' ')[-1]
                realprice = str(price[1].text.replace(',','')) +' ' + unit
            if not self.isSearchReturn: 
                with open("./go.csv", 'a') as f:
                    date = self.currentDate + datetime.timedelta(days=days.index(day)-1)
                    f.write('{},{} \r\n'.format(date.strftime('%Y-%m-%d'),realprice))
            else:
                with open("./back.csv", 'a') as f:
                    date = self.currentDate + datetime.timedelta(days=days.index(day)-1)
                    f.write('{},{} \r\n'.format(date.strftime('%Y-%m-%d'),realprice))
        if not self.isSearchReturn:        
            if self.currentDate < self.endDate:
                yield self.recordGo(daylens)
            else:
                #reset currentDate 
                self.currentDate = datetime.datetime.strptime(self.date[0],'%Y-%m-%d') - datetime.timedelta(days=5)
                self.isSearchReturn = True 
                yield self.recordBack(daylens)
        else:
            # pass
            if self.currentDate < self.endDate:
                yield self.recordBack(daylens)
    def recordGo(self,daylens):
        self.currentDate = self.currentDate + datetime.timedelta(days=daylens)
        time_str = self.currentDate.strftime('%Y-%m-%d')
        url = 'https://beta.cebupacificair.com/Flight/Select?o1={}&d1={}&o2=&d2=&dd1={}&ADT=1&CHD=0&INF=0&inl=0&pos=cebu.cn&culture=zh-cn'.format(self.origins[0],self.origins[1],time_str)
        return scrapy.Request(url,callback = self.parse_page)
    def recordBack(self,daylens):
        self.currentDate = self.currentDate + datetime.timedelta(days=daylens)
        time_str = self.currentDate.strftime('%Y-%m-%d')
        url = 'https://beta.cebupacificair.com/Flight/Select?o1={}&d1={}&o2=&d2=&dd1={}&ADT=1&CHD=0&INF=0&inl=0&pos=cebu.cn&culture=zh-cn'.format(self.origins[1],self.origins[0],time_str)
        return scrapy.Request(url,callback = self.parse_page)

        
        
