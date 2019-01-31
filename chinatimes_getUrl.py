# 引用相關套件
import requests
from bs4 import BeautifulSoup
import time, os, datetime

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context


if __name__ == "__main__":

    while True:
        # 紀錄爬蟲開始時間
        start_time = time.time()

        update_url_list = [] # 紀錄爬回來的各篇新聞網址
        count = 0  # 紀錄爬了幾筆
        page = 1  # 從蘋果即時新聞第一頁開始
        ## 開始爬蟲
        while True:
            outerurl = "https://www.chinatimes.com/realtimenews/?page=" + str(page)
            if page == 40:
                print("處理頁面：", outerurl)
            session = requests.session()
            page_response = session.get(outerurl, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

            page_html = BeautifulSoup(page_response.text)
            page_html = page_html.find("div", class_="listRight")
            if page_html.text.replace(" ", "").replace("\n", "") == "":
                break
            page_html = page_html.find_all("li", class_="clear-fix")

            for resp in page_html:
                a_list = resp.find_all("a")
                news_url = "https://www.chinatimes.com" + a_list[0]["href"]
                if news_url not in update_url_list:
                    update_url_list.append(news_url)
                count = count + 1
            time.sleep(10)
            if page == 90:
                break
            page = page + 1

        old_url_list = [] # 紀錄之前爬過的新聞網址
        # 開啟紀錄全部新聞網址的檔案
        if os.path.exists("./data/CT_news_url.txt"):
            with open("./data/CT_news_url.txt", "r", encoding="utf-8") as f:
                old_url_list = f.read().split("\n")
                old_url_list.remove("")
        #print(len(old_url_list))

        url_list = [] # 紀錄更新的新聞網址
        # 不記錄重複的新聞網址
        for url in update_url_list:
            if url not in old_url_list:
                url_list.append(url)
        #print(len(url_list))

        ## 如果檔案存在
        if os.path.exists("./data/update_CT_news_url.txt"):
            old_update_url_list = [] # 紀錄之前更新但還沒爬新聞內容的新聞網址
            new_update_url_list = [] # 紀錄此次更新的新聞網址
            new_update_url_list = url_list.copy()
            # 開啟之前紀錄更新的新聞網址的檔案
            with open("./data/update_CT_news_url.txt", "r", encoding="utf-8") as f:
                old_update_url_list = f.read().split("\n")
                old_update_url_list.remove("")
                #print(len(old_update_url_list))
                # 將此次更新的新聞網址跟之前更新但還沒爬新聞內容的新聞網址合併
                new_update_url_list.extend(old_update_url_list)
                #print(len(new_update_url_list))
            # 將更新的新聞網址存檔
            with open("./data/update_CT_news_url.txt", "w", encoding="utf-8") as f:
                for url in new_update_url_list:
                    f.write(str(url + "\n"))
        ## 如果檔案不存在
        else:
            # 將更新的新聞網址存檔
            with open("./data/update_CT_news_url.txt", "w", encoding="utf-8") as f:
                for url in url_list:
                    f.write(str(url + "\n"))

        # 將更新的新聞網址跟之前紀錄的新聞網址合併
        url_list.extend(old_url_list)
        # 將全部新聞網址存檔
        with open("./data/CT_news_url.txt", "w", encoding="utf-8") as f:
            for url in url_list:
                f.write(str(url + "\n"))

        # 紀錄存檔結束時間
        end_time = time.time()
        print("Save time:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        print('Done, Time cost: %s ' % (end_time - start_time))
        time.sleep(400)

# a_list = resp.find_all("a")
# news_title = a_list[0].text.replace("\n", "").lstrip(" ")
# news_url = "https://www.chinatimes.com" + a_list[0]["href"]
# news_source = a_list[1].text.replace("\n", "").lstrip(" ")
# news_tag = a_list[2].text.replace("\n", "").lstrip(" ")
# news_time = resp.find("time").text.split(" ")
# news_time = news_time[1].replace("/", "-") + " " + news_time[0]

