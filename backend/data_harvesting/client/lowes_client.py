import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import logging
from common.logging.log_utils import START_OF_METHOD, END_OF_METHOD
from common.logging.error.error import Error
from common.logging.error.error_messages import WEBSCRAPING_ISSUE
from common.decorators.disabled import disabled


class LowesClient:
    def __init__(self, delay, user_agent, base_url):
        self.delay = delay
        self.user_agent = user_agent
        self.base_url = base_url
        self.session = requests.Session()
        self.update_session_headers()

    def update_session_headers(self):
        """
        Updates the headers to the session attribute
        """
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.google.com/',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'}
        cookies = {
            'dbidv2': 'd45022f2-561d-43c4-a4ae-8d07608e0486',
            'EPID': 'd45022f2-561d-43c4-a4ae-8d07608e0486',
            'g_amcv_refreshed': '1',
            'AMCV_5E00123F5245B2780A490D45%40AdobeOrg': '-1303530583%7CMCIDTS%7C21049%7CMCMID%7C34079022286732675920562842150146538282%7CMCAAMLH-1756135971%7C7%7CMCAAMB-1756135971%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1755538371s%7CNONE%7CvVersion%7C3.3.0',
            'ph_aid': 'f944694a-4259-49a3-339c-71e224c1278c-74891b96eba92-4fa5114930526-260cf68419261',
            'sn': '1828',
            'sd': "%7B%22id%22%3A%221828%22%2C%22zip%22%3A%2260462%22%2C%22city%22%3A%22Orland%20Park%22%2C%22state%22%3A%22IL%22%2C%22name%22%3A%22Orland%20Park%20Lowe's%22%2C%22region%22%3A%224%22%7D",
            'zipcode': '60462',
            'nearbyid': '1828',
            'zipstate': 'IL',
            'regionNumber': '4',
            '_fbp': 'fb.1.1755531172703.724967208294849860',
            '_gcl_gs': '2.1.k1$i1755531168$u194733616',
            '_gcl_au': '1.1.1875055758.1755531173',
            'IR_PI': '12e08fa2-2413-11ef-be27-9b3fdd46cb1c%7C1755531172614',
            '_lc2_fpi': '03a9f48f544d--01k2ywzqy2cp4q3nxhzy593jm7',
            'kampyle_userid': '1e74-e9f7-4374-0840-d088-cb6d-ffec-851b',
            '_tt_enable_cookie': '1',
            '_ttp': '01K2YWZR3MZ24FY864S4D4BA9X_.tt.1',
            '_pin_unauth': 'dWlkPU16TXhaRGt4WmpndE9UVXhPQzAwTjJWbUxUZzFaREF0WkdJM01UQTBPVFUzTkRVMQ',
            'ndp_session_id': '6ee30a8b-93de-4350-80f5-c9f71957580b',
            '_scid': '3IFxIsJ13thjYRWntl34-rqWPaKMcgII',
            '_ScCbts': '%5B%5D',
            '_sctr': '1%7C1755493200000',
            'salsify_session_id': '80ddd9ff-fc2e-4971-8047-d6f362d73275',
            'BVBRANDID': '3d601ee8-2953-490e-b116-dac493ca6487',
            '_gcl_aw': 'GCL.1755533412.Cj0KCQjwnovFBhDnARIsAO4V7mBTF1Cv7UGVZilZO3-iQALkuDB1gZR66hMnlIJUXHe5Ns7Q-twQXE4aAowbEALw_wcB',
            '_gcl_dc': 'GCL.1755533412.Cj0KCQjwnovFBhDnARIsAO4V7mBTF1Cv7UGVZilZO3-iQALkuDB1gZR66hMnlIJUXHe5Ns7Q-twQXE4aAowbEALw_wcB',
            'user': '%7B%22zipPrompt%22%3Atrue%7D',
            'audience': 'DIY',
            'bm_ss': 'ab8e18ef4e',
            'al_sess': 'brukgPJGNBK59A5xZcXk0RDUp/taripR6VDs6G6l9NjwitorUNgCCYwZg6bfDWAE',
            'tpd': 'cxp0a',
            'seo-partner': '',
            'region': 'central',
            'AKA_A2': 'A',
            '_abck': 'F70E1B419F246DA723E598A3E0F8FE08~0~YAAQ8NbXF+7uVs+YAQAANh1u0w7L7SEUp+Q0fKD0geXNUhBbhG7b3tf/FgWCHpAXn5B0d9LD8XqZjvuLx7mNNN24VPF5BRrEnxE3XEOuXXVwaNLHM94FIuNmELi9ddZVH1RFKFkqbZmClLC49/DhC3L7kBm79Ca4ImxEFSYqSaSd8ydp9tj9fwEAMUuBod5peFIe6VgNSlOSEFyOBZAi+HahZB7Ww4UkDyXhBBtA1R6rOWJzzl+8C+/oWU3t2Dl6Vnn72W/7SLM6nxSTINEq4W+NLMdX09EJajdg7d/28g4sTFqaywsrka/pMt7uZ0qs6auh/mu0BPcG241W0/5nj3YRK9rJuileWBf9/fqYHHSyJ75Pf9x5r070d9WtVwEMe0vlL3j1Nw8dYUKzjC7jzbuJokcnc+NKETha3QJaRvaO/AeoRduXCCqCRdWurRQLp18sR0onUKvTLA+tOV/d4Ajbp+78ovvzIdeCXBeJr09QowmMqco8eqZ34oKFxPuu1U9Bjb4bWpv9t5fLAfEDfJm92CEQ+suBMblc4JggNdSCtJZxFxmCRy0s3TyDR2B8iszVq4ahzPq6X+cix/PGwNSDiclrU71sCxOC8nsTP3LQYQLD8BtddoXeDcZSkEkdaWG0+WQFJ6J9K+THqWO+0PpOKH0M0vxYvUUWSfMppBBwzrlJOdQav7W0PCdz7Oqfz4vVvgJ3H8w1edq25ZzcIWel/DLaZPonEdB6TfOrJDiKUkEsg4GO8oJbdxQ+dKYDCtWXCjEsnBQl3/K0vycbHK2Q2UsbcxotZ3H+X1FND6tRufukrwTN3cnI5RNZcWW0MbmgHDAiukHSJVBNEp0jWA==~-1~-1~-1~~',
            'PIM-SESSION-ID': 'vAr6Xn18NfIa8qd5',
            'luca-variant': 'variant',
            '__gads': 'ID=ca0479e23b300a2a:T=1755531171:RT=1755893866:S=ALNI_MZVzF_6mx1zfxwlIXl6hkzRiio7fw',
            '__gpi': 'UID=0000125ea0e8bad0:T=1755531171:RT=1755893866:S=ALNI_MbR4qTfrCiAFCb258657pyHeIb8PA',
            '__eoi': 'ID=702f2dc6d5ed8bdf:T=1755531171:RT=1755893866:S=AA-AfjZ1z9zGwnaFh8wK7Yr0mB3k',
            '_lgsid': '1755893868448',
            'AMCVS_5E00123F5245B2780A490D45%40AdobeOrg': '1',
            'TAsessionID': '9938b816-b300-41cb-b354-2270c29de77d|NEW',
            'IR_gbd': 'lowes.com',
            'luca-abTestVersion': 'variant',
            '_li_dcdm_c': '.lowes.com',
            '_lc2_fpi_js': '03a9f48f544d--01k2ywzqy2cp4q3nxhzy593jm7',
            '_li_ss': 'CncKBgj5ARDCGwoFCAoQwhsKBgikARDCGwoGCN0BEMIbCgYIiQEQwhsKBgiBARDCGwoFCAwQzBsKBgj1ARDCGwoGCKIBEMIbCgkI_____wcQzBsKBQgLEMIbCgYIgAIQxBsKBgjhARDCGwoGCNIBEMIbCgUIfhDCGxKIAQ3MoVFnEoABCgYIygEQwhsKBgjkARDCGwoGCJMBEMQbCgYIyQEQwhsKBgilARDCGwoGCPQBEMQbCgYIlAEQxBsKBgjmARDCGwoGCMYBEMUbCgYIxwEQxBsKBgjnARDCGwoGCMgBEMIbCgYI5QEQwhsKBgjFARDCGwoGCP4BEMIbCgYI6AEQwhsSPw2_S5_4EjgKBgjKARDCGwoGCJMBEMQbCgYIyQEQwhsKBgjFARDCGwoGCMYBEMUbCgYIxwEQxBsKBgjIARDCGw',
            'g_previous': '%7B%22gpvPageLoadTime%22%3A%220.00%22%2C%22gpvPageScroll%22%3A%2216%7C17%7C0%7C5737%22%2C%22gpvSitesections%22%3A%22hp%2Chp%2Chp%2Chp%22%2C%22gpvSiteId%22%3A%22desktop%22%2C%22gpvPageType%22%3A%22hp%22%7D',
            'bm_so': 'D822705679C318E7F4CD6D4FBA13F58EA76CFEC19F593CAD1B0EAF9FC13FB650~YAAQ8NbXF+y5V8+YAQAAittv0wTyrn0kAoeuyFhpJfRpUh26uvHc3lXdbHsIWSwrhxjKT1HyV0GyO2RMQUMUZDO3iuLIppGzua5HPEm10VGd/DFPFcYaL06DateLOp5xjbqb2Mxcgjh0YHKgOwlw/MrlPulXDc801e/zkmgSXKRTgYPtJybzdkkwtfFqWyeNC0qmcDM4+Mqjj8vMewcaXOKj0Vi1ScmhlWk/uVzQafVR/Ip9oCMMAp2qYKZfYLVsxB0tw/BpNOY8z9HTtA9ovK2d+gOV4IwDRZpOq/rgiqAkn7zEC2sOKuZ8PxQNumKUrI66qiK880UNnrkHvr5U02S1Sx1QPzcsE9RTtTadzM+j8aHoq+9A6fB2VVOygmqwFVGRDd6OKq2cA9SQnKKjeZ++iHlvRF2Lyqvz+zN09Ugp0L479+GFztR5Rl7+ouuOXKVe08+50Qc+EYpJRQ==',
            'akavpau_cart': '1755894288~id=00ca4c89d7cdd1bc516cbb42462a3d67',
            'bm_lso': 'D822705679C318E7F4CD6D4FBA13F58EA76CFEC19F593CAD1B0EAF9FC13FB650~YAAQ8NbXF+y5V8+YAQAAittv0wTyrn0kAoeuyFhpJfRpUh26uvHc3lXdbHsIWSwrhxjKT1HyV0GyO2RMQUMUZDO3iuLIppGzua5HPEm10VGd/DFPFcYaL06DateLOp5xjbqb2Mxcgjh0YHKgOwlw/MrlPulXDc801e/zkmgSXKRTgYPtJybzdkkwtfFqWyeNC0qmcDM4+Mqjj8vMewcaXOKj0Vi1ScmhlWk/uVzQafVR/Ip9oCMMAp2qYKZfYLVsxB0tw/BpNOY8z9HTtA9ovK2d+gOV4IwDRZpOq/rgiqAkn7zEC2sOKuZ8PxQNumKUrI66qiK880UNnrkHvr5U02S1Sx1QPzcsE9RTtTadzM+j8aHoq+9A6fB2VVOygmqwFVGRDd6OKq2cA9SQnKKjeZ++iHlvRF2Lyqvz+zN09Ugp0L479+GFztR5Rl7+ouuOXKVe08+50Qc+EYpJRQ==^1755893989112',
            'ak_bmsc': 'E69F2FA08D6920D9878101F73F64B2E8~000000000000000000000000000000~YAAQ8NbXF47OV8+YAQAAMA5w0xw4qjATCMICwAYiTf7tFPNd9JuRWMyVGS63PuvLAcvtHaYmXyMIRWhld4FMYZh/ev/7FWt8KrYEQ6fGjmRDHVV1Lo6UvcfYJLNReOFMF22v6Qx+mNTDJbPSoKze/+y2kxK2hQE0bx67W1h3Qxyha4ksmy4xSLHXoikN6SWCrZHdImHmTEg2W8va2OWsalLmbXDGeQt6YHi6RBnoyN6XOkG6P7TvaX5FvYQksKKhdtY+YwouJ6ChhhLgsCTc+onViIjvRbUjxeHGdpj0XnXosXEonibJA9WqWIuxWyicg8H0+A+jcc1OvF9rfY1rHeQ4DxG3rbZr2bZ1exdvR7nesjX9lJww6juKgr/mGndkiRQEC+snBDpwDzwmwIq3ynrYPb9rX5eU2ZWPQKCeBxVJTX0tyn30VtqqUZOsvDUSmyr1fhPi+7WZBFobf2w=',
            'bm_s': 'YAAQ8NbXF2jXV8+YAQAAKydw0wOfVL9jVM6EXZzK9srzJrmlnIlVeDzDq/l7Y2ENIYkkxY9rvjm+t08e/y6r/K1cfumO1C2p6gIz3oc1ENnHvKw1s0nKQO7saXRbYsPpG2AZxLQ9sgOiY2RBiT7ciORii7duzoP4klI6kQ20J8+hZYpQh2uTrADBTO8tfWCs1qk/3jDszrMFC6oLzO3+He2FLu7usWdfXLOln3k9780i+y+1vCHgunuK747WLX4fyFDAHOsgmqRWYxgwkmwOKrgILXOHaQwm+R/AAKcgAkroRwfaa1QDu6xW3XbmJkuSXFYY7bkKPwswi59mdnVpSWaYHMnflG6I8UD6hF9CoqU/8Wb0Dg+V81CPlazgtt6HtZK5pqKHCnd6vyi7iUKitw77lWIHi6CjCQNDoAqFKQdAJ/8ZR/wYIgdppgVzAq9+Ese84O58VQhFiKJxx6GNmMo46rr6eOdosgpv88r9Uv9jxH+fr2EBA2ZwW1OxB8XBg5duZ/zx4tk+ay2U6Ue347ziq9OEZzECovNN2VQiBNavQ3Huy5nqbTK9HzkQupqHJ1nu',
            'bm_sz': '9BF1FF55689EC22F6181075B34DBB6A0~YAAQ8NbXF2rXV8+YAQAAKydw0xyn4OK6+P9YAPt58CxtVxqLjOLwNj/fOO4rIEoBfSBiGmOqGxtl2jyjh5rE1f71h12ZlJ42D+Ca2z6cPRwBZuRJ7QKbpAixFPowreq0o3ttYVjGDvh4qMKEmBql0qcz107bq/D+tn1bTOmkzwSgU9uSYxDkawHNBTz86wHqLUtPnaUuhDn0yXoMAwseuO4hRnUHOTO08hCg3So31SYitK0u27KQqSzKnraCSe9zuD9St1lzm2vWMufQ7fAZtKMDqvfU8d8oTWUEzMGVXnykB1hdYUTlBASQZUpk6fGMgnZa+5PTWgqLuNRmJmeUEmSlVo+LhEiC3A4ZknGLxD1YL48DDU5OJJnG05sJYH76c7XO/FW0xFE6NiC1/Qo0oLkyDZdhR6LEyYIOvFYf57CUcfjmR5nU~4535600~3551283',
            'p13n': '%7B%22zipCode%22%3A%2260462%22%2C%22storeId%22%3A%221828%22%2C%22state%22%3A%22IL%22%2C%22audienceList%22%3A%5B%22FQSP%22%5D%7D',
            'notice_behavior': 'implied,eu',
            'IR_12374': '1755894001072%7C0%7C1755894001072%7C%7C',
            '_uetsid': '133b77507f9511f0912667972e96c7a4',
            '_uetvid': '9ae56aa07c4811f09bcf33724b9e2a31',
            'ttcsid': '1755893870974::35gQYYFJfruaWtqo_KNf.3.1755894003061',
            'kampyleUserSession': '1755894003083',
            'kampyleUserSessionsCount': '5',
            'kampyleUserPercentile': '62.207127351307754',
            'kampyleSessionPageCounter': '1',
            '_scid_r': '7wFxIsJ13thjYRWntl34-rqWPaKMcgIIcUUFMw',
            'ttcsid_C54UCBJG5HFBPDLNKB10': '1755893870973::WW4CJ6DIlcEZ56P-rdq_.3.1755894033264',
            'akavpau_default': '1755894360~id=7811aa75643cd00ea529bc4869079e3d',
            'akaalb_prod_dual': '1755980460~op=PROD_GCP_EAST_CTRL_DFLT:PROD_DEFAULT_CTRL|~rv=68~m=PROD_DEFAULT_CTRL:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=c2ec5ae34013705058b693c86aa57126',
            'akaalb_prod_single': '1755980631~op=PROD_GCP_EAST_DFLT:PROD_DEFAULT_EAST|~rv=54~m=PROD_DEFAULT_EAST:0|~os=352fb8a62db4e37e16b221fb4cefd635~id=a533704956ca1dd862738d38cf025389',
            'bm_sv': 'A4D67870188E0373198ACB1059596490~YAAQ8NbXF6liWc+YAQAAL7Jz0xzWUYM4AYTalQVwITz3f9aI3efXgh+oTLG6V3eiaUmxWTv6W1H1qNJZ6j68Y/YraXMtD8HZyjGAObLj2C4eS1vkW+/5Rd8kS04keSs50rr8tU4ek68/xrPXnLXqVFmNy9rky48Q0Nm0dEq3RNQyXXyt7tvtI0BNYiwjkFCqOiW54Fg7BYsavO8ZgbaMSmG7iSgwsal9AhGxzFYcXnXfCDgdPWyg9Ir0PKjqnQX8~1',
            'RT': '"z=1&dm=lowes.com&si=40f05ce3-cc28-43e8-a65c-8d61e5392ef1&ss=men9ved4&sl=5&tt=a46&bcn=%2F%2F17de4c0d.akstat.io%2F"',
            'prodNumber': '6',
        }

        self.session.cookies.update(cookies)
        self.session.headers.update(headers)
        print(self.session.cookies)
        print(self.session.headers)
        response = requests.get('https://www.lowes.com/', cookies=cookies, headers=headers)
        print(response.status_code)
        print(response.content)

    def fetch_session(self):
        return self.session

    def _get_page(self, url):
        """
        Method to navigate to a specific page on the lowes website
        """
        logging.info(START_OF_METHOD)
        try:
            print(self.session.get("https://www.lowes.com/", headers=self.session.headers).content)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(self.delay)
            logging.info(END_OF_METHOD)
            return BeautifulSoup(response.content, 'html.parser')

        except Exception as e:
            logging.error('An error occurred loading a page from Lowes',
                          exc_info=True,
                          extra={'information': {'error': str(e)}})
            raise Error(WEBSCRAPING_ISSUE)

    @staticmethod
    def _extract_price(price_text):
        """
        Helper method to extract the price from a set of HTML
        :param price_text: The text of the price
        :return: python float
        """
        if not price_text:
            return None
        price_text = price_text.replace('$', '').replace(',', '').strip()
        price_match = re.search(r'(\d+\.?\d*)', price_text)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                return None
        return None

    def scrape_product_page(self, product_url):
        """
        Scrapes the product page
        :param product_url:
        :return:
        """
        soup = self._get_page(product_url)
        if not soup:
            return {}

        product_data = {
            'url': product_url,
            'name': None,
            'price': None,
            'original_price': None,
            'model': None,
            'brand': None,
            'rating': None,
            'availability': None
        }

        # Extract product name
        name_selectors = [
            'h1[data-testid="product-title"]',
            'h1.product-title',
            '.product-title h1',
            'h1'
        ]

        for selector in name_selectors:
            name_element = soup.select_one(selector)
            if name_element:
                product_data['name'] = name_element.get_text().strip()
                break

        # Extract current price
        price_selectors = [
            '[data-testid="product-price-value"]',
            '.price-current',
            '.sr-only:contains("current price")',
            '.price .sr-only',
            '[data-automation-id="product-price"]'
        ]

        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text()
                product_data['price'] = self._extract_price(price_text)
                if product_data['price']:
                    break

        # Extract original price (if on sale)
        original_price_selectors = [
            '.price-was',
            '.was-price',
            '[data-testid="product-price-was"]'
        ]

        for selector in original_price_selectors:
            original_element = soup.select_one(selector)
            if original_element:
                original_text = original_element.get_text()
                product_data['original_price'] = self._extract_price(original_text)
                if product_data['original_price']:
                    break

        # Extract model number
        model_selectors = [
            '[data-testid="product-model"]',
            '.model-number',
            'span:contains("Model #")',
            'span:contains("Model")'
        ]

        for selector in model_selectors:
            model_element = soup.select_one(selector)
            if model_element:
                model_text = model_element.get_text()
                model_match = re.search(r'Model\s*#?\s*:?\s*([A-Za-z0-9\-_]+)', model_text)
                if model_match:
                    product_data['model'] = model_match.group(1)
                    break

        # Extract brand
        brand_selectors = [
            '[data-testid="product-brand"]',
            '.brand-name',
            '.product-brand'
        ]

        for selector in brand_selectors:
            brand_element = soup.select_one(selector)
            if brand_element:
                product_data['brand'] = brand_element.get_text().strip()
                break

        # Extract rating
        rating_selectors = [
            '[data-testid="average-rating"]',
            '.average-rating',
            '.rating-number'
        ]

        for selector in rating_selectors:
            rating_element = soup.select_one(selector)
            if rating_element:
                rating_text = rating_element.get_text()
                rating_match = re.search(r'(\d\.?\d*)', rating_text)
                if rating_match:
                    try:
                        product_data['rating'] = float(rating_match.group(1))
                        break
                    except ValueError:
                        continue

        # Extract availability
        availability_selectors = [
            '[data-testid="fulfillment-summary"]',
            '.availability',
            '.stock-status'
        ]

        for selector in availability_selectors:
            availability_element = soup.select_one(selector)
            if availability_element:
                product_data['availability'] = availability_element.get_text().strip()
                break

        return product_data

    def search_appliances(self, category, max_pages=1):
        """
        Searches the Lowes' website for appliances
        :param category: The category of appliances
        :param max_pages: The number of pages to paginate
        :return:
        """
        search_url = f"{self.base_url}/search/?searchTerm={category}"
        products = []
        for page in range(1, max_pages + 1):
            page_url = search_url + f"&offset={(page - 1) * 24}"
            soup = self._get_page(page_url)
            if not soup:
                break
            product_links = []
            link_selectors = [
                'a[data-testid="product-title-link"]',
                '.product-title a',
                'a.product-link',
                'a[href*="/pd/"]'
            ]
            for selector in link_selectors:
                links = soup.select(selector)
                if links:
                    product_links = [urljoin(self.base_url, link.get('href'))
                                     for link in links if link.get('href')]
                    break

            if not product_links:
                logging.warning(f'No product links found on this page: {page}')
                break
            for product_url in product_links:
                product_data = self.scrape_product_page(product_url)
                if product_data and product_data.get('price'):
                    products.append(product_data)
        return products

    @disabled
    def get_product_by_model(self, model_number):
        """
        FUTURE_UPDATE: This code will be used when we integrate with Google Lens for form fillout
        :param model_number: The specific model number to scrape
        :return: python dict
        """
        search_url = f"{self.base_url}/search?searchTerm={model_number}"
        soup = self._get_page(search_url)
        if not soup:
            return {}
        product_link = soup.select_one('a[data-testid="product-title-link"]')
        if not product_link:
            return {}
        product_url = urljoin(self.base_url, product_link.get('href'))
        return self.scrape_product_page(product_url)

    def close(self):
        """Close the session."""
        self.session.close()
