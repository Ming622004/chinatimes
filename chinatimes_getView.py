from bs4 import BeautifulSoup
import time, os, json
import requests, datetime

if __name__ == "__main__":
    # 建立路徑

    while True:
        start_time = time.time()

        # 開始爬蟲

        view_list = []  # 紀錄爬回來的新聞觀看數
        for i in range(1, 81):
            hoturl = "https://www.chinatimes.com/realtimenews/hot/?page=" + str(i)
            if i == 40 :
                print("正在處理頁面:", hoturl)

            try:
                session = requests.session()
                page_response = session.get(hoturl, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                if str(page_response) == "<Response [200]>":
                    page_html = BeautifulSoup(page_response.text)
                    hot_content = page_html.find("div", class_="listRight")
                    if hot_content.text == "":
                        break

                    web_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                    for news in hot_content.find_all("li"):
                        news_url = news.find_all("a")[0]["href"]
                        # print(news_url)
                        news_view = news.find("div").find("span").text
                        news_tag = news.find("div", class_="kindOf").text
                        view_list.append({"news_link": news_url[2:],
                                          "news_tag": news_tag.replace(" ", "").replace("\n", ""),
                                          "view": news_view,
                                          "time": web_time})

            except Exception as e:
                print("Crawler part Error")
                continue
            time.sleep(1)

        # end_time = time.time()
        # print('Crawler Done, Time cost: %s ' % (end_time - start_time))

        # 開始存檔
        # start_time = time.time()

        date_list = []  # 紀錄爬取觀看數的日期
        count = 0  # 紀錄爬了幾筆
        link_list = [] # 紀錄是否有重複的網址
        for view in view_list:
            if view["news_link"] in link_list:
                break
            else:
                link_list.append(view["news_link"])
            # print(view)
            if not view["time"].split(" ")[0] in date_list:
                date_list.append(view["time"].split(" ")[0])
            count = count + 1

        # 下面存檔參考冠廷的
        for date in date_list:
            date_view_list = []  # 紀錄分類過的新聞觀看數
            for view in view_list:
                if view["time"].split(" ")[0] == date:
                    date_view_list.append(view)
            view_dict = {"date": date, "views": date_view_list}



            ## 如果檔案存在
            if os.path.exists("./data/chinatimes/views/" + date + "_apple_news_view.json"):
                # 開啟之前紀錄新聞觀看數的檔案
                with open("./data/chinatimes/views/" + date + "_apple_news_view.json", "r", encoding="utf-8") as f:
                    file_content = json.load(f)
                # 將依照爬取日期分類的新聞觀看數存檔
                with open("./data/chinatimes/views/" + date + "_apple_news_view.json", "w", encoding="utf-8") as f:
                    # 將每筆新的新聞觀看數加入之前的紀錄
                    for view in date_view_list:
                        file_content["views"].append(view)
                    json.dump(file_content, f)
            ## 如果檔案不存在
            else:
                # 將依照爬取日期分類的新聞觀看數存檔
                with open("./data/chinatimes/views/" + date + "_apple_news_view.json", "w", encoding="utf-8") as f:
                    json.dump(view_dict, f)

        end_time = time.time()
        timecost = end_time - start_time
        print("Save time:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        print('Save Done, Total Time Cost: %s ' % timecost)

        if timecost < 299:
            time.sleep(299 - timecost)
        else:
            time.sleep(5)

# end