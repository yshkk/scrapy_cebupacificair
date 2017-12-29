import json
import xmltodict
import scrapy
import re,os,stat,time
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import datetime
class FlightSpider(scrapy.Spider):
    """This spider crawls the CebuPacific website select page."""
    name = "flight-sale"
    allowed_domains = ["cebupacificair.com"]
    start_urls = ['https://beta.cebupacificair.com']
    currentDate = datetime.datetime(2018, 10, 1)
    endDate = datetime.datetime(2018, 12, 31)
    delta = (endDate - currentDate).days
    def __init__(self, origins='PEK,MNL'):
        """:param origins: comma-separated ORIGIN of flights to look for"""
        self.allowed_origins = self._get_origins(origins) or []
        with open("./trip.csv", 'w') as f:
            pass
    def start_requests(self):
        yield scrapy.Request(url= self.start_urls[0], callback=self.start_query)

    def start_query(self,response = {}):
        print("\033[36;1mStart querying\n \033[0m")
        time_str = self.currentDate.strftime('%Y-%m-%d')
        url = 'https://beta.cebupacificair.com/Flight/Select?o1={}&d1={}&o2=&d2=&dd1={}&ADT=1&CHD=0&INF=0&inl=0&pos=cebu.cn&culture=zh-cn'.format(self.allowed_origins[0],self.allowed_origins[1],time_str)
        yield scrapy.Request(url,callback = self.parse_page)
            
    def parse_page(self, response):
         # We need to retrieve the HTML contents within the server response
        bs = BeautifulSoup(response.body,"lxml")
        days = bs.select('div.flights-schedule-col')
        if(self.currentDate>datetime.datetime(2018, 10, 28)):
            print("\033[36;1m{}\n \033[0m".format(days))
        for day in days:
            price = day.select('.price')
            realprice = float('nan')
            unit = 'not available'
            if len(price) == 2:
                unit = price[0].text.split(' ')[-1]
                realprice = float(price[1].text.replace(',',''))
            with open("./trip.csv", 'a') as f:
                date = self.currentDate + datetime.timedelta(days=days.index(day)-1)
                f.write('{},{},{} \r\n'.format(date.strftime('%Y-%m-%d'),realprice,unit.encode('utf-8')))
                
        if self.currentDate < self.endDate:
            self.currentDate = self.currentDate + datetime.timedelta(days=3)
            if (self.endDate-self.currentDate).days%60==0:
                time.sleep(10)
            time_str = self.currentDate.strftime('%Y-%m-%d')
            url = 'https://beta.cebupacificair.com/Flight/Select?o1={}&d1={}&o2=&d2=&dd1={}&ADT=1&CHD=0&INF=0&inl=0&pos=cebu.cn&culture=zh-cn'.format(self.allowed_origins[0],self.allowed_origins[1],time_str)
            yield scrapy.Request(url,callback = self.parse_page)

    def _get_origins(self, origins):
        """Splits the comma-separated ORIGIN values, returns None if passed with None."""

        if origins is None:
            return None
        
        return origins.split(',')