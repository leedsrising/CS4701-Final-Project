import sqlite3
import pandas as pd
import json # used to load the lines from data
from datetime import datetime # used to log
import convokit
from convokit import Corpus, download

subreddit = "subreddit-democrats"
corpus = Corpus(filename=download(subreddit))
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

def sql_insert_has_parent(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        #insert new row with parent id, comment id, parent text, comment text, subreddit, unix, score
        sql = """INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(parentid, commentid, parent, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion',str(e))

def text_of_id(id):
    return corpus.get_utterance(utter_ids[id])

for i in corpus.iter_utterances():
    id_to_text[i.id] = (i.text, i.meta["score"])

accum = 0
for i in corpus.iter_utterances():
    if (i.reply_to == None):
        continue
    else:
        try:
            parent_id = i.reply_to
            parent_text = id_to_text[parent_id][0]
            parent_score = id_to_text[parent_id][1]
            pair = [i.text, parent_text]
            if str.lower(i.text) != "[deleted]" and str.lower(parent_text) != "[deleted]":
                if str.strip(i.text) != "" and str.strip(parent_text) != "":
                    if i.meta["score"] >= 2 and parent_score >= 2:
                        sql_insert_has_parent(i, parent_id, parent_text, i.text, subreddit, "", i.meta["score"])
        #exception in the case of no parent ID
        except Exception as e: 
            print(str(e))

timeframe = '2010-01'
sql_transaction = []

# connection to sqlite3 database
connection = sqlite3.connect('/Users/leedsrising/Desktop/RC_{}.db'.format(timeframe))
c = connection.cursor()

#removing reddit specific terminology that is not relevant to conversation
def format_data(data):
    data = data.replace('\n','').replace('\r','').replace('"',"'")
    return data

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS parent_reply(parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT, comment TEXT, subreddit TEXT, unix INT, score INT)")

def transaction_bldr(sql):
    global sql_transaction
    #continuously append sql transactions until prespecified length
    sql_transaction.append(sql)
    if len(sql_transaction) > 1500:
        c.execute('BEGIN TRANSACTION')
        # execute all sql statments that do not result in an error
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        # commit changes made
        connection.commit()
        sql_transaction = []

def acceptable(data):
    # ensure comment is not empty or too long
    if len(data.split(' ')) > 50 or len(data) < 1:
        return False
    # ensure comment does not have over 1000 characters
    elif len(data) > 1000:
        return False
    # ensure no deleted or removed comments
    elif data == '[deleted]':
        return False
    elif data == '[removed]':
        return False
    else:
        return True

def find_parent(pid):
    try:
        #find parent comments
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    #exception in the case that the parent/parent id is not found
    except Exception as e:
        return False

def find_existing_score(pid):
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    #exception in the case that the comment/comment score is not found
    except Exception as e:
        return False

def sql_insert_replace_comment(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        sql = """UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id =?;""".format(parentid, commentid, parent, comment, subreddit, int(time), score, parentid)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion', str(e))

def sql_insert_no_parent(commentid,parentid,comment,subreddit,time,score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}",{},{});""".format(parentid, commentid, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion', str(e))

if __name__ == '__main__':
    create_table()
    row_counter = 0
    paired_rows = 0

    with open("/Users/leedsrising/Desktop/RC_{}".format(timeframe), buffering=1000) as f:
        for row in f:
            row_counter += 1
            row = json.loads(row)
            parent_id = row['parent_id']
            body = format_data(row['body'])
            created_utc = row['created_utc']
            score = row['score']
            comment_id = row['name']
            subreddit = row['subreddit']
            parent_data = find_parent(parent_id)

            if score >= 2:
                existing_comment_score = find_existing_score(parent_id)
                if existing_comment_score:
                    if score > existing_comment_score:
                        if acceptable(body):
                            sql_insert_replace_comment(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)
            else:
                if acceptable(body):
                    if parent_data:
                        sql_insert_has_parent(comment_id,parent_id,parent_data,body,subreddit,created_utc,score)
                        paired_rows += 1
                    else:
                        sql_insert_no_parent(comment_id,parent_id,body,subreddit,created_utc,score)
            if row_counter % 100000 == 0:
                print('Total Rows Read: {}, Paired Rows: {}, Time: {}'.format(row_counter, paired_rows, str(datetime.now())))
    
    