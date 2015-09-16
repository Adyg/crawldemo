import json
import urllib2
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import demjson

import diffbot

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Export reviews to json. Call it with `python manage.py export_reviews 123 2342 45345`'
    
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('pid', nargs='+', type=str)


    def handle(self, *args, **options):
        # make sure file option is present
        if options['pid'] == None :
            raise CommandError("Option `--pid=...` must be specified.")

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
            json_data = []
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

                    review_data_bits = review_data_raw.split(' = ')
                    review_data = review_data_bits[1]
                    review_data = review_data.replace(';', '')
                    decoded_data = demjson.decode(review_data)
                    for reviews in decoded_data:
                        review = reviews['r']
                        it = it + 1
                        json_data.append(
                            {
                                'sku': sku,
                                'title': review['h'],
                                'rating': review['r'],
                                'text': review['p'],
                                'submissionTime': review['d'],
                                'displayName': review['n'],
                                'externalId': review['id'],
                                'emailAddress': it,
                            }
                        )

                except:
                    done = True
                page = page + 1

            base_path = '/tmp/toysrus'

            file_path = '%s/%s.json' % (base_path, pid) 
            file_obj = open(file_path, 'w')
            file_obj.write(json.dumps(json_data))
            file_obj.close()

