from flask import Flask , request, jsonify
from flask_cors import CORS
from newsapi import NewsApiClient
import ast
import re

app = Flask(__name__ ,static_url_path='')
CORS(app)
app.config["DEBUG"] = True

# Init
newsapi = NewsApiClient(api_key='b843733b833f4f8aa9b9f69ce8fffbd1')
#8073a8b6efac4b679b0ebebcb3f5658f
#b843733b833f4f8aa9b9f69ce8fffbd1
# /v2/top-headlines
'''
top_headlines = newsapi.get_top_headlines(q='bitcoin',
                                          sources='bbc-news,the-verge',
                                          category='business',
                                          language='en',
                                          country='us')

# /v2/everything
all_articles = newsapi.get_everything(q='bitcoin',
                                      sources='bbc-news,the-verge',
                                      domains='bbc.co.uk,techcrunch.com',
                                      from_param='2017-12-01',
                                      to='2017-12-12',
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)

# /v2/sources
sources = newsapi.get_sources()
'''


@app.route('/', methods=['GET', 'POST'])
def home():
  return app.send_static_file('index.html')
  #return content_list
  #return content_list#app.send_static_file(content_list)


@app.route('/category', methods=['POST','GET'])
def category():
  category = request.values.get('category')
  sources = set()
  sources_list = []
  count = 0
  if category == "all":
    articles =  newsapi.get_sources(language='en', country='us')

    for i in range(len(articles['sources'])):
      if articles['sources'][i]['name'] not in sources:
        sources.add(articles['sources'][i]['name'])
        sources_list.append(articles['sources'][i])
        count += 1
        if count == 10:
          break

    return jsonify(sources_list)
  else:
    articles = newsapi.get_sources(language='en', country='us', category=category)
    for i in range(len(articles['sources'])):
      if articles['sources'][i]['name'] not in sources:
        sources.add(articles['sources'][i]['name'])
        sources_list.append(articles['sources'][i])
        count += 1
        if count == 10:
          break

    return jsonify(sources_list)


@app.route('/search', methods=['POST','GET'])
def search():
  keyword = request.values.get('keyword')
  source = request.values.get('source')
  fromd = request.values.get('fromd')
  tod = request.values.get('tod')
  search_cards = []

  if source == "all":
  	try:
  		articles = newsapi.get_everything(q=keyword, from_param=fromd, to=tod, language='en', page_size=80, sort_by='publishedAt')
  	except Exception as e:
  		print(ast.literal_eval(str(e))['message'])
  		error_dict = {'title':'error_date', 'error':ast.literal_eval(str(e))['message']}
  		
  		search_cards.append(error_dict)
  		return jsonify(search_cards)
  else:
  	try:
  		articles = newsapi.get_everything(q=keyword, from_param=fromd, to=tod, sources=source, language='en', page_size=80, sort_by='publishedAt')
  	except Exception as e:
  		print(ast.literal_eval(str(e))['message'])
  		error_dict = {'title':'error_date', 'error':ast.literal_eval(str(e))['message']}
  		
  		search_cards.append(error_dict)
  		return jsonify(search_cards)
  		
  article_keys = ['author', 'title', 'description', 'url', 'urlToImage', 'publishedAt', 'source']
  sources_keys = ['id', 'name']
  news_set = set()

  for i in range(len(articles['articles'])):
  	for k in article_keys:
  		if k not in articles['articles'][i].keys():
  			break
  	for k in sources_keys:
  		if k not in articles['articles'][i]['source'].keys(): 
  			break
  	#if articles['articles'][i]['author'] == "" or articles['articles'][i]['title'] == "" or articles['articles'][i]['description'] == "" or articles['articles'][i]['url'] == "" or articles['articles'][i]['urlToImage'] == "" or articles['articles'][i]['publishedAt'] == "" or articles['articles'][i]['source'] == "" or articles['articles'][i]['source']['id'] == "" or articles['articles'][i]['source']['name'] == "":
  	if articles['articles'][i]['author'] == None or articles['articles'][i]['title'] == None or articles['articles'][i]['description'] == None or articles['articles'][i]['url'] == None or articles['articles'][i]['urlToImage'] == None or articles['articles'][i]['publishedAt'] == None or articles['articles'][i]['source'] == None or articles['articles'][i]['source']['id'] == None or articles['articles'][i]['source']['name'] == None or articles['articles'][i]['author'] == "" or articles['articles'][i]['title'] == "" or articles['articles'][i]['description'] == "" or articles['articles'][i]['url'] == "" or articles['articles'][i]['urlToImage'] == "" or articles['articles'][i]['publishedAt'] == "" or articles['articles'][i]['source'] == "" or articles['articles'][i]['source']['id'] == "" or articles['articles'][i]['source']['name'] == "":
  		continue
  	if articles['articles'][i]['url'] not in news_set:
  		search_cards.append(articles['articles'][i])
  		news_set.add(articles['articles'][i]['url'])



  return jsonify(search_cards)


@app.route('/slides', methods=['GET', 'POST'])
def slides():
  articles =  newsapi.get_top_headlines()
  articles_five = []
  source_set = set()

  count = 0
  for i in range(len(articles['articles'])):
    s_name = articles['articles'][i]['source']['name']
    if s_name != "" and s_name not in source_set and articles['articles'][i]['urlToImage']!="":
      count+=1
      source_set.add(s_name)
      articles_five.append(articles['articles'][i])
  
  return jsonify(articles_five)

@app.route('/cnnfox', methods=['GET', 'POST'])
def cnnfox():
  articles_cnn =  newsapi.get_top_headlines(sources='cnn')
  result = []
  for i in range(4):
    result.append(articles_cnn['articles'][i])
  articles_fox =  newsapi.get_top_headlines(sources='fox-news')
  for i in range(4):
    result.append(articles_fox['articles'][i])
  return jsonify(result)

#word cloud
@app.route('/index', methods=['GET', 'POST'])
def yo():
  stopwords = []
  #read file
  with open('stopwords_en.txt') as f:
      # with open('test.txt') as f:
          for line in f:
              line = line.replace("\n", "")
              stopwords.append(line)

  articles =  newsapi.get_top_headlines(page_size=30)
  #articles_fox =  newsapi.get_everything(language="en", sources="fox-news")
  #articles_google =  newsapi.get_everything(language="en", sources="google-news")
  tmp_string_list = []
  #print(articles)
  for i in range(len(articles['articles'])):
    tmp_string_list.append(articles['articles'][i]['title'].lower())

  word_cloud_list = []
  for i in range(len(tmp_string_list)):
    tmp_string_split = tmp_string_list[i].split()
    for j in range(len(tmp_string_split)):
      if re.findall(r'[a-z]+', tmp_string_split[j]):
        word_cloud_list.append(re.findall(r'[a-z]+', tmp_string_split[j])[0])

  word_cloud_set = set(word_cloud_list)
  word_cloud_dict = dict()
  for key in word_cloud_set:
    word_cloud_dict[key] = word_cloud_list.count(key)
  word_cloud_dict = sorted(word_cloud_dict.items(), key=lambda k: k[1], reverse=True)

  

  count = 0
  content_list = []
  for k,v in word_cloud_dict:
    if k not in stopwords and k != "":
      content_list.append(k)
      count+=1
    if count == 30:
      break

  
  return ' '.join([str(elem) for elem in content_list])
'''
@app.route('/')
def home():
    #global content_list
    return app.send_static_file('hello.html')
    #return render_template('homepage.html', contents='This is index page')

     #return {%render_template('d3-cloud.js', contents='yo')%}
'''


#app.run(host='0.0.0.0', port=5500, use_reloader=False) # allow public connection
if __name__ == "__main__":
  app.run()