"""

Программа парсит вакансии с телефонами с сайта.

(https://russia.zarplata.ru/vacancy/vrach)
сохраняет постранично в файлы pageNUM.txt(столбцы разделе TAB) в формате
Вакансия, Организация, Контактное лицо, Телефоны

Использованы библиотеки:
selenium

Последние изменение: 05.06.2022

"""

from selenium import webdriver
from selenium.webdriver.common.by import By

start_page = 1  # начинать грабить со страницы начинается с 1
end_page = 2    # последняя

wait_4_page_loading = 10     # время ожидание загрузки страницы или элемента

vacs_per_page = 25  # выкансий на странице для вычисления смещения.
                    # в начале может быть любым. коректируется во время работы

# получать только первую вакансию со страницы. для отладки, чтобы не
# прощелкивать все контакты на странице
#test_mode = True
test_mode = False


options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

# chromedriver.exe - находится в папке программы
driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
driver.implicitly_wait(wait_4_page_loading)
driver.set_page_load_timeout(wait_4_page_loading)

for page_num in range(start_page-1, end_page):
    page_url = "https://russia.zarplata.ru/vacancy/vrach?offset=" + \
        str(page_num*vacs_per_page)
    print("URL: " + page_url)
    driver.get(page_url)
    try:
        # получаем все наименования вакансый на странице
        vac_titles = driver.find_elements(
            By.CLASS_NAME, value="vacancy-title_23EUM")
    except:
        print("Страница пуста. Все вакансии сграбили")
        break
    finally:
        vacs_per_page = len(vac_titles)
        print(str(vacs_per_page) + " вакансий на странице")
        with open("page" + str(page_num+1) + ".txt", "w", encoding="utf8")\
                as f:
            for vac_title in vac_titles:
                title = vac_title.text
                id = vac_title.get_attribute("href").split('/')[5][2:]
                try:
                    # ищем кнопку контакты. иногда не бывает
                    btn_contacts = driver.find_element(
                        By.XPATH, value="//a[contains(@href, '" + id +
                        "')][text() = 'Контакты']")
                except:
                    # у вакансии нет контактных телефонов. только отклик.
                    # просто переходим к следущей ваканчии
                    continue
                # открываем окошко с контактами
                btn_contacts.click()
                # получаем все контакные телефоны (пока закрытые от парсинга)
                vac_phones = driver.find_elements(
                    By.XPATH, value="//button[@class='link-button_2sNwl btn_29r4R medium_Vx2fa link_3l9EP']")
                if len(vac_phones) > 0:
                    # если контакт оставил телефон
                    # прокликиваем все контакные телефоны (окрываем)
                    {vac_phone.click() for vac_phone in vac_phones}
                    vac_phones = driver.find_elements(
                        By.XPATH, value="//a[@class='link_1izHq']")
                    phones = ", ".join(map(lambda x: x.text, vac_phones))
                    contact = driver.find_element(
                        By.XPATH, value="//div[@class='hr_cY2do']").text
                    firm = driver.find_element(
                        By.XPATH, value="//*[@class='company_1JXiB']").text
                    vac_str = "\t".join((title, firm, contact, phones))
                    print(vac_str)
                    f.write(vac_str + "\n")
                # закрываем окошко с контактами
                driver.find_element(
                    By.XPATH, value="//i[@class='icon-close_2BZik icon_1zVnE icon-large_close_3_xrt']").click()
                if test_mode:
                    break

driver.close()
