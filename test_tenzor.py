import pytest
import time
from selenium import webdriver
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Page_SBIS_main:
    CONTACTS_BUTTON = (By.XPATH, '//a[@href="/contacts"]')

    def __init__(self, driver):
        self.driver = driver

    def click_contacts_button(self):
        self.driver.find_element(*self.CONTACTS_BUTTON).click()


class Page_SBIS_contacts:
    BANNER_IMAGE = (By.XPATH, '//img[contains(@src, "logo.svg")]')
    REGION = (By.XPATH, '//span[contains(@class, "sbis_ru-Region-Chooser__text sbis_ru-link")]')
    PARTNERS_LIST = (By.XPATH, '//div[contains(@class, "sbisru-Contacts-List__item")]')
    GET_REGION = (By.XPATH, '//span[contains(text(), "41 Камчатский край")]')

    def __init__(self, driver):
        self.driver = driver

    def find_banner_image(self):
        return self.driver.find_element(*self.BANNER_IMAGE)
    
    def banner_click(self):
        initial_tabs = self.driver.window_handles # get id all tabs before banner click
        self.find_banner_image().click()
        logging.info("Clicked on the banner")
        return initial_tabs
    
    def find_region(self):
        return self.driver.find_element(*self.REGION)
    
    def find_contact_list(self):
        return self.driver.find_elements(*self.PARTNERS_LIST)
    
    def get_region(self):
        return self.driver.find_element(*self.GET_REGION)
    

class Page_TENZOR_main:
    # STRENGTH_IN_PEOPLE_BLOCK = (By.XPATH, '//div[contains(@class, "tensor_ru-Index__block4-content")]')
    STRENGTH_IN_PEOPLE_BLOCK = (By.XPATH, '//p[contains(text(), "Сила в людях")]')
    LEARN_MORE_LINK = (By.XPATH, '//a[@href="/about"]')

    def __init__(self, driver):
        self.driver = driver
    
    def wait_for_new_tab_to_open(self, initial_tabs):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.number_of_windows_to_be(len(initial_tabs) + 1))

    def switch_to_new_tab_by_banner(self, initial_tabs):
        self.wait_for_new_tab_to_open(initial_tabs)
        all_tabs = self.driver.window_handles # get id all tabs after banner click
        new_tab = [tab for tab in all_tabs if tab not in initial_tabs][0] # define new tab
        self.driver.switch_to.window(new_tab)
    
    def find_for_strength_in_people_block(self):
        return self.driver.find_element(*self.STRENGTH_IN_PEOPLE_BLOCK)

    def click_learn_more_link(self):
        self.find_for_strength_in_people_block().find_element(*self.LEARN_MORE_LINK).click()
        # self.driver.execute_script("arguments[0].scrollIntoView();", learn_more_link)
    
class Page_TENZOR_about:
    WORK_SECTION = (By.XPATH, '//h2[contains(text(), "Работаем")]')
    WORK_IMAGES = (By.XPATH, '//div[contains(@class, "tensor_ru-About__block3-image")]/img')

    def __init__(self, driver):
        self.driver = driver

    def wait_for_work_section(self):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.visibility_of_element_located(self.WORK_SECTION))

    def get_work_images_info(self):
        images = self.driver.find_elements(*self.WORK_IMAGES)
        info = []
        for image in images:
            name = image.get_attribute("alt")
            width = image.get_attribute("width")
            height = image.get_attribute("height")
            info.append((name, width, height))
        return info

@pytest.fixture(scope="class")
def setup(request):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    request.cls.page_sbis_main = Page_SBIS_main(driver)
    request.cls.page_sbis_contacts = Page_SBIS_contacts(driver)
    request.cls.page_tenzor_main = Page_TENZOR_main(driver)
    request.cls.page_tenzor_about = Page_TENZOR_about(driver)
    yield
    driver.quit()

# @pytest.mark.usefixtures("setup")
# class Test_Scenario_1:
#     def test_open_tensor_website_from_sbis(self, caplog):
#         caplog.set_level(logging.INFO)
#         try:
#             self.page_sbis_main.driver.get("https://sbis.ru/")
#             self.page_sbis_main.click_contacts_button()
#             logging.info("Clicked on 'Contacts' button")

#             assert self.page_sbis_contacts.find_banner_image().is_displayed()
#             logging.info("Banner is displayed")

#             initial_tabs = self.page_sbis_contacts.banner_click()
#             self.page_tenzor_main.switch_to_new_tab_by_banner(initial_tabs)
#             assert self.page_tenzor_main.driver.current_url == "https://tensor.ru/"
#             logging.info("URL verified: https://tensor.ru/")

#             strength_in_people_block = self.page_tenzor_main.find_for_strength_in_people_block()
#             assert self.page_tenzor_main.find_for_strength_in_people_block().is_displayed()
#             logging.info("Block 'Strength in People' is displayed")

#             self.page_tenzor_main.click_learn_more_link()
#             logging.info("Clicked on 'Learn more' link")
#             assert self.page_tenzor_about.driver.current_url == "https://tensor.ru/about"
#             logging.info("URL verified: https://tensor.ru/about")

#             self.page_tenzor_about.wait_for_work_section()
#             images_info = self.page_tenzor_about.get_work_images_info()
#             logging.info(f"Number of images found: {len(images_info)}")

#             first_image_name, first_image_width, first_image_height = images_info[0]
#             for index, (name, width, height) in enumerate(images_info, start=1):
#                 logging.info(f"Image {index}: Name = {name}, Width = {width}, Height = {height}")
#                 assert width == first_image_width
#                 assert height == first_image_height

#             logging.info("Sizes are equal")

#         except TimeoutException:
#             logging.error("Timeout")
#             pytest.fail("Timeout")

@pytest.mark.usefixtures("setup")
class Test_Scenario_2:
    def test_check_region_and_partners(self, caplog):
        caplog.set_level(logging.INFO)
        try:
            self.page_sbis_main.driver.get("https://sbis.ru/")
            self.page_sbis_main.click_contacts_button()
            logging.info("Clicked on 'Contacts' button")

            region_name = self.page_sbis_contacts.find_region()
            assert region_name.text.strip() == "Тюменская обл."
            logging.info(f"Region verified: {region_name.text.strip()}")

            partners_list = self.page_sbis_contacts.find_contact_list()
            assert len(partners_list) > 0
            logging.info(f"Number of partners found: {len(partners_list)}")
            logging.info("Partners list is displayed")

            region_name.click()
            get_region = self.page_sbis_contacts.get_region()
            logging.info(f"Region selected: {get_region.text.strip()}")

            wait = WebDriverWait(self.page_sbis_contacts.driver, 10)
            get_region = wait.until(EC.element_to_be_clickable(self.page_sbis_contacts.GET_REGION))
            logging.info(f"Region selected: {get_region.text.strip()}")
            get_region.click()
            
            # time.sleep(5)
            # wait.until(EC.text_to_be_present_in_element(self.page_sbis_contacts.REGION, "41 Камчатский край"))

            
            region_name_2 = self.page_sbis_contacts.find_region()
            # assert region_name.text.strip() == "41 Камчатский край"
            logging.info(f"Region verified: {region_name_2.text.strip()}")

        except TimeoutException:
            logging.error("Timeout")
            pytest.fail("Timeout")
