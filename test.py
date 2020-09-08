from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart


def flights_scrape():
    try:
        xp_flight_info = '//div[contains(@class,"offers-groups-item")]'

        xp_airline_sections = xp_flight_info + '//span[contains(@data-qa-id,"offer__airline-name")]'
        airline_elements = driver.find_elements_by_xpath(xp_airline_sections)
        if airline_elements:
            airline_titles = [title.text for title in airline_elements]
        else:
            airline_titles = None

        xp_depart_time_sections = xp_flight_info + '//div[contains(@data-qa-id,"offer__dep-time")]'
        depart_time_elements = driver.find_elements_by_xpath(xp_depart_time_sections)
        if depart_time_elements:
            depart_time_list = [time.text for time in depart_time_elements]
        else:
            depart_time_list = None

        xp_price_sections = driver.find_elements_by_xpath(xp_flight_info + '//div[contains(@class,"p-3 rounded-r-sm")]'
                                                                           '//div[contains(@class,"offers-group-prices")]')
        prices = [''.join(a.text.split('\n')[-2].split()[1:-1]) if '\nAviata' in a.text
                  else ''.join(a.text.split('\n')[0].split()[:-1]) for a in xp_price_sections[::3]]

        xp_duration_sections = '//div[contains(@class,"offers-groups-item-body")]' \
                               '//div[contains(@class,"text-center text-gray")]'
        duration_elements = driver.find_elements_by_xpath(xp_flight_info + xp_duration_sections)
        if duration_elements:
            durations = [duration.text for duration in duration_elements]
        else:
            durations = None

        return zip(airline_titles, depart_time_list, prices, durations)

    except Exception as e:
        print(e)


try:
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    chromedriver_path = '/usr/local/bin/chromedriver'

    driver = webdriver.Chrome(executable_path=chromedriver_path)  # , options=options)

    date_start = '12092020'

    str_from = 'ALA'
    str_to = 'TSE'
    year = '2020'
    month = '09'
    day = '09'
    seat_class = 'E'
    for i in range(2):
        chocotravel = f'https://aviata.kz/aviax/search/{str_from}-{str_to}{year}{month}{day}1000{seat_class}'
        driver.get(chocotravel)
        sleep(11)
        print('starting scrape.....')
        results = flights_scrape()

        for i, result in enumerate(results):
            airline_title, depart_time, price, duration = result
            print(i, airline_title, depart_time, price, duration)
        day = '10'

finally:
    driver.quit()
