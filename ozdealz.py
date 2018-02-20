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

def send_notification_via_pushbullet_channel(title, body, channel_name):
    data_send = {"type": "note", "title": title, "body": body, "channel_tag":channel_name}

    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
        headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'})

    if resp.status_code != 200:
        raise Exception('Something wrong when sending message to Pushbullet {0}:{1}'.format(resp.status_code, resp.reason))

def send_notification_via_xbmc(title, body):
    data_send = {"jsonrpc": "2.0", "method": "GUI.ShowNotification", "params": {"title": title, "message": body}, "id": 1}
    json_data = json.dumps(data_send)
    post_data =  json_data.encode('utf-8')

    requests.post(request_url, post_data,
        headers={'Authorization':authorization, 'Content-Type': 'application/json'})

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

def get_deal_title(deal):
    dealtag = deal.find('h2', attrs={'class':'title'})
    #return dealtag['data-title'].encode(sys.stdout.encoding, errors='replace')
    return dealtag['data-title'].encode(sys.getdefaultencoding(), errors='replace')

def get_main_link(deal):
    dealtag = deal.find('h2', attrs={'class':'title'}).find('a')
    return 'https://www.ozbargain.com.au' + dealtag['href'].encode(sys.getdefaultencoding(), errors='replace')

# Set current deal none
current_dealstr = ''

while True:
    deal_box = get_deal_box()

    if deal_box.count > 0:
        deal = deal_box[0] # get topmost deal

        dealstr = get_deal_title(deal)
        fafalinkstr = get_fafa_link(deal)
        deal_link = get_main_link(deal)

        if current_dealstr != dealstr:
            try:
                # debug
                # send_notification_via_pushbullet('Ozdealz', '{0}\n\n{1}'.format(dealstr,deal_link))

                current_dealstr = dealstr
                send_notification_via_pushbullet_channel('Ozdealz', '{0}\n\n{1}'.format(dealstr,deal_link), 'ozdealz')
                send_notification_via_xbmc('Ozdealz', '{0}\n{1}'.format(dealstr,fafalinkstr))
            except:
                print 'Exception occured!'

    time.sleep(300)  # Run every 5 mins
