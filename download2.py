import urllib.request
import concurrent.futures
import subprocess
import os
import requests
from bs4 import BeautifulSoup

def get_urls(path):
    r  = requests.get(path)
    data = r.text
    soup = BeautifulSoup(data)
    URLS = []
    for link in soup.find_all('a'):
        #print(link.get('href'))
        URLS.append(path+link.get('href'))
    return URLS

def load_url2(url, timeout):
    base=os.path.basename(url)
    out = os.path.splitext(base)
    outtxt = out[0] + out[1]
    if os.path.exists('download2/'+outtxt) == True:
        return "already complete"
    else:
        url = url
        print(url)
        urllib.request.urlretrieve(url, 'download2/'+outtxt)
        return url

def load_data2(workers):
    URLS = []
    long_url_2 = "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/UGS_Wasatch/UGS_Wasatch_be/Del_4/"
    two = get_urls(long_url_2)
    URLS = URLS + two
    #three = get_urls(long_url_3)
    #URLS = URLS + three
    #four = get_urls(long_url_4)
    #URLS = URLS + four
    print(URLS)
    print(len(URLS))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        
        future_to_url = {executor.submit(load_url2, url, 60): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('one finished')