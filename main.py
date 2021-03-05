from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート
import time
import jtalk

def main():
    url = 'https://baseball.yahoo.co.jp/npb/schedule'
    response = request.urlopen(url)
    soup = BeautifulSoup(response, features="html.parser")
    response.close()
    games=[]
    teams=[]
    for item in soup.select('.bb-score__item a'):
        game_info= {'top'     : item.select('.bb-score__awayLogo')[0].text,
                    'bottom'  : item.select('.bb-score__homeLogo')[0].text,
                    'ballpark': item.select('span')[0].text,
                    'url'     : item.get('href'),
                    'status'  : item.select('.bb-score__link')[0].text}
        games.append(game_info)
    # print(soup.select('.bb-score__team'))
    # .bbscore__itemでfor回す。速報可能かつチーム名かぶったらurlとtopbottomをteamsに格納
    # 終了していたら結果報告するといいかも見どころなら開始時刻と見どころ読み上げる？
    # print(soup.select('.bb-score__team')[5].text)
    # 最大6試合検索 速報可能ならteamsに追加
    if len(games)>0:
        print('速報してほしいチームを教えてください。')
        target_team=input()
        # 入力を変換
    else:
        print('本日の試合はありません。次の試合までお待ちください。')
    for game in games:
        if target_team == game['top'] or target_team == game['bottom']:
            teams=game
    if teams:
        if teams['status'].endswith(('表', '裏')):
            teams['url']=teams['url'].strip('index') + 'score'
            print(teams['url'])
            live_report(teams)
        elif teams['status']=='試合終了':
            after_report(teams)
        elif teams['status']=='試合前' or teams['status']=='予告先発' or teams['status']=='見どころ' or teams['status']=='スタメン':
            before_report(teams)
        elif teams['status']=='試合中止':
            canceled_report(teams)
        else:
            print(teams['status'])
            print('！！この状況にまだ対応していません。')
    else:
        print('一致する球団がありませんでした。')

def live_report(teams):
    print(teams['top'] + '対' + teams['bottom'] + 'の試合経過をお伝えします。')
    inning=''
    score=''
    bso={'ball': 0, 'strike': 0, 'out': 0}
    batter=''
    pitcher=''
    result=''
    runner=''
    while True:
        url=teams['url']
        response = request.urlopen(url)
        soup = BeautifulSoup(response, features="html.parser")
        response.close()
        message=''
        language ='ja'
        if inning!=soup.select('.live em')[0].text:
            inning=soup.select('.live em')[0].text
            score=score_converter(soup.select('.score table td'))
            try:
                message+=inning_message(inning, teams)
            except:
                if inning=='試合前':
                    print('試合前です。試合開始時刻を過ぎた後にまたお試しください。')
                    break
                elif inning=='試合終了':
                    print('試合は終了しました。実況を終了します。')
                    break
                else:
                    print('取得できませんでした。速報を終了します。')
                    break
            message+=(score_message(score, teams))

        if batter!=get_batter_name(soup):
            batter=get_batter_name(soup)
            message+=batter

        if pitcher!=get_pitcher_name(soup):
            pitcher=get_pitcher_name(soup)
            message+=pitcher

        # 起動時にノーアウトと出る。回が変わったときはノーアウトとは出さない。
        if runner!=get_runner(soup):
            runner=get_runner(soup)
            if count_name(bso['out'])!='スリー':
                message+=count_name(bso['out']) + 'アウト'
                message+=get_runner(soup)

        try:
            if result!=soup.select('[class=bb-splits__item] table')[2].select('tbody')[0].select('tr')[0].select('.bb-splitsTable__data'):
                result=soup.select('[class=bb-splits__item] table')[2].select('tbody')[0].select('tr')[0].select('.bb-splitsTable__data')
                batting_result=get_batting_result(result)
                message+=batting_result_message(batting_result)
        except:
            pass
            # print('次のバッターを待機しています。')

        bso_archive=bso
        if bso_archive!=bso_converter(soup.select('.sbo b')):
            bso=bso_converter(soup.select('.sbo b'))
            if bso_archive['out']==bso['out']:
                message+=bso_message(bso)

            else:
                message+=out_count_message(bso['out'])

        if score!=score_converter(soup.select('.score table td')):
            score=score_converter(soup.select('.score table td'))
            message+=score_message(score, teams)
        # TODO リプレー検証中に対応

        # 継投 代打 守備 代走など対応。その時は打者空白になる。
        if len(message) > 0:
            print(message)
            jtalk.jtalk (message)
        time.sleep(10.0)

def inning_message(inning, teams):
    inning_num=inning.split('回')[0]
    inning_frame=inning.split('回')[1]
    if inning_frame=='表':
        return inning_num + '回オモテ、' + teams['top'] + 'の攻撃。'
    elif inning_frame=='裏':
        return inning_num + '回ウラ、' + teams['bottom'] + 'の攻撃。'
    else:
        return inning

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

def score_message(score, teams):
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
        url='https://baseball.yahoo.co.jp' + soup.select('#pitcherL a')[1].get('href')
        name=soup.select('#pitcherL a')[1].text
    elif len(soup.select('#pitcherR a')):
        url='https://baseball.yahoo.co.jp' + soup.select('#pitcherR a')[1].get('href')
        name=soup.select('#pitcherR a')[1].text
    else:
        return ''
    try:
        response = request.urlopen(url)
        soup_player = BeautifulSoup(response, features="html.parser")
        response.close()
        if len(soup_player.select('.bb-profile__name rt')[0])>0:
            name=soup_player.select('.bb-profile__name rt')[0].text.strip('（）')
        else:
            name=soup_player.select('.bb-profile__name h1')[0].text.strip('（）')
    except:
        pass
    return 'ピッチャーは' + name + '。'

def get_runner(soup):
    runner=[len(soup.select('#base1 span')), len(soup.select('#base2 span')), len(soup.select('#base3 span'))]
    if runner[0] and runner[1] and runner[2]:
        return 'ランナー満塁。'
    elif runner[0] and runner[1]:
        return 'ランナー一塁二塁。'
    elif runner[0] and runner[2]:
        return 'ランナー一三塁。'
    elif runner[1] and runner[2]:
        return 'ランナー二塁三塁。'
    elif runner[0]:
        return 'ランナー一塁。'
    elif runner[1]:
        return 'ランナー二塁。'
    elif runner[2]:
        return 'ランナー三塁。'
    else:
        return 'ランナーなし。'

def get_batter_name(soup):
    if len(soup.select('#batter a')):
        url='https://baseball.yahoo.co.jp' + soup.select('#batter a')[1].get('href')
        name=soup.select('#batter a')[1].text
        try:
            response = request.urlopen(url)
            soup_player = BeautifulSoup(response, features="html.parser")
            response.close()
            if soup_player.select('.bb-profile__name rt')[0]:
                name=soup_player.select('.bb-profile__name rt')[0].text.strip('（）')
            else:
                name=soup_player.select('.bb-profile__name h1')[0].text.strip('（）')
            return 'バッターは' + name + '。'
        except:
            return 'バッターは' + name + '。'
    return ''

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
    elif result_name=='敬遠':
        return '歩かせました。敬遠です。'
    elif result_name=='死球':
        return count + 'これはデッドボールとなってしまいました。'
    elif result_name=='見三振':
        return count + '、入りました！見逃し三振！' + '最後は' + speed + 'の' + result['type'] + 'でした。'
    elif result_name=='空三振':
        return count + '、空振り三振！' + '最後は' + speed + 'の' + result['type'] + 'が決まりました。'
    elif result_name=='バ三振':
        return count + '、バントしましたが、打球は切れています。スリーバント失敗です。'
    elif result_name.endswith('安'):
        return count + position_name_converter(result_name.split('安')[0]) + 'へのヒットになりました。打ったのは' + result['type'] + 'でしょうか。'
    elif result_name.endswith(('２', '2')):
        return count + '捉えた当たりは？' + position_name_converter(result_name.split('２')[0]) + 'へのツーベースヒット！' + result['type'] + 'をうまく捉えました。'
    elif result_name.endswith(('３', '3')):
        return count + 'を打って、' + position_name_converter(result_name.split('３')[0]) + 'へのスリーベースヒット！' + result['type'] + 'をうまく捉えました。'
    elif result_name.endswith('本'):
        return count + '打って、これはどうだ？入ったー！' + position_name_converter(result_name.split('本')[0]) + 'スタンドに飛び込むホームラン！打ったのは' + result['type'] + 'でしょうか。すばらしい当たりでした。'
    elif result_name.endswith('ゴロ'):
        return count + 'これは' + position_name_converter(result_name.split('ゴロ')[0]) + 'へのゴロになりました。'
    elif result_name.endswith('邪飛'):
        return count + '打ち上げて、これはファウルフライになりそうです。' + position_name_converter(result_name.split('邪飛')[0]) + 'が、とりました。'
    elif result_name.endswith('邪直'):
        return count + '、ライナーとなりましたが、' + position_name_converter(result_name.split('邪直')[0]) + 'がファールゾーンでつかんでいます。。'
    elif result_name.endswith('犠飛'):
        return count + position_name_converter(result_name.split('犠飛')[0]) + 'へ上がった打球。' + 'ランナー帰って犠牲フライになりました。'
    elif result_name.endswith('犠飛失'):
        return count + '犠牲フライになりました。エラーによりランナーも出塁しています。'
    elif result_name.endswith('飛'):
        return count + position_name_converter(result_name.split('飛')[0]) + 'へ上がった打球。つかみました。' + position_name_converter(result_name.split('飛')[0]) + 'フライです。'
    elif result_name.endswith('直'):
        return count + position_name_converter(result_name.split('直')[0]) + 'ライナー。いい当たりでしたが、' + position_name_converter(result_name.split('直')[0]) + 'がとっています。'
    elif result_name.endswith('併打'):
        return count + position_name_converter(result_name.split('併打')[0]) + 'へのダブルプレー。最後は' + result['type'] + 'で打ち取りました。'
    elif result_name.endswith('野選'):
        return count + position_name_converter(result_name.split('野選')[0]) + 'のフィルダースチョイスです。'
    elif result_name.endswith('犠野'):
        return count + '、バントした打球、' + position_name_converter(result_name.split('犠野')[0]) + 'のフィルダースチョイスです。'
    elif result_name.endswith('犠打'):
        return count + '、バントしました。きっちり送ってきました。'
    elif result_name.endswith('犠打失'):
        return count + '、バントしました。守備のエラーが記録されています。'
    elif result_name.endswith('暴振逃'):
        return count + '、ピッチャーの暴投による振り逃げとなっています。'
    elif result_name.endswith('逸振逃'):
        return count + '、キャッチャーがそらして振り逃げとなっています。'
    elif result_name.endswith('打撃妨'):
        return count + '、打撃妨害が記録されています。'
    elif result_name.endswith('守妨害'):
        return count + '、守備妨害が記録されています。'
    elif result_name.endswith('規則違'):
        return count + '、規則違反となりました。'
    elif result_name.endswith('失'):
        return 'これはエラーとなってしまいました。' + position_name_converter(result_name.split('失')[0]) + 'のエラーが記録されています。'
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

def after_report(teams):
    print(teams['top'] + '対' + teams['bottom'] + 'の試合結果をお知らせします。1対1の引き分けに終わりました。')
    # 点数と勝敗、勝ち投手など。あれば戦評読む。その後終了。
    return

def before_report(teams):
    print(teams['top'] + '対' + teams['bottom'] + 'の試合情報です。')
    print('予告先発は、先発Aと先発Bです。')
    print('見どころは、4番の働きです。')
    print('18時プレイボール予定です。試合開始後にもう一度起動してください。')
    return

def canceled_report(teams):
    print('本日の、' + teams['top'] + '対' + teams['bottom'] + 'の試合は中止となりました。')
    return

if __name__ == "__main__":
    main()
