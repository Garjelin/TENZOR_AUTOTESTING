import pytest
from selenium import webdriver
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SBISPage:
    """Page Object для страницы sbis.ru"""

    CONTACTS_BUTTON = (By.XPATH, '//a[@href="/contacts"]')
    BANNER_IMAGE = (By.XPATH, '//img[contains(@src, "logo.svg")]')
    # STRENGTH_IN_PEOPLE_BLOCK = (By.XPATH, '//div[contains(@class, "tensor_ru-Index__block4-content")]')
    STRENGTH_IN_PEOPLE_BLOCK = (By.XPATH, '//p[contains(text(), "Сила в людях")]')
    LEARN_MORE_LINK = (By.XPATH, '//a[@href="/about"]')
    WORK_SECTION = (By.XPATH, "//h2[contains(text(), 'Работаем')]")
    WORK_IMAGES = (By.XPATH, "//div[contains(@class, 'tensor_ru-About__block3-image')]/img")

    REGION = (By.XPATH, "//span[contains(@class, 'sbis_ru-Region-Chooser__text sbis_ru-link')]")
    PARTNERS_LIST = (By.XPATH, "//div[contains(@class, 'sbisru-Contacts-List__item')]")

    def __init__(self, driver):
        self.driver = driver

    def click_contacts_button(self):
        self.driver.find_element(*self.CONTACTS_BUTTON).click()

    def find_banner_image(self):
        return self.driver.find_element(*self.BANNER_IMAGE)
    
    def wait_for_new_tab_to_open(self, initial_tabs):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.number_of_windows_to_be(len(initial_tabs) + 1))

    def switch_to_new_tab_by_banner(self):
        initial_tabs = self.driver.window_handles # get id all tabs before banner click
        self.find_banner_image().click()
        logging.info("Clicked on the banner")
        self.wait_for_new_tab_to_open(initial_tabs)
        all_tabs = self.driver.window_handles # get id all tabs after banner click
        new_tab = [tab for tab in all_tabs if tab not in initial_tabs][0] # define new tab
        self.driver.switch_to.window(new_tab)
    
    def find_for_strength_in_people_block(self):
        return self.driver.find_element(*self.STRENGTH_IN_PEOPLE_BLOCK)

    def click_learn_more_link(self):
        self.find_for_strength_in_people_block().find_element(*self.LEARN_MORE_LINK).click()

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
    


    def detect_region(self):
        region_element = self.driver.find_element(*self.REGION)
        return region_element.text.strip()
    def find_contact_list(self):
        return self.driver.find_elements(*self.PARTNERS_LIST)


@pytest.fixture(scope="class")
def setup(request):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    request.cls.page = SBISPage(driver)
    yield
    driver.quit()

@pytest.mark.usefixtures("setup")
class TestTensorBanner:
    def test_open_tensor_website_from_sbis(self, caplog):
        caplog.set_level(logging.INFO)
        try:
            self.page.driver.get("https://sbis.ru/")
            self.page.click_contacts_button()
            logging.info("Clicked on 'Contacts' button")

            assert self.page.find_banner_image().is_displayed()
            logging.info("Banner is displayed")

            self.page.switch_to_new_tab_by_banner()
            assert self.page.driver.current_url == "https://tensor.ru/"
            logging.info("URL verified: https://tensor.ru/")

            assert self.page.find_for_strength_in_people_block().is_displayed()
            logging.info("Block 'Strength in People' is displayed")

            self.page.click_learn_more_link()
            logging.info("Clicked on 'Learn more' link")
            assert self.page.driver.current_url == "https://tensor.ru/about"
            logging.info("URL verified: https://tensor.ru/about")

            self.page.wait_for_work_section()
            images_info = self.page.get_work_images_info()
            logging.info(f"Number of images found: {len(images_info)}")

            first_image_name, first_image_width, first_image_height = images_info[0]
            for index, (name, width, height) in enumerate(images_info, start=1):
                logging.info(f"Image {index}: Name = {name}, Width = {width}, Height = {height}")
                assert width == first_image_width
                assert height == first_image_height

            logging.info("Sizes are equal")

        except TimeoutException:
            logging.error("Timeout waiting for the banner to load")
            pytest.fail("Timeout waiting for the banner to load")

# @pytest.mark.usefixtures("setup")
# class TestSecondScenario:
#     def test_check_region_and_partners(self, caplog):
#         caplog.set_level(logging.INFO)
#         self.page.driver.get("https://sbis.ru/")
#         self.page.click_contacts_button()
#         logging.info("Clicked on 'Contacts' button")

#         try:
#             region_name = self.page.detect_region()
#             assert region_name == "Тюменская обл."
#             logging.info(f"Region verified: {region_name}")

#             partners_list = self.page.find_contact_list()
#             assert len(partners_list) > 0
#             logging.info(f"Number of partners found: {len(partners_list)}")
#             logging.info("Partners list is displayed")

#         except TimeoutException:
#             logging.error("Timeout waiting for the banner to load")
#             pytest.fail("Timeout waiting for the banner to load")
