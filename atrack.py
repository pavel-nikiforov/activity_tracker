# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By

import sys

driver = None
username = 'username'
password = 'password'


def login():
    # Create a new instance of the Firefox driver
    global driver
    driver = webdriver.Firefox()

    # go to the google home page
    driver.get("http://redmine.ln/projects/go-system-up-win/activity")

    # the page is ajaxy so the title is originally this:
    print(driver.title)

    # Login
    inputElement = driver.find_element_by_name("username")
    inputElement.send_keys(username)

    # Password
    inputElement = driver.find_element_by_name("password")
    inputElement.send_keys(password)

    # Logging in
    inputElement.submit()

    try:
        # we have to wait for the page to refresh, the last thing that seems to be updated is the title
        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'a.user.active'), username))

        # You should see "cheese! - Google Search"
        print("Logged in")


        #WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'div#content h2'), 'Действия'))
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div#content h2')))
        print("Page loaded")

    except (TimeoutException):
        print "Login failed"
        driver.quit()
        exit()



def read_tasks():

    try:
        tasknames = driver.find_elements_by_css_selector('div#activity dl:first-of-type dt.issue-edit a')
        for taskname in tasknames:
            print taskname.get_attribute("href")
    except NoSuchElementException as e:
        print("No task names found")



    try:
        authors = driver.find_elements_by_css_selector('div#activity dl:first-of-type dd span.author a')
        for author in authors:
            print author.get_attribute("href")
    except NoSuchElementException as e:
        print("No task names found")

    driver.quit()



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage:"
        print sys.argv[0] + " <login> <password>"
        sys.exit()
    else:
        username = sys.argv[1]
        password = sys.argv[2]

    login()
    read_tasks()