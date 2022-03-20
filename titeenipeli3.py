#!/usr/bin/python

import random
import sys
import traceback
import websocket
import json
from websocket import create_connection
from time import sleep

import argparse

parser = argparse.ArgumentParser(description='You must beat the game.')
parser.add_argument('-u', '--url', required=True, help='Url to WSS endpoint, check where browser connects. starts with "wss://api.titeenipeli.xyz/socket/websocket?token="')
parser.add_argument('-i', '--userid', required=True, help='user id, again, from go check browser wss connection. First sent packet.')
parser.add_argument('-r', '--room', required=True, type=int, help='room id. Someone make a list pls')
args = parser.parse_args()

URL=args.url
USER_ID_FIELD="user:"+args.userid
ROOM=args.room

first_num=11

MAX_RECV_PACKETS=100

HEARTBEAT_EVERY_N_ROUNDS=10

#websocket.enableTrace(True)

class NoResponse(Exception):
    pass

working_nondocumented_spells=[]

class Bot():
    def __init__(self, ws):
        self.ws = ws
        self.command_index=12

    def handle_response(self, validator):
        recv_packets=0
        #print("")
        while recv_packets <= MAX_RECV_PACKETS:
            r = self.ws.recv()
            res = json.loads(r)

            recv_packets += 1
            sys.stdout.write(f'\r{recv_packets}/{MAX_RECV_PACKETS}')

            if validator(res):
                print()
                return True
        return False

    def send(self, payload):
        print(f"Sending {payload}")
        self.ws.send(payload)

    def _heartbeat_validator(self, res):
        return res[2] == "phoenix" and res[3] == "phx_reply"

    def heartbeat(self):
        payload = json.dumps([None,str(self.command_index),"phoenix","heartbeat",{}])
        print(f"Sending {payload}")
        self.send(payload)
        self.command_index += 1

        if not self.handle_response(self._heartbeat_validator):
            raise NoResponse(payload)

    def _cast_validator(self, res):
        return res[3] == "phx_reply"

    def cast(self, spell_id):
        global working_nondocumented_spells
        #payload = '["11","'+str(self.command_index)+'","game_1:2","game:begin_cast",{"spell_id":'+str(spell_id)+'}]'
        payload = json.dumps([str(first_num),str(self.command_index),f"game:1:{self.roomid}","game:begin_cast",{"spell_id":spell_id}])
        #print(f"Sending {payload}")
        self.send(payload)
        self.command_index += 1

        if not self.handle_response(self._cast_validator):
            raise NoResponse(payload)

    def _move_to_room_validator(self, roomid):
        def validator(res):
            return res[3] == f"game:1:{roomid}" and "status" in res[4] and res[4]["status"] == "ok"
        return validator

    def move_to_room(self, roomid):

        payload = json.dumps(["11","11",f"game:1:{roomid}","phx_join",{}])

        self.send(payload)

        if self.handle_response(self._move_to_room_validator):
            self.roomid = roomid
        else:
            raise NoResponse(payload)


def main(ws):
    global working_nondocumented_spells
    print("Sending 'Hello, World'...")
    ws.send(json.dumps(["5","5",USER_ID_FIELD,"phx_join",{}]))
    print(ws.recv())
    ws.send(json.dumps(["8","8","chat:global","phx_join",{}]))
    print(ws.recv())
    #ws.send(json.dumps(["11","11",f"game:1:{ROOM}","phx_join",{}]))
    #print(ws.recv())

    print("Sent")

    bot = Bot(ws)

    bot.move_to_room(ROOM)

    rounds_since_heartbeat=0
    while(1):
        print('.')
        bot.cast(1)
        bot.cast(2)
        bot.cast(3)
        bot.cast(4)
        bot.cast(5)
        bot.cast(6)
        bot.cast(7)
        sleep(0.4)
        bot.cast(1)
        sleep(0.4)
        bot.cast(1)
        sleep(0.4)
        bot.cast(1)
        bot.cast(2)
        sleep(0.4)
        bot.cast(1)
        sleep(0.4)
        bot.cast(1)

        #spell_id_to_test = random.randint(-10000,10000)
        #cast(ws, spell_id_to_test)
        #print("working: " + str(working_nondocumented_spells))
        sleep(1)
        rounds_since_heartbeat += 1
        if rounds_since_heartbeat > HEARTBEAT_EVERY_N_ROUNDS:
        #if True:
            bot.heartbeat()
            rounds_since_heartbeat = 0

        
def run():
    ws = create_connection(args.url)
    main(ws)

while(1):
    try:
        run()
    except Exception as e:
        print(traceback.format_exc())
        #print(Exception, e)
