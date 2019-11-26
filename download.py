### check if saving directory contans / at last or not
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

from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


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
            os.mkdir(os.path.join(self.nse_root_directory, "RawData", "NiftyData"))
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
    def __read_config_file(nse_zipped, bse_zipped, include_weekend, saving_directory):
        with open("config.json") as f:
            config = json.load(f)
            Download.last_date_updated = parse(config['last_date_updated']).date()
            Download.to_date = parse(config['to_date']).date()
            Download.base_directory = saving_directory
            # Download.Include_Weekend = config['Include_Weekend']
            Download.Include_Weekend = include_weekend
            Download.nse_zipped = nse_zipped
            Download.bse_zipped = bse_zipped
            Download.Holidays = config['Holiday']
            Download.NseDetails = config['Nse']
            Download.BseDetails = config['Bse']

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

    def download_nifty(self, date1, date2):
        exact_dates = list(date1+timedelta(days=x) for x in range(0, ((date2-date1).days+1)))
        if all(Download.is_weekend_holiday(x) for x in exact_dates):
            return
        from_date = date1

        options = Options()
        options.add_argument('-headless')
        binary = FirefoxBinary(r'C:\\Program Files\\Mozilla Firefox\\firefox.exe')
        # driver = Firefox(firefox_binary=binary, executable_path="D:\\Downloads\\geckodriver.exe")
        if os.name == 'nt':
            driver = Firefox(firefox_binary=binary, options=options, executable_path="D:\\Downloads\\geckodriver.exe")
        else:
            driver = Firefox(firefox_binary=binary, options=options, executable_path="/home/sudip/geckodriver/geckodriver")

        # driver.get('https://www.nseindia.com/products/content/equities/indices/historical_index_data.htm')
        driver.get(Download.NseDetails["IndexPath"])
        timeout = 10
        for i in range(5):
            try:
                element_present = ec.presence_of_element_located((By.ID, 'indexType'))
                WebDriverWait(driver, timeout).until(element_present)
                break
            except TimeoutException:
                print("Timed out waiting for page to load")
                if i == 4:
                    sys.exit(1)
                continue
        Select(driver.find_element_by_id("indexType")).select_by_value("NIFTY 50")
        driver.find_element_by_id("fromDate").send_keys(from_date.strftime('%d-%m-%Y'))
        driver.find_element_by_id("toDate").send_keys(date2.strftime('%d-%m-%Y'))
        driver.find_element_by_xpath("//input[@src='/common/images/btn-get-data.gif']").click()

        timeout = 10
        for i in range(5):
            try:
                element_present = ec.presence_of_element_located((By.ID, 'csvContentDiv'))
                WebDriverWait(driver, timeout).until(element_present)

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
                  "S&P CNX NIFTY" + parse(every_date.text).date().
                  strftime("%d-%m-%Y-%d-%m-%Y")+".csv"), "w") as nifty_file:
                nifty_file.write("Date        Open         High         Low        Close\n")
                nifty_file.write(parse(every_date.text).date().strftime("%d-%m-%Y") + "," + numbers[0].text + ","
                                 + numbers[1].text + "," + numbers[2].text + "," + numbers[3].text+"\n")

        driver.quit()

    def process_nse_data(self, date1):
        only_csv_file_name = "cm" + date1.strftime('%d%b%Y').upper() + "bhav.csv"
        only_mto_file_name = "MTO_" + date1.strftime('%d%m%Y') + ".DAT"
        advance_num = 0
        decline_num = 0
        csv_file_name = os.path.join(self.nse_root_directory, only_csv_file_name)
        csv_del_file_name = os.path.join(self.nse_root_directory, "ModifiedCSV", "DeliveryVolume",
                                         only_csv_file_name)
        csv_trade_file_name = os.path.join(self.nse_root_directory, "ModifiedCSV", "TradingVolume",
                                           only_csv_file_name)
        mto_file_name = os.path.join(self.nse_root_directory, only_mto_file_name)

        csv_del_file_writer = open(csv_del_file_name, "w")
        csv_trade_file_writer = open(csv_trade_file_name, "w")
        csv_del_file_writer.AutoFlush = True
        csv_trade_file_writer.AutoFlush = True

        # open mto file
        with open(mto_file_name) as mtoFileReader:
            mto_file_data = mtoFileReader.read()

        nifty_file_name = os.path.join(self.nse_root_directory, "S&P CNX NIFTY" + date1.strftime("%d-%m-%Y-%d-%m-%Y")
                                       + ".csv")
        only_nifty_file_name = "S&P CNX NIFTY" + date1.strftime("%d-%m-%Y-%d-%m-%Y") + ".csv"

        with open(nifty_file_name) as niftyFileReader:
            next(niftyFileReader)
            nifty_file_data = niftyFileReader.read().strip().split(',')

        # Read the 1st junk line in csv file
        with open(csv_file_name) as csvFileReader:
            # write the 1st line in csvFileTemp file
            csv_del_file_writer.write("<ticker>,<date>,<open>,<high>,<low>,<close>,<volume>,<o/i>\n")
            csv_trade_file_writer.write("<ticker>,<date>,<open>,<high>,<low>,<close>,<volume>,<o/i>\n")
            next(csvFileReader)
            for every_line in csvFileReader:
                # Trim last character(',')
                every_line = every_line[:-1]
                stock_csv_data = every_line.split(',')
                stock_name, stock_type, close_price, prev_price = itemgetter(0, 1, 5, 7)(every_line.split(','))
                if stock_type != 'EQ' and stock_type != 'BE':
                    continue

                if close_price > prev_price:
                    advance_num += 1
                else:
                    decline_num += 1

                stock_data_regex = re.compile(stock_name + ",EQ,\d*,\d*")
                mto_data_filtered = re.search(stock_data_regex, mto_file_data, 0)
                if not mto_data_filtered:
                    csv_del_file_writer.write(stock_name + "," + date1.strftime('%Y%m%d')
                                              + "," + stock_csv_data[2] + "," + stock_csv_data[3]
                                              + "," + stock_csv_data[4] + "," + stock_csv_data[5]
                                              + "," + str(int(stock_csv_data[8])*0.4)+",0" + "\n")
                else:
                    mto_text = mto_data_filtered.group(0).split(',')

                    csv_del_file_writer.write(
                        stock_name + "," + date1.strftime('%Y%m%d') + ","
                        + stock_csv_data[2]+"," + stock_csv_data[3] + "," + stock_csv_data[4]
                        + "," + stock_csv_data[5] + "," + mto_text[3] + ",0" + "\n")

                    csv_trade_file_writer.write(
                        stock_name + "," + date1.strftime('%Y%m%d') + ","
                        + stock_csv_data[2] + "," + stock_csv_data[3] + "," + stock_csv_data[4]
                        + "," + stock_csv_data[5] + "," + stock_csv_data[11] + ",0" + "\n")

            csv_del_file_writer.write(
                        "NIFTY" + "," + date1.strftime('%Y%m%d') + ","
                        + nifty_file_data[1] + "," + nifty_file_data[2] + "," + nifty_file_data[3]
                        + "," + nifty_file_data[4] + "," + "0,0")
            csv_trade_file_writer.write(
                "NIFTY" + "," + date1.strftime('%Y%m%d') + ","
                + nifty_file_data[1] + "," + nifty_file_data[2] + "," + nifty_file_data[3]
                + "," + nifty_file_data[4] + "," + "0,0")

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
        os.replace(mto_file_name, os.path.join(
                        self.nse_root_directory,
                        "RawData", "DelivData", only_mto_file_name))
        os.replace(nifty_file_name, os.path.join(
                        self.nse_root_directory,
                        "RawData", "NiftyData", only_nifty_file_name))


    def download_nse(self, date1):
        # csv_net_path = "http://nseindia.com/content/historical/EQUITIES/"
        csv_net_path = Download.NseDetails["CsvPath"]
        # mto_net_path = "http://nseindia.com/archives/equities/mto/"
        mto_net_path = Download.NseDetails["MtoPath"]
        csv_file_name = "cm" + date1.strftime('%d%b%Y').upper() + "bhav.csv"
        csv_net_path = csv_net_path + date1.strftime("%Y/%b/").upper()
        if Download.nse_zipped:
            csv_file_name = csv_file_name + ".zip"
        csv_net_path = csv_net_path + csv_file_name

        failure_count = 0

        for tryCount in range(3):
            try:
                response = requests.get(csv_net_path)
                local_file = os.path.join(self.nse_root_directory, csv_file_name)
                open(local_file, 'wb').write(response.content)
                if Download.nse_zipped and os.path.getsize(local_file) > 5000:
                    try:
                        z = zipfile.ZipFile(local_file)
                        z.extractall(path=self.nse_root_directory)
                        z.close()
                    except Exception as e:
                        print("Error unzipping file {}, error:{}".format(local_file, e))
                    os.remove(local_file)

            except requests.exceptions.Timeout:
                failure_count += 1
                time.sleep(0.3)
                print("sudip:failed to get the file")
                continue
        if failure_count == 3:
            print("Unable to download equity file for {}".format(date1))
            return 1

        failure_count = 0

        mto_file_name = "MTO_" + date1.strftime("%d%m%Y") + ".DAT"
        mto_net_path = mto_net_path + mto_file_name
        for tryCount in range(3):
            try:
                response = requests.get(mto_net_path)
                local_file = os.path.join(self.nse_root_directory, mto_file_name)
                open(local_file, 'wb').write(response.content)

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
        self.download_nifty(from_date, to_date)

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
                 saving_directory=""):
        Download.__read_config_file(nse_zipped, bse_zipped, include_weekend, saving_directory)
        Download.__get_holiday_list(Download.Holidays)
        self.__create_directory(Download.base_directory)

'''
d = Download()
d.download_data()
'''
