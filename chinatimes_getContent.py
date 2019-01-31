# 引用相關套件
import time, os, json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

if __name__ == "__main__":
    tag_dict = {"政治": "politic",
            "生活": "life",
            "言論": "opinion",
            "娛樂": "star",
            "話題": "hottopic",
            "社會": "society",
            "國際": "world",
            "兩岸": "chinese",
            "財經": "money",
            "科技": "technologynews",
            "專輯": "album",
            "快點TV": "tube",
            "軍事": "armament",
            "玩食": "travel",
            "體育": "sports",
            "樂時尚": "styletc",
            "房市": "housefun",
            "快點購": "gotvshopping",
            "中國時報": "chinatimes",
            "工商時報": "commercialtimes",
            "旺報": "wantdaily",
            "時報周刊": "ctweekly",
            "周刊王": "wantweekly",
            "孝親獎": "loveparents",
            "更多": "more"}
    while True:

        # 開啟要爬的新聞網址檔案
        while True:
            if os.path.exists("./data/update_CT_news_url.txt.bak"):
                with open("./data/update_CT_news_url.txt.bak", "r", encoding="utf-8") as f:
                    url_list = f.read().split("\n")
                break
            elif os.path.exists("./data/update_CT_news_url.txt"):
                os.rename("./data/update_CT_news_url.txt", "./data/update_CT_news_url.txt.bak")
                with open("./data/update_CT_news_url.txt.bak", "r", encoding="utf-8") as f:
                    url_list = f.read().split("\n")
                break
            else:
                time.sleep(400)

        # 紀錄爬蟲開始時間
        start_time = time.time()

        news_list = [] # 紀錄爬回來的新聞內容
        date_list = [] # 紀錄新聞發布日期

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        i_count = 0
        print("Total url:", len(url_list))
        for news_url in url_list:
            driver = Chrome("/usr/local/share/chromedriver", chrome_options=chrome_options)

            if news_url == "":
                continue

            # print("處理頁面:", news_url)
            i_count = i_count + 1
            if i_count == 20:
                print("已經處理20個網頁")
                i_count = 0
            #     driver.quit()
            #     time.sleep(20)
            #     driver = Chrome("./chromedriver", chrome_options=chrome_options)

            driver.get(news_url)
            try:
                keyword = driver.find_element_by_xpath('//*[@name="news_keywords"]')
                keyword_list = keyword.get_attribute("content").replace(" ", "").split(",")
                # print(keyword_list)

                news_title = driver.find_element_by_id("h1").text

                news_create_time = driver.find_element_by_class_name("reporter")
                news_create_time = news_create_time.find_element_by_tag_name("time").text
                news_create_time = news_create_time.replace("年", "-").replace("月", "-").replace("日", "")

                content1 = driver.find_element_by_class_name("clummbox")
                content = content1.find_elements_by_tag_name("p")
                news_content = ""
                for cont in content:
                    news_content = news_content + cont.text

                if news_content[-1] == ")":
                    for i in range(2, 12):
                        i2 = i * -1
                        if news_content[i2] == "(":
                            news_content = news_content[:i2]
                            break

                try:
                    news_pageindex = driver.find_element_by_class_name("page_index")
                    h6 = news_pageindex.find_elements_by_tag_name("h6")
                    news_source = h6[1].text
                    news_tag = h6[2].text
                except Exception as e:
                    with open("./data/error.log", "a", encoding="utf-8") as f_err:
                        f_err.write("getTag_Error:" + news_url + "\n")
                    print("tag_error")


                fb_link = driver.find_element_by_xpath('//*[@title="fb:comments Facebook Social Plugin"]')
                news_fburl = fb_link.get_attribute("src")

                news_dict = {"id": "chinatimes-" + tag_dict[news_tag] + "-"+ news_url.split("/")[-1] ,
                             "news_create_time": news_create_time,
                             "news_link": news_url,
                             "news_fburl": news_fburl,
                             "news_keyword": keyword_list,
                             "news_title": news_title,
                             "news_tag": news_tag,
                             "news_source": news_source,
                             "news_content": news_content}
                # print(news_dict)
                news_list.append(news_dict)
                driver.quit()
            except Exception as e:
                driver.quit()
                print("網頁內容錯誤")
                with open("./data/error.log", "a", encoding="utf-8") as f_err:
                    f_err.write("getContent_Error:" + news_url + "\n")
                continue
            time.sleep(3)

        # print(news_list)
        ## 不紀錄重複的新聞發布日期
        for news in news_list:
            #print(news)
            if not news["news_create_time"].split(" ")[0] in date_list:
                date_list.append(news["news_create_time"].split(" ")[0])

        # 紀錄爬蟲結束時間
        end_time = time.time()
        print('Crawler Done, Time cost: %s ' % (end_time - start_time))

        # 紀錄存檔開始時間
        start_time = time.time()

        ## 將每筆新聞依照發布日期分類
        for date in date_list:
            date_news_list = [] # 紀錄分類過的新聞內容
            for news in news_list:
                if news["news_create_time"].split(" ")[0] == date:
                    date_news_list.append(news)
            news_dict = {"date": date, "news": date_news_list}

            ## 如果檔案存在
            if os.path.exists("./data/chinatimes/content/" + date + "_CT_news.json"):
                # 開啟之前紀錄新聞內容的檔案
                with open("./data/chinatimes/content/" + date + "_CT_news.json", "r", encoding="utf-8") as f:
                    file_content = json.load(f)
                # 將依照發布日期分類的新聞內容存檔
                with open("./data/chinatimes/content/" + date + "_CT_news.json", "w", encoding="utf-8") as f:
                    # 將每筆新的新聞內容加入之前的紀錄
                    for news in date_news_list:
                        file_content["news"].append(news)
                    json.dump(file_content, f)
            ## 如果檔案不存在
            else:
                # 將依照發布日期分類的新聞內容存檔
                with open("./data/chinatimes/content/" + date + "_CT_news.json", "w", encoding="utf-8") as f:
                    json.dump(news_dict, f)

        os.remove("./data/update_CT_news_url.txt.bak")
        end_time = time.time()
        print('Save Done,Total Time cost: %s ' % (end_time - start_time))
        time.sleep(200)
