import requests
import json
from bs4 import BeautifulSoup


def main():
    url = 'https://www.shixiseng.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    response = requests.get(url = url, headers = headers).text
    soup = BeautifulSoup(response , 'lxml')

    info = soup.find_all(class_='list-item clearfix')

    cityid_list = {}
    hot_city = info[0].find_all(class_='md_hid')
    for i in hot_city:
        city = i.get_text().strip()
        cityid = i['data-val']
        cityid_list[city] = cityid

    a_f = info[1].find_all(class_='md_hid')
    for a in a_f:
        city = a.get_text().strip()
        cityid = a['data-val']
        cityid_list[city] = cityid

    g_j = info[2].find_all(class_='md_hid')
    for g in g_j:
        city = g.get_text().strip()
        cityid = g['data-val']
        cityid_list[city] = cityid

    k_r = info[3].find_all(class_='md_hid')
    for k in k_r:
        city = k.get_text().strip()
        cityid = k['data-val']
        cityid_list[city] = cityid

    s_v = info[3].find_all(class_='md_hid')
    for s in s_v:
        city = s.get_text().strip()
        cityid = s['data-val']
        cityid_list[city] = cityid

    w_z = info[3].find_all(class_='md_hid')
    for w in w_z:
        city = w.get_text().strip()
        cityid = w['data-val']
        cityid_list[city] = cityid

    data = json.dumps(cityid_list)

    f = open('cityid_list.json', 'w', encoding='utf8')
    f.write(data)
    f.close()


if __name__ == '__main__':
    main()