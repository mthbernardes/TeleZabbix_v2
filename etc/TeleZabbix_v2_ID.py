import telepot,time
from pprint import pprint

Work = True

def get_conf():
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read('TeleZabbix.conf')
    api = config.get('Telegram','api')
    return api

def message(msg):
    global Work
    print 'Group ID:' , msg['chat']['id']
    print 'Group Name: ' + msg['chat']['title']
    print
    print 'Username ID:', msg['from']['id']
    hprint 'Username: ' + msg['from']['username']
    Work = False

api = get_conf()
bot = telepot.Bot(api)
bot.notifyOnMessage(message)

while Work == True:
    time.sleep(1)
