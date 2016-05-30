# -*- coding: utf-8 -*-
from variables import *

def check_words(driver, words):
    page = driver.page_source
    for word in words:
        assert word in page, word + " word not found!"

def sleep():
    time.sleep(sleep_sec)

def slee():
    time.sleep(1)

def get_token():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))

def put_input(driver, inputs):
    token_list = []
    for input_name in inputs:
        elem = driver.find_element_by_name(input_name)
        elem.clear()
        token = get_token()
        token_list.append(token)
        elem.send_keys(token)
    return token_list

def select_option(driver, elem_id, option_text):
    driver.find_element_by_id(elem_id).click()
    slee()
    options = driver.find_elements_by_xpath("//div[@id='"+elem_id+"']/div[@class='chosen-drop']/ul[@class='chosen-results']/li")
    for option in options:
        if option.text == option_text:
            option.click()

def select_data_tables_all(driver):
    driver.find_element_by_xpath("//div[@id='DataTables_Table_0_length']/label/div[@class='chosen-container chosen-container-single chosen-container-single-nosearch']").click()
    slee()
    options = driver.find_elements_by_xpath("//div[@id='DataTables_Table_0_length']/label/div/div[@class='chosen-drop']/ul[@class='chosen-results']/li")
    for option in options:
        if option.text == 'All':
            option.click()

def clean_coupons(driver):
    select_data_tables_all(driver)
    slee()
    t_rows = driver.find_elements_by_xpath("//table[@id='DataTables_Table_0']/tbody/tr[td='Test Com']")
    for t_row in t_rows:
        t_row.find_elements_by_xpath(".//td")[-1].find_element_by_xpath(".//a").click()

def clean_and_find_coupon(driver, text_error):
    select_data_tables_all(driver)
    slee()
    t_rows = driver.find_elements_by_xpath("//table[@id='DataTables_Table_0']/tbody/tr[td='Test Com']")
    assert len(t_rows), text_error
    for t_row in t_rows:
        t_row.find_elements_by_xpath(".//td")[-1].find_element_by_xpath(".//a").click()

def end_saving_coupon(driver):
    driver.find_element_by_id("genCouponCode").click()
    driver.find_element_by_id("usageAmount").send_keys("1")
    driver.find_element_by_id("submitCoupon").click()
    sleep()
    driver.find_element_by_xpath("//div[@id='dialog_modal']/div[@class='actions']/div[@class='center']/button").click()
    sleep()