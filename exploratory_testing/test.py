# -*- coding: utf-8 -*-
# lib -> variables -> func -> verification -> actions
from actions import *

class Walk_on_the_site(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_walk(self):
        driver = self.driver
        # Login & Logout
        driver = login(driver)
        driver = logout(driver)
        driver = login(driver)

        profile_add(driver)
        company_add(driver)
        company_list(driver)
        company_staff(driver)
        company_staff_focus(driver)
        payments(driver)
        company_group_list(driver)
        company_trailers(driver)
        company_social(driver)
        priceplans(driver)
        kiosks_list(driver)
        rentalfleet(driver)
        rentalfleet_disks(driver)
        rentalfleet_disks_add(driver)
        rentalfleet_disks_out(driver)
        movies_add(driver)
        movies_add_upc(driver)
        movies_all(driver)
        movies_featured(driver)
        deals(driver)
        coupons_all(driver)
        reports_patterns(driver)
        reports_reports(driver)
        reports_data_sources(driver)

    def tearDown(self):
        self.driver.close()

class Profile(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_profile_edit(self):
        driver = self.driver
        driver = login(driver)
        profile_edit(driver)
        profile_edit_my(driver)

    def tearDown(self):
        self.driver.close()

class EditCompany(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_company_edit(self):
        driver = self.driver
        driver = login(driver)
        company_edit(driver)

    def tearDown(self):
        self.driver.close()

class EditKiosk(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_kiosk_edit(self):
        driver = self.driver
        driver = login(driver)
        kiosk_edit(driver)

    def tearDown(self):
        self.driver.close()

class AddCoupons(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_add_coupons(self):
        driver = self.driver
        driver = login(driver)
        driver.get(site + urls["coupons_all"])
        is_coupons_all(driver)
        clean_coupons(driver)
        add_coupon_first_night_free(driver)
        add_coupon_rent_n_disks_get_n_free(driver)
        add_coupon_n_nn_off(driver)
        add_coupon_first_night_off(driver)
        add_coupon_rent_n_disks_get_off(driver)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()

"""assert "No results found." == 111
self.assertIn("Python", driver.title)
elem = driver.find_element_by_name("q")
elem.send_keys("pycon")
assert "No results found." not in driver.page_source
elem.send_keys(Keys.RETURN)"""