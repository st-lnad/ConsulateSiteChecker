from json import load

from selenium import webdriver

from src.parser.src.captcha import get_srt_captcha_from_screenshot

config_file = open('src/parser/cfg/Config.json', 'r')
config = load(config_file)
config_file.close()


def parse_docs_status(user_data):
    chrome_driver_path = config["Driver"]["chrome_driver_path"]
    target_site = config["Est_site"]["target_site"]

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
    browser.set_window_size(800, 600)

    browser.get(target_site)
    answer_available = False
    res: str = ""
    while not answer_available:
        ref_num_box = browser.find_element_by_name("RefNo")
        last_name_box = browser.find_element_by_name("LastName")
        cap_box = browser.find_element_by_name("CaptchaInputText")
        submit_button = browser.find_element_by_id("submitButton")

        # enter user data
        ref_num_box.send_keys(user_data["Ref_Num"])
        last_name_box.send_keys(user_data["Last_Name"])
        cap_damaged, cap_text = get_srt_captcha_from_screenshot(browser.get_screenshot_as_png())

        # enter captcha
        cap_box.send_keys(cap_text)

        # submit
        submit_button.click()

        # check answer
        wrong_cap_box = browser.find_elements_by_xpath(config["Est_site"]["wrong_cap_box_xpath"])
        is_cap_valid = True if (wrong_cap_box == [] and not cap_damaged) else False
        if not is_cap_valid:
            browser.get(target_site)
            continue

        # get_answer
        res = browser.find_element_by_xpath(config["Est_site"]["res_xpath"]).text
        answer_available = True
    browser.quit()
    return res
