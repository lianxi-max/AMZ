import requests
import json
import re
import time
import pandas as pd

# 请求链接的基础部分
url = "https://jc.zhcw.com/port/client_json.php"

# 请求头
headers = {
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "connection": "keep-alive",
    "cookie": "PHPSESSID=k353q66ruk02jimb9j7d4jr6l4; Hm_lvt_692bd5f9c07d3ebd0063062fb0d7622f=1736135143,1736138117,1736312291,1736312291; Hm_lpvt_692bd5f9c07d3ebd0063062fb0d7622f=1736312291; HMACCOUNT=7C4D5C4BC8842ECA; _ga_9FDP3NWFMS=GS1.1.1736312291.2.0.1736312291.0.0.0; Hm_lvt_12e4883fd1649d006e3ae22a39f97330=1736135143,1736138117,1736312291; Hm_lpvt_12e4883fd1649d006e3ae22a39f97330=1736312291; _ga=GA1.2.1393347910.1736135143; _gid=GA1.2.163997498.1736312292",
    "host": "jc.zhcw.com",
    "pragma": "no-cache",
    "referer": "https://www.zhcw.com/",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
params = {
    'callback': 'jQuery11220057751757625421174_1736312289807',
    'transactionType': '10001001',
    'lotteryId': '1',
    'issueCount': '0',
    'startIssue': '0',
    'endIssue': '0',
    'startDate': '2000-01-01',
    'endDate': '2025-01-08',
    'type': '2',
    'pageNum': '1',
    'pageSize': '30',
    'tt': '0.5636659058832396',
    '_': '1736312289811'
    }

# 获取当前时间戳并动态生成 tt
current_timestamp = time.time()
tt = round(current_timestamp + 0.5, 10)

# 你需要抓取的页数范围（根据需求可以调整）
pages_to_scrape = 1  # 例如，抓取前10页

# 初始化 _ 参数的起始值
underscore_value = 1736312289810  # 初始值（根据实际情况调整）

# 存储所有期号的开奖数据
lottery_data = []
#获取总记录数
response = requests.get(url, params=params, headers=headers)

    # 处理JSONP格式，提取JSON数据
jsonp_data = response.text
try:
        # 提取 JSON 数据
    json_data = re.search(r'jQuery11220057751757625421174_1736312289807\((.*)\)', jsonp_data).group(1)
    data = json.loads(json_data)
    print(f"总记录数: {data['total']}, 总页数: {data['pages']}")
    pages_to_scrape = int(data['pages'])
except Exception as e:
        print(f"Error")
# 遍历各个页数进行请求
for page_num in range(1, pages_to_scrape + 1):
    # 每次请求时动态增加 _ 参数的值
    underscore_value += 1

    params = {
        'callback': 'jQuery11220057751757625421174_1736312289807',
        'transactionType': '10001001',
        'lotteryId': '1',
        'issueCount': '0',
        'startIssue': '0',
        'endIssue': '0',
        'startDate': '2000-01-01',
        'endDate': '2025-01-08',
        'type': '2',
        'pageNum': str(page_num),  # 修改为当前页数
        'pageSize': '30',
        'tt': str(tt),  # 动态生成的 tt
        '_': str(underscore_value)  # 每次请求时动态增加 _ 值
    }

    # 发送请求
    response = requests.get(url, params=params, headers=headers)

    # 处理JSONP格式，提取JSON数据
    jsonp_data = response.text
    try:
        # 提取 JSON 数据
        json_data = re.search(r'jQuery11220057751757625421174_1736312289807\((.*)\)', jsonp_data).group(1)
        data = json.loads(json_data)
        print(f"Page {page_num} 数据:")
        print(f"总记录数: {data['total']}, 总页数: {data['pages']}")
        # 遍历每期数据
        for item in data['data']:
            front_winning_numbers = item['frontWinningNum'].split(' ') 
            issue_data = {
                '期号': item['issue'],
                '开奖时间': item['openTime'],
                # 拆分前区号码为6列
                '前区号码1': front_winning_numbers[0],
                '前区号码2': front_winning_numbers[1],
                '前区号码3': front_winning_numbers[2],
                '前区号码4': front_winning_numbers[3],
                '前区号码5': front_winning_numbers[4],
                '前区号码6': front_winning_numbers[5],
                '后区中奖号码': item['backWinningNum'],
                '一等奖人数': item['winnerDetails'][0]['baseBetWinner']['awardNum'],
                '一等奖奖金': item['winnerDetails'][0]['baseBetWinner']['awardMoney'],
                '二等奖人数': item['winnerDetails'][1]['baseBetWinner']['awardNum'],
                '二等奖奖金': item['winnerDetails'][1]['baseBetWinner']['awardMoney'],
                '三等奖人数': item['winnerDetails'][2]['baseBetWinner']['awardNum'],
                '三等奖奖金': item['winnerDetails'][2]['baseBetWinner']['awardMoney'],
                '四等奖人数': item['winnerDetails'][3]['baseBetWinner']['awardNum'],
                '四等奖奖金': item['winnerDetails'][3]['baseBetWinner']['awardMoney'],
                '五等奖人数': item['winnerDetails'][4]['baseBetWinner']['awardNum'],
                '五等奖奖金': item['winnerDetails'][4]['baseBetWinner']['awardMoney'],
                '六等奖人数': item['winnerDetails'][5]['baseBetWinner']['awardNum'],
                '六等奖奖金': item['winnerDetails'][5]['baseBetWinner']['awardMoney']
            }
            # 将数据添加到列表
            lottery_data.append(issue_data)

    except Exception as e:
        print(f"Error processing page {page_num}: {e}")

# 将数据保存到 Excel 文件
df = pd.DataFrame(lottery_data)

# 使用 openpyxl 引擎保存到 Excel 文件
df.to_excel("福彩双色球历史数据.xlsx", index=False, engine='openpyxl')

print("数据已保存到 福彩双色球历史数据.xlsx 文件中")
