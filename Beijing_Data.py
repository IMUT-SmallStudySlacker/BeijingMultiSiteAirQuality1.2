import requests
import re
import pandas as pd
from datetime import datetime
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
url1 = "http://www.tianqihoubao.com/aqi/beijing.html"


def tree_void(url):
    response = requests.get(headers=headers, url=url)
    data = response.text
    tree = etree.HTML(data)
    return tree


def main():
    tree1 = tree_void(url1)
    all_data = tree1.xpath('//*[@id="content"]/div[3]/table/tr')
    data_name = tree1.xpath('//*[@id="content"]/div[3]/table/tr[1]/td')
    data_name_list = []
    for i in data_name:
        data_name_list.append(i.xpath('b/text()'))
    data_name_list = sum(data_name_list, [])
    pattern = re.compile(r'[\u4e00-\u9fa5\d\.―]+')
    all_name_list = [data_name_list]
    for j in all_data[1:]:
        string_list = j.xpath('td/text()')
        output_list = []
        for item in string_list:
            # 对于每个输入的元素，查找匹配正则表达式的子串
            result = re.findall(pattern, item)
            # 将匹配结果添加到输出列表中
            output_list += result
        all_name_list.append(output_list)
    all_name_list = all_name_list[0: 13]

    time_list = tree1.xpath('//*[@id="content"]/div[1]/text()')
    pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})'
    match = re.search(pattern, time_list[0])
    if match:
        time = match.group(1)
    time = str(time)

    url2 = 'https://www.tianqi24.com/'
    url2_list = ['haidian/', 'changping/', 'shunyi/', 'dongchengqu/', 'xichengqu/', 'shijingshan/', 'huairou/',
                 'chaoyang/']
    url2_new_list = []
    for item in url2_list:
        url2_new_list.append(url2 + item)
    url2_new_list
    temps_list = []
    for url in url2_new_list:
        temp_list = []
        response = requests.get(headers=headers, url=url)
        data = response.text
        tree = etree.HTML(data)
        temp = tree.xpath('//*[@id="main"]/section/div/div/dl/dd[1]/text()')[0]
        pres = tree.xpath('//*[@id="main"]/aside/dl[2]/dd[7]/text()')[0]
        pattern = r"\d+(\.\d+)?"
        match = re.search(pattern, pres)
        pres = match.group()
        rain = tree.xpath('//*[@id="main"]/aside/dl[2]/dd[2]/span/b/text()')[0]
        wd = tree.xpath('//*[@id="main"]/section/div/div/div[3]/span[2]/text()')[0]
        pattern = r"[\u4e00-\u9fff]*风"
        match = re.search(pattern, wd)
        wd = match.group()
        wspm = tree.xpath('///*[@id="main"]/aside/dl[2]/dd[4]/text()')[0]
        pattern = r"\d+(\.\d+)?"
        match = re.search(pattern, wspm)
        wspm = match.group()
        temp_list.append([temp, pres, rain, wd, wspm])
        temp_list = sum(temp_list, [])
        temps_list.append(temp_list)
    if len(all_name_list) == 13:
        all_name_list[1] = all_name_list[1] + temps_list[4]
        all_name_list[2] = all_name_list[2] + temps_list[1]
        all_name_list[3] = all_name_list[3] + temps_list[3]
        all_name_list[4] = all_name_list[4] + temps_list[3]
        all_name_list[5] = all_name_list[5] + temps_list[7]
        all_name_list[6] = all_name_list[6] + temps_list[4]
        all_name_list[7] = all_name_list[7] + temps_list[0]
        all_name_list[8] = all_name_list[8] + temps_list[2]
        all_name_list[9] = all_name_list[9] + temps_list[6]
        all_name_list[10] = all_name_list[10] + temps_list[1]
        all_name_list[11] = all_name_list[11] + temps_list[7]
        all_name_list[12] = all_name_list[12] + temps_list[5]
        all_name_list[0] = all_name_list[0] + ['TEMP', 'PRES', 'RAIN', 'wd', 'WSPM']

        df = pd.DataFrame(all_name_list[1:], columns=all_name_list[0])
        df.drop(labels=['AQI指数', '空气质量状况'], axis=1, inplace=True)
        time_obj = datetime.strptime(time, '%Y-%m-%d %H:%M')
        year = time_obj.year
        month = time_obj.month
        day = time_obj.day
        hour = time_obj.hour
        year_list = []
        month_list = []
        day_list = []
        hour_list = []
        for i in range(12):
            year_list.append(year)
            month_list.append(month)
            day_list.append(day)
            hour_list.append(hour)
        df['year'] = year_list
        df['month'] = month_list
        df['day'] = day_list
        df['hour'] = hour_list
        df.columns = ['station', 'PM10', 'PM2.5', 'CO', 'NO2', 'SO2', 'O3', 'TEMP', 'PRES', 'RAIN', 'wd', 'WSPM',
                      'year',
                      'month', 'day', 'hour']
        df = df[['year', 'month', 'day', 'hour', 'PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES',
                 'RAIN', 'wd', 'WSPM', 'station']]
        df['RAIN'] = df['RAIN'].apply(lambda x: float(x))
        df['PRES'] = df['PRES'].apply(lambda x: float(x) * 10)
        df['CO'] = df['CO'].apply(lambda x: float(x) * 1000)
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']].astype(str).apply('-'.join, axis=1))
        df['datetime'] = pd.to_datetime(df['datetime'].astype(str) + " " + df['hour'].astype(str) + ":00")
        df = df.drop(columns=['year', 'month', 'day', 'hour'], axis=1)
        df.replace(['海淀万柳', '怀柔镇', '昌平镇', '顺义新城'], ['万柳', '怀柔', '昌平', '顺义'], inplace=True)
        df.replace(['东风', '北风', '东北风', '西北风', '南风', '东南风', '西南风', '西风'],
                       ['E', 'N', 'NE', 'NW', 'S', 'SE', 'SW', 'W'], inplace=True)
        title = './data/气象数据' + str(month) + '月' + str(day) + '日' + str(hour) + '时.csv'
        df.to_csv(title, index=False, encoding='utf_8_sig')

    else:
        print("本次爬取失败！")


if __name__ == '__main__':
    main()
