# -*- coding: utf-8 -*-


import requests 
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

DOMAIN = 'en.wikipedia.org'
HOST = 'https://'+ DOMAIN 
graph ={} # граф перхода между ссылками

def get_random_url():
    page = requests.get('https://en.wikipedia.org/wiki/Special:Random')
    return page.url

def add_all_links_recursive(url,  search_url, maxdepth=1, use_urls = []):
    
    # глубина рекурсии не более `maxdepth`
    if url in use_urls:
        return True
    
    if graph.get(url) == None:
        # множество ссылок
        links_to_handle_recursive = set()

        # получаем html код страницы
        request = requests.get(url)
       
        # парсим его с помощью BeautifulSoup
        soup = BeautifulSoup(request.content, 'html.parser')
        
        
        content = soup.find(id='mw-content-text')# or class_='mw-parser-output'
        
        if content == None:
            print('error: ', url)
            return True

        for ref in content.find_all('a', attrs={'href': re.compile('/wiki/')}):
            
            link = ref['href']
            
            if not ':' in link:
                
                if link.startswith('/') and not link.startswith('//'):
                    # преобразуем относительную ссылку в абсолютную
                    link = HOST + ref['href']
                    
                # проверяем, что ссылка ведёт на нужный домен
                if urlparse(link).netloc == DOMAIN:
                    links_to_handle_recursive.add(link)
                
            if str(link) == search_url:
                graph[url] = links_to_handle_recursive
                return True
            
        graph[url] = links_to_handle_recursive
        
        if maxdepth > 0:
            for link in links_to_handle_recursive:
                stop = add_all_links_recursive(link, search_url, maxdepth=maxdepth - 1 )
                if stop:
                    break
            
def find_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if graph.get(start)==None:
            return None
        for node in graph[start]:
            if node not in path:
                newpath = find_path(graph, node, end, path)
                if newpath: return newpath
        return None

url_1 = get_random_url()
url_2 = get_random_url()

#построение графа  
stop = False 
add_all_links_recursive(url_1, url_2, 10)

stop = False
add_all_links_recursive(url_2, url_1, 10, list(graph.keys()))

#поиск пути на графе
path_url_1_url_2 = find_path(graph, url_1, url_2)
path_url_2_url_1 = find_path(graph, url_2, url_1)

if path_url_1_url_2==None:
    print('path do not search')
else:
    print()
    print('PATH FROM URL1 IN URL2: ', path_url_1_url_2)

if path_url_2_url_1==None:
    print('path do not search')
else:
    print()
    print('PATH FROM URL2 IN URL1: ', path_url_2_url_1)

#for node in graph.keys():
#    print(graph.get(node))