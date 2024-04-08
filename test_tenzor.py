import pytest
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@pytest.fixture(scope="class")
def setup(request):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    request.cls.driver = driver
    yield
    driver.quit()

@pytest.mark.usefixtures("setup")
class TestTensorBanner:
    def test_open_tensor_website_from_sbis(self, caplog):
        caplog.set_level(logging.INFO)
        self.driver.get("https://sbis.ru/")
        
        # Найти и кликнуть на кнопку "Контакты"
        contacts_button = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Контакты')]")
        contacts_button.click()
        logging.info("Clicked on 'Contacts' button")

        try:
            # Дождаться загрузки изображения с увеличенным временем ожидания
            wait = WebDriverWait(self.driver, 20)
            tensor_banner = wait.until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@src, 'logo.svg')]")))
            logging.info("Banner loaded successfully")
            
            # Получить текущее количество вкладок
            initial_tabs = self.driver.window_handles
            
            # Кликнуть на изображение
            tensor_banner.click()
            logging.info("Clicked on the banner")
            
            # Ждем, пока не появится новая вкладка
            wait.until(EC.number_of_windows_to_be(len(initial_tabs) + 1))
            
            # Получить все вкладки после открытия новой
            all_tabs = self.driver.window_handles
            
            # Переключиться на новую вкладку
            new_tab = [tab for tab in all_tabs if tab not in initial_tabs][0]
            self.driver.switch_to.window(new_tab)

            # Проверить URL на новой вкладке
            assert self.driver.current_url == "https://tensor.ru/"
            logging.info("URL verified: https://tensor.ru/")

            # Проверить наличие блока "Сила в людях"
            block_sila_v_lyudyakh = wait.until(EC.visibility_of_element_located((By.XPATH, "//p[@class='tensor_ru-Index__card-title tensor_ru-pb-16'][contains(text(), 'Сила в людях')]")))
            assert block_sila_v_lyudyakh.is_displayed()
            logging.info("Block 'Strength in People' is displayed")

            # Найти ссылку "Подробнее" в блоке "Сила в людях" и кликнуть по ней
            link_podrobnее = block_sila_v_lyudyakh.find_element(By.XPATH, "//a[@href='/about'][contains(text(), 'Подробнее')]")
            # Выполнить скроллинг до элемента, чтобы он оказался в видимой области
            self.driver.execute_script("arguments[0].scrollIntoView();", link_podrobnее)
            link_podrobnее.click()
            logging.info("Clicked on 'Learn more' link")

            # Проверить, что URL перешел на страницу "О компании"
            assert self.driver.current_url == "https://tensor.ru/about"
            logging.info("URL verified: https://tensor.ru/about")

            # Найти раздел "Работаем"
            section_work = self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Работаем')]")

            # Доскроллить страницу до раздела "Работаем"
            self.driver.execute_script("arguments[0].scrollIntoView();", section_work)

            # Найти все изображения в разделе "Работаем"
            images_work = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'tensor_ru-About__block3-image')]/img")))
            logging.info(f"Number of images found: {len(images_work)}")

            # Получить размеры первого изображения
            first_image_size = images_work[0].size
            first_image_width = first_image_size['width']
            first_image_height = first_image_size['height']

            # Проверить размеры всех изображений и записать информацию в лог
            for index, image in enumerate(images_work, start=1):
                image_size = image.size
                image_width = image_size['width']
                image_height = image_size['height']
                logging.info(f"Image {index}: Width = {image_width}, Height = {image_height}")

                # Проверить, что размеры всех изображений одинаковые
                assert image_width == first_image_width
                assert image_height == first_image_height

            logging.info("Sizes are equal")

        except TimeoutException:
            logging.error("Timeout waiting for the banner to load")
            pytest.fail("Timeout waiting for the banner to load")
