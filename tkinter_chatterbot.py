from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import jsonlines
#Creating GUI with tkinter
import tkinter as tk
from tkinter import *
import pickle

def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(font=("Verdana", 12 ,'bold'),fg='green')


        res =chatbot.get_response(msg)
        # res = ""
        ChatLog.insert(END, "MyBot:: " + str(res) + '\n\n')

        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)

base = Tk()
base.title("Baseline Chatbot System")
base.geometry("900x500")
base.resizable(width=True, height=True)

#Create Chat window
ChatLog = Text(base, bg="#CCD1D1", height="8", width="300", font="Arial")

ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

with open('repub_list.pkl', 'rb') as f:
    pairs = pickle.load(f)

chatbot = ChatBot('Republican')

# Create a new trainer for the chatbot
trainer = ListTrainer(chatbot)

for i in pairs:
    trainer.train(i)

#Create Button to send message
SendButton = Button(base, font=("Verdana",15,'bold'), text="Enter", width="12", height=10,
                    bd=10, bg='green', fg='#58D68D',
                    command= send )

#Create the box to enter message
EntryBox = Text(base, bg="#CCD1D1",width="29", height="5", font="Arial")
EntryBox.pack()

#Place all components on the screen
scrollbar.place(x=106,y=500, height=200)
ChatLog.place(x=6,y=6, height=386, width=870)
EntryBox.place(x=128, y=401, height=90, width=748)
SendButton.place(x=6, y=401, height=90)

base.mainloop()



