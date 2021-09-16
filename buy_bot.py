import sys
import logging
import traceback
import time
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from module import upbit
from decimal import Decimal

# -----------------------------------------------------------------------------
# - Name : start_selltrade
# - Desc : 매도 로직
# - Input
# 1) target_item : 대상 종목
# 2) mfi_sell_value : 매도 기준 MFI 값
# 3) mfi_buy_value : 매수 기준 MFI 값
# 4) buy_amt : 매수 금액
# -----------------------------------------------------------------------------
def start_selltrade(target_item, mfi_sell_value, mfi_buy_value, buy_amt):
    try:

        # 매도 될때까지 반복
        while True:
            logging.info('매도 로직 가동중...')
            # 해당 종목의 MFI 지표 산출
            # 1. 10분봉 기준 MFI 지표 산출
            mfi_data = upbit.get_indicators(target_item, '10', 200, 5)

            # MFI 값이 기준값을 초과하면 매도
            if Decimal(mfi_data[1][0]['MFI']) > Decimal(mfi_sell_value):
                # 기준 충족 종목 MFI 데이터
                logging.info(mfi_data)

                # 시장가 매도
                logging.info('시장가 매도 시작!')
                upbit.sellcoin_mp(target_item, 'Y')

                # 매도 시간 처리 고려
                time.sleep(3)

                # 다시 매수 로직 시작
                start_buytrade(mfi_buy_value, mfi_sell_value, buy_amt)

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise


# -----------------------------------------------------------------------------
# - Name : start_buytrade
# - Desc : 매수 로직
# - Input
# 1) mfi_buy_value : 매수 기준 mfi 값
# 2) mfi_sell_value : 매도 기준 mfi 값
# 3) buy_amt : 매수금액
# -----------------------------------------------------------------------------
def start_buytrade(mfi_buy_value, mfi_sell_value, buy_amt):
    try:

        data_cnt = 0

        # 매수 될 때까지 반복 수행
        while True:

            # 전체 종목 추출
            # 1. KRW마켓
            # 2. upbit.get_items('살,거','제,외')
            item_list = upbit.get_items('KRW-BCHA,KRW-HBAR,KRW-ARK,KRW-IOST', '')

            # 전체 종목 반복
            for item_list_for in item_list:

                # 해당 종목의 MFI 지표 산출
                # 1. 10분봉 기준 MFI 지표 산출
                mfi_data = upbit.get_indicators(item_list_for['market'], '10', 200, 5)

                # MFI 값이 기준값 미만으로 떨어지면 매수, mfi_data[0][0]['RSI'], mfi_data[2][0]['MACD'], mfi+data 3 : BB
                if Decimal(mfi_data[1][0]['MFI']) < Decimal(mfi_buy_value):
                    # 기준 충족 종목 로깅
                    logging.info(item_list_for)

                    # 기준 충족 종목 MFI 데이터
                    logging.info(mfi_data)

                    # 시장가 매수
                    logging.info('시장가 매수 시작!')
                    upbit.buycoin_mp(item_list_for['market'], buy_amt)

                    # 매수 시간 처리 고려
                    time.sleep(3)

                    # 매도 로직 호출
                    start_selltrade(item_list_for['market'], mfi_sell_value, mfi_buy_value, buy_amt)

                if data_cnt == 0 or data_cnt % 100 == 0:
                    logging.info("매수 로직 가동중...[" + str(data_cnt) + "]")

                # 조회건수증가
                data_cnt = data_cnt + 1

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception:
        raise


# -----------------------------------------------------------------------------
# - Name : main
# - Desc : 메인
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    # noinspection PyBroadException
    try:

        print("***** USAGE ******")
        print("[1] 로그레벨(D:DEBUG, E:ERROR, 그외:INFO)")

        # 로그레벨(D:DEBUG, E:ERROR, 그외:INFO)
        upbit.set_loglevel('I')

        # ---------------------------------------------------------------------
        # Logic Start!
        # ---------------------------------------------------------------------
        mfi_buy_value = input("매수 기준 RSI 값(ex. 30):")
        mfi_sell_value = input("매도 기준 RSI 값(ex. 70):")
        krw_balance = upbit.get_krwbal()
        buy_amt = krw_balance['available_krw']

        logging.info("매수 기준 MFI 20:" + str(mfi_buy_value))
        logging.info("매도 기준 MFI 80:" + str(mfi_sell_value))
        logging.info("매수금액:" + str(buy_amt))

        # 매수로직 시작
        start_buytrade(mfi_buy_value, mfi_sell_value, buy_amt)

    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt Exception 발생!")
        logging.error(traceback.format_exc())
        sys.exit(-100)

    except Exception:
        logging.error("Exception 발생!")
        logging.error(traceback.format_exc())
        sys.exit(-200)
