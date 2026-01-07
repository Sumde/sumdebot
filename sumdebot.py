# I was a bit lazy so I copied and pasted code from another project I built, so the code won't make sense.

import socket
import time
import threading
import requests
import random
from markov import MarkovBot

server = "irc.efnet.nl"
port = 6667
nick = "sumdebot"
channels = [""]
datafile = ""

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, port))
irc.setblocking(False)
irc.send(f"NICK {nick}\r\n".encode())
irc.send(f"USER {nick} 0 * :Bridge Bot\r\n".encode())

markov = MarkovBot(order=2)
with open(datafile,"r",encoding="utf-8") as f:
    markov.train(f.read())

people = ["Sumde","NovemberXmas","Jeff Calc 84","Delta X","Yourlocalceilingfan","Floofyboy","System","twisted_nematic57","Scaralover123"]

buffer = ""
joined = False

def listen_irc(channels):
    while True:
        global buffer
        global joined
        
        try:
            data = irc.recv(4096).decode("utf-8", errors="ignore")
        except BlockingIOError:
            data = ""
            
        if data:
            buffer+=data
            
            while "\r\n" in buffer:
                line, buffer = buffer.split("\r\n",1)
                
                if not line:
                    continue
                print("<<<", line)
                
                if line.startswith("PING"):
                    token = line.split()[1].lstrip(':')
                    irc.send(f"PONG {token}\r\n".encode())
                    continue
                
                if " 433 " in line:
                    nick += "_"
                    irc.send(f"NICK {nick}\r\n".encode())
                    print("Nick in use, trying:", nick)
                    continue
                
                if " 001 " in line:
                    for channel in channels:
                        irc.send(f"JOIN {channel}\r\n".encode())
                        print(">>> JOIN", channel)
                    joined = True
                    break
                
                for channel in channels:
                    if " PRIVMSG " in line:
                        try:
                            prefix_rest = line.split(" PRIVMSG", 1)
                            if len(prefix_rest) < 2:
                                continue
                            prefix = prefix_rest[0]
                            rest = prefix_rest[1]
                            if " :" not in rest:
                                continue
                            target, text = rest.split(" :", 1)
                            target = target.strip()
                            text = text.rstrip("\r\n")
                            
                            if target.lower() == channel.lower():
                                sender = prefix.split("!")[0].lstrip(":")
                                print(f"[{target}] <{sender}> {text}")
                                try:
                                    if text.find("sumdebot bannings")!=-1:
                                        irc.send(f"PRIVMSG {channel} :RANDOM MONTHLY BANNINGS\r\n".encode())
                                        irc.send(f"PRIVMSG {channel} :{random.choice(people)}: You lose!\r\n".encode())
                                    elif text.find("sumdebot")!=-1 and text.find("help")!=-1:
                                        irc.send(f"PRIVMSG {channel} :I am a bot that spits out random premade responses when I am called upon. https://github.com/Sumde/sumdebot\r\n".encode())
                                    elif text.find("sumdebot")!=-1:
                                            for i in range(random.randint(1,3)):
                                                message = markov.generate_from_prompt(text)
                                                irc.send(f"PRIVMSG {channel} :{message}\r\n".encode())
                                except Exception as e:
                                    print("Error: ", e)
                        except Exception as e:
                            print("PRIVMSG parse error:", e)
        
listen_irc(channels)

while True:
    time.sleep(0.1)
