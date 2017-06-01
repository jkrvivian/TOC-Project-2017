import requests
import re
from transitions.extensions import GraphMachine
from bs4 import BeautifulSoup

class TocMachine(GraphMachine):
    s2015_1 = 'http://justlaughtw.blogspot.com/2014/05/20151.html'
    s2015_4 = 'http://justlaughtw.blogspot.com/2014/04/20154.html'
    s2015_7 = 'http://justlaughtw.blogspot.com/2015/02/2015.html'
    s2015_10 = 'http://justlaughtw.blogspot.com/2015/04/201510.html'
    s2016_1 = 'http://justlaughtw.blogspot.com/2015/08/20161.html'
    s2016_4 = 'http://justlaughtw.blogspot.com/2015/11/20164.html'
    s2016_7 = 'http://justlaughtw.blogspot.com/2016/02/20167.html'
    s2016_10 = 'http://justlaughtw.blogspot.com/2016/04/201610.html'
    s2017_1 = 'http://justlaughtw.blogspot.com/2016/07/20171.html'
    s2017_4 = 'http://justlaughtw.blogspot.com/2016/11/20174_26.html'
    s2017_7 = 'http://justlaughtw.blogspot.com/2017/01/20177.html'
    s2017_10 = 'http://justlaughtw.blogspot.com/2017/03/201710.html'
    popularbl = 'http://www.ikanman.com/list/funv/view.html'
    comic_modify = 'http://justlaughtw.blogspot.com/search/label/%E6%BC%AB%E7%95%AB%E6%94%B9%E7%B7%A8'
    real_modify = 'http://justlaughtw.blogspot.com/search/label/%E7%9C%9F%E4%BA%BA%E6%94%B9%E7%B7%A8'
    original_modify = 'http://justlaughtw.blogspot.com/search/label/%E5%8E%9F%E5%89%B5%E5%8B%95%E7%95%AB'
    user_name = ('')
    animat_list = []
    img = []

    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )

    def get_web_page(self, url):
        resp = requests.get(
                url = url
        )
        if resp.status_code != 200:
            print('Invalid url: ', resp.url)
            return None
        else:
            return resp.text

    def on_enter_instruction1(self, update):
        update.message.reply_text("Hi, 我是 SuperHome, 你呢?")

    def is_going_to_state1(self, update):
        text = update.message.text
        return text.lower() != '/start' 
        

    def on_enter_state1(self, update):
        self.user_name = update.message.text
        update.message.reply_text("Hello," + update.message.text)
        update.message.reply_text("我可以提供以下資訊，直接輸入選項編號就好囉！\n(1) 查詢指定年度及季節新番列表\n(2) 近期宅新聞\n(3) 腐向漫畫推薦\n")

    def is_going_to_ask_for_year_season(self, update):
        return update.message.text == '1'

    def on_enter_ask_for_year_season(self, update):
        update.message.reply_text("新番一年有四期, 分別在 1 月, 4 月, 7 月和 10 月有新的產出！\n我可以幫你查 2015 年至 2017 年的新番資訊喔！\n請先告訴我你想要找哪一期的動畫呢?\n\n(格式： 2016_4, 2017_10)\n想回上一步請輸入 '4'\n")
    
    def is_going_to_check_year_season(self, update):
        if update.message.text != '4':
            lists = update.message.text.split("_") 
            yflag = (int(lists[0]) >= 2014) and (int(lists[0]) <= 2017)
            sflag = (int(lists[1]) == 1) or (int(lists[1]) == 4) or (int(lists[1]) == 7) or (int(lists[1]) == 10)
            return (yflag and sflag)
        else:
            return False

    def on_enter_check_year_season(self, update):
        # get webpage
        text = update.message.text
        page = ('')
        if text == '2017_1':
            page = self.get_web_page(self.s2017_1)
        elif text == '2017_4':
            page = self.get_web_page(self.s2017_4)
        elif text == '2017_7':
            page = self.get_web_page(self.s2017_7)
        elif text == '2017_10':
            page = self.get_web_page(self.s2017_10)
        elif text == '2016_1':
            page = self.get_web_page(self.s2016_1)
        elif text == '2016_4':
            page = self.get_web_page(self.s2016_4)
        elif text == '2016_7':
            page = self.get_web_page(self.s2016_7)
        elif text == '2016_10':
            page = self.get_web_page(self.s2016_10)
        elif text == '2015_1':
            page = self.get_web_page(self.s2015_1)
        elif text == '2015_4':
            page = self.get_web_page(self.s2015_4)
        elif text == '2015_7':
            page = self.get_web_page(self.s2015_7)
        elif text == '2015_10':
            page = self.get_web_page(self.s2015_10)
            
        # parse webpage
        soup = BeautifulSoup(page, 'html.parser')
        data = soup.find_all('span', style = re.compile('font-size: 15px;( line-height: 22.5px;)?$'))
        self.img = soup.find_all('a',  style = re.compile('clear: left; float: left; margin-bottom: 1em; margin-right: 1em;'))

        # store each animation to lists
        del self.animat_list[:]
        count = -1
        if text == '2015_4':
            self.animat_list.append([])
            self.animat_list[0].append("網球少女")
            update.message.reply_text(self.animat_list[0][0])
            count = 0

        for t in data:
            if t.text.isspace():
                continue
            else:
                name = re.search('.*《(.*)》.*', t.text)
                rest = re.search('.*》(.*)', t.text)
                if name:
                    count = count + 1
                    self.animat_list.append([])
                    self.animat_list[count].append(name.group(1))
                    self.animat_list[count].append(rest.group(1))
                    print(name.group(1))
                    update.message.reply_text(name.group(1))
                else:
                    self.animat_list[count].append(t.text)
        update.message.reply_text("有想要再知道哪一部的詳細介紹嗎？\n(1) 我想了解更多！\n(2) 返回\n")

    def is_going_to_go_deeper_animainfo1(self, update):
        return update.message.text == '1'
    
    def on_enter_go_deeper_animainfo1(self, update):
        update.message.reply_text("直接告訴我想要看哪一部吧！") 

    def is_going_to_go_deeper_animainfo2(self, update):
        return update.message.text != '2'

    def on_enter_go_deeper_animainfo2(self, update):
        retstr = ('')
        i = 0
        for i in range(len(self.animat_list)):
            if update.message.text in self.animat_list[i]:
                for j in range(len(self.animat_list[i])):
                    if j == 0:
                        retstr = "【" + self.animat_list[i][j] + "】\n\n"
                    elif j == 1:
                        retstr += "劇情: " + self.animat_list[i][j] + "\n"
                    else:
                        retstr += self.animat_list[i][j] + "\n"
                print(self.animat_list[i][0])
                break
        update.message.reply_text(retstr)
        update.message.reply_photo(self.img[i].get('href'))
        update.message.reply_text("可以再繼續查你有興趣的番喔！\n想返回就輸入 '2'\n")

    def is_going_to_go_deeper_animback(self, update):
        return update.message.text == '2'

    def on_enter_go_deeper_animback(self, update):
        update.message.text = '1'
        self.go_back(update)




    def is_going_to_news(self, update):
        return update.message.text == '2'

    def on_enter_news(self, update):
        update.message.reply_text("想知道哪個類別的新聞呢？\n(1) 原創動畫\n(2) 真人改編\n(3) 漫畫改編\n(4) 返回\n")

    def is_going_to_news_ori(self, update):
        return update.message.text == '1'

    def on_enter_news_ori(self, update):
        page = self.get_web_page(self.original_modify)
        
        # parse webpage
        update.message.reply_text("前三則 原創動畫 新聞： \n")
        soup = BeautifulSoup(page, 'html.parser')
        p = soup.find_all('div',  class_ = 'penghalus')
        i = 0
        while i < 3:
            print(p[i].text + '\n')
            u = soup.find('a', title = p[i].text)
            update.message.reply_text(u.get('href'))
            i = i + 1
        update.message.text = '2'
        self.go_back(update)

    def is_going_to_news_commod(self, update):
        return update.message.text == '3'
   
    def on_enter_news_commod(self, update):
        page = self.get_web_page(self.comic_modify)
        
        # parse webpage
        update.message.reply_text("前三則 漫畫改編 新聞： \n")
        soup = BeautifulSoup(page, 'html.parser')
        p = soup.find_all('div',  class_ = 'penghalus')
        i = 0
        while i < 3:
            print(p[i].text + '\n')
            u = soup.find('a', title = p[i].text)
            update.message.reply_text(u.get('href'))
            i = i + 1
        update.message.text = '2'
        self.go_back(update)

    def is_going_to_news_realmod(self, update):
        return update.message.text == '2'
   
    def on_enter_news_realmod(self, update):
        page = self.get_web_page(self.real_modify)
        
        # parse webpage
        update.message.reply_text("前三則 真人改編 新聞： \n")
        soup = BeautifulSoup(page, 'html.parser')
        p = soup.find_all('div',  class_ = 'penghalus')
        i = 0
        while i < 3:
            print(p[i].text + '\n')
            u = soup.find('a', title = p[i].text)
            update.message.reply_text(u.get('href'))
            i = i + 1
        update.message.text = '2'
        self.go_back(update)

    def is_going_to_news_back(self, update):
        return update.message.text == '4'

    def on_enter_news_back(self, update):
        update.message.text = self.user_name
        self.go_back(update)

    def is_going_to_boyslove(self, update):
        return update.message.text == '3'

    def on_enter_boyslove(self, update):
        update.message.reply_text("你即將到一個全新世界，禁忌又神秘，你準備好了嗎?\n(1) 什麼是「腐向」啊？\n(2) 廢話不多說，速速端上好東西吧！\n")

    def is_going_to_get_BLcomic(self, update):
        return update.message.text == '2'

    def on_enter_get_BLcomic(self, update):  
        update.message.reply_text("人氣最旺 前十名")
        page = self.get_web_page(self.popularbl)
        
        # parse webpage
        soup = BeautifulSoup(page, 'html.parser')
        p = soup.find_all('a',  class_ = 'bcover')
        self.img = soup.find_all('img')
        i = 0
        while i < 10:
            update.message.reply_text(p[i].get('title') + '\n' + self.img[i].get('src') + '\n漫畫連結：' + p[i].get('href'))
            i = i + 1
        update.message.reply_text("返回，請輸入 '3'")

    def is_going_to_teach_boyslove(self, update):
        return update.message.text == '1'
    
    def on_enter_teach_boyslove(self, update):
        update.message.reply_text("【腐女子】\n腐女子」一詞源自於日語，是由同音的「婦女子（ふじょし）」轉化而來，為喜愛BL（boys love）的女性自嘲的用語。腐女子的「腐」字在日文有無藥可救的意思，而腐女子是專門指稱對於男男愛情（BL系）作品情有獨鍾的女性，通常是喜歡此類作品的女性之間彼此自嘲的講法；非此族群以「腐女子」稱呼這些女性時，則是帶有貶低、蔑視意味的詞彙。在日本一些地方，直接稱呼對方為「腐女」是不禮貌的事情。\n\n【同人女】本來單純用來指愛好創作同人作品的女性。由於腐女喜歡由BL的觀點詮釋原創作品，所以會有不少腐女親自繪畫和書寫相關同人作品。但同人女不一定是腐女，腐女亦不一定會進行同人創作。所以同人女與腐女的定義仍然應該清楚的區別開來。\n")
        update.message.reply_text("(1) 我想繼續！\n(2) 我心臟可能負荷不了\n")

    def is_going_to_stillBL(self, update):
        return update.message.text == '1'

    def on_enter_stillBL(self, update):
        update.message.text = '2'
        self.go_back(update)
    
    def is_going_to_refuseBL(self, update):
        return update.message.text == '2'

    def on_enter_refuseBL(self, update):
        update.message.text = self.user_name
        self.go_back(update)

