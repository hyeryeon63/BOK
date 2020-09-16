import scrapy
import re
from naver_crawler.items import NaverCrawlerItem
from datetime import datetime
from dateutil.relativedelta import  relativedelta

##### news_office_cookie_list
##### 2227 : 연합 인포맥스
##### 1018 : E-daily
##### 1001 : 연합뉴스 
#각각의 언론사 별로 설정된 cookie를 request를 보낼때 변경해주며, 3번에 걸처 scraping 시행
class NaverSpider(scrapy.Spider):
    name = "naver"
    def start_requests(self):
        startdate = 0
        enddate = 0
        start_time = datetime(2005,5,1) # start time
        last_time = 2017
        #네이버 뉴스 페이지가 400이 한계이므로 월별로 나눠서 검색하여 파싱한다
        while True: # 17년도 까지만 크롤링 할 예
        

            if startdate != 0:
                startdate = startdate + relativedelta(months=1)
                enddate = startdate + relativedelta(months=1, days=-1)
                #날짜 formating 변환
                
                ds = datetime.strftime(startdate,'%Y.%m.%d')
                de = datetime.strftime(enddate,'%Y.%m.%d')
                
                #2017년 넘어가면 작업 중지
                if startdate.year == last_time+1:
                    break
            else : 
                startdate = start_time
                enddate = startdate + relativedelta(months=1, days=-1)
                ds = datetime.strftime(startdate,'%Y.%m.%d')
                de = datetime.strftime(enddate,'%Y.%m.%d')


            url_org = 'https://search.naver.com/search.naver?where=news&query=%EA%B8%88%EB%A6%AC&sm=tab_opt&sort=2&mynews=1&pd=3&ds={}&de={}'.format(ds, de)
            
            # 아래 request에서 cookies의 4자리 번호를 수정해가며 원하는 언론사의 뉴스 scrapy
            yield scrapy.Request(url=url_org, cookies={'news_office_checked': '2227'}, callback=self.parse_url_num)
            #request에 cookie 추가

    def parse_url_num(self, response):

        article_num=re.findall('\\d+',response.xpath('//*[@id="main_pack"]/div[2]/div[1]/div[1]/span/text()').extract()[0].split(' ')[-1].replace(',',''))[0]
        print(article_num,'------------'*3)

        #마지막 페이지넘버계산
        max_page = (int(article_num)//10)*10+1
        # print(max_page,'-----------------')
        for i in range(1,max_page,10):
            
            url=response.url+'&start={}'.format(i)

            yield scrapy.Request(url=url, meta={'article_num':article_num, 'max_page':max_page}, callback=self.parse_url)
            
    def parse_url(self, response):

        for sel in response.xpath('//*[@id="main_pack"]/div/ul/li'):
           
            med = sel.xpath('//span[@class="_sp_each_source"]/text()').extract()[0]#media 어디인지 파싱한것

            if med=='연합뉴스'or med =='이데일리':   
                url=sel.xpath('dl/dd/a/@href').extract()[0]
                time=sel.xpath('dl/dd[1]/text()').getall()[1]
                print(time)
                yield scrapy.Request(url=url, callback=self.parse_body, meta={'med':med,'time':time})
            elif med=='연합인포맥스':
                url=sel.xpath('dl/dt/a/@href').extract()[0]
                time=sel.xpath('dl/dd[1]/text()').getall()[1]
                print(time)
                yield scrapy.Request(url=url, callback=self.parse_infomax, meta={'med':med, 'time':time})

    #연합뉴스, 이데일리 파싱하는 함수
    def parse_body(self, response):
        item = NaverCrawlerItem()

        item['time'] = response.meta['time']
        item['body'] = response.xpath('//*[@id="articleBodyContents"]/text()').getall()
        item['media'] = response.meta['med']
        yield item

    #연합인포맥스부분 파싱함수
    def parse_infomax(self, response):
        item = NaverCrawlerItem()
       
        item['time'] = response.meta['time']
        
        item['body'] = response.xpath('//*[@id="article-view-content-div"]/text()').getall()
        item['media'] = response.meta['med']
        yield item

