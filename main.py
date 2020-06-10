from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート

print('速報できる試合を調べています。')

# チーム名入力
teams={'top': 'バッファローズ', 'bottom': 'ホークス'}

print(teams['top'] + '対' + teams['bottom'] + 'の試合経過をお伝えします。')



def main():
    url = 'https://baseball.yahoo.co.jp/npb_practice/game/2020060915/score?index=0320300'
    response = request.urlopen(url)
    soup = BeautifulSoup(response, features="html.parser")
    response.close()

    inning=soup.select('.live em')[0].text
    score=score_converter(soup.select('.score table td'))
    bso=bso_converter(soup.select('.sbo b'))

    batter=get_batter_name(soup)
    pitcher=get_pitcher_name(soup)

    print(inning)
    print(score_message(score))
    # TODO ランナー文字変換関数作る
    runner='なし'
    # print(bso['out'] + 'アウト、ランナー' + runner)
    print(pitcher)
    print(batter)
    print(bso_message(bso))
    # print('カウントは、' + bso['ball'] + 'ボール' + bso['strike'] + 'ストライク')

    result=soup.select('[class=bb-splits__item] table')[2].select('tbody')[0].select('tr')[-1].select('.bb-splitsTable__data')
    batting_result=get_batting_result(result)
    print('ここ')
    print(batting_result_message(batting_result))
    print('ここ')
    print(batting_result)
    # 継投 代打 守備 代走など対応。その時は打者空白になる。


# def get_match_data():
    # top_team='ホークス'
    # bottom_team='ライオンズ'

# 関数呼び出しはbsoが3まであることを確認してから！様々な処理に使うから大事。
def bso_converter(bso):
    return {'ball': len(bso[0]), 'strike': len(bso[1]), 'out': len(bso[2])}

def bso_message(bso):
    return 'カウントは' + count_name(bso['ball']) + 'ボール' + count_name(bso['strike']) + 'ストライク' if len(count_name(bso['ball'])) * len(count_name(bso['strike'])) else ''

def count_name(num):
    if num == 0:
        return 'ノー'
    elif num == 1:
        return 'ワン'
    elif num == 2:
        return 'ツー'
    elif num == 3:
        return 'スリー'
    else:
        return ''    

def score_converter(score):
    return {'top': int(score[1].text), 'bottom': int(score[3].text)}

def score_message(score):
    score_name=str(score['top']) + '対' + str(score['bottom'])
    if score['top']==score['bottom']:
        return score_name + 'の同点です。'
    elif score['top']>score['bottom']:
        return score_name + 'で、' + teams['top'] + 'がリードしています。'
    elif score['top']<score['bottom']:
        return score_name + 'で、' + teams['bottom'] + 'がリードしています。'
    else:
        return ''

def get_pitcher_name(soup):
    if len(soup.select('#pitcherL a')):
        return 'ピッチャーは' + soup.select('#pitcherL a')[0].text
    elif len(soup.select('#pitcherR a')):
        return 'ピッチャーは' + soup.select('#pitcherR a')[0].text
    else:
        return ''

def get_batter_name(soup):
    return 'バッターは' + soup.select('#batter a')[0].text if soup.select('#batter a') else ''

def get_batting_result(result):
    return{'number' : result[0].text.strip(), 'total' : result[1].text.strip(), 'type' : result[2].text.strip(), 'speed' : result[3].text.strip(), 'result' : result[4].text.replace(' ', '').replace('\n', '')}

# 打席継続 or 打席終了 or イニング終了のラベルつける？ アウトカウントで判断すればいらないかも。バッター名毎回取得するのは大変でもない。ただ変更はどうにか検知？
# ①継続系の結果を取り出す。メッセージ作成
# ②打球飛ばない系の結果取り出す。メッセージ作成。
# ③打球が飛んだ結果の解析。後半で結果を判定。最初の文字でポジション判別。右中間左中間に注意。見逃している結果もあるかもしれないから注意。
def batting_result_message(result):
    result_name=result['result'].split('[')[0]
    # continue_list=['見逃し', '空振り', 'ボール', 'ファウル']
    # next_list=['四球', '死球']
    if result_name=='ボール':
        return ''
    return '編集中！'

if __name__ == "__main__":
    main()