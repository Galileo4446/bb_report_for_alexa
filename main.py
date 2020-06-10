from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート

url = 'https://baseball.yahoo.co.jp/npb_practice/game/2020060915/score?index=0710200'
response = request.urlopen(url)
soup = BeautifulSoup(response, features="html.parser")
response.close()


inning=soup.select('.live em')
print(inning)

score=soup.select('.score table td')
print(score)

sbo=soup.select('.sbo b')
print(sbo)

result=soup.select('#result')
print(result)
# 継投 代打 守備 代走など対応。その時は打者空白になる。

batter=soup.select('#batter a')
print(batter)

pitcher=soup.select('#pitcherL a')
print(pitcher)

pitcher=soup.select('#pitcherR a')
print(pitcher)