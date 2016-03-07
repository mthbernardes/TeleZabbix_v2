#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyzabbix import ZabbixAPI
from datetime import datetime,timedelta
from daemon import Daemon
import json,pytz,time,telepot,sys


class daemon_server(Daemon):
    def run(self):
        main()

def handle_message(msg):
    try:
        username = msg['from']['username']
    except:
        username = ''
    content_type, chat_type, chat_id = telepot.glance2(msg)
    if chat_type == 'group' and username in admins:
        if content_type is 'text':
            command = msg['text'].lower()
            actions(command)
    else:
        bot.sendMessage(group_id, 'Desculpe '+username+' nao tenho permissao para falar com voce!')

def actions(command):
    command = command.split()
    if command[0] == '/hosts':
        hosts()

    elif command[0] == '/triggers':
        triggers()

    elif command[0] == '/users':
        users()

    elif command[0] == '/web':
        web()

    elif command[0] == '/events':
        if len(command) > 1:
            if command[1].isnumeric():
                events(int(command[1]))
            else:
                events(4)
        else:
            events(4)

def hosts():
    for h in zapi.host.get(output="extend"):
        if int(h['available']) == 1:
            status = 'On-line'
        else:
            status = 'Offline'
        bot.sendMessage(group_id, 'ID: '+h['hostid']+'\nStatus: '+status+'\nHost: '+h['host']+'\nNome: '+h['name'])

def triggers():
    for t in zapi.trigger.get(only_true=1,active=1,output='extend',expandDescription=1,expandData='host'):
        last_change = datetime.fromtimestamp(int(t['lastchange']),pytz.timezone('America/Sao_Paulo')).strftime('%d-%m-%Y %H:%M:%S')
        bot.sendMessage(group_id, 'Descricao: '+t['description']+'\nPrioridade: '+t['priority']+'\nHost: \nNome: \nUltima Alteracao: '+last_change)

def users():
    for u in zapi.user.get(output='extend'):
        name = u['name'] + ' ' + u['surname']
        bot.sendMessage(group_id, 'ID: '+u['userid']+'\nUsuario: '+u['alias']+'\nNome: '+name)

def web():
    for w in zapi.httptest.get(output='extend',monitored=True,selectSteps="extend"):
        next_check = datetime.fromtimestamp(int(w['nextcheck']),pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')
        bot.sendMessage(user_id, 'Nome: '+w['name']+'\nProxima Verificacao: '+next_check)
        for s in w['steps']:
            bot.sendMessage(group_id, 'URL: '+s['url']+'\nStatus conexao: '+s['status_codes'])

def events(last):
    last_hour = datetime.today() - timedelta(hours = last)
    last_hour = time.mktime(last_hour.timetuple())
    for e in zapi.event.get(output='extend',select_acknowledges='message',selectHosts='extend',time_from=last_hour,value=1,source=0):
        bot.sendMessage(group_id, 'ID Evento: '+e['eventid']+'\nHost: '+e['hosts'][0]['host'])

def get_conf():
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read('TeleZabbix.conf')
    api = config.get('Telegram','api')
    group_id = config.get('Telegram','group_id')
    admins = config.get('Telegram','admins')
    username = config.get('Zabbix','username')
    password = config.get('Zabbix','password')
    server = config.get('Zabbix','server')

    return api,group_id,admins,username,password,server

def main():
    bot.notifyOnMessage(handle_message)
    while 1:
        time.sleep(10)

daemon_service = daemon_server('/var/run/TeleZabbix_v2.pid')
if len(sys.argv) >= 2:
    if sys.argv[1] == 'start':
        api,group_id,admins,username,password,server = get_conf()
        admins = admins.split(',')
        zapi = ZabbixAPI(server)
        zapi.login(username, password)
        bot = telepot.Bot(api)
        daemon_service.start()

    elif sys.argv[1] == 'stop':
        daemon_service.stop()

    elif sys.argv[1] == 'restart':
        daemon_service.restart()

    elif sys.argv[1] == 'status':
        daemon_service.is_running()
else:
    print 'Usage:',sys.argv[0],'star | stop | restart | status'
