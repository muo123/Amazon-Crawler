import requests
from bs4 import BeautifulSoup
import csv
import time
import random

# 配置请求头模拟浏览器访问
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.amazon.com/'
}

def scrape_amazon_product(url):
    """抓取单个产品页面数据"""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 解析产品数据
        title = soup.select_one('span#productTitle').get_text(strip=True) if soup.select_one('span#productTitle') else 'N/A'
        
        # 价格解析
        price_whole = soup.select_one('span.a-price-whole')
        price_fraction = soup.select_one('span.a-price-fraction')
        price = f"${price_whole.get_text(strip=True)}{price_fraction.get_text(strip=True)}" if price_whole and price_fraction else 'N/A'
        
        # 评分和评论数量
        rating = soup.select_one('span.a-icon-alt').get_text(strip=True).split()[0] if soup.select_one('span.a-icon-alt') else 'N/A'
        review_count = soup.select_one('span#acrCustomerReviewText').get_text(strip=True).split()[0] if soup.select_one('span#acrCustomerReviewText') else 'N/A'
        
        return {
            'Title': title,
            'Price': price,
            'Rating': rating,
            'Reviews': review_count,
            'URL': url
        }
        
    except Exception as e:
        print(f"抓取失败 {url}: {str(e)}")
        return None

def scrape_search_results(keyword, pages=1):
    """抓取搜索结果页面的多个产品"""
    base_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
    products_data = []
    
    for page in range(1, pages + 1):
        print(f"正在抓取第 {page} 页...")
        url = f"{base_url}&page={page}"
        try:
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 获取当前页所有产品链接
            product_links = []
            for item in soup.select('div.s-result-item[data-asin]'):
                link = item.select_one('a.a-link-normal.s-no-outline')
                if link and link['href']:
                    product_links.append('https://www.amazon.com' + link['href'])
            
            # 抓取每个产品的数据
            for link in product_links[:5]:  # 限制每页5个产品防止封IP
                product_data = scrape_amazon_product(link)
                if product_data:
                    products_data.append(product_data)
                time.sleep(random.uniform(1.5, 3))  # 随机延迟
            
        except Exception as e:
            print(f"搜索页抓取失败: {str(e)}")
        
        time.sleep(2)  # 页面间延迟
    
    return products_data

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Title', 'Price', 'Rating', 'Reviews', 'URL']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    # 配置参数
    SEARCH_KEYWORD = "seat covers"
    PAGES_TO_SCRAPE = 3
    OUTPUT_FILE = "amazon_market_research.csv"
    
    # 执行抓取
    print("亚马逊市场调研爬虫启动...")
    market_data = scrape_search_results(SEARCH_KEYWORD, PAGES_TO_SCRAPE)
    
    if market_data:
        save_to_csv(market_data, OUTPUT_FILE)
        print(f"成功抓取 {len(market_data)} 条产品数据，已保存至 {OUTPUT_FILE}")
    else:
        print("未获取到有效数据")