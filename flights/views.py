from django.http import JsonResponse
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from .models import Airport, Flight, Carrier, GroundTransportation
from .serializers import AirportSerializer, FlightSerializer, CarrierSerializer
import requests
import json
from datetime import datetime
from datetime import timedelta

from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart

# options = webdriver.ChromeOptions()
# options.add_argument('headless')
chromedriver_path = '/usr/local/bin/chromedriver'
#
# driver = webdriver.Chrome(executable_path=chromedriver_path)  # , options=options)


@api_view(["GET"])
def get_data(request):
    airports = Airport.objects.all()
    headers = {'X-Access-Token': '6fee0f66347517eed229b6e7632e237b'}

    for airport_from in airports:
        for airport_to in airports:
            if airport_from != airport_to:
                IATA_from = airport_from.IATA_code
                IATA_to = airport_to.IATA_code
                date = datetime.now().date()
                for i in range(60):
                    depart_date = str(date)
                    res = requests.get(
                        f"http://min-prices.aviasales.ru/calendar_preload?origin={IATA_from}&destination={IATA_to}&depart_date={depart_date}&one_way=true&currency=KZT",
                        headers=headers)
                    try:
                        flights = json.loads(res.text)['best_prices']
                        for flight in flights:
                            if flight['depart_date'] == depart_date:
                                Flight.objects.create(city_from=airport_from, city_to=airport_to,
                                                      depart_date=depart_date,
                                                      number_of_changes=flight['number_of_changes'],
                                                      price=flight['value'],
                                                      provider=flight['gate'], distance=flight['distance'])
                    except:
                        print(res.text)
                        break
                    date += timedelta(days=1)
    return Response(status=HTTP_200_OK)


@api_view(["POST"])
def add_data_to_db(request):
    try:
        # airports = Airport.objects.all()
        #     for airport_from in airports:
        #         for airport_to in airports:
        #             if airport_from != airport_to:
        #                 IATA_from = airport_from.IATA_code
        #                 IATA_to = airport_to.IATA_code
        #                 print(IATA_from, IATA_to)
        #
        #                 date_start = '11092020'
        #
        #                 chocotravel = ('https://www.chocotravel.com/ru/search?dest=' + IATA_from + '-' + IATA_to +
        #                                '#params=' + IATA_from + IATA_to + ':' + date_start + ':2:1-0-0-0:3:0')
        #                 driver.get(chocotravel)
        #                 sleep(3)
        #                 print('starting scrape.....')
        #                 results = flights_scrape()
        #                 while not results:
        #                     results = flights_scrape()
        #                 for price, duration in results:
        #                     print(price, duration)
        #                     city_from = Airport.objects.get(IATA_code=IATA_from)
        #                     city_to = Airport.objects.get(IATA_code=IATA_to)
        #                     # FIXME
        #                     carrier = Carrier.objects.get(name='Fly Arystan')
        #                     Flight.objects.create(city_from=city_from, city_to=city_to, depart_date=date_start,
        #                                           duration=duration, price=price, carrier=carrier)

        airports = Airport.objects.all()
        for airport_from in airports:
            for airport_to in airports:
                print(airport_from.city_name, airport_to.city_name, 'all')
                if airport_from != airport_to:
                    date = datetime.now().date()
                    for i in range(60):
                        date_start = ''.join(str(date).split('-')[::-1])

                        city_from = airport_from.railway_station_code
                        city_to = airport_to.railway_station_code
                        if not city_from or not city_to:
                            continue
                        if city_to == 'GUW' or city_from == 'GUW' or city_to == 'SCO' or city_from == 'SCO':
                            continue
                        print(city_from, city_to)
                        chocotravel = ('https://www.chocotravel.com/ru/search?dest=' + city_from + '-' + city_to +
                                       '&searchresult=1&railways=1#params=' + city_from + city_to + ':' + date_start + ':2:1-0-0-0:1:0')
                        driver.get(chocotravel)
                        sleep(5)
                        print('starting scrape.....')
                        results = trains_scrape()
                        if not results:
                            continue
                        city_from = Airport.objects.get(railway_station_code=city_from)
                        city_to = Airport.objects.get(railway_station_code=city_to)
                        for result in results:
                            if not result:
                                continue
                            GroundTransportation.objects.create(
                                city_from=city_from, city_to=city_to, depart_date=date_start,
                                train_number=result[0], duration=result[1], seat_type=result[2],
                                available_tickets=result[3], price=result[4])
                        date += timedelta(days=1)
        return Response(status=HTTP_200_OK)
    finally:
        driver.quit()


def trains_scrape():
    try:
        xp_price_sections = '//div[contains(@class,"train-card__wagon-list")]'
        price_elements = driver.find_elements_by_xpath(xp_price_sections)
        if price_elements:
            prices = [price.text.split('\n') for price in price_elements]
        else:
            return None

        xp_duration_sections = '//span[contains(@class,"train-card__duration-time")]'
        duration_elements = driver.find_elements_by_xpath(xp_duration_sections)
        if duration_elements:
            durations = [duration.text for duration in duration_elements]
        else:
            return None

        xp_train_sections = '//div[contains(@class,"train-card__train")]'
        train_numbers = driver.find_elements_by_xpath(xp_train_sections)
        if train_numbers:
            train_numbers = [train.text.split('\n')[0] for train in train_numbers]
        else:
            return None

        results = []
        for train_number, duration in zip(train_numbers, durations):
            for pr in prices:
                i = len(pr)
                for i, p in enumerate(pr):
                    p = pr[2 * i: 2 * i + 2]
                    if 2 * i >= len(pr):
                        break
                    results += [[train_number, duration, p[0].split()[0], p[0].split()[1], ''.join(p[1].split()[:-1])]]
        return results
    except Exception as e:
        print(e)
        return None



def flights_scrape():
    try:
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

        # xp_airline_sections = '//div[contains(@class,"airline")]'
        # airline_elements = driver.find_elements_by_xpath(xp_airline_sections)
        # if airline_elements:
        #     airline_titles = [airline.find_element_by_xpath(
        #         "//img[contains(@src,'https://www.chocotravel.com/media/images/logo')]"
        #     ).get_attribute("title") for airline in airline_elements]
        # else:
        #     airline_titles = 'no flights'

        print(len(prices), '==', len(durations), 'must be equal')
        # print(airline_titles)
        # print(len(airline_titles))

        # return prices, durations#, airline_titles

        if prices == 'no flights' or durations == 'no flights':
            return None
        else:
            return zip(prices, durations)
    except Exception as e:
        return Response({"message": str(e)}, status=HTTP_400_BAD_REQUEST)


class FlightView(generics.ListAPIView):
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = Flight.objects.filter(carrier__type='AP')
        return queryset[:10]

