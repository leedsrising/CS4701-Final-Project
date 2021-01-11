import sqlite3
import pandas as pd
from datetime import datetime

#reddit data up to January 2010
timeframes = ['2010-01']

for timeframe in timeframes:
    connection = sqlite3.connect('/Users/leedsrising/Desktop/RC_{}.db'.format(timeframe))
    c = connection.cursor()
    limit = 5000 
    last_unix = 0 
    cur_length = limit
    counter = 0
    test_done = False
    while cur_length == limit:
        print('Before, Time: {}'.format(str(datetime.now())))
        df = pd.read_sql("SELECT * FROM parent_reply WHERE unix > {} and parent NOT NULL and score > 0 ORDER BY unix ASC LIMIT {}".format(last_unix,limit),connection)
        print('After, Time: {}'.format(str(datetime.now())))
        last_unix = df.tail(1)['unix'].values[0]
        cur_length = len(df)
        if not test_done:
            with open('/Users/leedsrising/Desktop/test.from','a', encoding='utf8') as f:
                for content in df['parent'].values:
                    f.write(content+'\n')

            with open('/Users/leedsrising/Desktop/test.to','a', encoding='utf8') as f:
                for content in df['comment'].values:
                    f.write(str(content)+'\n')

            test_done = True
            
        else:
            with open('/Users/leedsrising/Desktop/train.from','a', encoding='utf8') as f:
                for content in df['parent'].values:
                    f.write(content+'\n')

            with open('/Users/leedsrising/Desktop/train.to','a', encoding='utf8') as f:
                for content in df['comment'].values:
                    f.write(str(content)+'\n')
        
        counter += 1
        if counter % 20 == 0:
            print(counter*limit,'rows completed so far')

                