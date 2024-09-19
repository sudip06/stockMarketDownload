from datetime import *
from dateutil.parser import parse
import json
import os
import requests
import zipfile
import time
import sys
from operator import itemgetter
import re

from selenium import webdriver
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from copy import deepcopy
import sqlalchemy
from models import Base, StockData, AdvDec
from sqlalchemy.orm import sessionmaker
import yfinance as yf

MTO_NOT_NEEDED = True

class Download:
    last_date_updated = 0
    to_date = 0
    base_directory = ""
    Include_Weekend = 0
    Holidays = []
    NseDetails = {}
    BseDetails = {}
    DownloadFolder = {}
    nse_zipped = True
    bse_zipped = True
    headless = True
    adv_dec_file_writer = ""


    def __create_directory(self, base_directory):
        self.nse_root_directory = os.path.join(base_directory, "Nse")
        self.bse_root_directory = os.path.join(base_directory, "Bse")
        if not os.path.exists(base_directory):
            os.mkdir(base_directory)
        if not os.path.exists(self.nse_root_directory):
            os.mkdir(self.nse_root_directory)
        if not os.path.exists(self.bse_root_directory):
            os.mkdir(self.bse_root_directory)

        adv_dec_file_name = os.path.join(self.nse_root_directory, "advDec.txt")
        if not os.path.exists(adv_dec_file_name):
            first_line = "Date	Nifty-Open	Nifty-High	Nifty-Low	Nifty-Close	Advance	Decline\n"
            adv_dec_file_writer = open(adv_dec_file_name, "w")
            adv_dec_file_writer.write(first_line)
            adv_dec_file_writer.close()

        if not os.path.isdir(os.path.join(self.nse_root_directory, "ModifiedCSV")):
            os.mkdir(os.path.join(self.nse_root_directory, "ModifiedCSV"))
            os.mkdir(os.path.join(self.nse_root_directory, "ModifiedCSV", "DeliveryVolume"))
            os.mkdir(os.path.join(self.nse_root_directory, "ModifiedCSV", "TradingVolume"))
        if not os.path.isdir(os.path.join(self.bse_root_directory, "ModifiedCSV")):
            os.mkdir(os.path.join(self.bse_root_directory, "ModifiedCSV"))
            os.mkdir(os.path.join(self.bse_root_directory, "ModifiedCSV", "DeliveryVolume"))
            os.mkdir(os.path.join(self.bse_root_directory, "ModifiedCSV", "TradingVolume"))
        if not os.path.isdir(os.path.join(self.nse_root_directory, "RawData")):
            os.mkdir(os.path.join(self.nse_root_directory, "RawData"))
            os.mkdir(os.path.join(self.nse_root_directory, "RawData", "DelivData"))
            os.mkdir(os.path.join(self.nse_root_directory, "RawData", "EquityData"))
            os.mkdir(os.path.join(self.nse_root_directory, "RawData", "IndexData"))
        if not os.path.isdir(os.path.join(self.bse_root_directory, "RawData")):
            os.mkdir(os.path.join(self.bse_root_directory, "RawData"))
            os.mkdir(os.path.join(self.bse_root_directory, "RawData", "DelivData"))
            os.mkdir(os.path.join(self.bse_root_directory, "RawData", "EquityData"))
            os.mkdir(os.path.join(self.bse_root_directory, "RawData", "SensexData"))

    @staticmethod
    def __get_holiday_list(holiday_str):
        for i, j in holiday_str.items():
            holiday_list = j.split(',')
            holiday_list_mod = list([parse(x).date() for x in holiday_list])
            holiday_str[i] = holiday_list_mod

    @staticmethod
    def __read_config_file(nse_zipped, bse_zipped, include_weekend,
                           saving_directory, headless, dont_download_indices,
                           only_today, dont_download_bhavcopy, indices_source):
        with open("config.json") as f:
            config = json.load(f)
            Download.last_date_updated = parse(config['last_date_updated']).date()
            Download.to_date = parse(config['to_date']).date()
            Download.base_directory = saving_directory
            # Download.Include_Weekend = config['Include_Weekend']
            Download.Include_Weekend = include_weekend
            Download.nse_zipped = nse_zipped
            Download.bse_zipped = bse_zipped
            Download.headless = headless
            Download.dont_download_indices = dont_download_indices
            Download.only_today = only_today
            Download.dont_download_bhavcopy = dont_download_bhavcopy
            Download.Holidays = config['Holiday']
            Download.NseDetails = config['Nse']
            Download.BseDetails = config['Bse']
            Download.indices_source = indices_source

    @staticmethod
    def is_weekend_holiday(date1):
        if date1 in Download.Holidays[str(date1.year)]:
            return True
        if date1.weekday() >= 5:
            if Download.Include_Weekend == 0:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def start_chrome(headless):
        options = Options()
        if headless:
            options.add_argument('--headless')

        # Common settings for all platforms
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors=true")
        options.add_argument("--no-sandbox")

        # Windows-specific settings
        if os.name == 'nt':
            options.add_argument("--user-data-dir=C:\\chrome-dev-disabled-security-for-cors-stock-market-software")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-site-isolation-trials")
            driver = webdriver.Chrome(options=options, executable_path='chromedriver.exe')
        else:
            # Non-Windows (e.g., Linux) specific settings
            options.add_argument("--disable-blink-features")
            options.add_argument("--disable-blink-features=AutomationControlled")
            driver = webdriver.Chrome(options=options, executable_path='/home/sudip/geckodriver/chromedriver')

        driver.set_page_load_timeout(20)
        return driver

    def download_index(self, date1, date2):
        exact_dates = list(date1+timedelta(days=x) for x in range(0, ((date2-date1).days+1)))
        if all(Download.is_weekend_holiday(x) for x in exact_dates):
            return
        from_date = date1
        if Download.indices_source in ("Nse", "Moneycontrol"):
            # broekn currently
            driver = Download.start_chrome(Download.headless)
            driver.set_page_load_timeout(60000)
        #driver.manage().timeouts().pageLoadTimeout(40, TimeUnit.SECONDS);
        if Download.indices_source in ("Nse", "Nsepython", "YahooFinance"):
            indexes = [x.strip() for x in Download.NseDetails["IndexList"].split(",")]
        else: #for Moneycontrol
            index = [x.strip() for x in Download.NseDetails["MoneyControlIndex"].split(",")]
            indexes = list(map(lambda x: x.split(":")[2], index))
            index_names = list(map(lambda x: x.split(":")[0], index))

        if Download.indices_source == "Nse":
            driver.get(Download.NseDetails["IndexPath"])
            timeout = 60
            for i in range(5):
                try:
                    element_present = ec.presence_of_element_located((By.ID, 'indexType'))
                    WebDriverWait(driver, timeout).until(element_present)
                    time.sleep(5)
                    driver.find_element_by_id("fromDate").send_keys(from_date.strftime('%d-%m-%Y'))
                    time.sleep(2)
                    driver.find_element_by_id("toDate").send_keys(date2.strftime('%d-%m-%Y'))
                    break
                except TimeoutException:
                    print("Timed out waiting for page to load")
                    if i == 4:
                        sys.exit(1)
                    continue
            # driver.get('https://www.nseindia.com/products/content/equities/indices/historical_index_data.htm')
            for individualElements in indexes:
                try:
                    Select(driver.find_element_by_id("indexType")).select_by_value(individualElements)
                    time.sleep(5)
                    driver.find_element_by_xpath("//input[@src='/common/images/btn-get-data.gif']").click()
                    timeout = 20
                    for i in range(5):
                        try:
                            element_present = ec.presence_of_element_located((By.ID, 'csvContentDiv'))
                            WebDriverWait(driver, timeout).until(element_present)
                            break

                        except TimeoutException:
                            print("Timed out waiting for page to load")
                            if i == 4:
                                sys.exit(1)
                            continue

                    all_dates = driver.find_elements_by_xpath('//td[@class="date"]')
                    for every_date in all_dates:
                        numbers = every_date.find_elements_by_xpath('.//following-sibling::td[@class="number"]')
                        # form the nifty file as S&P CNX NIFTY01-11-2019-01-11-2019
                        with open(os.path.join(
                              self.nse_root_directory,
                              individualElements.replace(" ", "_") + "-" + parse(every_date.text).date().
                              strftime("%d-%m-%Y-%d-%m-%Y")+".csv"), "w") as index_file:
                            index_file.write("Date        Open         High         Low        Close\n")
                            index_file.write(parse(every_date.text).date().
                                             strftime("%d-%m-%Y") + "," +
                                             numbers[0].text + "," + numbers[1].text +
                                             "," + numbers[2].text + "," +
                                             numbers[3].text+"\n")

                    time.sleep(5)

                except TimeoutException:
                    driver.quit()
                    driver = Download.start_chrome()
                    continue
            driver.quit()
        elif Download.indices_source == "Moneycontrol":
            for idx, individualElements in enumerate(indexes):
                driver.get(Download.NseDetails["MoneycontrolIndexPath"])
                timeout = 120
                for i in range(5):
                    try:
                        element_present = ec.presence_of_element_located((By.ID, 'hdn_historic_data'))
                        WebDriverWait(driver, timeout).until(element_present)
                        break
                    except TimeoutException:
                        print("Timed out waiting for page to load")
                        if i == 4:
                            sys.exit(1)
                        continue
                driver.find_element_by_id('wutabs2').click()
                if date1 == date2:
                    date2 = date2 + timedelta(days=1)

                Select(driver.find_element_by_id("indian_indices")).select_by_value(individualElements)
                Select(driver.find_element_by_xpath(
                    "//form[@name='frm_dly']/div[@class='PT4']/select[@name='frm_dy']")).\
                    select_by_value(str('{:02d}'.format(date1.day)))
                Select(driver.find_element_by_xpath(
                    "//form[@name='frm_dly']/div[@class='PT4']/select[@name='frm_mth']")).\
                    select_by_value(str('{:02d}'.format(date1.month)))
                Select(driver.find_element_by_xpath(
                    "//form[@name='frm_dly']/div[@class='PT4']/select[@name='frm_yr']")). \
                    select_by_value(str(date1.year))

                Select(driver.find_element_by_xpath(
                    "//form[@name='frm_dly']/div[@class='PT4']/select[@name='to_dy']")). \
                    select_by_value(str('{:02d}'.format(date2.day)))
                Select(driver.find_element_by_xpath(
                    "//form[@name='frm_dly']/div[@class='PT4']/select[@name='to_mth']")). \
                    select_by_value(str('{:02d}'.format(date2.month)))
                Select(driver.find_element_by_xpath(
                    "//form[@name='frm_dly']/div[@class='PT4']/select[@name='to_yr']")). \
                    select_by_value(str(date2.year))
                # driver.find_element_by_xpath("//input[@src='http://img1.moneycontrol.com/images/histstock/go_btn.gif']").click()
                driver.find_element_by_xpath("//input[@src='https://images.moneycontrol.com/images/histstock/go_btn.gif']").click()

                WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//table[@class='tblchart']")))

                table = driver.find_element_by_xpath("//table[@class='tblchart']")
                for row in table.find_elements_by_xpath(".//tr"):
                    value = [td.text for td in row.find_elements_by_xpath(".//td")]
                    if len(value):
                        every_date =datetime.strptime(value[0], "%Y-%m-%d")

                        with open(os.path.join(
                            self.nse_root_directory,
                            index_names[idx].replace(" ", "_") + "-" + every_date.
                                    strftime("%d-%m-%Y-%d-%m-%Y") + ".csv"), "w") as index_file:
                            index_file.write("Date        Open         High         Low        Close\n")
                            index_file.write(every_date.strftime("%d-%m-%Y") + "," +
                                             value[1] + "," + value[2] +
                                             "," + value[3] + "," +
                                             value[4] + "\n")
                time.sleep(5)
            driver.quit()
        elif Download.indices_source == "Nsepython": #Nsepython
            from_date = date1.strftime('%d-%b-%Y')
            to_date = date2.strftime('%d-%b-%Y')

            from nsepython import index_history
            for idx, individualElements in enumerate(indexes):
                x = index_history(individualElements, from_date, to_date)
                for i in range(len(x)):
                    every_date = datetime.strptime(x['HistoricalDate'][i].replace(" ", "-"), "%d-%b-%Y")
                    with open(os.path.join(
                                self.nse_root_directory,
                                individualElements.replace(" ", "_") + "-" + every_date.
                                        strftime("%d-%m-%Y-%d-%m-%Y") + ".csv"), "w") as index_file:
                            index_file.write("Date        Open         High         Low        Close\n")
                            index_file.write(every_date.strftime("%d-%m-%Y") + "," +
                                             x['OPEN'][i] + "," + x['HIGH'][i] +
                                             "," + x['LOW'][i] + "," +
                                             x['CLOSE'][i] + "\n")
                time.sleep(2)
        elif Download.indices_source == "YahooFinance": #YahooFinance
            index_tickers = {
                'NIFTY 50': '^NSEI',
                'NIFTY AUTO': '^CNXAUTO',
                'NIFTY BANK': '^NSEBANK',
                'NIFTY FIN SERVICE': '^CNXFIN',
                'NIFTY FMCG': '^CNXFMCG',
                'NIFTY IT': '^CNXIT',
                'NIFTY MEDIA': '^CNXMEDIA',
                'NIFTY METAL': '^CNXMETAL',
                'NIFTY PHARMA': '^CNXPHARMA',
                'NIFTY PVT BANK': '^CNXPVTBANK',
                'NIFTY PSU BANK': '^CNXPSUBANK',
                'NIFTY REALTY': '^CNXREALTY'
            }
            #from_date = date1.strftime('%d-%b-%Y')
            #to_date = date2.strftime('%d-%b-%Y')

            from_date = date1
            to_date = date2

            # Fetch and write data
            for index_name in indexes:
                ticker = index_tickers.get(index_name)
                if not ticker:
                    print(f"Ticker not found for index: {index_name}")
                    continue

                # Fetch data from Yahoo Finance
                data = yf.download(ticker, start=from_date, end=to_date + timedelta(days=1))  # end is exclusive

                # Write data to CSV
                for date, row in data.iterrows():
                    file_name = f"{index_name.replace(' ', '_')}-{date.strftime('%d-%m-%Y')}-{date.strftime('%d-%m-%Y')}.csv"
                    file_path = os.path.join(self.nse_root_directory, file_name)
                    with open(file_path, "w") as index_file:
                        index_file.write("Date,Open,High,Low,Close\n")
                        index_file.write(f"{date.strftime('%d-%m-%Y')},{row['Open']},{row['High']},{row['Low']},{row['Close']}\n")
                time.sleep(2)
        

    def process_nse_data(self, date1):
        only_csv_file_name = "cm" + date1.strftime('%d%b%Y').upper() + "bhav.csv"
        if not MTO_NOT_NEEDED:
            only_mto_file_name = "MTO_" + date1.strftime('%d%m%Y') + ".DAT"
        advance_num = 0
        decline_num = 0
        stock_obj_list = []
        stock_index_obj_list = []
        csv_file_name = os.path.join(self.nse_root_directory, "sec_bhavdata_full_" + date1.strftime('%d%m%Y') + ".csv")
        csv_del_file_name = os.path.join(self.nse_root_directory, "ModifiedCSV", "DeliveryVolume",
                                         only_csv_file_name)
        csv_trade_file_name = os.path.join(self.nse_root_directory, "ModifiedCSV", "TradingVolume",
                                           only_csv_file_name)
        if not MTO_NOT_NEEDED:
            mto_file_name = os.path.join(self.nse_root_directory, only_mto_file_name)

        csv_del_file_writer = open(csv_del_file_name, "w")
        csv_trade_file_writer = open(csv_trade_file_name, "w")
        csv_del_file_writer.AutoFlush = True
        csv_trade_file_writer.AutoFlush = True

        session = sessionmaker(bind=self.engine)
        sess = session()
        if sess.query(StockData).filter(StockData.date==date1).count()==0:
            data_to_be_inserted_to_db = True
        else:
            data_to_be_inserted_to_db = False 
        
        if not MTO_NOT_NEEDED:
            # open mto file
            with open(mto_file_name) as mtoFileReader:
                mto_file_data = mtoFileReader.read()

        if Download.indices_source=="Nse":
            indexes = [x.strip() for x in Download.NseDetails["IndexList"].split(",")]
        else:
            index = [x.strip() for x in Download.NseDetails["MoneyControlIndex"].split(",")]
            indexes = list(map(lambda x: x.split(":")[0], index))
        # driver.get('https://www.nseindia.com/products/content/equities/indices/historical_index_data.htm')

        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX111 filename:{}".format(csv_file_name))
        # Read the 1st junk line in csv file
        with open(csv_file_name) as csvFileReader:
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX filename:{}".format(csv_file_name))
            # write the 1st line in csvFileTemp file
            csv_del_file_writer.write("<ticker>,<date>,<open>,<high>,<low>,<close>,<volume>,<o/i>\n")
            csv_trade_file_writer.write("<ticker>,<date>,<open>,<high>,<low>,<close>,<volume>,<o/i>\n")
            next(csvFileReader)
            for every_line in csvFileReader:
                # Trim last character(',')
                # every_line = every_line[:-1]
                stock_csv_data = [element.strip() for element in every_line.split(',')]
                stock_name, stock_type, close_price, prev_price = itemgetter(0, 1, 8, 3)(every_line.split(','))
                print("XXXXXXXXXXXXXXXXXX stock_name:{} stock_type:{}, close_price:{}, prev_price:{}".format(stock_name, stock_type, close_price, prev_price ))
                if stock_type not in ('EQ','BE'):
                    continue

                if close_price > prev_price:
                    advance_num += 1
                else:
                    decline_num += 1

                if not MTO_NOT_NEEDED:
                    stock_data_regex = re.compile(rf"{stock_name},EQ,\d*,\d*")
                    mto_data_filtered = re.search(stock_data_regex, mto_file_data, 0)
                    if not mto_data_filtered:
                        del_volume = str(int(int(stock_csv_data[8])*0.4))
                    else:
                        mto_text = mto_data_filtered.group(0).split(',')
                        del_volume = str(mto_text[3])
                csv_del_file_writer.write(stock_name + "," + date1.strftime('%Y%m%d')
                                            + "," + stock_csv_data[4] + "," + stock_csv_data[5]
                                            + "," + stock_csv_data[6] + "," + stock_csv_data[8]
                                            + "," + stock_csv_data[13] +",0" + "\n")
                csv_trade_file_writer.write(
                        stock_name + "," + date1.strftime('%Y%m%d') + ","
                        + stock_csv_data[4] + "," + stock_csv_data[5] + "," + stock_csv_data[6]
                        + "," + stock_csv_data[8] + "," + stock_csv_data[10] + ",0" + "\n")

                if data_to_be_inserted_to_db:
                    stock_obj = StockData(stock_name=stock_name, date=date1,
                                          open=stock_csv_data[4], high=stock_csv_data[5],
                                          low=stock_csv_data[6], close=stock_csv_data[8],
                                          del_volume=stock_csv_data[13], trade_volume=stock_csv_data[10])
                    stock_obj_list.append(stock_obj)
                    # sess.add(stock_obj)

            for individualElements in indexes:
                index_file_name = os.path.join(self.nse_root_directory,
                                               individualElements.replace(" ", "_") + "-" +
                                               date1.strftime("%d-%m-%Y-%d-%m-%Y")
                                               + ".csv")
                only_index_file_name = individualElements.replace(" ", "_") + "-" + \
                                        date1.strftime("%d-%m-%Y-%d-%m-%Y") + \
                                        ".csv"

                if not os.path.exists(index_file_name):
                    continue

                with open(index_file_name) as indexFileReader:
                    next(indexFileReader)
                    index_file_data = indexFileReader.read().strip().split(',')
                if data_to_be_inserted_to_db:
                    stock_index_obj = StockData(stock_name=individualElements.replace(" ", "_"),
                                          date=date1, open=index_file_data[1],
                                          high=index_file_data[2], low=index_file_data[3],
                                          close=index_file_data[4], del_volume=0,
                                          trade_volume=0)
                    #sess.add(stock_obj)
                    stock_obj_list.append(stock_index_obj)

                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX index_file_data:{}".format(index_file_data))
                if "NIFTY_50" in only_index_file_name:
                    nifty_file_data = deepcopy(index_file_data)

                csv_del_file_writer.write(
                    individualElements.replace(" ", "_") + "," + date1.strftime('%Y%m%d') + ","
                    + index_file_data[1] + "," + index_file_data[2] + "," + index_file_data[3]
                    + "," + index_file_data[4] + "," + "0,0" + "\n")

                csv_trade_file_writer.write(
                    individualElements.replace(" ", "_") + "," + date1.strftime('%Y%m%d') + ","
                    + index_file_data[1] + "," + index_file_data[2] + "," + index_file_data[3]
                    + "," + index_file_data[4] + "," + "0,0" + "\n")

        # before the stockdata was added below, moving down because its giving no key present in adv_dec table,
        # might be because we are adding it below. hence moving it below the adv_dec add code.
        # sess.bulk_save_objects(stock_obj_list)
        # find if the entry already exist
        data_in_adv_dec=sess.query(AdvDec).filter(AdvDec.date==date1).count()
        if data_in_adv_dec==0:
        #if sess.query(AdvDec).filter(AdvDec.date==date1).count()==0:
            adv_dec_obj = AdvDec(date=date1, advance=advance_num, decline=decline_num)
            sess.add(adv_dec_obj)
            sess.commit()

        sess.bulk_save_objects(stock_obj_list)
        sess.commit()
        sess.close()

        Download.adv_dec_file_writer.write(
            date1.strftime('%d/%m/%Y') + "\t"
            + nifty_file_data[1] + "\t" + nifty_file_data[2] + "\t"
            + nifty_file_data[3] + "\t" + nifty_file_data[4] + "\t"
            + str(advance_num) + "\t" + str(decline_num) + "\n")

        csv_del_file_writer.close()
        csv_trade_file_writer.close()
        time.sleep(1)
        os.replace(csv_file_name, os.path.join(
                        self.nse_root_directory,
                        "RawData", "EquityData", only_csv_file_name))
        if not MTO_NOT_NEEDED:
            os.replace(mto_file_name, os.path.join(
                            self.nse_root_directory,
                            "RawData", "DelivData", only_mto_file_name))
        for individualElements in indexes:
            index_file_name = os.path.join(self.nse_root_directory,
                                           individualElements.replace(" ", "_") + "-" +
                                           date1.strftime("%d-%m-%Y-%d-%m-%Y")
                                           + ".csv")

            only_index_file_name = individualElements.replace(" ", "_") + "-" + \
                                   date1.strftime("%d-%m-%Y-%d-%m-%Y") + \
                                   ".csv"
            if not os.path.exists(index_file_name):
                    continue
            try:
                os.replace(index_file_name, os.path.join(
                           self.nse_root_directory,
                           "RawData", "IndexData", only_index_file_name))
            except Exception as e:
                print(f'''Probably couldn't find {only_index_file_name}:{e}''')

    def download_nse(self, date1):
        # csv_net_path = "http://nseindia.com/content/historical/EQUITIES/"
        csv_net_path = Download.NseDetails["CsvPath"]
        if not MTO_NOT_NEEDED:
            # mto_net_path = "http://nseindia.com/archives/equities/mto/"
            mto_net_path = Download.NseDetails["MtoPath"]
        #csv_file_name = "cm" + date1.strftime('%d%b%Y').upper() + "bhav.csv"
        csv_file_name = "sec_bhavdata_full_" + date1.strftime('%d%m%Y') + ".csv"
        #csv_net_path = csv_net_path + csv_file_name
        if Download.nse_zipped:
            csv_file_name = csv_file_name + ".zip"
        csv_net_path = csv_net_path + csv_file_name

        failure_count = 0

        for tryCount in range(3):
            fail_to_unzip=0
            try:
                local_file = os.path.join(self.nse_root_directory, csv_file_name)
                if not Download.dont_download_bhavcopy:
                    response = requests.get(csv_net_path)
                    open(local_file, 'wb').write(response.content)
                elif Download.nse_zipped and (os.path.getsize(local_file) > 5000):
                    try:
                        z = zipfile.ZipFile(local_file)
                        z.extractall(path=self.nse_root_directory)
                        z.close()
                        os.remove(local_file)
                        break
                    except Exception as e:
                        fail_to_unzip = 1
                        print("Error unzipping file {}, error:{}".format(local_file, e))
                    os.remove(local_file)
            except requests.exceptions.Timeout:
                failure_count += 1
                time.sleep(0.3)
                continue
            if failure_count == 3 or fail_to_unzip == 1:
                print("Unable to download equity or unzip file for {}".format(date1))
                return 1

        failure_count = 0
        if not MTO_NOT_NEEDED:
            mto_file_name = "MTO_" + date1.strftime("%d%m%Y") + ".DAT"
            mto_net_path = mto_net_path + mto_file_name
            for tryCount in range(3):
                try:
                    response = requests.get(mto_net_path)
                    local_file = os.path.join(self.nse_root_directory, mto_file_name)
                    open(local_file, 'wb').write(response.content)
                    break
                except requests.exceptions.Timeout:
                    failure_count += 1
                    time.sleep(0.3)
                    continue
            if failure_count == 3:
                print("Unable to download deliverables file for {}".format(date1))
                return 1

        return 0

    @staticmethod
    def download_bse(date1):
        pass

    def download_data(self, from_date, to_date):
        adv_dec_file_name = os.path.join(self.nse_root_directory, "advDec.txt")
        Download.adv_dec_file_writer = open(adv_dec_file_name, "a")
        Download.adv_dec_file_writer.AutoFlush = True

        # from_date = datetime.strptime(parse(from_date), "%d-%b-%Y")
        # to_date = datetime.strptime(parse(to_date), "%d-%b-%Y")
        if not Download.dont_download_indices:
            self.download_index(from_date, to_date)

        for every_date in range(0, (to_date - from_date).days+1):
            exact_date = (from_date + timedelta(days=every_date))
            if exact_date > datetime.now().date():
                print("Date selected cannot be greator than today")
                sys.exit(1)
            if exact_date in Download.Holidays[str(exact_date.year)]:
                continue
            # if Download.Include_Weekend == 0:
            if exact_date.weekday() >= 5 and Download.Include_Weekend == 0:
                continue
            else:
                ret_nse_download = self.download_nse(exact_date)
                Download.download_bse(exact_date)

                if ret_nse_download == 0:
                    self.process_nse_data(exact_date)

        Download.adv_dec_file_writer.close()

    def __init__(self, nse_zipped=True, bse_zipped=True, include_weekend=False,
                 saving_directory="", headless=False, dont_download_indices=True,
                 only_today=False, dont_download_bhavcopy=False, indices_source="Nse", docker_host="127.0.0.1"):
        Download.__read_config_file(nse_zipped, bse_zipped, include_weekend,
                                    saving_directory, headless, dont_download_indices,
                                    only_today, dont_download_bhavcopy, indices_source)
        Download.__get_holiday_list(Download.Holidays)
        self.__create_directory(Download.base_directory)
        #self.engine = sqlalchemy.create_engine('postgresql://postgres:docker@localhost:5432/stock_data', echo=False)
        self.engine = sqlalchemy.create_engine('postgresql://postgres:docker@127.0.0.1:5432/stock_data', echo=False)
        Base.metadata.create_all(self.engine)

'''
d = Download()
d.download_data()
'''
