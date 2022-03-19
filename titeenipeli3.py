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

command_index=12
first_num=11

MAX_RECV_PACKETS=100

HEARTBEAT_EVERY_N_ROUNDS=10

#websocket.enableTrace(True)

class NoResponseToCast(Exception):
    pass

class UnknownPlayerException(Exception):
    pass

working_nondocumented_spells=[]

def heartbeat(ws):
    global command_index
    payload = json.dumps([None,str(command_index),"phoenix","heartbeat",{}])
    print(f"Sending {payload}")
    ws.send(payload)
    command_index += 1


    recv_packets=0
    while recv_packets <= MAX_RECV_PACKETS:
        r = ws.recv()
        #print(r, flush=True)
        res = json.loads(r)
        #print(res[3])

        #['11', '755', 'game:1:4', 'phx_reply', {'response': {'reason': 'Unknown spell'}, 'status': 'error'}]


        if res[2] == "phoenix" and res[3] == "phx_reply":
            # Assume it's done
            print(res)
            return
        else:
            print("no")
        recv_packets += 1
        
    raise NoResponseToCast()

def cast(ws, spell_id):
    global command_index
    global working_nondocumented_spells
    #payload = '["11","'+str(command_index)+'","game_1:2","game:begin_cast",{"spell_id":'+str(spell_id)+'}]'
    payload = json.dumps([str(first_num),str(command_index),f"game:1:{ROOM}","game:begin_cast",{"spell_id":spell_id}])
    #print(f"Sending {payload}")
    ws.send(payload)
    command_index += 1

    recv_packets=0
    while recv_packets <= MAX_RECV_PACKETS:
        res = json.loads(ws.recv())
        #print(res[3])

        #['11', '755', 'game:1:4', 'phx_reply', {'response': {'reason': 'Unknown spell'}, 'status': 'error'}]


        if res[3] == "phx_reply":
            if "reason" in res[4]['response'] and res[4]['response']['reason'] == 'Unknown player':
                raise UnknownPlayerException()
            # Assume it's done
            #print(res)
            if spell_id > 7 or spell_id < 1:
                if res[4]['response']['reason'] != 'Unknown spell':
                    working_nondocumented_spells.append(spell_id)
            return
        else:
            #print("no")
            pass
        recv_packets += 1
        
    raise NoResponseToCast()

def  main(ws):
    global working_nondocumented_spells
    print("Sending 'Hello, World'...")
    ws.send(json.dumps(["5","5",USER_ID_FIELD,"phx_join",{}]))
    print(ws.recv())
    ws.send(json.dumps(["8","8","chat:global","phx_join",{}]))
    print(ws.recv())
    ws.send(json.dumps(["11","11",f"game:1:{ROOM}","phx_join",{}]))
    print(ws.recv())
    print("Sent")

    rounds_since_heartbeat=0
    while(1):
        print('.')
        cast(ws, 1)
        cast(ws, 2)
        cast(ws, 3)
        cast(ws, 4)
        cast(ws, 5)
        cast(ws, 6)
        cast(ws, 7)
        sleep(1)
        cast(ws, 1)
        sleep(1)
        cast(ws, 1)
        cast(ws, 2)
        sleep(1)
        cast(ws, 1)

        #spell_id_to_test = random.randint(-10000,10000)
        #cast(ws, spell_id_to_test)
        #print("working: " + str(working_nondocumented_spells))
        sleep(1)
        rounds_since_heartbeat += 1
        if rounds_since_heartbeat > HEARTBEAT_EVERY_N_ROUNDS:
        #if True:
            heartbeat(ws)
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
