import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import csv
import os
from datetime import datetime
'''
name：亚马逊商品关键词排名监控
author：Max

'''
#设置商品链接对应型号信息，便于查看输出信息
product_set = {
        "https://www.amazon.com/dp/XXXXXXX": "XXXXX"
       
    }
#动态请求头
def get_dynamic_headers(current_url):
    """ 动态生成请求头，设置 Referer """
    headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Connection": "keep-alive",
    # "Host": "www.amazon.com",
    "Upgrade-Insecure-Requests": "1",
    "Referer": get_dynamic_referer(current_url),  # 设置 referer 来模拟正常的浏览行为
    "cookie" : "session-id=140-1656429-1776832; i18n-prefs=USD; ubid-main=134-1275536-6754714; lc-main=en_US; regStatus=pre-register; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C20020%7CMCMID%7C30690645601436139133522644256410103990%7CMCAAMLH-1730262591%7C3%7CMCAAMB-1730262591%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1729664992s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-20027%7CvVersion%7C4.4.0; aws-target-data=%7B%22support%22%3A%221%22%7D; aws-target-visitor-id=1729657792941-191084.48_0; s_nr=1730691683624-New; s_vnum=2162691683624%26vn%3D1; s_dslv=1730691683625; s_fid=7CB30AF3B09A4B15-22273CDB6053D728; AMCV_A7493BC75245ACD20A490D4D%40AdobeOrg=1585540135%7CMCIDTS%7C20043%7CMCMID%7C30198636936680111743719346273863795657%7CMCAAMLH-1732260319%7C3%7CMCAAMB-1732260319%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1731662719s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; s_ev15=%5B%5B%27NSGoogle%27%2C%271729740801721%27%5D%2C%5B%27SCUSWPDirect%27%2C%271731655520400%27%5D%5D; ttc=1731655520400; ph_phc_tGCcl9SINhy3N0zy98fdlWrc1ppQ67KJ8pZMzVZOECH_posthog=%7B%22distinct_id%22%3A%2201932eb6-5344-7452-8f79-25e3cedda5f1%22%2C%22%24sesid%22%3A%5B1731655522483%2C%2201932eb6-534c-79c2-88eb-3e5a1bd7a2c1%22%2C1731655521100%5D%7D; session-id-time=2082787201l; skin=noskin; session-token=LPVL5TplxGSvO8kNHI6K/0dEcjolWB6v0zwzyTf8dJVSe2bXVG5YDPdDXuhl8hvr9s/DD8aeyXqr9l2rg1Q9IrwwakK8oSePlG3/Bg8XCUL8nCA8vr4XSMWmtKcRK1uAgihXbGKpzMFuCBQH8/MSwrRZu66KUABW2EyywI8XX6rX20GIqPx3ZBtYpqhi4e2vMoNhg/2bE7Xc1gxky4o1LB40z2tqlhXeHKrl9+W/kyJJNTC1CqWe4C9KlXfXyq4MB/6a9cWjM3uhFqR1FTyi8ilrxRpha4PHKrCeuo5Vt137Eaeo9JSCnPn/+XpZDm/fHrUivw4iLmdSAzaVmlD/vxxaP8rZW2Fz; csm-hit=tb:VQV9BAWAEPAKEYMS6G1D+s-KK1DVP9ZTY58R1HMRJEQ|1732842133092&t:1732842133092&adb:adblk_no"
    }
    return headers
def get_dynamic_referer(current_url):
    """ 根据当前访问的 URL 动态生成 Referer """
    referer = current_url  
    return referer
# 设置日志
logging.basicConfig(level=logging.INFO)

# 亚马逊各个国家站点的基本URL
site_urls = {
    "US": "https://www.amazon.com",
    "UK": "https://www.amazon.co.uk",
    "DE": "https://www.amazon.de",
    "FR": "https://www.amazon.fr",
    "JP": "https://www.amazon.co.jp",
    "CA": "https://www.amazon.ca",
    
}

# 亚马逊搜索结果页面URL模板
search_url = "{base_url}/s?k={search_term}"

def get_amazon_search_page(search_term, page=1, country="US"):
    """ 获取指定商品搜索页面内容 """
    base_url = site_urls.get(country)
    if not base_url:
        logging.error(f"不支持的站点: {country}")
        return None
    
    url = search_url.format(base_url=base_url, search_term=search_term) + "&page=" + str(page)
    # logging.info("当前爬取的站点"+url)
    headers = get_dynamic_headers(base_url+'/')
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果返回状态码不是200，抛出异常
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching page {page} from {country}: {e}")
        return None

def parse_search_results(html,country):
    """ 解析搜索结果页面，获取商品链接和排名 """
    base_url1 = site_urls.get(country)
    # print(base_url1)
    if not base_url1:
        logging.error(f"不支持的站点: {country}")
        return None
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find('div',{'class':'s-main-slot s-result-list s-search-results sg-row'}).find_all('div', {'data-component-type': "s-search-result"})  # 获取所有包含ASIN的商品项
    product_links = []
    for item in items:
        asin = item.get('data-asin')
        if not asin:
            continue  # 如果没有ASIN，跳过该商品
        title = item.find('span', {'class': 'a-size-base-plus a-color-base a-text-normal'})
        if title:
            title = title.get_text(strip=True)
        else :
            continue # 如果没有标题，跳过该商品
        link = base_url1 + "/dp/" +asin
        # print(link)
        product_links.append({'title': title, 'asin': asin, 'link': link})

    return product_links

def get_deal_and_coupon_info(product_url, country="US"):
    base_url = site_urls.get(country)
    headers = get_dynamic_headers(base_url+'/')

    """ 解析商品详情页信息 """
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取秒杀信息（如Deal of the Day等）
        deal = None
        deal_section = soup.find('div', {'id': 'dealPriceBlock'})
        if deal_section:
            deal_price = deal_section.find('span', {'class': 'a-size-medium a-color-price'})
            if deal_price:
                deal = deal_price.get_text(strip=True)
        #获取是否参加黑五活动
        black_section = soup.find('span',{'class':'dealBadge aok-relative'})
        if black_section:
            black_action = black_section.find('span',{'id':'dealBadgeSupportingText'})
            if black_action:
                deal = black_action.get_text(strip=True)
        # 获取优惠券信息（如Apply Coupon按钮等）
        coupon = None
        coupon_section = soup.find('span', {'data-csa-c-owner': 'PromotionsDiscovery'})
        if coupon_section:
            coupon = coupon_section.get_text(strip=True)
        else:
            apply_coupon_button = soup.find('span', {'data-csa-c-action': 'clipPromotion'})
            if apply_coupon_button:
                coupon = "优惠券可用"
                
        #获取购物车信息
        seller = None
        # sold = soup.find('div',{'class':'offer-display-feature-text'})
        sold = soup.find("div", {"id": "sellerProfileTriggerId"})
        if sold:
            # sold_by = sold.find('span',{'class':'a-size-small offer-display-feature-text-message'}).find('a',{'id':'sellerProfileTriggerId'})
            # if sold_by:
            #     seller = sold_by.get_text(strip=True)
            seller = sold.get_text(strip=True)
            print(seller)
        else:
            seller ="购物车状态异常"
        #获取商品价格信息
        price = None
        price_div = soup.find('div',{'class':'a-section a-spacing-none aok-align-center aok-relative'})
        # 查找商品页面中是否存在应用优惠券的按钮（更具通用性）
        # apply_coupon_button = soup.find('span', {'data-csa-c-action': 'clipPromotion'})
        # if apply_coupon_button:
        #     coupon = "优惠券可用"
        return deal, coupon,seller

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching product page from {country}: {e}")
        return None, None
def find_product_position(search_term, target_link, country, max_pages=5):
    """ 在搜索结果页面中查找指定商品的排名 """
    page = 1
    while page <= max_pages:
        html = get_amazon_search_page(search_term, page, country)
        if html:
            products = parse_search_results(html, country)
            # logging.info(products)
            for index, product in enumerate(products):
                if product['link'] == target_link:
                    # logging.info(f"Found product at page {page}, position {index + 1} in {country}")
                    return page, index + 1
        else:
            logging.warning(f"Unable to fetch page {page} from {country}. Retrying...")
        
        # 如果没有找到，继续获取下一页
        page += 1
        time.sleep(random.uniform(2, 5))  # 增加间隔时间，减少反爬风险

    # 如果超过最大页数还没有找到，返回未找到信息
    # logging.info(f"商品未进入前 {max_pages} 页，无法找到商品位置。")
    return None, None
def get_product_rankings(search_term,product_urls, country="US"):
    """ 查询多个商品链接的排名 """
    for product_url in product_urls:
        # 查找商品排名
        page, position = find_product_position(search_term, product_url, country)

        if page and position:
            print(f"商品在第 {page} 页，排名 {position}.")
        else:
            print("商品未能找到，可能未进入前十页。")
        print("-" * 40)
    #查询商品型号
def get_productvalue(url):
    product_set.get(url)
    if isinstance(url, str):
        return product_set.get(url, "产品型号未找到")
    else:
        return "传参格式有误"
    
def save_to_csv(data, product_link):
    """ 将爬取的数据持久化 """
    file_name = product_link
    file_path = f"D:/products/{file_name}.csv"

    # 确保保存目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    fieldnames = ['timestamp','product','rank', 'deal', 'coupon','seller']
    
    try:
        # 检查文件是否已存在，如果存在就追加数据，否则创建新文件
        file_exists = os.path.isfile(file_path)

        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:  # 如果文件不存在，写入表头
                writer.writeheader()

            # 数据字典，包含当前时间戳，商品排名等
            row = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'product':data.get("product"),
                'rank': data.get('rank'),
                'deal': data.get('deal'),
                'coupon': data.get('coupon'),
                'seller':data.get('seller')
            }
            writer.writerow(row)

        # print(f"数据已保存到 {file_path}")

    except Exception as e:
        print(f"保存数据失败: {e}")
    #批量查询
def get_products(urls,search_term):
     for product_url in urls:
        parts = product_url.split("/")
        country_code = parts[2]
        country = country_code.split(".")[2].upper()
        if country =="COM":
            country="US"
        if country =="CO":
            country="UK"
    # 查找商品在搜索结果中的位置
        page,position = find_product_position(search_term,product_url,country)
        if page and position:
            product_value = get_productvalue(product_url)
            deal, coupon,seller = get_deal_and_coupon_info(product_url, country)
            print(f"商品 {product_url} ,(型号:{product_value}) 在第 {page} 页，自然排名 {position} 卖家:{seller} 站点代码（{country}）")         
            #封装商品信息
            product_data ={
                'product':product_url,
                'rank': position,              # 商品排名
                'deal': deal,   # 秒杀信息
                'coupon': coupon,     # 优惠券信息
                'seller' :seller
            }
            if deal:
                print(f"商品活动信息: {deal}")
            else:
                print("未发现黑五活动信息。")
            if coupon:
                print(f"优惠券信息: {coupon}")
            else:
                print("未发现优惠券信息。")
        else:
            product_value = get_productvalue(product_url)
            print(f"商品 {product_url} ,(型号:{product_value})未进入前5页 无法找到位置，站点代码（{country})")   
        product_url  = product_url.split('/')[-1]
        product_name = f"{product_url}-{product_value}-{country}"
        save_to_csv(product_data,product_name)   
def main():
    # 输入商品关键词和要监控的商品链接 
    print("欢迎使用亚马逊链接监控 \n 作者: Max")
    default_value = "sunset lamp"
    search_term = input("请输入要查询的关键词：(留空默认：sunset lamp)\n")
    if not search_term:
        search_term = default_value
    target_link = input("请输入商品完整链接，多个请使用,分隔（必填）： (例如：https://www.amazon.de/dp/B0BZYV7L4V)\n") 
    product_urls = target_link.split(",")
    urls = [url.strip() for url in product_urls]
    get_products(urls,search_term)
    while True: 
        logging.info(f"等待2小时后再次爬取...")
        time.sleep(2 * 60 * 60)  # 等待2小时
        get_products(urls,search_term)
    # input("查询完毕按任意键退出...")

if __name__ == "__main__":
    main()
