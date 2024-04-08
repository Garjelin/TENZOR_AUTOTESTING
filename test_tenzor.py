import pytest
from selenium import webdriver
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class SBISPage:
    """Page Object для страницы sbis.ru"""

    CONTACTS_BUTTON = (By.XPATH, "//a[contains(text(), 'Контакты')]")
    BANNER_IMAGE = (By.XPATH, "//img[contains(@src, 'logo.svg')]")
    STRENGTH_IN_PEOPLE_BLOCK = (By.XPATH, "//p[@class='tensor_ru-Index__card-title tensor_ru-pb-16'][contains(text(), 'Сила в людях')]")
    LEARN_MORE_LINK = (By.XPATH, "//a[@href='/about'][contains(text(), 'Подробнее')]")
    WORK_SECTION = (By.XPATH, "//h2[contains(text(), 'Работаем')]")
    WORK_IMAGES = (By.XPATH, "//div[contains(@class, 'tensor_ru-About__block3-image')]/img")

    def __init__(self, driver):
        self.driver = driver

    def click_contacts_button(self):
        """Нажать на кнопку 'Контакты'"""
        self.driver.find_element(*self.CONTACTS_BUTTON).click()

    def wait_for_banner_image(self):
        """Дождаться загрузки баннера"""
        wait = WebDriverWait(self.driver, 20)
        return wait.until(EC.visibility_of_element_located(self.BANNER_IMAGE))

    def click_banner_image(self):
        """Нажать на изображение баннера"""
        self.wait_for_banner_image().click()
        logging.info("Clicked on the banner")

    def switch_to_new_tab(self):
        """Переключиться на новую вкладку"""
        initial_tabs = self.driver.window_handles
        self.click_banner_image()
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.number_of_windows_to_be(len(initial_tabs) + 1))
        all_tabs = self.driver.window_handles
        new_tab = [tab for tab in all_tabs if tab not in initial_tabs][0]
        self.driver.switch_to.window(new_tab)
    
    def wait_for_strength_in_people_block(self):
        """Дождаться появления блока 'Сила в людях' с прокруткой страницы вниз"""
        wait = WebDriverWait(self.driver, 20)
        strength_in_people_block = wait.until(EC.visibility_of_element_located(self.STRENGTH_IN_PEOPLE_BLOCK))
        # Прокрутка страницы до блока "Сила в людях"
        self.driver.execute_script("arguments[0].scrollIntoView(true);", strength_in_people_block)
        return strength_in_people_block

    def click_learn_more_link(self):
        """Нажать на ссылку 'Подробнее'"""
        self.wait_for_strength_in_people_block().find_element(*self.LEARN_MORE_LINK).click()

    def wait_for_work_section(self):
        """Дождаться раздела 'Работаем'"""
        wait = WebDriverWait(self.driver, 20)
        return wait.until(EC.visibility_of_element_located(self.WORK_SECTION))

    def get_work_images(self):
        """Получить список изображений в разделе 'Работаем'"""
        return self.driver.find_elements(*self.WORK_IMAGES)


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
        self.page.driver.get("https://sbis.ru/")
        self.page.click_contacts_button()
        logging.info("Clicked on 'Contacts' button")

        try:
            tensor_banner = self.page.wait_for_banner_image()
            logging.info("Banner loaded successfully")

            self.page.switch_to_new_tab()
            assert self.page.driver.current_url == "https://tensor.ru/"
            logging.info("URL verified: https://tensor.ru/")

            assert self.page.wait_for_strength_in_people_block().is_displayed()
            logging.info("Block 'Strength in People' is displayed")

            self.page.click_learn_more_link()
            logging.info("Clicked on 'Learn more' link")

            assert self.page.driver.current_url == "https://tensor.ru/about"
            logging.info("URL verified: https://tensor.ru/about")

            self.page.wait_for_work_section()
            images_work = self.page.get_work_images()
            logging.info(f"Number of images found: {len(images_work)}")

            first_image_size = images_work[0].size
            first_image_width = first_image_size['width']
            first_image_height = first_image_size['height']

            for index, image in enumerate(images_work, start=1):
                image_size = image.size
                image_width = image_size['width']
                image_height = image_size['height']
                logging.info(f"Image {index}: Width = {image_width}, Height = {image_height}")

                assert image_width == first_image_width
                assert image_height == first_image_height

            logging.info("Sizes are equal")

        except TimeoutException:
            logging.error("Timeout waiting for the banner to load")
            pytest.fail("Timeout waiting for the banner to load")
