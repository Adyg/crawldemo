import json
import urllib2
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import demjson
import datetime

import diffbot

from django.core.management.base import BaseCommand, CommandError

BASE_PATH = '/tmp/toysrus'

class Command(BaseCommand):

    help = 'Export reviews to json. Call it with `python manage.py export_reviews 123 2342 45345`'
        
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('format', type=str)

        # Positional arguments
        parser.add_argument('pid', nargs='+', type=str)


    def handle(self, *args, **options):
        # make sure file option is present
        if options['pid'] == None :
            raise CommandError("Option `--pid=...` must be specified.")

        if options['format'] == None :
            raise CommandError("Option `--format=...` must be specified (json or xml).")

        pids = options['pid']

        for pid in pids:
            #diffbot
            url = 'http://www.toysrus.com/product/index.jsp?productId=%s' % pid

            json_result = diffbot.product(url, token=settings.DIFFBOT_TOKEN)
            data_product = json_result['objects'][0]

            sku = data_product['specs']['sku']
            title = data_product['title']

            #start retrieving reviews

            #pid encoding
            str_pid = str(pid)
            s = 0
            i = 0

            for char in pid:
              r = ord(char)
              r = r * (255 - r)
              s = s + r

            s = s % 1023
            s = str(s)

            n = 4
            fromParts = [c for c in s]
            i = 0

            while i < n - len(s):
                fromParts.insert(0, '0')
                i = i + 1

            s = ''.join(fromParts)
            s = s[:(n/2)] + "/" + s[(n/2):n]
            # end pid encoding
            page = 1


            # build the url (http://www.toysrus.com/pwr/content/10/07/24447876-en_US-12-reviews.js)
            base_url = 'http://www.toysrus.com/pwr/content/%s/%s-en_US-%s-reviews.js'
            done = False
            decoded_data = []
            exportable_data = []
            it = 0
            while not done:
                review_page_url = base_url % (s, pid, page)

                try:
                    review_data_page = urllib2.urlopen(review_page_url)
                    review_data_lines = []
                    review_data = ''

                    for line in review_data_page.readlines():
                        review_data_lines.append(line)
                    review_data_raw = ''.join(review_data_lines)

                    # split at the first '=' char
                    review_data_bits = review_data_raw.split(' = ', 1)
                    review_data = review_data_bits[1]
                    review_data = review_data.replace(';', '')
                    decoded_data = demjson.decode(review_data)
                    for reviews in decoded_data:
                        review = reviews['r']

                        it = it + 1
                        exportable_data.append(
                            {
                                'sku': sku,
                                'title': review['h'],
                                'rating': review['r'],
                                'text': review['p'],
                                'submissionTime': review['db'],
                                'displayName': review['n'],
                                'externalId': review['id'],
                                'emailAddress': it,
                            }
                        )

                except:
                    done = True
                page = page + 1

            export_to_file(options['format'], exportable_data, pid)


def export_to_file(format, exportable_data, pid):
    if format == 'json':
        export_to_json(exportable_data, pid)

        return 

    export_to_xml(exportable_data, pid)


def export_to_json(data, pid):
    file_path = '%s/%s.json' % (BASE_PATH, pid)
    file_obj = open(file_path, 'w')
    file_obj.write(json.dumps(data))
    file_obj.close()


def export_to_xml(data, pid):
    import xml.etree.cElementTree as ET

    reviewsFeed = ET.Element("reviewsFeed")
    reviews = ET.SubElement(reviewsFeed, "reviews")
    it = 1
    for review_data in data:
        review = ET.SubElement(reviews, "review")
        raw_date = datetime.datetime.strptime(review_data['submissionTime'], '%Y-%m-%dT%H:%M:%S')
        formatted_date = raw_date.strftime('%d/%m/%Y %H:%M:%S -0500')


        ET.SubElement(review, "sku").text = review_data['sku']
        ET.SubElement(review, "title").text = review_data['title']
        ET.SubElement(review, "text").text = review_data['text']
        ET.SubElement(review, "submissionTime").text = formatted_date
        #int not serializable 
        ET.SubElement(review, "rating").text = str(review_data['rating'])
        
        user = ET.SubElement(review, "user")

        ET.SubElement(user, "displayName").text = review_data['displayName']
        ET.SubElement(user, "emailAddress").text = str(it)


    file_path = '%s/%s.xml' % (BASE_PATH, pid)
    tree = ET.ElementTree(reviewsFeed)
    tree.write(file_path)
