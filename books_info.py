import json, time, asyncio, aiohttp
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

t0 = time.time()
data = []
count = 1

async def get_html(page_number):
    url = f'https://www.teacherspayteachers.com/Browse/Price-Range/On-Sale/Page:{page_number}'

    path = r'C:\Users\Валик\Documents\GitHub\chromedriver.exe'

    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={UserAgent().random}')
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.binary_location = 'C:\Program Files\Google\Chrome Beta\Application\chrome.exe'

    service = Service(path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)

        html = driver.page_source

        soup = BS(html, 'lxml')
        book_on_page = soup.find_all(attrs={'data-testid': 'PromotedImpressionTracker'})

        for book in book_on_page:
            title = book.find(class_='NextSearchProductRowLayout__titleContainer').find('h2').text
            author = book.find(class_='ProductRowStoreBespoke__storeName').text
            description = book.find(class_='NextSearchProductRowLayout__descriptionContainer').find(class_='SearchProductRowLayout__description').text
            try:
                sale_price = book.find(class_='ProductRowPriceAndBundleText').find(attrs={'data-testid': 'productrow-price-sale'}).text
            except Exception:
                sale_price = None
            try:
                full_price = book.find(class_='ProductRowPriceAndBundleText').find(attrs={'data-testid': 'productrow-price-original'}).text
            except Exception:
                full_price = None

            data.append({
                'title': title,
                'author': author,
                'description': description,
                'sale_price': sale_price,
                'full_price': full_price
            })

            print(count)
            count += 1

    except Exception as ex:
        print(ex)
    finally:
        driver.stop_client()
        driver.close()
        driver.quit()

async def get_page_data(session, page_number):
    global count
    url = f'https://www.teacherspayteachers.com/Browse/Price-Range/On-Sale/Page:{page_number}'

    # headers = {
    #     'accept': 'application/json',
    #     'user-agent': UserAgent().random
    # }
    async with await session.get(url=url) as response:
        page_text = await response.text()

        print(count)
        count += 1
        # soup = BS(page_text, 'lxml')
        # book_on_page = soup.find_all(attrs={'data-testid': 'PromotedImpressionTracker'})
        #
        # for book in book_on_page:
        #     title = book.find(class_='NextSearchProductRowLayout__titleContainer').find('h2').text
        #     author = book.find(class_='ProductRowStoreBespoke__storeName').text
        #     description = book.find(class_='NextSearchProductRowLayout__descriptionContainer').find(class_='SearchProductRowLayout__description').text
        #     try:
        #         sale_price = book.find(class_='ProductRowPriceAndBundleText').find(attrs={'data-testid': 'productrow-price-sale'}).text
        #     except Exception:
        #         sale_price = None
        #     try:
        #         full_price = book.find(class_='ProductRowPriceAndBundleText').find(attrs={'data-testid': 'productrow-price-original'}).text
        #     except Exception:
        #         full_price = None
        #
        #     data.append({
        #         'title': title,
        #         'author': author,
        #         'description': description,
        #         'sale_price': sale_price,
        #         'full_price': full_price
        #     })

async def gather_data():
    async with aiohttp.ClientSession():
        tasks = []
        for page_number in range(1, 43):
            tasks.append(asyncio.create_task(get_html(page_number)))

        await asyncio.gather(*tasks)

def main():
    asyncio.get_event_loop().run_until_complete(gather_data())

    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(time.time() - t0)

if __name__ == '__main__':
    main()