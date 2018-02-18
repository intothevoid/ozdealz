import sys
import urllib2
from bs4 import BeautifulSoup
import requests
import json
import time
import base64

# kodi/xbmc constants
xbmc_ip = '127.0.0.1'
request_url = 'http://%s:8080/jsonrpc?request=' % xbmc_ip
credentials = b'user:password'
encoded_credentials = base64.b64encode(credentials)
authorization = b'Basic ' + encoded_credentials

# pushbullet constants
ACCESS_TOKEN = ''

def send_notification_via_pushbullet(title, body):
    data_send = {"type": "note", "title": title, "body": body}

    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
        headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'})

    if resp.status_code != 200:
        raise Exception('Something wrong when sending message to Pushbullet {0}:{1}'.format(resp.status_code, resp.reason))

def send_notification_via_xbmc(title, body):
    data_send = {"jsonrpc": "2.0", "method": "GUI.ShowNotification", "params": {"title": title, "message": body}, "id": 1}
    json_data = json.dumps(data_send)
    post_data =  json_data.encode('utf-8')

    resp = requests.post(request_url, post_data,
        headers={'Authorization':authorization, 'Content-Type': 'application/json'})

    if resp.status_code != 200:
        raise Exception('Something wrong when sending message to XBMC {0}:{1}'.format(resp.status_code, resp.reason))

def get_deal_box():
    # set our page
    deal_page = "https://www.ozbargain.com.au"

    # grab the html of the page
    page = urllib2.urlopen(deal_page)

    # parse the html
    soup = BeautifulSoup(page, 'html.parser')
    #deal_box = soup.findAll('h2', attrs={'class': 'title'})
    deal_box = soup.findAll(
        'div', attrs={'class': 'node node-ozbdeal node-teaser'})

    return deal_box

def get_fafa_link(deal):
    fa_fa_link = deal.findAll('span', attrs={'class':'via'})
    if fa_fa_link.count > 0:
        return fa_fa_link[0].a.text
    return ''

def get_deal_title(deal_box):
    deal = deal_box[0].find('h2', attrs={'class':'title'})
    return deal['data-title'].encode(sys.stdout.encoding, errors='replace')

# Set current deal none
current_deal = ''

while True:
    deal_box = get_deal_box()

    if deal_box.count > 0:
        if current_deal != get_deal_title(deal_box):
            fafalinkstr = get_fafa_link(deal_box[0])
            dealstr = get_deal_title(deal_box)

            send_notification_via_pushbullet('Ozdealz', '{0}\n{1}'.format(dealstr,fafalinkstr))
            send_notification_via_xbmc('Ozdealz', '{0}\n{1}'.format(dealstr,fafalinkstr))

            current_deal = dealstr

    time.sleep(300)  # Run every 5 mins
