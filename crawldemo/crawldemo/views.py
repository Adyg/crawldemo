import json
import urllib2
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import ast
import demjson

import diffbot

@csrf_exempt
def home(request):
    data = {
        'url': ''
    }

    if request.method == 'POST':
        data['url'] = request.POST.get('url', 'http://www.toysrus.com/product/index.jsp?productId=24447876')

        print data['url']

        json_result = diffbot.product(data['url'], token=settings.DIFFBOT_TOKEN)
        print json_result
        data['product'] = json_result['objects'][0]
        product_id_bits = data['url'].split('productId=')
        data['product_id'] = product_id_bits[1]


    return render(request, 'home.html', data)


def reviews(request, pid, page):

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

    # build the url (http://www.toysrus.com/pwr/content/10/07/24447876-en_US-12-reviews.js)
    base_url = 'http://www.toysrus.com/pwr/content/%s/%s-en_US-%s-reviews.js'

    base_url = base_url % (s, pid, page)

    review_data_page = urllib2.urlopen(base_url)
    review_data_lines = []
    review_data = ''

    for line in review_data_page.readlines():
        review_data_lines.append(line)
    review_data_raw = ''.join(review_data_lines)

    review_data_bits = review_data_raw.split(' = ')
    review_data = review_data_bits[1]
    review_data = review_data.replace(';', '')
    decoded_data = demjson.decode(review_data)

    data = {
        'reviews': decoded_data,
    }

    return render(request, 'reviews.html', data)
