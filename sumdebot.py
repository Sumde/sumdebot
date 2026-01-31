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

ignore_words = [
'\n', '_', 'sumdebot',
'a', 'about', 'above', 'after', 'again', 'against', 'ah', 'all', 'also',
'am', 'an', 'and', 'any', 'anything', 'are', 'as', 'at', 'back', 'be', 'been',
'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'cant',
'come', 'could', 'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont',
'down', 'during', 'each', 'even', 'ever', 'else', 'everything', 'few', 'first',
'for', 'from', 'further', 'get', 'getting', 'give', 'go', 'goes', 'going',
'good', 'got', 'had', 'has', 'have', 'havent', 'having', 'he', 'hello', 'her',
'here', 'hers', 'herself', 'hi', 'him', 'himself', 'his', 'how', 'i', 'id',
'if', 'ill', 'im', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'know',
'like', 'look', 'make', 'me', 'more', 'most', 'much', 'my', 'myself', 'new',
'no', 'nor', 'not', 'now', 'of', 'off', 'ok', 'okay', 'on', 'once', 'one',
'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
'people', 'same', 'say', 'see', 'she', 'should', 'since', 'so', 'some',
'something', 'such', 'take', 'than', 'that', 'thatd', 'thats', 'the', 'their',
'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'thing',
'think', 'this', 'those', 'though', 'through', 'to', 'too', 'two', 'under',
'until', 'up', 'us', 'use', 'very', 'want', 'was', 'way', 'we', 'well', 'were',
'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will',
'with', 'work', 'would', 'yeah', 'yes', 'yep', 'you', 'your', 'yours',
'yourself', 'yourselves',
] # uh partially stolen list from nikkybot hehe

ignore_words_french = [
'\n', '_', 'sumdebot',
'un', 'à propos', 'au-dessus', 'après', 'encore', 'contre', 'ah', 'tout', 'aussi',
'suis', 'une', 'et', 'n\'importe quel', 'n\'importe quoi', 'sont', 'comme', 'à', 'retour', 'être', 'été',
'avant', 'étant', 'en dessous', 'entre', 'les deux', 'mais', 'par', 'peut', 'ne peut pas',
'venir', 'pourrait', 'a fait', 'n\'a fait pas', 'faire', 'fait', 'ne fait pas', 'en train de faire', 'ne fait pas',
'en bas', 'pendant', 'chaque', 'même', 'jamais', 'autre', 'tout', 'peu', 'premiere',
'pour', 'à partir de', 'plus loin', 'obtenir', 'obtenir', 'donner', 'aller', 'va', 'aller',
'bien', 'avoir', 'avait', 'a', 'avoir', 'n\'a pas', 'ayant', 'il', 'bonjour', 'elle',
'ici', 'le sien', 'elle-même', 'salut', 'lui', 'lui-même', 'son', 'comment', 'je', 'je',
'si', 'vais', 'il', 'dedans', 'dans', 'est', 'il', 'son', 'lui-même', 'juste', 'savoir',
'aimer', 'regarder', 'faire', 'moi', 'plus', 'la plupart', 'beaucoup', 'mon', 'moi-même', 'nouveau',
'non', 'ni', 'pas', 'maintenant', 'de', 'éteint', 'ok', 'okay', 'allumé', 'une fois', 'un fois',
'seulement', 'ou', 'autre', 'notre', 'les nôtres', 'nous-mêmes', 'dehors', 'terminé', 'propre',
'les gens', 'meme', 'dire', 'vois', 'elle', 'devrait', 'puisque', 'donc', 'certains',
'quelque chose', 'tel', 'prendre', 'que', 'que', 'que', 'c\'est', 'le', 'leur',
'leurs', 'eux', 'eux-mêmes', 'alors', 'là', 'ceux', 'ils', 'chose',
'penser', 'ceci', 'ceux', 'bien que', 'à travers', 'à', 'trop', 'deux', 'sous',
'jusqu\'à', 'en haut', 'nous', 'utiliser', 'très', 'vouloir', 'était', 'chemin', 'nous', 'bien', 'étions',
'quoi', 'quand', 'où', 'lequel', 'pendant que', 'qui', 'que', 'pourquoi', 'va',
'travailler', 'voudriez', 'ouais', 'oui', 'ouais', 'vous', 'votre', 'vos',
'vous-même', 'nous-mêmes',
] # translation from the last list to french

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, port))
irc.setblocking(False)
irc.send(f"NICK {nick}\r\n".encode())
irc.send(f"USER {nick} 0 * :Bridge Bot\r\n".encode())

markov = MarkovBot(order=2)
with open(datafile,"r",encoding="utf-8") as f:
    markov.train(f.read())

people = ["Sumde","NovemberXmas","Jeff Calc 84","Delta X","Yourlocalceilingfan","Floofyboy","System","twisted_nematic57","Scaralover123","clevor"]

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
                                    for word in ignore_words:
                                        text = text.replace(word, "")
                                    
                                    if text.lower().find("sumdebot bannings")!=-1:
                                        irc.send(f"PRIVMSG {channel} :RANDOM MONTHLY BANNINGS\r\n".encode())
                                        irc.send(f"PRIVMSG {channel} :{random.choice(people)}: You lose!\r\n".encode())
                                    elif text.lower().find("sumdebot")!=-1 and text.lower().find("help")!=-1:
                                        irc.send(f"PRIVMSG {channel} :I am a Markov Chain that spits out answers similar to what sumde says. https://github.com/Sumde/sumdebot\r\n".encode())
                                    elif text.lower().find("sumdebot")!=-1 and text.lower().find("aide")!=-1:
                                        irc.send(f"PRIVMSG {channel} :Je suis un « chaîne de Markov » que dit mots ce similaire à ce que dit sumde. https://github.com/Sumde/sumdebot\r\n".encode())
                                    elif text.lower().find("sumdebot")!=-1:
                                        if(random.randint(1,50)<40):
                                            repeated_message_trys = 1
                                        elif(random.randint(1,50)>=40):
                                            repeated_message_trys = random.randint(2,3)

                                        for i in range(repeated_message_trys):
                                            message = markov.generate_from_prompt(text)
                                            irc.send(f"PRIVMSG {channel} :{message}\r\n".encode())
                                except Exception as e:
                                    print("Error: ", e)
                        except Exception as e:
                            print("PRIVMSG parse error:", e)
        
listen_irc(channels)

while True:
    time.sleep(0.1)
