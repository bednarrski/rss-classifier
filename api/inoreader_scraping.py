from api import inoreader_api
import json
    
def scrape(feed, start_time, file_name):
    current_time = 1918252800 # some data in year 2030
    all_articles = []
    mods = ''
    while current_time > start_time:
        answer = inoreader_api.inoreader_request('stream/contents/'+feed+mods)
        batch = answer['items']
        mods = '?c=' + answer['continuation']
        current_time = (batch[0])['published']
        all_articles=all_articles+batch

    json_content = {'all_articles' : all_articles}
    json_string = json.dumps(json_content)
    f = open(file_name, 'w')
    f.write(json_string)
    f.close()
    
    return len(all_articles)

if __name__ == '__main__':

    start_time = 1508112001
    feed = 'user/-/label/arXiv'
    file_name = 'articles_raw.json'

    num = inoreader_request(sample_input)
    print(num)
