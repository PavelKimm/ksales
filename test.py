from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart



def flights_scrape():
    try:
        xp_airline_sections = '//div[contains(@class,"logos single  ")]'
        airline_elements = driver.find_elements_by_xpath(xp_airline_sections)
        if airline_elements:
            airline_titles = airline_elements
        else:
            airline_titles = 'no flights'

        xp_price_sections = '//p[contains(@class,"fare-families-choose-price")]'
        price_elements = driver.find_elements_by_xpath(xp_price_sections)
        if price_elements:
            prices = [''.join(price.text[3:-4].split()) for price in price_elements]
        else:
            prices = 'no flights'

        xp_duration_sections = '//p[contains(@class,"duration time_0")]'
        duration_elements = driver.find_elements_by_xpath(xp_duration_sections)
        if duration_elements:
            durations = [duration.text for duration in duration_elements]
        else:
            durations = 'no flights'



        print(len(prices), '==', len(durations), 'must be equal')
        # print(airline_titles)
        # print(len(airline_titles))

        # return prices, durations#, airline_titles

        if prices == 'no flights' or durations == 'no flights':
            return None
        else:
            return zip(prices, durations)
    except Exception as e:
        print(e)

try:
    # options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    chromedriver_path = '/usr/local/bin/chromedriver'
    #
    driver = webdriver.Chrome(executable_path=chromedriver_path)  # , options=options)

    date_start = '11092020'

    chocotravel = ('https://www.chocotravel.com/ru/search?dest=2708001-CIT-2708001&searchresult=1&is_refundable_only=0#params=2708001CIT:18092020:2:1-0-0-0:3:0')
    driver.get(chocotravel)
    sleep(3)
    print('starting scrape.....')
    results = flights_scrape()
    # while not results:
    #     results = flights_scrape()
    # for price, duration in results:
    #     print(price, duration)
    #     city_from = Airport.objects.get(IATA_code=IATA_from)
    #     city_to = Airport.objects.get(IATA_code=IATA_to)
    #     # FIXME
    #     carrier = Carrier.objects.get(name='Fly Arystan')
    #     Flight.objects.create(city_from=city_from, city_to=city_to, depart_date=date_start,
    #                           duration=duration, price=price, carrier=carrier)

finally:
    driver.quit()
