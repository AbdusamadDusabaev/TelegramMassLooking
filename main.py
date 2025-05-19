import csv
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import undetected_chromedriver as uc


DOMAIN = "https://web.telegram.org/a/"
DELAY_VALUE = 5
GLOBAL_DELAY_VALUE = 15

user_statuses = dict()


def get_usernames() -> list[str]:
    with open(file="output.csv", mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        usernames = [row[0].strip() if row[0].startswith("@") else "@" + row[0].strip() for row in reader]
    return usernames


def write_user_statuses() -> None:
    data = [[key, value] for key, value in user_statuses.items()]
    with open(file="output.csv", mode="w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Result"])
        writer.writerows(data)


def init_browser() -> uc.Chrome:
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options = uc.ChromeOptions()
    options.page_load_strategy = 'normal'
    options.add_experimental_option("prefs", prefs)
    return uc.Chrome(options=options)


def like_user_post(browser: uc.Chrome, username: str) -> None:
    search_input = browser.find_element(by=By.ID, value="telegram-search-input")
    search_input.clear()
    time.sleep(DELAY_VALUE)
    search_input.click()
    search_input.send_keys(username)
    time.sleep(DELAY_VALUE)

    try:
        target_user_chat_result = browser.find_element(by=By.XPATH, value=f"//div[contains(@class, 'chat-item-clickable') and .//span[text()='{username[1:]}']]")
        target_user_chat_result.click()
        time.sleep(DELAY_VALUE)
    except Exception:
        try:
            browser.find_element(by=By.XPATH, value="//h3[@class='section-heading' and text()='Chats and Contacts']")
            target_user_chat_result = browser.find_element(by=By.CSS_SELECTOR, value=".search-result")
            target_user_chat_result.click()
            time.sleep(DELAY_VALUE)
        except Exception:
            print(f"{username} не найден")
            user_statuses[username] = "не найден"
            browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(GLOBAL_DELAY_VALUE)
            return

    chat_info_header = browser.find_element(by=By.CSS_SELECTOR, value=".ChatInfo")
    chat_info_header.click()
    time.sleep(DELAY_VALUE)

    try:
        stories_list = browser.find_element(by=By.CSS_SELECTOR, value=".stories-list")
        first_story = stories_list.find_element(by=By.CSS_SELECTOR, value="div")
        first_story.click()
        time.sleep(DELAY_VALUE)
    except Exception:
        print(f"У {username} нет постов")
        user_statuses[username] = "нет постов"
        browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(GLOBAL_DELAY_VALUE)
        return


    like_button = browser.find_element(by=By.CSS_SELECTOR, value=".story-reaction-button")
    like_button.click()
    time.sleep(DELAY_VALUE)

    browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    user_statuses[username] = "успешно"
    print(f"{username} успешно обработан")
    time.sleep(GLOBAL_DELAY_VALUE)


def main() -> None:
    usernames = get_usernames()
    browser = init_browser()
    browser.get(url=DOMAIN)
    input("[INPUT] После авторизации нажмите ENTER >>> ")

    for username in usernames:
        try:
            like_user_post(browser=browser, username=username)
        except Exception as ex:
            user_statuses[username] = "ошибка"
            print(f"[ERROR] Неожиданная ошибка: {ex}")
            browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    write_user_statuses()
    print("[INFO] Работа успешно завершена!")


if __name__ == '__main__':
    main()
