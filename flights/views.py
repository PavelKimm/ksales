from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from .models import Airport, Flight, Carrier, GroundTransportation
from .serializers import AirportSerializer, FlightSerializer, CarrierSerializer
from datetime import datetime
from datetime import timedelta
import re

from time import sleep
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('headless')
chromedriver_path = '/usr/local/bin/chromedriver'
# driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)


@api_view(["POST"])
def purify_database(request):
    flights = Flight.objects.all()
    for flight in flights:
        # q = flight.duration
        # q = "1 ч 40 м"
        # q1 = q.split()[::2]
        # q2 = q.split()[1::2]
        #
        # print(q1, q2)
        # exit()
        flight.price = re.sub("[^0-9]", "", flight.price)
        flight.save()
        if flight.price == '':
            flight.delete()

    trains = GroundTransportation.objects.all()
    for train in trains:
        train.price = re.sub("[^0-9]", "", train.price)
        train.save()
        if train.price == '':
            train.delete()
    return Response(status=HTTP_200_OK)


@api_view(["POST"])
def add_plane_data_to_db(request):
    try:
        airports = Airport.objects.all()
        for airport_from in airports:
            for airport_to in airports:
                if airport_from != airport_to:
                    IATA_from = airport_from.IATA_code
                    IATA_to = airport_to.IATA_code
                    date = datetime.now().date()

                    for i in range(60):
                        depart_date = ''.join(str(date).split('-'))
                        for c in range(2):
                            if c == 0:
                                seat_class = 'E'
                            else:
                                seat_class = 'B'
                            try:
                                chocotravel = f'https://aviata.kz/aviax/search/{IATA_from}-{IATA_to}{depart_date}1000{seat_class}'
                                driver.get(chocotravel)
                                sleep(14)
                                if seat_class == 'E':
                                    seat_class = 'Economy'
                                else:
                                    seat_class = 'Business'
                                print('starting scrape.....')
                                results = flights_scrape()

                                for result in results:
                                    airline_title, depart_time, price, duration = result

                                    Flight.objects.create(city_from=airport_from, city_to=airport_to,
                                                          depart_date=''.join(str(date).split('-')[::-1]),
                                                          duration=duration, price=price, carrier=airline_title,
                                                          seat_class=seat_class)
                            except:
                                continue
                        date += timedelta(days=1)
        return Response(status=HTTP_200_OK)

    finally:
        driver.quit()


@api_view(["POST"])
def add_train_data_to_db(request):
    try:
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


class FlightView(generics.ListAPIView):
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = Flight.objects.filter(carrier__type='AP')
        return queryset[:10]
