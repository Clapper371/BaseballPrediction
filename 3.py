from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
import pandas as pd
import timeit
import time
#import json
#import elasticsearch


def is_alert(driver):
    try:
        driver.switch_to.alert()
        return True
    except NoAlertPresentException:
        return False


if __name__ == '__main__':
    # 전체등록현황|선수현황 url
    RegisterAll_URL = 'https://www.koreabaseball.com/Player/RegisterAll.aspx'
    # 게임 날짜별 참여선수 url
    player_line_up_URL = 'https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx'
    # 팀 타자 기록
    team_record_hitter_URL = 'https://www.koreabaseball.com/Record/Team/Hitter/Basic1.aspx'
    # 팀 투수 기록
    team_record_pitcher_URL = 'https://www.koreabaseball.com/Record/Team/Pitcher/Basic1.aspx'
    # 팀 수비 기록
    team_record_defense_URL = 'https://www.koreabaseball.com/Record/Team/Defense/Basic.aspx'
    # 팀 주루 기록
    team_record_runner_URL = 'https://www.koreabaseball.com/Record/Team/Runner/Basic.aspx'
    # 선수기록_타자
    record_hitter_URL = 'https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx'
    # 선수 기록_투수
    record_pitcher_URL = 'https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx'

    browser = webdriver.Chrome(executable_path='chromedriver')# 드라이버는 어디에 있는지 변경
    browser.implicitly_wait(30) # 30초안에 크롬이 안켜지면 프로그램 종료
    """
    # 팀 타자 기록 긁어오기
    browser.get(team_record_hitter_URL)
    record_hitter_year_select = browser.find_element_by_class_name('select03')

    # 모든 년도 기록 긁어오기
    option_list = record_hitter_year_select.find_elements_by_tag_name('option')
    year_list = []
    for option in option_list:
        year_list.append(option.text)

    team_record_hitter_dfs = []
    for year in year_list:
        # select element를 갱신하지 않으면 오래되어 사용할 수 없는 오류가 뜸
        record_hitter_year_select = browser.find_element_by_class_name('select03')
        for option in record_hitter_year_select.find_elements_by_tag_name('option'):
            if option.text == year:
                option.click()
                #WebDriverWait(browser, 10)

                try :
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break
                # 오래된 요소라고 한다면 다시 시도
                except StaleElementReferenceException:
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break

                team_record_prev_button = browser.find_element_by_class_name('prev')
                try:
                    team_record_prev_button.click()
                except StaleElementReferenceException:
                    team_record_prev_button = browser.find_element_by_class_name('prev')
                    team_record_prev_button.click()

                click_time = timeit.default_timer()
                while True:
                    if (timeit.default_timer() - click_time) > 10:
                        team_record_prev_button.click()
                        click_time = timeit.default_timer()
                    if '경기' in browser.find_element_by_class_name('tData').get_attribute('summary'):
                        break

                team_record_hitter_df1 = pd.read_html(browser.page_source, attrs={'class': 'tData tt'})
                team_record_hitter_df1 = team_record_hitter_df1[0]

                team_record_next_button = browser.find_element_by_class_name('next')
                try:
                    team_record_next_button.click()
                except StaleElementReferenceException:
                    team_record_next_button = browser.find_element_by_class_name('next')
                    team_record_next_button.click()

                click_time = timeit.default_timer()
                # 다음 버튼을 눌러 갱신된 테이블의 설명에 볼넷이라는 용어가 있다면 갱신 완료
                while True:
                    if (timeit.default_timer() - click_time) > 10:
                        team_record_next_button.click()
                        click_time = timeit.default_timer
                    if '볼넷' in browser.find_element_by_class_name('tData').get_attribute('summary'):
                        break

                team_record_hitter_df2 = pd.read_html(browser.page_source, attrs={'class': 'tData tt'})
                team_record_hitter_df2 = team_record_hitter_df2[0]
                team_record_hitter_df2.drop('순위', axis='columns', inplace=True)
                team_record_hitter_df2.drop('AVG', axis='columns', inplace=True)
                team_record_hitter_df = pd.merge(team_record_hitter_df1, team_record_hitter_df2, on='팀명')
                team_record_hitter_df = team_record_hitter_df[team_record_hitter_df['팀명'] != '합계']
                team_record_hitter_df.loc[:, '해당 년도'] = year
                #print(team_record_hitter_df)
                team_record_hitter_dfs.append(team_record_hitter_df)
                # 해당 년도의 데이터를 수집했으므로 select 요소 갱신
                break
            # end if
        # end for select-option
    # end for year
    merged_team_record_hitter_df = team_record_hitter_dfs[0]
    for index in range(1, len(team_record_hitter_dfs)):
        merged_team_record_hitter_df = merged_team_record_hitter_df.append(team_record_hitter_dfs[index])
    print(merged_team_record_hitter_df)
    merged_team_record_hitter_df.to_csv('팀 타자 기록.csv', encoding='ms949')


    # 팀 투수 기록 긁어오기
    browser.get(team_record_pitcher_URL)
    record_pitcher_year_select = browser.find_element_by_class_name('select03')

    # 모든 년도 기록 긁어오기
    option_list = record_pitcher_year_select.find_elements_by_tag_name('option')
    year_list = []
    for option in option_list:
        year_list.append(option.text)

    team_record_pitcher_dfs = []
    for year in year_list:
        # select element를 갱신하지 않으면 오래되어 사용할 수 없는 오류가 뜸
        record_pitcher_year_select = browser.find_element_by_class_name('select03')
        for option in record_pitcher_year_select.find_elements_by_tag_name('option'):
            if option.text == year:
                option.click()

                try:
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break
                # 오래된 요소라고 한다면 다시 시도
                except StaleElementReferenceException:
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break

                team_record_prev_button = browser.find_element_by_class_name('prev')
                try:
                    team_record_prev_button.click()
                except StaleElementReferenceException:
                    team_record_prev_button = browser.find_element_by_class_name('prev')
                    team_record_prev_button.click()
                click_time = timeit.default_timer()
                while True:
                    if (timeit.default_timer() - click_time) > 10:
                        team_record_prev_button.click()
                        click_time = timeit.default_timer()
                    if '승리' in browser.find_element_by_class_name('tData').get_attribute('summary'):
                        break

                team_record_pitcher_df1 = pd.read_html(browser.page_source, attrs={'class': 'tData tt'})
                team_record_pitcher_df1 = team_record_pitcher_df1[0]

                team_record_next_button = browser.find_element_by_class_name('next')
                try:
                    team_record_next_button.click()
                except StaleElementReferenceException:
                    team_record_next_button = browser.find_element_by_class_name('next')
                    team_record_next_button.click()
                click_time = timeit.default_timer()
                # 다음 버튼을 눌러 갱신된 테이블의 설명에 완투라는 용어가 있다면 갱신 완료
                while True:
                    if (timeit.default_timer() - click_time) > 10:
                        team_record_next_button.click()
                        click_time = timeit.default_timer
                    if '완투' in browser.find_element_by_class_name('tData').get_attribute('summary'):
                        break

                team_record_pitcher_df2 = pd.read_html(browser.page_source, attrs={'class': 'tData tt'})
                team_record_pitcher_df2 = team_record_pitcher_df2[0]
                team_record_pitcher_df2.drop('순위', axis='columns', inplace=True)
                team_record_pitcher_df2.drop('ERA', axis='columns', inplace=True)
                team_record_pitcher_df = pd.merge(team_record_pitcher_df1, team_record_pitcher_df2, on='팀명')
                team_record_pitcher_df = team_record_pitcher_df[team_record_pitcher_df['팀명'] != '합계']
                team_record_pitcher_df.loc[:, '해당 년도'] = year
                team_record_pitcher_dfs.append(team_record_pitcher_df)
                # 해당 년도의 데이터를 수집했으므로 select 요소 갱신
                break
            # end if
        # end for select-option
    # end for year
    merged_team_record_pitcher_df = team_record_pitcher_dfs[0]
    for index in range(1, len(team_record_pitcher_dfs)):
        merged_team_record_pitcher_df = merged_team_record_pitcher_df.append(team_record_pitcher_dfs[index])
    print(merged_team_record_pitcher_df)
    merged_team_record_pitcher_df.to_csv('팀 투수 기록.csv', encoding='ms949')

    # 팀 수비 기록 긁어오기
    browser.get(team_record_defense_URL)
    record_defense_year_select = browser.find_element_by_class_name('select03')

    # 모든 년도 기록 긁어오기
    option_list = record_defense_year_select.find_elements_by_tag_name('option')
    year_list = []
    for option in option_list:
        year_list.append(option.text)

    team_record_defense_dfs = []
    for year in year_list:
        # select element를 갱신하지 않으면 오래되어 사용할 수 없는 오류가 뜸
        record_defense_year_select = browser.find_element_by_class_name('select03')
        for option in record_defense_year_select.find_elements_by_tag_name('option'):
            if option.text == year:
                option.click()

                try:
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break
                # 오래된 요소라고 한다면 다시 시도
                except StaleElementReferenceException:
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break

                team_record_defense_df = pd.read_html(browser.page_source, attrs={'class': 'tData tt'})
                team_record_defense_df = team_record_defense_df[0]
                team_record_defense_df = team_record_defense_df[team_record_defense_df['팀명'] != '합계']
                team_record_defense_df.loc[:, '해당 년도'] = year
                team_record_defense_dfs.append(team_record_defense_df)
                # 해당 년도의 데이터를 수집했으므로 select 요소 갱신
                break
            # end if
        # end for select-option
    # end for year
    merged_team_record_defense_df = team_record_defense_dfs[0]
    for index in range(1, len(team_record_defense_dfs)):
        merged_team_record_defense_df = merged_team_record_defense_df.append(team_record_defense_dfs[index])
    print(merged_team_record_defense_df)
    merged_team_record_defense_df.to_csv('팀 수비 기록.csv', encoding='ms949')

    # 팀 주루 기록 긁어오기
    browser.get(team_record_runner_URL)
    record_runner_year_select = browser.find_element_by_class_name('select03')

    # 모든 년도 기록 긁어오기
    option_list = record_runner_year_select.find_elements_by_tag_name('option')
    year_list = []
    for option in option_list:
        year_list.append(option.text)

    team_record_runner_dfs = []
    for year in year_list:
        # select element를 갱신하지 않으면 오래되어 사용할 수 없는 오류가 뜸
        record_runner_year_select = browser.find_element_by_class_name('select03')
        for option in record_runner_year_select.find_elements_by_tag_name('option'):
            if option.text == year:
                option.click()

                try:
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break
                # 오래된 요소라고 한다면 다시 시도
                except StaleElementReferenceException:
                    game_type_select = browser.find_element_by_class_name('select02')

                    # 정규 시즌 통계만 수집
                    for g_type in game_type_select.find_elements_by_tag_name('option'):
                        if g_type.text == 'KBO 정규시즌':
                            g_type.click()
                            break

                team_record_runner_df = pd.read_html(browser.page_source, attrs={'class': 'tData tt'})
                team_record_runner_df = team_record_runner_df[0]
                team_record_runner_df = team_record_runner_df[team_record_runner_df['팀명'] != '합계']
                team_record_runner_df.loc[:, '해당 년도'] = year
                team_record_runner_dfs.append(team_record_runner_df)
                # 해당 년도의 데이터를 수집했으므로 select 요소 갱신
                break
            # end if
        # end for select-option
    # end for year
    merged_team_record_runner_df = team_record_runner_dfs[0]
    for index in range(1, len(team_record_runner_dfs)):
        merged_team_record_runner_df = merged_team_record_runner_df.append(team_record_runner_dfs[index])
    print(merged_team_record_runner_df)
    merged_team_record_runner_df.to_csv('팀 주루 기록.csv', encoding='ms949')
    """
    """
    # 타자 기록 긁어오기
    browser.get(record_hitter_URL)

    # 타자 기본 기록1
    base_record_hitter1 = pd.read_html(browser.page_source, attrs={
        'class': 'tData01 tt'
    })
    next_hitter_button = browser.find_element_by_id('cphContents_cphContents_cphContents_ucPager_btnNo2')
    next_hitter_button.click()

    while True:
        base_record_hitter1_1 = pd.read_html(browser.page_source, attrs={
            'class': 'tData01 tt'
        })
        if base_record_hitter1_1[0]['순위'][0] != base_record_hitter1[0]['순위'][0]:
            break
    base_record_hitter1 = pd.DataFrame(base_record_hitter1[0])
    base_record_hitter1_1 = pd.DataFrame(base_record_hitter1_1[0])
    base_record_hitter1 = pd.concat([base_record_hitter1, base_record_hitter1_1], axis=0)

    # 타자 기본 기록2
    record_hitter_URL = 'https://www.koreabaseball.com/Record/Player/HitterBasic/Basic2.aspx'
    browser.get(record_hitter_URL)
    base_record_hitter2 = pd.read_html(browser.page_source, attrs={
        'class': 'tData01 tt'
    })
    next_hitter_button = browser.find_element_by_id('cphContents_cphContents_cphContents_ucPager_btnNo2')
    next_hitter_button.click()
    while True:
        base_record_hitter2_1 = pd.read_html(browser.page_source, attrs={
            'class': 'tData01 tt'
        })
        if base_record_hitter2_1[0]['순위'][0] != base_record_hitter2[0]['순위'][0]:
            break
    base_record_hitter2 = pd.DataFrame(base_record_hitter2[0])
    base_record_hitter2_1 = pd.DataFrame(base_record_hitter2_1[0])
    base_record_hitter2 = pd.concat([base_record_hitter2, base_record_hitter2_1], axis=0)

    base_record_hitter1.reset_index(drop=True)
    base_record_hitter2.reset_index(drop=True)
    base_record_hitter = pd.merge(base_record_hitter1, base_record_hitter2)
    base_record_hitter.to_csv('2019_KBO_타자 기본 기록.csv', encoding='ms949')

    browser.get(record_pitcher_URL)

    # 투수 기본 기록1
    base_record_pitcher1 = pd.read_html(browser.page_source, attrs={
        'class': 'tData01 tt'
    })
    # 투수 기본 기록2
    record_hitter_URL = 'https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic2.aspx'
    browser.get(record_hitter_URL)
    base_record_pitcher2 = pd.read_html(browser.page_source, attrs={
        'class': 'tData01 tt'
    })
    base_record_pitcher1 = pd.DataFrame(base_record_pitcher1[0])
    base_record_pitcher2 = pd.DataFrame(base_record_pitcher2[0])
    base_record_pitcher = pd.merge(base_record_pitcher1, base_record_pitcher2)
    base_record_pitcher.to_csv('2019_KBO_투수 기본 기록.csv', encoding='ms949')
    """
    print("checkcheck")

    # 기존에 저장된 파일 읽어오기
    is_ex_df = True #기존 엑셀 파일이 있었느냐
    try:
        ex_df = pd.read_csv('2019_KBO_경기 데이터.csv', engine='python') #기존의 경기파일이 있었으면 읽어와라 ->기존의 경기파일이 있는데 똑같은거 읽어오면 안되서
    except FileNotFoundError:  #없으면 false
        is_ex_df = False 

    # 경기 기록 긁어오기
    browser.get(player_line_up_URL) #url을 가져와서 브라우저를 구동을 시킨다.->kbo홈페이지

    # away team이 이기면 1 지면 0 # 데이터 프레임의 틀을 짜놓은 거다. 이 틀안에 맞춰서 크롤링 하겠다. 선수들은 크롤랑하면서 일일이 컬럼추가
    baseball_df = pd.DataFrame(
        columns=['날짜', 'home team', 'away team', '장소', '경기 분류', 'home_score', 'away_score', 'away result'])

    # 시작 페이지의 날짜 선택
    datepicker = browser.find_element_by_class_name('ui-datepicker-trigger') #클래스네임이 ui-datepicker-trigger 인걸 찾아라 
    datepicker.click() #찾은 다음 클릭해라
    # 시작 년도
    datepicker_year = browser.find_element_by_class_name('ui-datepicker-year')
    for option in datepicker_year.find_elements_by_tag_name('option'): #for문으로 리스트 2001년 2021년까지 다 나오고 option중에 텍스트가 2019냐 그러면 클릭해라
        if option.text == '2022':
            option.click()
            break #for문 더 이상 돌리지 말아라
    # 시작 월
    datepicker_month = browser.find_element_by_class_name('ui-datepicker-month')#이제 year에서 month고 10월 부터 시작하겠다.
    for option in datepicker_month.find_elements_by_tag_name('option'):
        # 1월(JAN) 2월(FEB) 3월(MAR) 4월(APR) 5월(MAY) 6월(JUN) 7월(JUL) 8월(AUG) 9월(SEP) 10월(OCT) 11월(NOV) 12월(DEC)
        if option.text == '10월(OCT)':
            option.click()
            print("check1")
            break
    # 시작 일(현재는 시작 하루 후)
    datepicker_calendar = browser.find_element_by_class_name('ui-datepicker-calendar') 
    aes = datepicker_calendar.find_elements_by_tag_name('a')
    for a in aes:
        if a.text == '12': #text ?을 클릭해라
            a.click()
            print("check2")
            break

    # elastic search 오브젝트 생성
    #es_client = elasticsearch.Elasticsearch('localhost:9200')

    # 동명이인(이승현 2명) 구분을 위한 승/패/세이브 확인용 데이터 생성
    same_name_lee = 0
    lee1Win = -1
    lee2Win = -1
    lee1Lose = -1
    lee2Lose = -1
    lee1Save = -1
    lee2Save = -1

    # 경기 날짜 선택
    while True:
        print('while check')
        try:
            # 하루 전 날짜 선택
            prev_button = browser.find_element_by_class_name('prev') #previous라는 버튼이있다 이걸 가져와라
            click_time = timeit.default_timer()
            today = browser.find_element_by_class_name('today').text #today라는 텍스트를 가져와라
            prev_button.click()
            while True: #문제 발생 그당시에 traffic이 많아 버튼이 작동을안해 그러면 while을 걸어서 그 당시에 10초이상 지나가면 한번 더 클릭해라 무한루프로 10초마다 한번씩
                if timeit.default_timer() - click_time > 10:
                    prev_button.click()
                if today != browser.find_element_by_class_name('today').text: #만약에 today가 내가 원하는 today랑 똑같다면 break해라
                    break
        except ElementClickInterceptedException: #traffic이 무지하게 많으면 그냥 무시
            pass
        except UnexpectedAlertPresentException: # 팝업창이 뜨거나 알람이 뜨면 그냥 확인 버튼 눌러
            browser.switch_to.alert.accept()
            #
        today = browser.find_element_by_class_name('today').text  #today텍스트를 또 가져와라
        today_year, today_month, today_day = str(today).split('.') #나눔 . 기준으로 년 월 일로
        today_day, today_etc = str(today_day).split('(') 

        # 몇 년도 까지 읽을 것인가?
        if int(today_year) < 2022:  #2019년 밑으로 2018년이 되면 break
            print("check3")
            break
        print(today_month)
        print(today_day)
        # 19년 3월 23일부터 본 경기. 이전 경기는 시범 경기인듯
        # 몇 달 까지 읽을 것인가?
        if int(today_month) <= 3:  #월 break
            if int(today_day) < 31: #일 break
                print("check4")
                break
        print("check5")
        # 우천 등으로 모든 경기가 취소된 경우
        if browser.find_element_by_id('gameComment').text == '당일 경기는 모두 취소되었습니다.': #그때는 모두 취소 되었다고 떴는데 지금은 잘 모름 보면서 확인
            continue  #continue을 걸어 while문이 돌긴 도는데  continue 걸면 밑에는 진행 안한다. 그래서 for문으로 다시 올라가서 previous button으로 다시 #2903

        # 선택된 날짜에 열린 경기들 선택
        game_list = browser.find_element_by_class_name('game-list-n').find_elements_by_class_name('game-cont') #game_list 가져온다 경기 5개  대체로 5개인데 늘어나는 경우도 있다.
        # 하루에 연속 게임을 하는 경우 검사
        print("check6")
        is_continuous = False #하루 연속경우가 있는 경우가 연타로 하는 경우가 있다. 이전에 못했던 경기를 연타로 하는 경우가 있다.
        b_home_team = -1
        for game in game_list:
            print("check7")
            print(game)
            try:
                game.click()
                print("try")
            except ElementClickInterceptedException: #traffic걸려도 한번 더 클릭해라
                click_time = timeit.default_timer() 
                while timeit.default_timer() - click_time > 3:
                    break
                game.click()
            
            # 경기가 열린(열릴) 장소
            area = game.get_attribute('s_nm') #place 열린 장소 가져옴
            print(area)
            # 게임의 상태 : 경기종료, 취소, "", : 등
            print("check8")
            game_state = game.find_element_by_class_name('staus').text
            print(game_state)
            if '취소' in game_state:
                continue
            elif '예정' in game_state:
                continue
            elif '' == game_state: #공란인 경우도 있다. 취소
                continue
            elif ':' == game_state: #시간이 변경되는 경우도 취소
                continue
            elif 'None' == game_state:
                continue
            # 현재 게임 진행중인 경우 사용
            elif '회' in game_state:
                continue
            game_broadcasting = game.find_element_by_class_name('broadcasting').text #방송 스폰 가져옴
            
            # away team vs home team
            # vs_string = str(game.find_elements_by_tag_name('img')[0].get_attribute('alt')) + ' vs ' + str(game.find_elements_by_tag_name('img')[1].get_attribute('alt'))
            away_team = game.find_elements_by_tag_name('img')[0].get_attribute('alt') #이미지마크에 텍스트 alt 변수가 있다. #alt="두산"
            home_team = game.find_elements_by_tag_name('img')[1].get_attribute('alt')
            if '나눔' in away_team:
                continue
            elif '드림' in away_team:
                continue
            print('check9')

            # home team 이 이전 홈 팀과 같다면 하루에 연속으로 게임하는 경우에 속함
            if home_team == b_home_team: #연타를 하는경우 이조건문에 걸린다. table에 다른 형식으로 들어간다.
                is_continuous = True
            else: 
                is_continuous = False
                b_home_team = home_team

            if game_state == '경기종료':
                # 경기 승/패 결과
                print('check10')
                # result = game.find_element_by_css_selector('span.today-pitcher > span > span').text #span span 두 번 들어가서 today-pitcher 선발투수 텍스트를 가져와라
                winner = game.find_elements_by_class_name('today-pitcher')[0].text
                loser = game.find_elements_by_class_name('today-pitcher')[1].text
                print(winner)
                print(loser)
                print('check11')
                #score_list = game.find_elements_by_class_name('score') #score 읽어오라
                #a_score, h_score = int(score_list[0].text), int(score_list[1].text) #첫번째는 away score 두번째는 home score 앞에있는게 항상 away

                a_score = int(game.find_elements_by_class_name('score')[0].text)
                h_score = int(game.find_elements_by_class_name('score')[1].text)
                print(a_score)
                print(h_score)

                if a_score > h_score:
                    result = '승'
                elif a_score < h_score:
                    result = '패'
                elif a_score == h_score:
                    result = '무'
                # 경기 별 홈, 원정 팀 점수
                # print(away_team, result) #디버그 할라고
                # 1점차 이내는 무승부
                # if -1 <= (a_score - h_score) & (a_score - h_score) <= 1:
                # result = 2
                # el
                if result == '승': #첫번째 away만 가져왔다. away가 이긴 경우 1
                    result = 1
                elif result == '패': #지면 0
                    result = 0
                elif result == '무': #무승부 0 무승부면 그냥 away가 진걸로 우선 해놓았다.
                    # result = 2
                    result = 0
            else: #나같은 경우에는 이런 경우 없는데 경기가 아직 안 일어난 경우 결과가 없다. 아무 텍스트가 없어서 000 
                # result = 2
                result = 0
                a_score, h_score = 0, 0

            baseball_df = baseball_df.append({ #dataframe에다가 긁어온 정보들을 넣어줌
                '날짜': today,
                'home team': home_team,
                'away team': away_team,
                '장소': area,
                '경기 분류': game_broadcasting,
                'home_score': h_score,
                'away_score': a_score,
                'away result': result
            }, ignore_index=True) #보기 편하게 ignore_index

            # 프리뷰가 있다면 열리지 않은 경기라는 뜻
            if browser.find_element_by_class_name('tab-tit').text == '프리뷰': #경기가 아직 안 일어난 경우는 밑에 처럼 읽어 와야한다. #참고로 이부분은 건너뛰고 606줄로 간다.
                # 열리지 않은 경기는 선발 투수를 가져옴
                starter_button = browser.find_element_by_partial_link_text('선발투수 전력분석')
                click_time = timeit.default_timer()
                starter_button.click()
                while True:
                    if (timeit.default_timer() - click_time) > 10:
                        print('경과 시간(초) :', timeit.default_timer() - click_time)
                        starter_button.click()
                        click_time = timeit.default_timer()
                    try:
                        if browser.find_element_by_class_name('sub-tit').text == '선발투수 전력분석':
                            break
                    except StaleElementReferenceException:
                        continue
                pitcher_names = browser.find_elements_by_class_name('name')
                away_pitcher = pitcher_names[0].text
                home_pitcher = pitcher_names[1].text
                baseball_df.loc[(baseball_df['날짜'] == today) &
                                (baseball_df['home team'] == home_team) &
                                (baseball_df['away team'] == away_team), away_team + '_' + away_pitcher] = 1
                baseball_df.loc[(baseball_df['날짜'] == today) &
                                (baseball_df['home team'] == home_team) &
                                (baseball_df['away team'] == away_team), home_team + '_' + home_pitcher] = 1

                # 열리지 않은 경기는 라인업을 가져옴
                line_up_button = browser.find_element_by_link_text('라인업 분석')
                click_time = timeit.default_timer()
                line_up_button.click()
                while True:
                    if (timeit.default_timer() - click_time) > 10:
                        print('경과 시간(초) :', timeit.default_timer() - click_time)
                        line_up_button.click()
                        click_time = timeit.default_timer()
                    try:
                        if browser.find_element_by_class_name('sub-tit').text == '라인업 분석':
                            break
                    except StaleElementReferenceException:
                        continue

                line_up_df = pd.read_html(browser.page_source, attrs={
                    'id': 'tblAwayLineUp'
                })
                line_up_df = pd.DataFrame(line_up_df[0])
                for player in line_up_df['선수명']:
                    baseball_df.loc[(baseball_df['날짜'] == today) &
                                    (baseball_df['home team'] == home_team) &
                                    (baseball_df['away team'] == away_team), away_team + '_' + player] = 1

                line_up_df = pd.read_html(browser.page_source, attrs={
                    'id': 'tblHomeLineUp'
                })
                line_up_df = pd.DataFrame(line_up_df[0])
                for player in line_up_df['선수명']:
                    baseball_df.loc[(baseball_df['날짜'] == today) &
                                    (baseball_df['home team'] == home_team) &
                                    (baseball_df['away team'] == away_team), home_team + '_' + player] = 1


            # 프리뷰가 없다면 진행된 경기라는 뜻
            else:
                # 선택된 경기의 리뷰 열기
                review_button = browser.find_element_by_link_text('리뷰') #리뷰라는 텍스트가 있는 element를 찾아라
                review_class_name = review_button.get_attribute('class') #리뷰인 경우가 있고 아닌 경우가있어서 프린트해봐서 확인해보려고-> 키플레이어 리뷰 하이라이트 뒤죽박죽인 경우가 있다.
                print(review_class_name)
                click_time = timeit.default_timer()
                review_button.click()
                while True:#클릭했는데 리뷰가 떠야하는데 키플레이어가 뜨는 경우가 있다. 이 경우에 10초지나고 한번 더 클릭해라.
                    if (timeit.default_timer() - click_time) > 10:
                        print('경과 시간(초) :', timeit.default_timer() - click_time)
                        review_button.click()
                        click_time = timeit.default_timer()
                    try:
                        if browser.find_element_by_class_name('sub-tit').text == '리뷰':
                            break
                    except StaleElementReferenceException:
                        continue

                WebDriverWait(browser, 10).until(
                    expected_conditions.presence_of_element_located((By.ID, 'tblHomePitcher'))) #id기 tblHomePitcher인 element가 나올때 까지 최대 10초를 기다린다.

                # tblAwayHitter1이라는 id의 테이블을 모두 가져와 list 형태로 담음
                # lxml 설치가 필요하다는 import error 가 뜰 경우 lxml 설치 필요
                # html5lib 설치가 필요하다는 import error 가 뜰 경우 html5lib 설치 필요
                # BeautifulSoup4 설치가 필요하다는 import error 가 뜰 경우 BeautifulSoup4 설치 필요
                away_hitter_df1 = pd.read_html(browser.page_source, attrs={
                    'id': 'tblAwayHitter1' #테이블을 가져와라  테이블이 123로 나누어져있음 가져와라 
                })
                """
                away_hitter_df2 = pd.read_html(browser.page_source, attrs={
                    'id': 'tblAwayHitter2'    
                })
                """
                # table 2 의 경우에는 id 가 table 이 아닌 table 부모 div 태그에 달려있음
                table_list = pd.read_html(browser.page_source) #html에서는 깔끔하게 보이나 코드에서는 드럽게 복잡함
                away_hitter_df2 = pd.DataFrame(table_list[5])[:-1] #그래서 table_list를 가져옴 hitter2는 가져온 테이블이 6번째 그게 또 table list임(2차원 리스트) 거기에서 가장 최근것을 가져오면
                away_hitter_df3 = pd.read_html(browser.page_source, attrs={
                    'id': 'tblAwayHitter3'
                })
                away_hitter_df1 = pd.DataFrame(away_hitter_df1[0])
                away_hitter_df1.dropna(axis='rows', how='all', inplace=True) #row축으로 널값을 제거해라
                # away_hitter_df2 = pd.DataFrame(away_hitter_df1[0])
                # away_hitter_df2.dropna(axis='rows', how='all', inplace=True)
                away_hitter_df3 = pd.DataFrame(away_hitter_df3[0])
                # total 기록 제거
                away_hitter_df3 = away_hitter_df3[:-1]  #타자기록 맨마지막에 total이 있다. 그 밑에부분 제거하는 부분이다.
                away_hitter_df = pd.concat((away_hitter_df1, away_hitter_df2), axis=1) #concat= 합치는거
                away_hitter_df = pd.concat((away_hitter_df, away_hitter_df3), axis=1)

                # 몇 이닝까지 진행된 경기인가?
                # max_inning = len(away_hitter_df.columns) - 3
                max_inning = len(away_hitter_df.columns) - 8 #연장전 된 경우를 대비해서 예외처리
                # print('진행된 이닝 : ', max_inning)

                away_hitter_list = list(away_hitter_df['선수명'].unique()) #동명이인 처리 # 한 팀에 동명이인이 있는 경우
                hitter_number = -1 #기본값 초기화
                for hitter in away_hitter_list: 
                    if len(away_hitter_df.loc[away_hitter_df['선수명'] == hitter]) == 1:  #4123
                        # i = away_hitter_df.loc[away_hitter_df['선수명'] == hitter].count(axis=1).item() - 3
                        # i = away_hitter_df.loc[away_hitter_df['선수명'] == hitter].count(axis=1).item() - 8
                        # i = i / max_inning

                        # 번호가 이전 선수와 같다면 추가 투입 선수
                        if hitter_number == away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item(): #교체선수 파악
                            baseball_df.loc[(baseball_df['날짜'] == today) &
                                            (baseball_df['home team'] == home_team) &
                                            (baseball_df['away team'] == away_team), away_team
                                            # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                            + '_' + hitter] = 0.5  # i
                        else: #같지 않으면 선발타자 선발투수 1로 주자->DataFrame에 날짜는 오늘 날짜 홈팀과 어웨이 팀 선수명을 이렇게 가져와라
                            baseball_df.loc[(baseball_df['날짜'] == today) &
                                            (baseball_df['home team'] == home_team) &
                                            (baseball_df['away team'] == away_team), away_team
                                            # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                            + '_' + hitter] = 1  # i
                    else:
                        for index in away_hitter_df.loc[away_hitter_df['선수명'] == hitter].index:
                            i = away_hitter_df.iloc[index].count().item() - 3
                            i = i / max_inning
                            # 번호가 이전 선수와 같다면 추가 투입 선수
                            if hitter_number == away_hitter_df.loc[
                                away_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item():
                                baseball_df.loc[(baseball_df['날짜'] == today) &
                                                (baseball_df['home team'] == home_team) &
                                                (baseball_df['away team'] == away_team), away_team
                                                # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                                + '_' + hitter] = 0.5  # i
                            else:
                                baseball_df.loc[(baseball_df['날짜'] == today) &
                                                (baseball_df['home team'] == home_team) &
                                                (baseball_df['away team'] == away_team), away_team
                                                # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                                + '_' + hitter] = 1  # i
                            hitter_number = home_hitter_df.loc[home_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item()
                    hitter_number = away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item()
                # end for away hitter

                home_hitter_df1 = pd.read_html(browser.page_source, attrs={
                    'id': 'tblHomeHitter1'
                })
                """
                home_hitter_df2 = pd.read_html(browser.page_source, attrs={
                    'id': 'tblHomeHitter2'
                })
                """
                # table 2 의 경우에는 id 가 table 이 아닌 table 부모 div 태그에 달려있음
                home_hitter_df2 = pd.DataFrame(table_list[8])[:-1]
                home_hitter_df3 = pd.read_html(browser.page_source, attrs={
                    'id': 'tblHomeHitter3'
                })
                home_hitter_df1 = pd.DataFrame(home_hitter_df1[0])
                home_hitter_df1.dropna(axis='rows', how='all', inplace=True)
                # home_hitter_df2 = pd.DataFrame(home_hitter_df2[0])
                home_hitter_df2.dropna(axis='rows', how='all', inplace=True)
                home_hitter_df3 = pd.DataFrame(home_hitter_df3[0])
                # total 기록 제거
                home_hitter_df3 = home_hitter_df3[:-1]

                home_hitter_df = pd.concat((home_hitter_df1, home_hitter_df2), axis=1)
                home_hitter_df = pd.concat((home_hitter_df, home_hitter_df3), axis=1)

                home_hitter_list = list(home_hitter_df['선수명'].unique())
                hitter_number = -1
                for hitter in home_hitter_list:
                    # 몇 이닝을 참여했는지
                    if len(home_hitter_df.loc[home_hitter_df['선수명'] == hitter]) == 1:
                        # i = home_hitter_df.loc[home_hitter_df['선수명'] == hitter].count(axis=1).item() - 3
                        # i = home_hitter_df.loc[home_hitter_df['선수명'] == hitter].count(axis=1).item() - 8
                        # 참여한 이닝 비율을 할당
                        # i = i / max_inning
                        # 번호가 이전 선수와 같다면 추가 투입 선수
                        if hitter_number == home_hitter_df.loc[home_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item():
                            baseball_df.loc[(baseball_df['날짜'] == today) &
                                            (baseball_df['home team'] == home_team) &
                                            (baseball_df['away team'] == away_team), home_team
                                            # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                            + '_' + hitter] = 0.5  # i
                        else:
                            baseball_df.loc[(baseball_df['날짜'] == today) &
                                            (baseball_df['home team'] == home_team) &
                                            (baseball_df['away team'] == away_team), home_team
                                            # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                            + '_' + hitter] = 1  # i

                    # 동명이인이 같은 팀에 존재할 경우
                    else:
                        for index in home_hitter_df.loc[home_hitter_df['선수명'] == hitter].index:
                            i = home_hitter_df.iloc[index].count().item() - 3
                            i = i / max_inning
                            # 번호가 이전 선수와 같다면 추가 투입 선수
                            if hitter_number == home_hitter_df.loc[
                                home_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item():
                                baseball_df.loc[(baseball_df['날짜'] == today) &
                                                (baseball_df['home team'] == home_team) &
                                                (baseball_df['away team'] == away_team), home_team
                                                # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                                + '_' + hitter] = 0.5  # i
                            else:
                                baseball_df.loc[(baseball_df['날짜'] == today) &
                                                (baseball_df['home team'] == home_team) &
                                                (baseball_df['away team'] == away_team), home_team
                                                # + '_' + away_hitter_df.loc[away_hitter_df['선수명'] == hitter, 'Unnamed: 1'].item()
                                                + '_' + hitter] = 1  # i
                            hitter_number = home_hitter_df.loc[home_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item()
                            hitter_number = home_hitter_df.loc[home_hitter_df['선수명'] == hitter, 'Unnamed: 0'].item()
                # end for home hitter
                #0906
                away_pitcher_df = pd.read_html(browser.page_source, attrs={ #pitcher(투수)는 형식이 좀 다르다.
                    'id': 'tblAwayPitcher'
                })
                # 투수 테이블은 마지막에 total 또한 선수명에 포함되어 있으므로 마지막 행 제거 
                # 홀드 세이브 승리 다 필요 없다.
                # 1. 날짜와 경기마다 데이터 크롤링하는 중 그 날짜 안에서 동명이인인 경우 찾기
                # 2. 동명이인이 나오면 그 이름과 기록 저장해놓기, 저장한 이름은 날짜가 바뀌어도 변화가 없어야 함
                # 3. 크롤링 중 동명이인의 이름이 나왔을때, 제일 최근 그 사람의 기록과 유사한 사람으로 매칭
                # 4. 매칭된 선수의 이름으로 기록 저장
                
                '''
                away_pitcher_df = pd.DataFrame(away_pitcher_df[0][:-1])
                away_pitcher_df.dropna(axis='rows', how='all', inplace=True)
                for i in range(len(away_pitcher_df['선수명'])):
                    for j in range(i, len(away_pitcher_df['선수명'])):
                        if i == j:
                            continue
                        if away_pitcher_df['선수명'][i] == away_pitcher_df['선수명'][j]:
                            away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_1'
                            away_pitcher_df['선수명'][j] = away_pitcher_df['선수명'][j]+'_2'
                away_pitcher_list = list(away_pitcher_df['선수명'].unique()) #리스트 읽어오기
                '''
                # 0. 그냥 '이승현' 이름으로 구분
                # 1. 이승현 이름을 가진 투수가 나오면 기록 확인을 통해서 이승현_1인지 이승현_2인지 구별
                # 
                away_pitcher_df = pd.DataFrame(away_pitcher_df[0][:-1])
                away_pitcher_df.dropna(axis='rows', how='all', inplace=True)
                same_name_lee_counter = 0
                for i in range(len(away_pitcher_df['선수명'])):
                    if away_pitcher_df['선수명'][i] == '이승현':
                        if same_name_lee == 0:
                            same_name_lee = 1
                            away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_1'
                            lee1Win = int(away_pitcher_df['승'][i])
                            lee1Lose = int(away_pitcher_df['패'][i])
                            lee1Save = int(away_pitcher_df['세'][i])
                            same_name_lee_counter = same_name_lee_counter + 1
                        elif same_name_lee == 1 and same_name_lee_counter == 0:
                            if str(lee1Win) == away_pitcher_df['승'][i] and str(lee1Lose) == away_pitcher_df['패'][i] and str(lee1Save) == away_pitcher_df['세'][i]:
                                away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(away_pitcher_df['승'][i])
                                lee1Lose = int(away_pitcher_df['패'][i])
                                lee1Save = int(away_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            elif str(lee1Win-1) == away_pitcher_df['승'][i] and str(lee1Lose) == away_pitcher_df['패'][i] and str(lee1Save) == away_pitcher_df['세'][i]:
                                away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(away_pitcher_df['승'][i])
                                lee1Lose = int(away_pitcher_df['패'][i])
                                lee1Save = int(away_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            elif str(lee1Win) == away_pitcher_df['승'][i] and str(lee1Lose-1) == away_pitcher_df['패'][i] and str(lee1Save) == away_pitcher_df['세'][i]:
                                away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(away_pitcher_df['승'][i])
                                lee1Lose = int(away_pitcher_df['패'][i])
                                lee1Save = int(away_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            elif str(lee1Win) == away_pitcher_df['승'][i] and str(lee1Lose) == away_pitcher_df['패'][i] and str(lee1Save-1) == away_pitcher_df['세'][i]:
                                away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(away_pitcher_df['승'][i])
                                lee1Lose = int(away_pitcher_df['패'][i])
                                lee1Save = int(away_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            else:
                                away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_2'
                                lee2Win = int(away_pitcher_df['승'][i])
                                lee2Lose = int(away_pitcher_df['패'][i])
                                lee2Save = int(away_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 2
                        elif same_name_lee_counter == 1:
                            away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_2'
                            lee2Win = int(away_pitcher_df['승'][i])
                            lee2Lose = int(away_pitcher_df['패'][i])
                            lee2Save = int(away_pitcher_df['세'][i])
                        elif same_name_lee_counter == 2:
                            away_pitcher_df['선수명'][i] = away_pitcher_df['선수명'][i]+'_1'
                            lee1Win = int(away_pitcher_df['승'][i])
                            lee1Lose = int(away_pitcher_df['패'][i])
                            lee1Save = int(away_pitcher_df['세'][i])
                away_pitcher_list = list(away_pitcher_df['선수명'].unique()) #리스트 읽어오기             
                
                


                # 경기에 참여한 이닝 비율을 할당
                # 이닝 가져와서 나눠주고 지금은 그냥 1로 가져오는데 예전에는 가중치 준 적이 있어서 나누어져 있는 것이다. 그래서 지금은 1로 가져와라만  작동할 것이다.
                for pitcher in away_pitcher_list:
                    print(str(away_pitcher_df.loc[away_pitcher_df['선수명'] == pitcher, '이닝'].item()))
                    inning = str(away_pitcher_df.loc[away_pitcher_df['선수명'] == pitcher, '이닝'].item())
                    if '/' in inning:
                        if ' ' in inning:
                            inning1, inning2 = str(inning).split(' ')
                            inning2, inning3 = str(inning2).split('/')
                            inning = float(inning1) + float(inning2) / float(inning3)
                        else:
                            inning1, inning2 = str(inning).split('/')
                            inning = float(inning1) / float(inning2)
                    else:
                        inning = float(inning)

                    baseball_df.loc[(baseball_df['날짜'] == today) &
                                    (baseball_df['home team'] == home_team) &
                                    (baseball_df['away team'] == away_team), away_team + '_' + pitcher] = 1  # inning / max_inning

                home_pitcher_df = pd.read_html(browser.page_source, attrs={
                    'id': 'tblHomePitcher'
                })
                '''
                home_pitcher_df = pd.DataFrame(home_pitcher_df[0][:-1])
                home_pitcher_df.dropna(axis='rows', how='all', inplace=True)
                for i in range(len(home_pitcher_df['선수명'])):
                    for j in range(i, len(home_pitcher_df['선수명'])):
                        if i == j:
                            continue
                        if home_pitcher_df['선수명'][i] == home_pitcher_df['선수명'][j]:
                            home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_1'
                            home_pitcher_df['선수명'][j] = home_pitcher_df['선수명'][j]+'_2'
                home_pitcher_list = list(home_pitcher_df['선수명'].unique())
                '''
                home_pitcher_df = pd.DataFrame(home_pitcher_df[0][:-1])
                home_pitcher_df.dropna(axis='rows', how='all', inplace=True)
                same_name_lee_counter = 0
                for i in range(len(home_pitcher_df['선수명'])):
                    if home_pitcher_df['선수명'][i] == '이승현':
                        if same_name_lee == 0:
                            same_name_lee = 1
                            home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_1'
                            lee1Win = int(home_pitcher_df['승'][i])
                            lee1Lose = int(home_pitcher_df['패'][i])
                            lee1Save = int(home_pitcher_df['세'][i])
                            same_name_lee_counter = same_name_lee_counter + 1
                        elif same_name_lee == 1 and same_name_lee_counter == 0:
                            if str(lee1Win) == home_pitcher_df['승'][i] and str(lee1Lose) == home_pitcher_df['패'][i] and str(lee1Save) == home_pitcher_df['세'][i]:
                                home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(home_pitcher_df['승'][i])
                                lee1Lose = int(home_pitcher_df['패'][i])
                                lee1Save = int(home_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            elif str(lee1Win-1) == home_pitcher_df['승'][i] and str(lee1Lose) == home_pitcher_df['패'][i] and str(lee1Save) == home_pitcher_df['세'][i]:
                                home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(home_pitcher_df['승'][i])
                                lee1Lose = int(home_pitcher_df['패'][i])
                                lee1Save = int(home_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            elif str(lee1Win) == home_pitcher_df['승'][i] and str(lee1Lose-1) == home_pitcher_df['패'][i] and str(lee1Save) == home_pitcher_df['세'][i]:
                                home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(home_pitcher_df['승'][i])
                                lee1Lose = int(home_pitcher_df['패'][i])
                                lee1Save = int(home_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            elif str(lee1Win) == home_pitcher_df['승'][i] and str(lee1Lose) == home_pitcher_df['패'][i] and str(lee1Save-1) == home_pitcher_df['세'][i]:
                                home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_1'
                                lee1Win = int(home_pitcher_df['승'][i])
                                lee1Lose = int(home_pitcher_df['패'][i])
                                lee1Save = int(home_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 1
                            else:
                                home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_2'
                                lee2Win = int(home_pitcher_df['승'][i])
                                lee2Lose = int(home_pitcher_df['패'][i])
                                lee2Save = int(home_pitcher_df['세'][i])
                                same_name_lee_counter = same_name_lee_counter + 2
                        elif same_name_lee_counter == 1:
                            home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_2'
                            lee2Win = int(home_pitcher_df['승'][i])
                            lee2Lose = int(home_pitcher_df['패'][i])
                            lee2Save = int(home_pitcher_df['세'][i])
                        elif same_name_lee_counter == 2:
                            home_pitcher_df['선수명'][i] = home_pitcher_df['선수명'][i]+'_1'
                            lee1Win = int(home_pitcher_df['승'][i])
                            lee1Lose = int(home_pitcher_df['패'][i])
                            lee1Save = int(home_pitcher_df['세'][i])
                home_pitcher_list = list(home_pitcher_df['선수명'].unique()) #리스트 읽어오기
                

                # 경기에 참여한 이닝 비율을 할당
                for pitcher in home_pitcher_list:
                    inning = str(home_pitcher_df.loc[home_pitcher_df['선수명'] == pitcher, '이닝'].item())
                    if '/' in inning:
                        if ' ' in inning:
                            inning1, inning2 = str(inning).split(' ')
                            inning2, inning3 = str(inning2).split('/')
                            inning = float(inning1) + float(inning2) / float(inning3)
                        else:
                            inning1, inning2 = str(inning).split('/')
                            inning = float(inning1) / float(inning2)
                    else:
                        inning = float(inning)

                    baseball_df.loc[(baseball_df['날짜'] == today) &
                                    (baseball_df['home team'] == home_team) &
                                    (baseball_df['away team'] == away_team), home_team + '_' + pitcher] = 1  # inning / max_inning
            #home, away 투수들의 정보를 다 가져왔다.
                # logos = browser.find_elements_by_class_name('tit-team')
            # 만들어진 경기 정보 dataframe
            print(baseball_df)#하루에 있는 첫 번째 경기 하나 가지고------ 온 것이다.
    #for문이 지금까지 4개 나왔다. => 큰 for문 2개:ex)달력
    #이거 출력하고 보면 for문을 쭉 돌고 받아오고 출력하면 완성된 for문이 출력될 것이다.

    #이제 경기를 dictionary 형태로 정리

            # 경기 정보를 dictionary 형태로 변환
            baseball_dict = {
                '날짜': today,
                '홈 팀': 0,
                '원정 팀': 0,
                '장소': area,
                '경기 분류': game_broadcasting,
                '홈 팀 점수': h_score,
                '원정 팀 점수': a_score,
                '원정 결과': result,
                ##데이터프레임을 만들기 위한 기본작업
                '홈 선발 투수': [],
                '홈 선발 타자': [],
                '홈 교체 투수': [],
                '홈 교체 타자': [],
                '원정 선발 투수': [],
                '원정 선발 타자': [],
                '원정 교체 투수': [],
                '원정 교체 타자': []
            }
            # 팀 정보 임시 정리
            baseball_dict['홈 팀'] = {
                '이름': home_team
            }
            baseball_dict['원정 팀'] = {
                '이름': away_team
            }

            # home 투수 기록 정리
            for pitcher in home_pitcher_list: #누구였는지 일단 정리를 해줬다. 그당시에는  다가 져왔다.
                pitcher_dict = {
                    '이름': pitcher,
                    '등판': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['등판'].array[0]),
                    '결과': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['결과'].array[0]),
                    '승': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['승'].array[0]),
                    '패': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['패'].array[0]),
                    '세': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['세'].array[0]),
                    '이닝': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['이닝'].array[0]),
                    '타자': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['타자'].array[0]),
                    '투구수': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['투구수'].array[0]),
                    '타수': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['타수'].array[0]),
                    '피안타': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['피안타'].array[0]),
                    '홈런': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['홈런'].array[0]),
                    '4사구': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['4사구'].array[0]),
                    '삼진': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['삼진'].array[0]),
                    '실점': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['실점'].array[0]),
                    '자책': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['자책'].array[0]),
                    '평균자책점': str(home_pitcher_df[home_pitcher_df['선수명'] == pitcher]['평균자책점'].array[0])
                }
                if pitcher_dict['등판'] == '선발':
                    baseball_dict['홈 선발 투수'].append(pitcher_dict)
                else:
                    baseball_dict['홈 교체 투수'].append(pitcher_dict)

            #투수도 정보 다 가져왔고 타자도 정보 다 가져왔다.
            # home 타자 기록 정리 
            for index, hitter in enumerate(home_hitter_list):
                hitter_dict = {
                    '이름': hitter,
                    '포지션': str(home_hitter_df[home_hitter_df['선수명'] == hitter]['Unnamed: 1'].array[0]),
                    '번호': str(home_hitter_df[home_hitter_df['선수명'] == hitter]['Unnamed: 0'].array[0]),
                    '이닝 기록': [],
                    '타수': str(home_hitter_df[home_hitter_df['선수명'] == hitter]['타수'].array[0]),
                    '안타': str(home_hitter_df[home_hitter_df['선수명'] == hitter]['안타'].array[0]),
                    '타점': str(home_hitter_df[home_hitter_df['선수명'] == hitter]['타점'].array[0]),
                    '득점': str(home_hitter_df[home_hitter_df['선수명'] == hitter]['득점'].array[0]),
                    '타율': str(home_hitter_df[home_hitter_df['선수명'] == hitter]['타율'].array[0]),
                }

                for inning in range(max_inning):
                    inning_rec = home_hitter_df.iloc[index][str(inning + 1)]
                    if str(inning_rec) != 'nan':
                        hitter_dict['이닝 기록'].append({
                            '이닝': str(inning + 1),
                            '기록': inning_rec
                        })

                if baseball_df[(baseball_df['날짜'] == today) & (baseball_df['home team'] == home_team)][
                    home_team + '_' + hitter].array[0] == 1:
                    baseball_dict['홈 선발 타자'].append(hitter_dict)
                elif baseball_df[(baseball_df['날짜'] == today) & (baseball_df['home team'] == home_team)][
                    home_team + '_' + hitter].array[0] == 0.5:
                    baseball_dict['홈 교체 타자'].append(hitter_dict)

            # away 투수 기록 정리
            for pitcher in away_pitcher_list:
                pitcher_dict = {
                    '이름': pitcher,
                    '등판': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['등판'].array[0]),
                    '결과': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['결과'].array[0]),
                    '승': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['승'].array[0]),
                    '패': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['패'].array[0]),
                    '세': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['세'].array[0]),
                    '이닝': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['이닝'].array[0]),
                    '타자': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['타자'].array[0]),
                    '투구수': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['투구수'].array[0]),
                    '타수': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['타수'].array[0]),
                    '피안타': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['피안타'].array[0]),
                    '홈런': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['홈런'].array[0]),
                    '4사구': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['4사구'].array[0]),
                    '삼진': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['삼진'].array[0]),
                    '실점': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['실점'].array[0]),
                    '자책': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['자책'].array[0]),
                    '평균자책점': str(away_pitcher_df[away_pitcher_df['선수명'] == pitcher]['평균자책점'].array[0])
                }
                if pitcher_dict['등판'] == '선발':
                    baseball_dict['원정 선발 투수'].append(pitcher_dict)
                else:
                    baseball_dict['원정 교체 투수'].append(pitcher_dict)

            # away 타자 기록 정리
            for index, hitter in enumerate(away_hitter_list):
                hitter_dict = {
                    '이름': hitter,
                    '포지션': str(away_hitter_df[away_hitter_df['선수명'] == hitter]['Unnamed: 1'].array[0]),
                    '번호': str(away_hitter_df[away_hitter_df['선수명'] == hitter]['Unnamed: 0'].array[0]),
                    '이닝 기록': [],
                    '타수': str(away_hitter_df[away_hitter_df['선수명'] == hitter]['타수'].array[0]),
                    '안타': str(away_hitter_df[away_hitter_df['선수명'] == hitter]['안타'].array[0]),
                    '타점': str(away_hitter_df[away_hitter_df['선수명'] == hitter]['타점'].array[0]),
                    '득점': str(away_hitter_df[away_hitter_df['선수명'] == hitter]['득점'].array[0]),
                    '타율': str(away_hitter_df[away_hitter_df['선수명'] == hitter]['타율'].array[0]),
                }

                for inning in range(max_inning):
                    inning_rec = away_hitter_df.iloc[index][str(inning + 1)]
                    if str(inning_rec) != 'nan':
                        hitter_dict['이닝 기록'].append({
                            '이닝': str(inning + 1),
                            '기록': inning_rec
                        })

                if baseball_df[(baseball_df['날짜'] == today) & (baseball_df['away team'] == away_team)][
                    away_team + '_' + hitter].array[0] == 1:
                    baseball_dict['원정 선발 타자'].append(hitter_dict)
                else:
                    baseball_dict['원정 교체 타자'].append(hitter_dict)

            """
            # 변환된 dictionary 를 json 으로 저장
            json_file_name = today + '_' + home_team + '_' + away_team
            # 연속 게임일 경우 파일 이름에 '_' 추가
            if is_continuous:
                json_file_name += '_'

            with open('경기 데이터 json/' + json_file_name, mode='w',encoding='utf-8-sig') as file_pointer:
                json.dump(baseball_dict, file_pointer, indent='\t', ensure_ascii=False)
            """

            # 변환된 dictionary 를 elastic search 에 저장
            #response = es_client.index(index='kbo', doc_type='rec', body=baseball_dict)

            #연타 같은 경우로 5개 경기가 아니라 6개 7개 경기일 경우 다음 버튼을 누른다. 
            #그래서 if문을 걸어둠
            # 다음 경기 버튼이 있다면 클릭 
            next_button = browser.find_element(By.CSS_SELECTOR, 'a.bx-next')
            print(next_button.get_attribute('class'))
            if next_button.get_attribute('class') == 'bx-next':
                next_button.click()
            # end if : 프리뷰 / 리뷰
        # end for games
    # end while all days
    #하루 경기를 다 읽어 온것이다.

    # elastic search 의 index 갱신
    #es_client.indices.refresh(index='kbo')

#기존 정보가 있냐 없냐를 if문 걸어두었는데 이게 여기에 사용 되는 것이다. 기존 정보가 있으면은 긁어온 정보들 중에 중복 된 정보가 있을 수 있으니까 
#그거 중복되는 부분 제거하라 라는 부분
    if is_ex_df:
        ex_df = ex_df.drop_duplicates()
        baseball_df = pd.merge(baseball_df, ex_df, how='outer') #outer merge:겹치는 부분과 겹치지 않은 부분을 다 가져오는것
                                                                #inner merge:겹치는 것만 merge하는 것
    baseball_df.set_index('날짜', inplace=True, drop=True)
    baseball_df.sort_index(ascending=False, inplace=True)
    baseball_df = baseball_df.drop_duplicates()

    baseball_df.to_csv('2022_KBO_경기 데이터_동명이인 처리.csv', encoding='utf-8-sig')

    browser.close()

    """
    temp_dfs = pd.read_html(RegisterAll_URL)
    print(temp_dfs)
    counter = 0
    for temp_df in temp_dfs:
        temp_df.to_csv('구단 선수 목록' + str(counter) + '.csv', encoding='ms949')
        counter += 1

    browser = webdriver.Chrome()
    browser.implicitly_wait(30)
    browser.get(RegisterAll_URL)

    for i in range(0, 100):
        try:
            current_date = BeautifulSoup(browser.page_source, 'lxml').find('span', id='cphContents_cphContents_cphContents_lblGameDate').text
            print(current_date)
            temp_dfs = pd.read_html(browser.page_source)
            print(temp_dfs[0])

            python_button = browser.find_element_by_id('cphContents_cphContents_cphContents_btnPreDate')
            python_button.click()
            while True:
                if current_date != BeautifulSoup(browser.page_source, 'lxml').find('span', id='cphContents_cphContents_cphContents_lblGameDate').text :
                    break
        except ElementClickInterceptedException:
            pass
    browser.close()
    """
