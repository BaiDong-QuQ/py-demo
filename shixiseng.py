import re
import csv
import requests
import jieba
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.misc import imread
from bs4 import BeautifulSoup
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import seaborn as sns


import warnings
warnings.filterwarnings('ignore')
# 不发出警告


def get_one_page(cityid, keyword, pages):
    # 获取网页html内容并返回
    paras = {
        'k': keyword,
        'p': pages
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
        'Host': 'www.shixiseng.com',
        'Referer': 'https://www.shixiseng.com/gz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    url = 'https://www.shixiseng.com/interns/c-{}_?'.format(cityid)

    # 获取网页内容，返回html数据
    response = requests.get(url, headers=headers, params=paras)
    # 通过状态码判断是否获取成功
    if response.status_code == 200:
        return response.text
    return None


def get_mpage(response):
    mpage = re.findall('.*?p=(\d+)">尾页</a>.*?',response)[0]
    return int(mpage)


def get_detail_pageinfo(response):
    hrefs = re.findall('.*?<a class="name" href="(.*?)" target=.*?', response, re.S)
    return hrefs


def get_detail_page(href):
    url = 'https://www.shixiseng.com' + href

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
        'Host': 'www.shixiseng.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    # 获取网页内容，返回html数据
    response = requests.get(url=url, headers=headers)
    # 通过状态码判断是否获取成功
    if response.status_code == 200:
        return response.text
    return None


def parse_detail_info(response):
    response = decrypt_text(response)
    soup = BeautifulSoup(response, 'lxml')

    info1 = soup.find(class_='job-header')
    job = info1.find(class_='new_job_name').get_text()

    info1_detail = info1.find(class_='job_msg')
    salary = info1_detail.find(class_='job_money cutom_font').get_text()
    city = info1_detail.find(class_='job_position').get_text()
    education = info1_detail.find(class_='job_academic').get_text()
    workday = info1_detail.find(class_='job_week cutom_font').get_text()
    worktime = info1_detail.find(class_='job_time cutom_font').get_text()

    job_good = info1.find(class_='job_good').get_text()
    job_detail = soup.find(class_='job_detail').get_text().replace('\n','')

    info2 = soup.find(class_='job-com')
    company_href_pre = info2.a
    company_href = 'https://www.shixiseng.com' + company_href_pre['href']
    company_pic_pre = info2.find('img')
    company_pic = company_pic_pre['src']

    company_info = info2.find('div')
    company_name = company_info.get_text()
    company_scale = info2.find(class_='com-num').get_text()
    company_class = info2.find(class_='com-class').get_text()

    return {
        'job':job,
        'salary':salary,
        'city':city,
        'education':education,
        'workday':workday,
        'worktime':worktime,
        'job_good':job_good,
        'job_detail':job_detail,
        'company_pic':company_pic,
        'company_name':company_name,
        'company_scale':company_scale,
        'company_class':company_class
    }


def write_csv_headers(file, headers):
    # 写入表头
    with open(file, 'a', encoding='gb18030', newline='') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()


def write_csv_rows(file, headers, rows):
    # 写入行
    with open(file, 'a', encoding='gb18030', newline='') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writerow(rows)


def read_scv(file):
    data = pd.read_csv(file , engine = 'python')
    return data


def decrypt_text(text):
    # 定义文本信息处理函数，通过字典mapping中的映射关系解密
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text


def write_txt_file(file, txt):
    # 写入txt文本
    with open(file, 'a', encoding='gb18030', newline='') as f:
        f.write(txt)


def read_txt_file(file):
    # 读取txt文本
    with open(file, 'r', encoding='gb18030', newline='') as f:
        return f.read()


def wordcloud(words_df, keyword, cityid):
    stopwords = pd.read_csv("stopwords.txt", index_col=False, quoting=3, sep=" ", names=['stopword'], encoding='utf-8')
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)]

    words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数": np.size})
    words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

    # 设置词云属性
    color_mask = imread('backgroud.png')
    wordcloud = WordCloud(font_path="simhei.ttf",   # 设置字体可以显示中文
                    background_color="white",       # 背景颜色
                    max_words=100,                  # 词云显示的最大词数
                    mask=color_mask,                # 设置背景图片
                    max_font_size=100,              # 字体最大值
                    random_state=42,
                    width=1000, height=860, margin=2,# 设置图片默认的大小,但是如果使用背景图片的话,                                                   # 那么保存的图片大小将会按照其大小保存,margin为词语边缘距离
                    )


    # 生成词云, 可以用generate输入全部文本,也可以我们计算好词频后使用generate_from_frequencies函数
    word_frequence = {x[0]:x[1]for x in words_stat.head(100).values}
    word_frequence_dict = {}
    for key in word_frequence:
        word_frequence_dict[key] = word_frequence[key]

    wordcloud.generate_from_frequencies(word_frequence_dict)
    # 从背景图片生成颜色值
    image_colors = ImageColorGenerator(color_mask)
    # 重新上色
    wordcloud.recolor(color_func=image_colors)
    # 保存图片
    picname = cityid + "_" + keyword + '_' + '热词图.png'
    wordcloud.to_file(picname)
    plt.imshow(wordcloud)
    plt.axis("off")


def education_pie(data, city, keyword):
    s = data.groupby('education').count()
    n = len(s.index)
    lst = ['salmon','yellowgreen','lightskyblue']
    if n >= 4:
        lst.append('violet')

    plt.axis('equal')  # 保证长宽相等
    plt.pie(s['job'],
            labels=s.index,
            colors=lst,
            autopct='%.2f%%',
            pctdistance=0.5,
            labeldistance=0.8,
            startangle=0,
            radius=1.3)
    name = city + "_" + keyword + '_' + '学历分布饼图.png'
    plt.savefig(name, dpi=300)


def salary_hist(data, city, keyword):
    data['low_salary'] = data['salary'].str.strip('／天').str.split('-').str[0]
    data['high_salary'] = data['salary'].str.strip('／天').str.split('-').str[1]
    data['mean_salary'] = ( data['low_salary'].astype(np.int) + data['high_salary'].astype(np.int) ) / 2
    s = data['mean_salary']
    mean = s.mean()

    plt.figure(figsize=(8, 4))  # 设置作图大小
    plt.title('工资分布图')  # 图名
    plt.xlabel('salary')  # x轴标签
    sns.distplot(s, hist=False, kde=True, rug=True,
                 rug_kws={'color': 'y', 'lw': 2, 'alpha': 0.5, 'height': 0.1},  # 设置数据频率分布颜色
                 kde_kws={"color": "y", "lw": 1.5, 'linestyle': '--'})  # 设置密度曲线颜色，线宽，标注、线形

    plt.axvline(mean, color='g', linestyle=":", alpha=0.8)
    plt.text(mean + 2, 0.005, 'salary_mean: %.1f元' %mean, color='g')
    # 绘制平均工资辅助线

    name = city + "_" + keyword + '_' + '工资分布直方图.png'
    plt.savefig(name, dpi=300)


def main(city, keyword, pages):
    f_cityid = open('cityid_list.json','r', encoding ='utf8')
    data_id = f_cityid.read()
    data_id = json.loads(data_id)
    cityid = data_id[city]

    csv_filename = 'sxs' + city +'_' +keyword +'.csv'
    txt_filename = 'sxs' + city + '_' + keyword + '.txt'
    headers = ['job','salary','city','education','workday','worktime','job_good','job_detail',
               'company_pic','company_name','company_scale','company_class']
    write_csv_headers(csv_filename, headers)
    n = 0

    response = get_one_page(cityid, keyword, 1)
    mpage = get_mpage(response)
    if pages >= mpage:
        pages = mpage

    for i in tqdm(range(pages)):
        # 获取该页中的所有职位信息，写入csv文件
        i = i + 1
        response = get_one_page(cityid, keyword, i)

        hrefs = get_detail_pageinfo(response)
        for href in hrefs:
            n += 1
            response_detail = get_detail_page(href)
            items = parse_detail_info(response_detail)

            pattern = re.compile(r'[一-龥]+')        # 清除除文字外的所有字符
            data = re.findall(pattern, items['job_detail'])
            write_txt_file(txt_filename, ''.join(data))          # 不能直接写data，此时的data是列表格式
            write_csv_rows(csv_filename, headers, items)
            print('已录入 %d 条数据' % n)

    content = read_txt_file(txt_filename)
    segment = jieba.lcut(content)
    words_df = pd.DataFrame({'segment': segment})
    wordcloud(words_df, keyword, city)

    data_csv = read_scv(csv_filename)
    education_pie(data_csv, city, keyword)
    salary_hist(data_csv, city, keyword)


if __name__ == '__main__':
    # 手动输入解密映射，需要时自助更新
    mapping = {'&#xf399': '0', '&#xeb70': '1', '&#xe174': '2', '&#xe8df': '3', '&#xf502': '4',
           '&#xe874': '5', '&#xe111': '6', '&#xe781': '7', '&#xe91c': '8', '&#xe8c9': '9'}

    '''
    注意：
    1、main()参数输入
    第一个参数 ：工作城市（小城市搜索不到会报错，可查看 cityid_list 文档里可搜索的城市）
    第二个参数 ：岗位关键词
    第三个参数 ：爬取的岗位网页页数，一页有10个岗位信息
    2、云图热词生图
    可更换图片，注意图片名字不变
    3、停止词
    云图生成的热词经过‘stopwords’过滤掉不必要的词语，可按需要自助添加删减
    '''
    main('广州', '数据分析', 6)
