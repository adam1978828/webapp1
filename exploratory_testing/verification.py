# -*- coding: utf-8 -*-
from func import *

def is_login(driver):
    check_words(driver, ["Login", "E-mail", "Password"] + [often[0]])

def is_profile(driver):
    check_words(driver, ["Profile", "Personal Details", "Update Details"] + often)

def is_logout(driver):
    check_words(driver, often)

def is_profile_add(driver):
    check_words(driver, ["Add new worker", "Personal information", "Email", "First name", "City", "Phone"] + often)

def is_company_add(driver):
    check_words(driver, ["Add new Company", "Password", "Company name", "City", "Phone", "Card number"] + often)

def is_company_list(driver):
    check_words(driver, ["All Companies", "Logo"] + data_tab + often)

def is_company_staff(driver):
    check_words(driver, ["staff", "Phone"] + data_tab + often)

def is_company_staff_focus(driver):
    check_words(driver, ["staff", "Phone"] + data_tab + often)

def is_payments(driver):
    check_words(driver, ["Merchant Accounts", "Account name", "Status"] + often)

def is_company_group_list(driver):
    check_words(driver, ["Add group", "groups", "Name"] + data_tab + often)

def is_company_settings_list(driver):
    check_words(driver, ["Company settings", "Test"] + data_tab + often)

def is_company_settings(driver):
    check_words(driver, ["Company settings", "time zone", "sale tax", "Language buttons", "Skip Days"] + often)

def is_company_trailers(driver):
    check_words(driver, ["Add trailer", "Trailer", "Trailers"] + data_tab + often)

def is_company_social(driver):
    check_words(driver, ["Logo", "Showing", "entries"] + often)

def is_priceplans(driver):
    check_words(driver, ["Price plans", "Name", "Sale", "Date"] + often)

def is_kiosks_list(driver):
    check_words(driver, ["All Kiosks", "id", "Name"] + data_tab + often)

def is_rentalfleet(driver):
    check_words(driver, ["Rental Fleet", "UPC", "id"] + often)

def is_rentalfleet_disks(driver):
    check_words(driver, ["Company", "UPC", "id", "Content"] + often)

def is_rentalfleet_disks_add(driver):
    check_words(driver, ["Company", "UPC", "RFID"] + often)

def is_rentalfleet_disks_out(driver):
    check_words(driver, ["Title", "UPC", "Format"] + data_tab + often)

def is_movies_add(driver):
    check_words(driver, ["Cover", "Length", "Rating"] + often)

def is_movies_add_upc(driver):
    check_words(driver, ["UPC", "Movie", "Format"] + often)

def is_movies_all(driver):
    check_words(driver, ["id", "Title", "Length"] + data_tab + often)

def is_movies_featured(driver):
    check_words(driver, ["#", "Title", "Length"] + data_tab + often)

def is_deals(driver):
    check_words(driver, ["Company", "ID", "Card"] + data_tab + often)

def is_coupons_all(driver):
    check_words(driver, ["Company", "Type", "Code"] + data_tab + often)

def is_reports_patterns(driver):
    check_words(driver, ["Data Source", "ID", "Actions"] + data_tab + often)

def is_reports_reports(driver):
    check_words(driver, ["Reports", "ID", "Actions"] + data_tab + often)

def is_reports_data_sources(driver):
    check_words(driver, ["Type", "ID", "Actions"] + often)

def is_profile_edit(driver):
    check_words(driver, ["First name", "City", "Phone"] + often)

def is_tokens(driver, token_list):
    check_words(driver, token_list + often)

def is_company_edit(driver):
    check_words(driver, ["Company name", "Address", "Phone"] + often)

def is_kiosk_edit(driver):
    check_words(driver, ["Kiosk uuid", "City", "State"] + often)