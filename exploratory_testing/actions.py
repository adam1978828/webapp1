# -*- coding: utf-8 -*-
from verification import *

def do_login(driver):
    driver.find_element_by_name("login_name").send_keys("meteor_@list.ru")
    driver.find_element_by_name("login_pw").send_keys("Selezniov2015Kit")
    driver.find_element_by_name("login_btn").click()
    return driver

def do_logout(driver):
    driver.get(site + "auth/logout/")
    return driver

def login(driver):
    driver.get(site)
    is_login(driver)
    driver = do_login(driver)
    sleep()
    is_profile(driver)
    return driver

def logout(driver):
    is_logout(driver)
    driver = do_logout(driver)
    sleep()
    is_login(driver)
    return driver

def profile_add(driver):
    driver.get(site + urls["profile_add"])
    is_profile_add(driver)
    return driver

def company_add(driver):
    driver.get(site + urls["company_add"])
    is_company_add(driver)
    return driver

def company_list(driver):
    driver.get(site + urls["company_list"])
    is_company_list(driver)
    return driver

def company_staff(driver):
    driver.get(site + urls["company_staff"])
    is_company_staff(driver)
    return driver

def company_staff_focus(driver):
    driver.get(site + urls["company_staff_focus"])
    is_company_staff_focus(driver)
    return driver

def payments(driver):
    driver.get(site + urls["payments"])
    is_payments(driver)
    return driver

def company_group_list(driver):
    driver.get(site + urls["company_group_list"])
    is_company_group_list(driver)
    return driver

def company_settings_list(driver):
    driver.get(site + urls["company_settings_list"])
    is_company_settings_list(driver)
    driver.get(site + "company/21/company_settings/")
    is_company_settings(driver)
    return driver

def company_trailers(driver):
    driver.get(site + urls["company_trailers"])
    is_company_trailers(driver)
    return driver

def company_social(driver):
    driver.get(site + urls["company_social"])
    is_company_social(driver)
    return driver

def priceplans(driver):
    driver.get(site + urls["priceplans"])
    is_priceplans(driver)
    return driver

def kiosks_list(driver):
    driver.get(site + urls["kiosks_list"])
    is_kiosks_list(driver)
    return driver

def rentalfleet(driver):
    driver.get(site + urls["rentalfleet"])
    is_rentalfleet(driver)
    return driver

def rentalfleet_disks(driver):
    driver.get(site + urls["rentalfleet_disks"])
    is_rentalfleet_disks(driver)
    return driver

def rentalfleet_disks_add(driver):
    driver.get(site + urls["rentalfleet_disks_add"])
    is_rentalfleet_disks_add(driver)
    return driver

def rentalfleet_disks_out(driver):
    driver.get(site + urls["rentalfleet_disks_out"])
    is_rentalfleet_disks_out(driver)
    return driver

def movies_add(driver):
    driver.get(site + urls["movies_add"])
    is_movies_add(driver)
    return driver

def movies_add_upc(driver):
    driver.get(site + urls["movies_add_upc"])
    is_movies_add_upc(driver)
    return driver

def movies_all(driver):
    driver.get(site + urls["movies_all"])
    is_movies_all(driver)
    return driver

def movies_featured(driver):
    driver.get(site + urls["movies_featured"])
    is_movies_featured(driver)
    return driver

def deals(driver):
    driver.get(site + urls["deals"])
    sleep()
    is_deals(driver)
    return driver

def coupons_all(driver):
    driver.get(site + urls["coupons_all"])
    is_coupons_all(driver)
    return driver

def reports_patterns(driver):
    driver.get(site + urls["reports_patterns"])
    is_reports_patterns(driver)
    return driver

def reports_reports(driver):
    driver.get(site + urls["reports_reports"])
    is_reports_reports(driver)
    return driver

def reports_data_sources(driver):
    driver.get(site + urls["reports_data_sources"])
    is_reports_data_sources(driver)
    return driver

def profile_edit(driver):
    driver.get(site + urls["profile_edit"])
    is_profile_edit(driver)
    token_list = put_input(driver, ["i_first_name", "i_last_name", "line_2", "i_city", "i_state", "i_country"])
    driver.find_element_by_id("profileChange").click()
    sleep()
    is_profile(driver)
    is_tokens(driver, token_list)

def company_edit(driver):
    driver.get(site + urls["company_edit_21"])
    is_company_edit(driver)
    token_list = put_input(driver, ["line_2", "i_city", "i_state", "i_country"])
    driver.find_element_by_xpath("//input[@type='submit']").click()
    sleep()
    driver.get(site + urls["company_edit_21"])
    is_company_edit(driver)
    is_tokens(driver, token_list)

def profile_edit_my(driver):
    driver.get(site + urls["profile_edit_my"])
    is_profile_edit(driver)
    token_list = put_input(driver, ["i_first_name", "i_last_name", "line_2", "i_city", "i_state", "i_country"])
    driver.find_element_by_id("profileChange").click()
    sleep()
    driver.get(site + urls["profile_edit_my"])
    is_profile_edit(driver)
    is_tokens(driver, token_list)

def kiosk_edit(driver):
    driver.get(site + urls["kiosks_edit_56"])
    is_kiosk_edit(driver)
    token_list = put_input(driver, ["line2", "city", "state", "country"])
    driver.find_element_by_xpath("//input[@type='submit']").click()
    sleep()
    driver.get(site + urls["kiosks_edit_56"])
    sleep()
    is_kiosk_edit(driver)
    is_tokens(driver, token_list)

def add_coupon_first_night_free(driver):
    select_option(driver, 'f_company_id_chosen', 'Test Com')
    select_option(driver, 'couponTypeId_chosen', 'First Night Free')
    end_saving_coupon(driver)
    clean_and_find_coupon(driver, "First Night Free not found in table")


def add_coupon_rent_n_disks_get_n_free(driver):
    select_option(driver, 'f_company_id_chosen', 'Test Com')
    select_option(driver, 'couponTypeId_chosen', 'Rent n Disks, Get n Free')
    driver.find_element_by_xpath("//div[@id='params']/input[1]").send_keys("1")
    driver.find_element_by_xpath("//div[@id='params']/input[2]").send_keys("1")
    end_saving_coupon(driver)
    clean_and_find_coupon(driver, "Rent n Disks, Get n Free not found in table")

def add_coupon_n_nn_off(driver):
    select_option(driver, 'f_company_id_chosen', 'Test Com')
    select_option(driver, 'couponTypeId_chosen', '$n.nn Off')
    driver.find_element_by_xpath("//div[@id='params']/input[1]").send_keys("1.1")
    end_saving_coupon(driver)
    clean_and_find_coupon(driver, "$n.nn Off not found in table")

def add_coupon_first_night_off(driver):
    select_option(driver, 'f_company_id_chosen', 'Test Com')
    select_option(driver, 'couponTypeId_chosen', 'First Night % Off')
    driver.find_element_by_xpath("//div[@id='params']/input[1]").send_keys("20")
    end_saving_coupon(driver)
    clean_and_find_coupon(driver, "First Night % Off not found in table")

def add_coupon_rent_n_disks_get_off(driver):
    select_option(driver, 'f_company_id_chosen', 'Test Com')
    select_option(driver, 'couponTypeId_chosen', 'Rent n Disks, Get % Off')
    driver.find_element_by_xpath("//div[@id='params']/input[1]").send_keys("1")
    driver.find_element_by_xpath("//div[@id='params']/input[2]").send_keys("20")
    end_saving_coupon(driver)
    clean_and_find_coupon(driver, "Rent n Disks, Get % Off not found in table")