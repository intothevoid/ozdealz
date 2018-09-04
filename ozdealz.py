import sys
from urllib.request import urlopen
import urllib.error, urllib.parse
from bs4 import BeautifulSoup
import requests
import json
import time
import base64

# kodi/xbmc constants
xbmc_ip = '127.0.0.1'
request_url = 'http://%s:8080/jsonrpc?request=' % xbmc_ip
credentials = b'user:pass'
encoded_credentials = base64.b64encode(credentials)
authorization = b'Basic ' + encoded_credentials

# pushbullet constants
ACCESS_TOKEN = ''


def send_notification_via_pushbullet(title, body):
    data_send = {"type": "note", "title": title, "body": body}

    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'})

    if resp.status_code != 200:
        raise Exception('Something wrong when sending message to Pushbullet {0}:{1}'.format(
            resp.status_code, resp.reason))


def send_notification_via_pushbullet_channel(title, body, channel_name):
    data_send = {"type": "note", "title": title,
                 "body": body, "channel_tag": channel_name}

    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'})

    if resp.status_code != 200:
        raise Exception('Something wrong when sending message to Pushbullet {0}:{1}'.format(
            resp.status_code, resp.reason))


def send_notification_via_xbmc(title, body):
    data_send = {"jsonrpc": "2.0", "method": "GUI.ShowNotification",
                 "params": {"title": title, "message": body}, "id": 1}
    json_data = json.dumps(data_send)
    post_data = json_data.encode('utf-8')

    requests.post(request_url, post_data,
                  headers={'Authorization': authorization, 'Content-Type': 'application/json'})


def get_deal_box():
    # set our page
    deal_page = "http://www.ozbargain.com.au"

    # grab the html of the page
    # req = urllib.request.Request(deal_page)
    # page = urllib.request.urlopen(req)
    page = requests.get(deal_page)

    # parse the html
    soup = BeautifulSoup(page.text, 'html.parser')

    #deal_box = soup.findAll('h2', attrs={'class': 'title'})
    deal_box = soup.findAll(
        'div', attrs={'class': 'node node-ozbdeal node-teaser'})

    return deal_box


def get_deal_box_as_dict(deal_box):
    deal_dict = {}
    for deal in deal_box:
        deal_dict[get_main_link(deal)] = get_deal_title(deal)
    return deal_dict


def get_fafa_link(deal):
    fa_fa_link = deal.findAll('span', attrs={'class': 'via'})
    if fa_fa_link.count > 0:
        return fa_fa_link[0].a.text
    return ''


def get_deal_title(deal):
    dealtag = deal.find('h2', attrs={'class': 'title'})
    return str(dealtag['data-title'].encode('utf-8').decode('utf-8'))


def get_main_link(deal):
    dealtag = deal.find('h2', attrs={'class': 'title'}).find('a')
    return 'https://www.ozbargain.com.au' + str(dealtag['href'].encode('utf-8').decode('utf-8'))


def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same


# Set current deal none
# current_dealstr = ''
current_deal_box_dict = {}
deal_box_dict = {}

while True:
    try:
        deal_box = get_deal_box()

        if deal_box is not None:
            deal_box_dict = get_deal_box_as_dict(deal_box)
            added, removed, modified, same = dict_compare(deal_box_dict, current_deal_box_dict)

            if len(added) > 0:
                for key in added:
                    # debug
                    # send_notification_via_pushbullet('Ozdealz', '{0}\n\n{1}'.format(deal_box_dict[key], str(key)))
                    send_notification_via_pushbullet_channel('Ozdealz', '{0}\n\n{1}'.format(deal_box_dict[key], str(key)), 'ozdealz')
                    # send_notification_via_xbmc('Ozdealz', '{0}\n{1}'.format(deal_box_dict[key], str(key)))
                    time.sleep(5) # wait a second before pushing next deal

                    if len(added) > 10: # First script run don't bomb the feed with too many pushes
                        break

        time.sleep(300)  # Run every 5 mins

    except Exception as e:
        print(e)
        #sys.exit(0)
    
    finally:
        current_deal_box_dict = deal_box_dict
