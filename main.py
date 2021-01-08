import time
import pandas as pd
from selenium.webdriver import ActionChains
from utils import user_name, password
from utils import api
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep

options = Options()
options.add_argument("--disable-infobars")
options.add_argument('--start-maximized')
options.add_argument("--disable-extensions")
options.add_argument('disable-blink-features=AutomationControlled')
options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')

d = webdriver.Chrome(options=options, executable_path='drivers/chromedriver')


def login(d):
    d.get("https://www.linkedin.com/login")
    sleep(3)
    actions = ActionChains(d)
    actions.send_keys(user_name)
    actions.send_keys(Keys.TAB)
    actions.send_keys(password)
    actions.send_keys(Keys.ENTER)
    actions.perform()

    content = d.page_source
    soup = BeautifulSoup(''.join(content), 'html.parser')

    if 'input__email_verification_pin' in soup.text:
        code = d.find_element_by_id('input__email_verification_pin')
        key = input('Enter key:')
        code.send_keys(key)
        code.send_keys(Keys.ENTER)

    return "Successfully logged in! "


def scroll_down(driver, url, keyword):
    print('Page loading.......')
    d.get(url + '/people/?keywords={}'.format(keyword))
    """A method for scrolling the page."""

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(1.5)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height
    print('Page loaded!')


def get_links(d):
    links = []
    content = d.page_source
    soup = BeautifulSoup(''.join(content), 'html.parser')
    ul = soup.find_all('ul', attrs={'class': 'org-people-profiles-module__profile-list'})
    li = ul[0].find_all('li')

    for i in li:
        try:
            links.append(i.find('a')['href'])
        except:
            pass
    return links


def get_employee(id):
    # print(id)
    temp = api.get_profile(id.split('/')[2])
    link = 'https://www.linkedin.com/' + id
    company = temp['experience'][0]['companyName']
    full_name = '{} {}'.format(temp['firstName'], temp['lastName'])
    try:
        current_position = temp['experience'][0]['title']
    except:
        current_position = ''
    try:
        current_position_start = '{}/{}'.format(temp['experience'][0]['timePeriod']['startDate']['month'],
                                                temp['experience'][0]['timePeriod']['startDate']['year'])
    except:
        current_position_start = ''
    try:
        header_location = temp['locationName']
    except:
        header_location = ''
    try:
        geo = temp['experience'][0]['geoLocationName']
        city = geo.split(', ')[0]
        country = geo.split(', ')[-1]
    except:
        city = ''
        country = ''
    try:
        education_1 = temp['education'][0]['schoolName']
    except:
        education_1 = ''

    try:
        education_1_year = '{}-{}'.format(temp['education'][0]['timePeriod']['startDate']['year'],
                                          temp['education'][0]['timePeriod']['endDate']['year'])
    except:
        education_1_year = ''

    if len(temp['education']) > 1:
        try:
            education_2 = temp['education'][1]['schoolName']
        except:
            education_2 = ''
        try:
            education_2_year = '{}-{}'.format(temp['education'][1]['timePeriod']['startDate']['year'],
                                              temp['education'][1]['timePeriod']['endDate']['year'])
        except:
            education_2_year = ''
            pass
    else:
        education_2 = ''
        education_2_year = ''
    return [full_name, company, current_position, current_position_start, header_location, city, country, education_1,
            education_1_year,
            education_2, education_2_year, link]


login(d)
while True:
    url = input("Enter the URL:")
    keyword = input("Enter keyword:")
    file = input('Enter save file name:')
    scroll_down(d, url, keyword)
    links = get_links(d)
    print('{} employees found'.format(len(links)))
    data = []
    for i in range(len(links)):
        print(i + 1, 'extracting...')
        try:
            data.append(get_employee(links[i]))
        except Exception as e:
            pass
    df = pd.DataFrame(data,
                      columns=['full_name', 'company', 'current_position', 'current_position_start', 'header_location',
                               'city', 'country',
                               'education_1', 'education_1_year',
                               'education_2', 'education_2_year', 'linkedin_url'])
    df.to_csv('output/{}.csv'.format(file), index=False)
