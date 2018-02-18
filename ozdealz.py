import sys
import urllib2
from bs4 import BeautifulSoup
import requests
import json
import time


def send_notification_via_pushbullet(title, body):
    """ Sending notification via pushbullet.
        Args:
            title (str) : title of text.
            body (str) : Body of text.
    """
    data_send = {"type": "note", "title": title, "body": body}

    ACCESS_TOKEN = ''
    resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Something wrong')

def get_deal_box():
    # set our page
    deal_page = "https://www.ozbargain.com.au"

    # grab the html of the page
    page = urllib2.urlopen(deal_page)

    # parse the html
    soup = BeautifulSoup(page, 'html.parser')
    deal_box = soup.findAll('h2', attrs={'class': 'title'})

    return deal_box


# Set current deal none
current_deal = ''

while True:
    deal_box = get_deal_box()

    if current_deal != deal_box[0]:
        deal = deal_box[0]
        dealstr = deal['data-title'].encode(sys.stdout.encoding, errors='replace')
        send_notification_via_pushbullet('KDealz - found new deal!', dealstr)
        current_deal = deal

    time.sleep(600) # Run every 10 mins
