from django.http import JsonResponse
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from .models import Airport, Flight, Carrier
from .serializers import AirportSerializer, FlightSerializer, CarrierSerializer

from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart

options = webdriver.ChromeOptions()
options.add_argument('headless')
chromedriver_path = '/usr/local/bin/chromedriver'

driver = webdriver.Chrome(executable_path=chromedriver_path)  # , options=options)


@api_view(["POST"])
def add_data_to_db(request):
    try:
        airports = Airport.objects.all()
        for airport_from in airports:
            for airport_to in airports:
                if airport_from != airport_to:
                    IATA_from = airport_from.IATA_code
                    IATA_to = airport_to.IATA_code
                    print(IATA_from, IATA_to)

                    date_start = '11092020'

                    chocotravel = ('https://www.chocotravel.com/ru/search?dest=' + IATA_from + '-' + IATA_to +
                                   '#params=' + IATA_from + IATA_to + ':' + date_start + ':2:1-0-0-0:3:0')
                    driver.get(chocotravel)
                    sleep(3)
                    print('starting scrape.....')
                    results = flights_scrape()
                    while not results:
                        results = flights_scrape()
                    for price, duration in results:
                        print(price, duration)
                        city_from = Airport.objects.get(IATA_code=IATA_from)
                        city_to = Airport.objects.get(IATA_code=IATA_to)
                        # FIXME
                        carrier = Carrier.objects.get(name='Fly Arystan')
                        Flight.objects.create(city_from=city_from, city_to=city_to, date_start=date_start,
                                              duration=duration, price=price, carrier=carrier)

        for airport_from in airports:
            for airport_to in airports:
                if airport_from != airport_to:
                    city_from = airport_from.city_name
                    city_to = airport_to.city_name
                    print(city_from, city_to)

                    date_start = '11092020'

                    chocotravel = ('https://www.chocotravel.com/ru/search?dest=' + IATA_from + '-' + IATA_to +
                                   '#params=' + IATA_from + IATA_to + ':' + date_start + ':2:1-0-0-0:3:0')
                    driver.get(chocotravel)
                    sleep(3)
                    print('starting scrape.....')
                    results = flights_scrape()
                    while not results:
                        results = flights_scrape()
                    for price, duration in results:
                        print(price, duration)
                        city_from = Airport.objects.get(IATA_code=IATA_from)
                        city_to = Airport.objects.get(IATA_code=IATA_to)
                        # FIXME
                        carrier = Carrier.objects.get(name='Fly Arystan')
                        Flight.objects.create(city_from=city_from, city_to=city_to, date_start=date_start,
                                              duration=duration, price=price, carrier=carrier)

    except Exception as e:
        return Response({"message": str(e)}, status=HTTP_400_BAD_REQUEST)
    finally:
        driver.quit()


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
        queryset = Flight.objects.all()
        return queryset[:10]
