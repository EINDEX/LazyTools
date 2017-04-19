import re
import time
from bs4 import BeautifulSoup
import requests

URI = 'http://www.liaoxuefeng.com'


def get_request_index(url):
    r = requests.get('http://www.liaoxuefeng.com' + url)
    if r.ok:
        bs = BeautifulSoup(r.content.decode(), 'lxml')
        return [e.attrs['href'] for e in
                bs.find('div', 'x-sidebar-left-content').find_all('a', {'href': re.compile('^/wiki/')})]


def get_context(url):
    print('sleeping 1 second')
    time.sleep(1)
    try:
        r = requests.get(URI + url)
        if r.ok:
            bs = BeautifulSoup(r.content.decode(), 'lxml')
            wiki_root = bs.find('div', 'x-content')
            title = wiki_root.h4.text
            print('downloading page: %s' % title)
            context = wiki_root.find('div', 'x-wiki-content')
            context = change_image2local(title, context)
            return '<h1>' + title + '</h1>' + str(context)
    except OSError:
        time.sleep(10)
        return get_context(url)


def change_image2local(title, content):
    try:
        count = 0
        for image in content.find_all('img', {'src': re.compile('^/files/')}):
            print('downloading image: %s-%d' % (title, count))
            src = 'image/%s-%d.png' % (title.replace('/', '_'), count)
            with open(src, 'wb') as f:
                f.write(requests.get(URI + image.attrs['src'], stream=True).content)
            content.find('img', {'src': image.attrs['src']}).attrs['src'] = src
            count += 1
        return content
    except OSError:
        time.sleep(10)
        return change_image2local(title, content)


if __name__ == '__main__':
    q = get_request_index('/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000')
    res = ''.join([get_context(link) for link in q])
    print(res)
    with open('res.html', 'wb') as html:
        html.write(res.encode('utf-8'))
