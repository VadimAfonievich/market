from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from chromedriver_py import binary_path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import re
import time
import json


def timed(func):
    """
	records approximate durations of function calls
	"""

    def wrapper(*args, **kwargs):
        start = time.time()
        print('{name:<30} started'.format(name=func.__name__))
        result = func(*args, **kwargs)
        duration = "{name:<30} finished in {elapsed:.2f} seconds".format(
            name=func.__name__, elapsed=time.time() - start
        )
        print(duration)
        return result

    return wrapper


class Market:
    driver = None

    def __init__(self, proxy=None) -> None:
        service_object = Service(binary_path)
        options = webdriver.ChromeOptions()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        if proxy is not None:
            proxyO = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': f'{proxy}',
                'sslProxy': f'{proxy}',
                'noProxy': 'localhost,127.0.0.1'
            })

            proxyO.add_to_capabilities(capabilities)
        # capabilities['proxy'] = proxy
        # options.add_argument("--proxy-server={}".format('app:3128'))
        else:
            wire_options = {
                'addr': 'app.localhost'
            }
        # options.add_argument('--proxy-server=%s' % proxy)

        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--proxy-server={}".format('app:3128'))
        # options.headless = True

        prefs = {"profile.managed_default_content_settings.images": 2}  # disable loading images
        options.add_experimental_option("prefs", prefs)

        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f"user-agent={user_agent}")
        # self.driver = webdriver.Chrome(service=service_object, options=options, seleniumwire_options=wire_options)
        # self.driver = webdriver.Remote('http://chrome.localhost:4444/wd/hub', desired_capabilities=webdriver.DesiredCapabilities.CHROME, options=options)
        # self.driver = webdriver.Remote(command_executor='http://chrome.localhost:4444/wd/hub', desired_capabilities=webdriver.DesiredCapabilities.CHROME, options=options, seleniumwire_options=wire_options)
        #TODO: раскомментировать строку 80, закомментировать 81
        self.driver = webdriver.Remote(command_executor='http://45.67.230.21:4444/wd/hub', desired_capabilities=capabilities, options=options, )
        # self.driver = webdriver.Remote(command_executor='http://chrome.localhost:4444/wd/hub', desired_capabilities=capabilities, options=options, )
        self.driver.maximize_window()

        # self.driver.get("https://api.ipify.org?format=json")
        # ip = self.driver.page_source

        # send_command = ('POST', '/session/$sessionId/chromium/send_command')
        # self.driver.command_executor._commands['SEND_COMMAND'] = send_command
        # self.driver.execute('SEND_COMMAND', dict(cmd='Network.clearBrowserCookies', params={}))
        pass

    def get_driver(self):
        return self.driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()

    def get_page_by_url(self, url):
        while True:
            try:
                self.driver.get(url)
                break
            except Exception as e:
                time.sleep(1)
                self.driver.quit()
                print(e)

        try:
            # print(self.driver.page_source)
            dom = pq(self.driver.page_source)
            button = dom.find(".CheckboxCaptcha-Button")

            # значит капчу нам показали и мы ее обходим
            if button:
                # print("Чек-бокс есть!")
                while (True):
                    # проходим капчу пока не пройдем
                    result = self.pass_captcha()
                    if result:
                        break
        except Exception as e:
            print(e)
            # print("Чекбокса нет!")

        # вернули страницу
        # pageSource = self.driver.execute_script("return document.body.innerHTML;")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # self.driver.get("view-source:"+url)
        # pageSource = self.driver.find_element(By.TAG_NAME, 'body').text
        pageSource = self.driver.page_source
        time.sleep(2)
        return pageSource

    # return self.driver.page_source

    def get_main_page(self):
        return self.get_page_by_url("https://market.yandex.ru/")

    def pass_captcha(self):
        clickable = self.driver.find_element(By.CLASS_NAME, "CheckboxCaptcha-Button")
        webdriver.ActionChains(self.driver).click(clickable).perform()

        try:
            # print("Found CAPTCHA!")

            self.driver.save_screenshot("screenshot.png")
            html_code = self.driver.page_source

            elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.AdvancedCaptcha-View img"))
            )

        except:
            return True
        finally:
            pass

        dom = pq(self.driver.page_source)
        captcha_link = dom.find("div.AdvancedCaptcha-View img").attr('src')
        # print(captcha_link)

        response = requests.get(captcha_link)
        filename = "filename.jpg"
        open(filename, "wb").write(response.content)
        # key = "194303913cb8b39ad644272f17520a06"
        # key = "c8b0482c754458c754c4b9dc0ae5a3cf"
        key = "e8bc9aaa8f019c9abf43f7cdacd68e21"


        r = requests.post("http://rucaptcha.com/in.php", data={
            "key": key,
            "lang": "ru",
        }, files={
            "file": ("filename.jpg", open(filename, "rb"))
        })

        # print(r.text)
        rr = r.text.split("|")
        result = ''
        if rr[0] == 'OK':
            rr_id = rr[1]
            while (True):
                time.sleep(1)
                r = requests.get(f"http://rucaptcha.com/res.php?key={key}&action=get&id={rr_id}")
                # print(r.text)
                rr = r.text.split("|")
                if rr[0] == 'OK':
                    result = rr[1]
                    break
                if rr[0] == 'ERROR_CAPTCHA_UNSOLVABLE':
                    return True
                if rr[0] == 'ERROR_WRONG_CAPTCHA_ID':
                    return True

        if result:
            text_input = self.driver.find_element(By.ID, "xuniq-0-1")
            text_input.send_keys(result)
            button = self.driver.find_element(By.CLASS_NAME, "CaptchaButton_view_action")
            webdriver.ActionChains(self.driver).click(button).perform()

        return True

    def get_product_by_url(self, url):
        pass

    # @timed
    def get_product_by_id(self, product_id):
        return self.get_page_by_url(f"https://market.yandex.ru/product/{product_id}")

    # @timed
    def get_product_specs_by_id(self, product_id):
        return self.get_page_by_url(f"https://market.yandex.ru/product/{product_id}/spec")

    # @timed
    def get_product_reviews_by_id(self, product_id):
        return self.get_page_by_url(f"https://market.yandex.ru/product/{product_id}/reviews?cpa=1")

    # @timed
    def get_model_name_dy_id(self, product_id):
        return self.get_page_by_url(f"view-source:https://market.yandex.ru/product/{product_id}/spec")

    # @timed
    def get_category_by_url(self, url):
        return self.get_page_by_url(url)

    def set_location(self):
        title = ""
        try:
            # html_proxy = self.get_page_by_url("https://iphey.com/")
            # time.sleep(5)
            # self.driver.get_screenshot_as_file("proxy_in.png")
            # print(html_proxy)

            # html = self.driver.get("https://market.yandex.ru/")
            html = self.get_page_by_url("https://market.yandex.ru/")
            # print("html получил")
            # time.sleep(2)
            # print(self.driver.page_source)

            # # прокрутка в самый вверх страницы
            # # Получить текущую высоту окна браузера
            # current_height = self.driver.execute_script("return window.pageYOffset;")
            # # Прокрутить страницу в начало
            # self.driver.execute_script("window.scrollTo(0, 0);")
            # # Подтвердить прокрутку, если это необходимо
            # ActionChains(self.driver).move_by_offset(0, 0).click().perform()
            # # self.driver.get_screenshot_as_file("glavnaya_verh.png")
            # # print("прокрутил в самый верх страницы!")

            button = self.driver.find_element(By.CSS_SELECTOR, "div#hyperlocation-unified-dialog-anchor button")
            # print(f"кнопку нашел - {button}")
            # print(self.driver.page_source)

            title = button.get_attribute("title")
            # print(f"City DO: {title}!")

            button.click()
            # print("на кнопку нажал")

            time.sleep(2)

            input = self.driver.find_element(By.CSS_SELECTOR, 'div[data-zone-name="AddressMapEdit"] input')
            # print("Элемент input нашел")
            input_value = input.get_attribute("value")

            input.click()

            action_chains = ActionChains(self.driver)
            action_chains.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()

            input.send_keys("Москва, площадь Революции, д. 2/3")
            action_chains.key_down(Keys.DOWN).key_up(Keys.DOWN).perform()
            action_chains.key_down(Keys.ENTER).key_up(Keys.ENTER).perform()

            time.sleep(1)

            title = input.get_attribute("value")
            # print(f"City POSLE: {title}!")

            button_ok = self.driver.find_element(By.CSS_SELECTOR, 'div[data-zone-name="AddressMapEdit"] button span')
            button_ok.click()
            time.sleep(1)

        except Exception as e:
            # print(e)
            pass

        return title

    # @timed
    def get_category_by_id(self, category_id, page=1):
        return self.get_page_by_url(f"https://market.yandex.ru/catalog/{category_id}/list?page={page}")

    # @timed
    def parse_products_from_html(self, text):
        dom = pq(text)
        products = dom.find("article[data-autotest-id=\"product-snippet\"]")
        items = []
        # print(f"Всего бъявлений на странице: {len(products)}")
        # time.sleep(2)
        for product in products:
            item = dict()
            item['price'] = pq(product).find("span[data-auto=\"mainPrice\"] span").eq(0).text().replace(" ", "").strip()
            if not item['price']:
                item['price'] = pq(product).find("div[data-zone-name=\"price\"] span").eq(0).text().replace(" ",
                                                                                                            "").replace(
                    "&thinsp;", "").strip()
            item['name'] = pq(product).find("h3 a").text()
            item['link'] = urljoin("https://market.yandex.ru/", pq(product).find("h3 a").attr('href'))
            m = re.search(r".*?/(\d+).*", item['link'])
            if m:
                item['id'] = m.group(1)
            item['short_specs'] = []
            lis = pq(product).find("ul[data-auto=\"specs-from-filters\"] li")
            if not lis:
                lis = pq(product).find("ul[data-auto=\"snippet-specs\"] li")

            for li in lis:
                r = pq(li).text()
                rr = r.split(":", 1)
                if rr[0] == 'Производитель':
                    item['brand'] = rr[1].strip()
                if rr[0] == 'Тип':
                    item['type'] = rr[1].strip()
                ss = {"label": rr[0], "value": rr[1].strip()}
                item['short_specs'].append(ss)

            items.append(item)
        return items

    def parse_product_brand(self, text):
        dom = pq(text)
        brand = dom.find("div[data-zone-name=\"AllVendorProductsLink\"] a span").text()
        if brand == "":
            brand = "no_manufacturer_name"
        return brand

    def parse_product_price(self, text):
        dom = pq(text)
        price = dom.find("span[data-auto=\"mainPrice\"] span").eq(0).text().replace(" ", "").strip()

        #TODO: change price
        try:
            if price == "":
                price = re.search(r'<span data-auto="price-value">(.*?)</span>', text).group(1).replace(" ", "")
                return price
        except Exception as ex:
            return price

    def parse_product_images(self, text):
        dom = pq(text)
        images = []
        imgs = dom.find("ul[data-auto=\"gallery-nav\"] li img")

        if imgs:
            for img in imgs:
                images.append(pq(img).attr('src'))
            return images
        elif imgs == []:
            try:
                img = re.search('class="_2gUfn" src="(.+?)"', text).group(1)
                images.append(img)
                return images
            except Exception as ex:
                # print(f"Не найдены картинки. Ошибка {ex}")
                return images
        else:
            images = []
            return images

    def parse_reviews(self, text):
        try:
            reviews = {}
            soup = BeautifulSoup(text, 'html.parser')
            authors = soup.find_all('meta', itemprop='author')
            dates_published = soup.find_all('meta', itemprop='datePublished')
            descriptions = soup.find_all('meta', itemprop='description')
            ratings = soup.find_all('meta', itemprop='ratingValue')

            i = 0
            for author in authors:
                author = author['content']
                date = dates_published[i]['content']
                rating = ratings[i]['content']
                description = descriptions[i]['content']
                description = description.replace("\n", " ")

                description = re.search(
                    r"(?:(Достоинства: )(.+?))?\s*(?:(Недостатки: )(.+?))?\s*(?:(Комментарий: )(.+?))?\s*$",
                    description)
                positive_comment = description.group(2) or ""
                negative_comment = description.group(4) or ""
                comment = description.group(6) or ""

                reviews[author] = {}
                reviews[author]['date'] = date
                reviews[author]['rating'] = rating
                reviews[author]['positive_comment'] = positive_comment
                reviews[author]['negative_comment'] = negative_comment
                reviews[author]['comment'] = comment

                i += 1

            return reviews

        except Exception as ex:
            # print(f"Отзывы не найдены. Ошибка: {ex}")
            return {}

    def parse_model_name(self, text):
        try:
            model_name = re.search(r'modelName.*?raw\":\"(.*?)\"}', text)
            model_name = model_name.group(1)
            return model_name
        except Exception as ex:
            # print(f"Модель не найдена: {ex}")
            return "no_model_name"

    def parse_specs(self, text):
        dom = pq(text)
        h2s = dom.find("div[data-auto=\"product-full-specs\"] h2")
        item = {}
        attributes = []
        for h2 in h2s:
            if pq(h2).text() == 'Описание':
                desc = pq(h2).next('div').text()
                if desc == "":
                    try:
                        desc = re.search(r'<h2 class="_307uP">Описание</h2><div>(.*?)</div>', text).group(1)
                        desc = desc.replace("<br>", " ")
                        item['desc'] = desc
                    except:
                        item['desc'] = desc
            if pq(h2).text() == 'Подробные характеристики':
                divs = pq(h2).next_all('div')
                for div in divs:
                    sec = {}
                    section = pq(div).children('h2').text().strip()
                    if not section:
                        continue

                    sec['name'] = section
                    dls = pq(div).find('dl')
                    attrs = []
                    for dl in dls:
                        label = pq(dl).find('dt').text()
                        value = pq(dl).find('dd').text()
                        attrs.append({'label': label, 'value': value})
                    sec['attrs'] = attrs
                    attributes.append(sec)
        item['attributes'] = attributes
        return item

    def parse_next_page_category(self, text):
        dom = pq(text)
        try:
            data = json.loads(dom.find("[data-baobab-name=next]").attr('data-zone-data'))
            if 'pageno' in data:
                return data['pageno']
        except:
            pass
        return False

    def parse_products_from_json(self, text):
        items = []
        try:
            data = json.loads(text, strict=False)
            if 'collections' in data:
                for key, widget in data['collections'].items():
                    if key == 'product':
                        for k, v in widget.items():
                            item = dict()
                            item['id'] = v['id']
                            item['name'] = v['titles']['raw']
                            imgs = []
                            for pic in v['pictures']:
                                imgs.append(
                                    f"https://avatars.mds.yandex.net/get-mpic/{pic['original']['groupId']}/{pic['original']['key']}/orig")
                            item['images'] = imgs
                            item['rating'] = v['rating']
                            item['prices'] = v['prices']
                            print(f"{item['id']} - {item}")
                            items.append(item)
                    pass
                for collection in data['collections']:
                    if collection == "searchView":
                        pass
        except Exception as e:
            print(e)
        return items
