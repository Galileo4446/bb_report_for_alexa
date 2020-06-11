from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート
import time

# print('速報できる試合を調べています。')

# チーム名入力
teams={'top': 'バッファローズ', 'bottom': 'ホークス'}

print(teams['top'] + '対' + teams['bottom'] + 'の試合経過をお伝えします。')

def main():
    inning=''
    score=''
    bso={'ball': -1, 'strike': -1, 'out': -1}
    batter=''
    pitcher=''
    result=''
    while True:
        url = 'https://baseball.yahoo.co.jp/npb_practice/game/2020061116/score'
        response = request.urlopen(url)
        soup = BeautifulSoup(response, features="html.parser")
        response.close()

        if inning!=soup.select('.live em')[0].text:
            inning=soup.select('.live em')[0].text
            print(inning)

        if score!=score_converter(soup.select('.score table td')) or inning!=soup.select('.live em')[0].text:
            score=score_converter(soup.select('.score table td'))
            print(score_message(score))

        if batter!=get_batter_name(soup):
            batter=get_batter_name(soup)
            print(batter)

        if pitcher!=get_pitcher_name(soup):
            pitcher=get_pitcher_name(soup)
            print(pitcher)

        # TODO ランナー文字変換関数作る
        runner='なし'
        # print(bso['out'] + 'アウト、ランナー' + runner)
        # 打席中（打者名が変わっていない）ならボールカウント
        # アウトカウント変わったらアウトカウント

        try:
            if result!=soup.select('[class=bb-splits__item] table')[2].select('tbody')[0].select('tr')[0].select('.bb-splitsTable__data'):
                result=soup.select('[class=bb-splits__item] table')[2].select('tbody')[0].select('tr')[0].select('.bb-splitsTable__data')
                batting_result=get_batting_result(result)
                print(batting_result_message(batting_result))
        except:
            pass
            # print('次のバッターを待機しています。')
        
        bso_archive=bso
        if bso_archive!=bso_converter(soup.select('.sbo b')):
            bso=bso_converter(soup.select('.sbo b'))
            if bso_archive['out']==bso['out']:
                print(bso_message(bso))
            else:
                print(out_count_message(bso['out']))

                
                

        
        # 点差に応じて得点コメントする。
        # 継投 代打 守備 代走など対応。その時は打者空白になる。
        # print('10秒ごとに更新します')
        time.sleep(10.0)


# def get_match_data():
    # top_team='ホークス'
    # bottom_team='ライオンズ'

# 関数呼び出しはbsoが3まであることを確認してから！様々な処理に使うから大事。
def bso_converter(bso):
    return {'ball': len(bso[0].text), 'strike': len(bso[1].text), 'out': len(bso[2].text)}

def bso_message(bso):
    if bso['strike']==0 and bso['ball']==0:
        return ''
    elif bso['strike']==3 or bso['ball']==4:
        return ''
    else:
        return count_name(bso['ball']) + 'ボール' + count_name(bso['strike']) + 'ストライク'

def out_count_message(out_count):
    if 0<out_count<3:
        return count_name(out_count) + 'アウトです。'
    elif out_count==3:
        return count_name(out_count) + 'アウトチェンジです。'
    else:
        return ''

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

def batting_result_message(result):
    result_name=result['result'].split('[')[0]
    speed=result['speed'].split('km/h')[0] + 'キロ'
    count=result['number'] + '球目'
    if result_name=='ボール':
        return count + 'は、外れてボールです。' + result['type'] + 'が外れました。' + speed + 'でした。'
    elif result_name=='見逃し':
        return count + '、見逃してストライク。' + speed + 'の' + result['type'] + 'が決まっています。'
    elif result_name=='空振り':
        return count + 'を空振り。' + result['type'] + 'でした。'
    elif result_name=='ファウル':
        return count + '、' + result['type'] + 'を打って、ファウルボール。'
    elif result_name=='四球':
        return count + '、見送ってフォアボール'
    elif result_name=='死球':
        return 'おっと、これはデッドボールとなってしまいました。'
    elif result_name=='見三振':
        return count + '、入りました！見逃し三振！' + '最後は' + speed + 'の' + result['type'] + 'でした。'
    elif result_name=='空三振':
        return count + '、空振り三振！' + '最後は' + speed + 'の' + result['type'] + 'が決まりました。'
    elif result_name.endswith('安'):
        return count + position_name_converter(result_name.split('安')[0]) + 'へのヒットになりました。打ったのは' + result['type'] + 'でしょうか。'
    elif result_name.endswith(('２', '2')):
        return count + '捉えた当たりは？' + position_name_converter(result_name.split('２')[0]) + 'へのツーベースヒット！' + result['type'] + 'をうまく捉えました。'
    elif result_name.endswith(('３', '3')):
        return count + 'を打って、' + position_name_converter(result_name.split('３')[0]) + 'へのスリーベースヒット！' + result['type'] + 'をうまく捉えました。'
    elif result_name.endswith('本'):
        return count + '打って、これはどうだ？入るか？入ったー！' + position_name_converter(result_name.split('本')[0]) + 'スタンドに飛び込むホームラン！打ったのは' + result['type'] + 'でしょうか。すばらしい当たりでした。'
    elif result_name.endswith('ゴロ'):
        return count + 'これは' + position_name_converter(result_name.split('ゴロ')[0]) + 'へのゴロになりました。' 
    elif result_name.endswith('邪飛'):
        return count + '打ち上げて、これはファウルフライになりそうです。' + position_name_converter(result_name.split('邪飛')[0]) + 'が、とりました。'
    elif result_name.endswith('犠飛'):
        return count + position_name_converter(result_name.split('犠飛')[0]) + 'への当たり。' + 'ランナー帰って犠牲フライになりました。' 
    elif result_name.endswith('飛'):
        return count + position_name_converter(result_name.split('飛')[0]) + 'へ上がった打球。つかみました。' + position_name_converter(result_name.split('飛')[0]) + 'フライです。' 
    elif result_name.endswith('直'):
        return count + position_name_converter(result_name.split('直')[0]) + 'ライナー。いい当たりでしたが、' + position_name_converter(result_name.split('飛')[0]) + 'がとっています。' 
    elif result_name.endswith('併打'):
        return count + position_name_converter(result_name.split('併打')[0]) + 'へのダブルプレー。最後は' + result['type'] + 'で打ち取りました。' 
    elif result_name.endswith('犠打'):
        return count + 'バントしました。きっちり送ってきました。'
    elif result_name.endswith('失'):
        return 'おっと、これはエラーとなってしまいました。' + position_name_converter(result_name.split('失')[0]) + 'のエラーが記録されています。'
    else:
        return 'まだ登録していない打撃結果です。' + result_name


def position_name_converter(pos):
    if pos=='投':
        return 'ピッチャー'
    elif pos=='捕':
        return 'キャッチャー'
    elif pos=='一':
        return 'ファースト'
    elif pos=='二':
        return 'セカンド'
    elif pos=='三':
        return 'サード'
    elif pos=='遊':
        return 'ショート'
    elif pos=='左':
        return 'レフト'
    elif pos=='中':
        return 'センター'
    elif pos=='右':
        return 'ライト'
    elif pos=='右中':
        return '右中間'
    elif pos=='左中':
        return '左中間'
    else:
        return ''

if __name__ == "__main__":
    main()