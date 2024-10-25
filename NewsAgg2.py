from gnews import GNews
import sqlite3

google_news = GNews(period='7d',max_results= 5)
issues = ['Free Speach', 'AI', 'Health','Border Security', 'Nuclear War', 'Cosmic Intervention'] 
test = []
stories=[]

def publish():
    get_news()
    create_stories(test)
    to_db(stories)

def get_news():
    # test = []
    issues = ['Free Speach', 'AI', 'Health','Border Security', 'Nuclear War', 'Cosmic Intervention'] 
    for i in range(len(issues)):
        if issues[i] == 'Cosmic Intervention':
            test.append(google_news.get_news('Threats from Space'))
        else:
            test.append(google_news.get_news(issues[i]))
    return test

def create_stories(test):
    i = 0
    j= 0
    print(len(test))
    for i in range(len(issues)):
        for j in range(len(test[i])):
            stories.append({
                'topic':issues[i],
                'title':test[i][j]['title'],
                'link':test[i][j]['url'],
                'date':test[i][j]['published date'],
                'publisher':test[i][j]['publisher']['title']
        })        
            j+=1
            # google_news.clear()
        i+=1
    return stories


def to_db(stories):
    conn = sqlite3.connect('data/news2.db')
    c = conn.cursor()
    for i in stories:
        # print(i['title'])
        data = (i['topic'], i['title'], i['link'],i['date'], i['publisher'])
        query = '''INSERT INTO content (topic,title,link,date,publisher) VALUES (?,?,?,?,?)'''
        c.execute(query, data)
        conn.commit()

    conn.close()

