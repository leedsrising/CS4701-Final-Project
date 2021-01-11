from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import jsonlines
import convokit
from convokit import Corpus, download
#Creating GUI with tkinter
import tkinter
from tkinter import *

corpus = Corpus(filename=download("subreddit-republicans"))

# corpus = Corpus(filename=download("subreddit-democrats"))
utter_ids = corpus.get_utterance_ids()
#print(type(utter_ids))

# relevant = lambda utt: utt.meta['score'] >= 2
# utter_ids.transform(corpus, selector=relevant)
# print(len(utter_ids))

# has_parent = lambda utt: utt.meta['parent'] != null
# utter_ids.transform(corpus, selector=has_parent)
# print(len(utter_ids))

id_to_text = {}
pairs = []

def text_of_id(id):
    return corpus.get_utterance(utter_ids[id])

for i in corpus.iter_utterances():
    id_to_text[i.id] = (i.text, i.meta["score"])

for i in corpus.iter_utterances():
    if (i.reply_to == None): # or whatever else you'd like to do
        continue
    else:
        parent_id = i.reply_to
        parent_text = id_to_text[parent_id][0]
        parent_score = id_to_text[parent_id][1]
        pair = [i.text, parent_text]
        if str.lower(i.text) != "[deleted]" and str.lower(parent_text) != "[deleted]":
            if str.strip(i.text) != "" and str.strip(parent_text) != "":
                if i.meta["score"] >= 2 and parent_score >= 2:
                    pairs.append(pair)

#print(len(pairs))

# with jsonlines.open('republican_utterances.jsonl') as f:
#     accum = 0
#     for line in f.iter():
#         if accum == 5:
#             break
#         elif (line["reply_to"] == None): # or whatever else you'd like to do
#             continue
#         else:
#             parent_id = line["reply_to"]
#             #how to get parent efficiently
#             pair = [line["text"], parent_id]
            
#             accum += 1

chatbot = ChatBot('Republican')

# Create a new trainer for the chatbot
trainer = ListTrainer(chatbot)

for i in pairs:
    trainer.train(i)

import pickle

with open('repub_list.pkl', 'wb') as f:
    pickle.dump(pairs, f)
#creating own corpus
#training on reddit data

# Train the chatbot based on the english corpus
trainer.train("chatterbot.corpus.english")

# Get a response to an input statement
print("-----RESPONSE------")

while True:
    response = input("Talk : ")
    while True:
        response = chatbot.get_response(response)
        if (str.strip(str(response)) == "") or (str.strip(str.lower(str(response))) == "[deleted]"):
            continue
        else:
            break
    print(response)

# def send():
#     msg = EntryBox.get("1.0",'end-1c').strip()
#     EntryBox.delete("0.0",END)

#     if msg != '':
#         ChatLog.config(state=NORMAL)
#         ChatLog.insert(END, "You: " + msg + '\n\n')
#         ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

#         res = response
#         ChatLog.insert(END, "Bot: " + res + '\n\n')

#         ChatLog.config(state=DISABLED)
#         ChatLog.yview(END)


# base = Tk()
# base.title("Hello")
# base.geometry("400x500")
# base.resizable(width=FALSE, height=FALSE)

# #Create Chat window
# ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)

# ChatLog.config(state=DISABLED)

# #Bind scrollbar to Chat window
# scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
# ChatLog['yscrollcommand'] = scrollbar.set

# #Create Button to send message
# SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
#                     bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff',
#                     command= send )

# #Create the box to enter message
# EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Arial")
# #EntryBox.bind("<Return>", send)


# #Place all components on the screen
# scrollbar.place(x=376,y=6, height=386)
# ChatLog.place(x=6,y=6, height=386, width=370)
# EntryBox.place(x=128, y=401, height=90, width=265)
# SendButton.place(x=6, y=401, height=90)

# base.mainloop()
