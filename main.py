import pandas as pd
from bs4 import BeautifulSoup 
import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import tweepy

liste = []
new = []


def Tweetle(tweet):
    
    consumer_key=""
    consumer_secret=""
    access_token=""
    access_token_secret=""
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API(auth)
    try:
        api.update_status(tweet)
    except:
        pass


def urldata():
    urls = []
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    url = "https://www.oddstorm.com/odds/"
    response = requests.get(url, headers=headers,verify=False)
    html = response.content
    soup = BeautifulSoup(html,"lxml")
    linkler = soup.find_all("tr",{"class":"mro"})     
    for i in linkler:
        if "."not in i.text[-4:]:
            if "-" not in i.text[-4:]:
                urls.append(i.a['href'])
    for i in urls:
        new.append(url+i+"&k=0")
    


def GetData(url):
    odds = []
    oddss = []
    bookmaker = []
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    response = requests.get(url, headers=headers,verify=False)
    html_icerigi = response.content
    soup = BeautifulSoup(html_icerigi,"lxml")
    birlik = soup.find_all('span',{"class":"oddtip"})
    bookmakers = soup.find_all('td',{"class":"bn"})
    for i in birlik:
        odds.append(i.text)
    for i in range (0,len(odds),3):
        oddss.append(odds[i:i+3])
    

    for i in bookmakers:
        bookmaker.append(i.text)
    if 'Tempobet' in bookmaker:
        yenidata = pd.DataFrame(oddss,bookmaker)
        yenidata.columns = ["MS 1","MS X","MS 2"]
        yenidata["MS 1"] = yenidata["MS 1"].astype(float)
        yenidata["MS X"] = yenidata["MS X"].astype(float)
        yenidata["MS 2"] = yenidata["MS 2"].astype(float)
        yenidata["Payout"] = 1*1/((1/yenidata["MS 1"])+(1/yenidata["MS X"])+(1/yenidata["MS 2"]))
        yenidata["ORT P.O"] = yenidata["Payout"].mean()
        yenidata["ORT D.O 1"] = yenidata["MS 1"].mean()
        yenidata["ORT D.O X"] = yenidata["MS X"].mean()
        yenidata["ORT D.O 2"] = yenidata["MS 2"].mean()
    
        yenidata["MS 1Y"]=(yenidata["ORT P.O"]/yenidata["ORT D.O 1"])
        yenidata["MS XY"]=(yenidata["ORT P.O"]/yenidata["ORT D.O X"])
        yenidata["MS 2Y"]=(yenidata["ORT P.O"]/yenidata["ORT D.O 2"])
    
        yenidata["MS 1K"] = 1-yenidata["MS 1Y"]
        yenidata["MS XK"] = 1-yenidata["MS XY"]
        yenidata["MS 2K"] = 1-yenidata["MS 2Y"]
    
        yenidata["VALUE1"] = (yenidata["MS 1"]-1)
        yenidata["VALUEX"] = (yenidata["MS X"]-1)
        yenidata["VALUE2"] = (yenidata["MS 2"]-1)
        yenidata["Kelly1"] = (((yenidata["VALUE1"])*yenidata["MS 1Y"])-yenidata["MS 1K"])/yenidata["VALUE1"]
        yenidata["KellyX"] = (((yenidata["VALUEX"])*yenidata["MS XY"])-yenidata["MS XK"])/yenidata["VALUEX"]
        yenidata["Kelly2"] = (((yenidata["VALUE2"])*yenidata["MS 2Y"])-yenidata["MS 2K"])/yenidata["VALUE2"]
        yenidata.to_csv('yenidata.csv')
        y = pd.read_csv('yenidata.csv', index_col=[0],squeeze=True)
        value =y["Kelly1"] > 0.02
        value2 =y["Kelly2"] > 0.02
        yuzde1 =y["MS 1Y"] > 0.50
        yuzde2 =y["MS 2Y"] > 0.50
        ms1y = yuzde1['Tempobet']
        ms2y = yuzde2['Tempobet']
        tempo = value["Tempobet"]
        tempox = value2["Tempobet"]
        if (tempo == True) and (ms1y == True):
            a = ("Value Detected = {}".format(url))
            Tweetle(a)
            print("ValueDetected")
                
                   
        elif (tempox == True) and (ms2y == True):
            b = ("Value Detected = {}".format(url))
            Tweetle(b)
            print("ValueDetected")
            
        else:
            pass
            
    else:
        
        pass

s = input("Başlamak için s'ye basınız")
if s == 's':
    while True:
        urldata()        
        for i in new:
            try:
                GetData(i)
                          
                print('{}',i)
            except:
                pass
