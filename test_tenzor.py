import pytest
import time
from selenium import webdriver
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import os
import requests
import re

class Page_SBIS_main:
    CONTACTS_BUTTON = (By.XPATH, '//a[@href="/contacts"]')
    DOWNLOAD_LOCAL_VERS_BUTTON = (By.XPATH, '//a[@href="/download"]')
    CLOSE_COOCIE_AGREEMENT_BUTTON = (By.XPATH, '//div[contains(@class, "sbis_ru-CookieAgreement__close")]')

    def __init__(self, driver):
        self.driver = driver

    def click_contacts_button(self):
        self.driver.find_element(*self.CONTACTS_BUTTON).click()

    def click_close_coocie_agreements_button(self):
        return self.driver.find_element(*self.CLOSE_COOCIE_AGREEMENT_BUTTON).click()

    def click_download_local_vers_button(self):
        return self.driver.find_element(*self.DOWNLOAD_LOCAL_VERS_BUTTON).click()


class Page_SBIS_contacts:
    BANNER_IMAGE = (By.XPATH, '//img[contains(@src, "logo.svg")]')
    REGION = (By.XPATH, '//span[contains(@class, "sbis_ru-Region-Chooser__text sbis_ru-link")]')
    PARTNERS_LIST = (By.XPATH, '//div[contains(@class, "sbisru-Contacts-List__name")]')
    REGION_IN_LIST = (By.XPATH, '//span[@title="Камчатский край"]')

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
    
    def find_contact_list_with_titles(self):
        contacts_with_titles = self.driver.find_elements(*self.PARTNERS_LIST)
        return [contact.get_attribute("title") for contact in contacts_with_titles]
    
    def find_new_region_in_list(self):
        return self.driver.find_element(*self.REGION_IN_LIST)
    
class Page_SBIS_download:
    PLUGIN_BUTTON = (By.XPATH, '//div[contains(text(), "СБИС Плагин")]')
    WINDOWS_BUTTON = (By.XPATH, '//span[contains(text(), "Windows")]')
    DOWNLOAD_LINK = (By.XPATH, '//a[@href="https://update.sbis.ru/Sbis3Plugin/master/win32/sbisplugin-setup-web.exe"]')
    
    def __init__(self, driver):
        self.driver = driver

    def find_plugin_button(self):
        return self.driver.find_element(*self.PLUGIN_BUTTON)
    
    def find_windows_button(self):
        return self.driver.find_element(*self.WINDOWS_BUTTON)
    
    def find_file_to_download(self):
        return self.driver.find_element(*self.DOWNLOAD_LINK)

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
    request.cls.page_sbis_download = Page_SBIS_download(driver)
    request.cls.page_tenzor_main = Page_TENZOR_main(driver)
    request.cls.page_tenzor_about = Page_TENZOR_about(driver)
    yield
    driver.quit()

@pytest.mark.usefixtures("setup")
class Test_Scenario_1:
    def test_scenario_1(self, caplog):
        caplog.set_level(logging.INFO)
        try:
            logging.info("")
            logging.info("******SCENARIO_1******")
            logging.info("")
            self.page_sbis_main.driver.get("https://sbis.ru/")
            self.page_sbis_main.click_contacts_button()
            logging.info("Clicked on 'Контакты' button")

            assert self.page_sbis_contacts.find_banner_image().is_displayed()
            logging.info("Banner is displayed")

            initial_tabs = self.page_sbis_contacts.banner_click()
            self.page_tenzor_main.switch_to_new_tab_by_banner(initial_tabs)
            assert self.page_tenzor_main.driver.current_url == "https://tensor.ru/"
            logging.info("URL verified: https://tensor.ru/")

            strength_in_people_block = self.page_tenzor_main.find_for_strength_in_people_block()
            assert self.page_tenzor_main.find_for_strength_in_people_block().is_displayed()
            logging.info("Block 'Сила в людях' is displayed")

            self.page_tenzor_main.click_learn_more_link()
            logging.info("Clicked on 'Подробнее' link")
            assert self.page_tenzor_about.driver.current_url == "https://tensor.ru/about"
            logging.info("URL verified: https://tensor.ru/about")

            self.page_tenzor_about.wait_for_work_section()
            images_info = self.page_tenzor_about.get_work_images_info()
            logging.info(f"Number of images found: {len(images_info)}")

            first_image_name, first_image_width, first_image_height = images_info[0]
            for index, (name, width, height) in enumerate(images_info, start=1):
                logging.info(f"Image {index}: Name = '{name}', Width = {width}, Height = {height}")
                assert width == first_image_width
                assert height == first_image_height

            logging.info("Sizes are equal")

        except TimeoutException:
            logging.error("Timeout")
            pytest.fail("Timeout")

@pytest.mark.usefixtures("setup")
class Test_Scenario_2:
    def test_scenario_2(self, caplog):
        caplog.set_level(logging.INFO)
        try:
            logging.info("")
            logging.info("******SCENARIO_2******")
            logging.info("")
            self.page_sbis_main.driver.get("https://sbis.ru/")
            self.page_sbis_main.click_contacts_button()
            logging.info("Clicked on 'Контакты' button")

            region_name = self.page_sbis_contacts.find_region()
            assert region_name.text.strip() == "Тюменская обл."
            logging.info(f"Region verified: '{region_name.text.strip()}'")

            partners_list_titles = self.page_sbis_contacts.find_contact_list_with_titles()
            assert len(partners_list_titles) > 0
            logging.info(f"Number of partners found: {len(partners_list_titles)}")
            logging.info("Partners list is displayed:")
            for index, partner_title in enumerate(partners_list_titles, start=1):
                logging.info(f"         Partner {index}: '{partner_title}'")

            region_name.click() # open region list
            new_region = self.page_sbis_contacts.find_new_region_in_list()
            logging.info(f"Region selected: '{new_region.text.strip()}'")
           
            # simple method click() doesn't work
            # click using a mouse
            action_chains = ActionChains(self.page_sbis_contacts.driver)
            action_chains.move_to_element(new_region).click().perform()
            # new region doesn't appear without delay
            wait = WebDriverWait(self.page_sbis_contacts.driver, 10)
            wait.until(EC.text_to_be_present_in_element(self.page_sbis_contacts.REGION, "Камчатский край"))
            new_region = self.page_sbis_contacts.find_region()
            assert region_name.text.strip() == "Камчатский край"
            logging.info(f"Region verified: '{new_region.text.strip()}'")
            # time.sleep(5)

            partners_list_titles = self.page_sbis_contacts.find_contact_list_with_titles()
            assert len(partners_list_titles) > 0
            logging.info(f"Number of partners found: {len(partners_list_titles)}")
            logging.info("Partners list is displayed:")
            for index, partner_title in enumerate(partners_list_titles, start=1):
                logging.info(f"         Partner {index}: '{partner_title}'")

            assert "41-kamchatskij-kraj" in self.page_sbis_contacts.driver.current_url
            logging.info("URL contains '41-kamchatskij-kraj'")
            

        except TimeoutException:
            logging.error("Timeout")
            pytest.fail("Timeout")

@pytest.mark.usefixtures("setup")
class Test_Scenario_3:
    def test_scenario_3(self, caplog):
        caplog.set_level(logging.INFO)
        try:
            logging.info("")
            logging.info("******SCENARIO_3******")
            logging.info("")
            self.page_sbis_main.driver.get("https://sbis.ru/")
            
            self.page_sbis_main.click_close_coocie_agreements_button()
            self.page_sbis_main.click_download_local_vers_button()
            logging.info("Clicked on 'Скачать локальные версии' button")

            assert "sbis.ru/download" in self.page_sbis_contacts.driver.current_url
            logging.info("URL verified: https://sbis.ru/download")
            
            plug = self.page_sbis_download.find_plugin_button()
            time.sleep(5) # somnitelno no okey
            # wait = WebDriverWait(self.page_sbis_download.driver, 10) 
            # plug = wait.until(EC.element_to_be_clickable(self.page_sbis_download.PLUGIN_BUTTON))
            action_chains = ActionChains(self.page_sbis_download.driver)
            action_chains.move_to_element(plug).click().perform()
            plug.click()
            assert plug.text.strip() == "СБИС Плагин"
            logging.info(f"Clicked on '{plug.text.strip()}'")

            windows_but = self.page_sbis_download.find_windows_button()
            action_chains = ActionChains(self.page_sbis_download.driver)
            action_chains.move_to_element(windows_but).click().perform()
            assert windows_but.text.strip() == "Windows"
            logging.info(f"Clicked on '{windows_but.text.strip()}'")

            download_file = self.page_sbis_download.find_file_to_download()
            file_url = download_file.get_attribute('href')
            current_directory = os.getcwd()
            file_name = file_url.split('/')[-1]
            file_path = os.path.join(current_directory, file_name)
            assert file_name.strip() == "sbisplugin-setup-web.exe"
            logging.info(f"File path: '{file_path}'")
            start_time = time.time()
            response = requests.get(file_url)
            end_time = time.time()
            logging.info(f"Time taken for download: {round((end_time - start_time), 1)} seconds")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            assert os.path.exists(file_path), "Downloaded file does not exist"
            logging.info(f"File '{file_name}' exists")
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            download_link_text = self.page_sbis_download.find_file_to_download().text
            pattern = r'\d+\.\d+' 
            matches = re.findall(pattern, download_link_text)
            file_size_expected = float(matches[0]) if matches else None
            assert file_size_expected == file_size_mb
            logging.info(f"Expected file size: {file_size_expected} mb - Actual file size: {file_size_mb} mb")

            time.sleep(5)
        except TimeoutException:
            logging.error("Timeout")
            pytest.fail("Timeout")
