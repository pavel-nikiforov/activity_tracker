# -*- coding: utf-8 -*-


from datetime import date
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By

import sys
import os

#products = ["Go-RFID", "Go-RFID Android", "Go-System Windows client"]
products = ["Go-RFID", "Go-Server", "Go-RFID Android", "Go-RFID.RU"]

redmines = {}
redmines["Go-RFID"] = "http://redmine.ln/projects/go-rfid/activity"
#redmines["Go-RFID"] = "http://redmine.ln/projects/go-rfid/activity?from=2017-01-24"
redmines["Go-Server"] = "http://redmine.ln/projects/go/activity?utf8=1&show_issues=1&with_subprojects=0"
redmines["Go-RFID Android"] = "http://rdm.go-rost.ru/projects/go-rfid-android/activity"
redmines["Go-System Windows client"] = "http://redmine.ln/projects/go-system-up-win/activity"
redmines["Go-RFID.RU"] = "http://rdm.go-rost.ru/projects/go-rfid-ru/activity"

report_filename = ""
filename_head = u""
filename_head = os.path.expanduser('~') + u"/Documents/reports/"
filename_tail = u" \u041E\u0442\u0447\u0435\u0442 \u043F\u043E \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u0430\u043D\u043D\u044B\u043C \u0437\u0430\u0434\u0430\u0447\u0430\u043C.txt"



driver = None
user_id = None
user_display_name = None
is_user_display_name_written = False

my_times = []
my_links = []
my_descr = []

username = 'username'
password = 'password'




def login(product):
    # Create a new instance of the Firefox driver
    global driver
    #driver = webdriver.Firefox()
    driver = webdriver.PhantomJS()
    driver.set_window_size(1024, 768)
    driver.implicitly_wait(15)

    # go to the google home page
    #driver.get("http://redmine.ln/projects/go-system-up-win/activity")
    #driver.get("http://redmine.ln/projects/go-rfid/activity?from=2016-05-31")
    #driver.get("http://redmine.ln/projects/go-rfid/activity")
    #driver.get("http://rdm.go-rost.ru/projects/go-rfid-android/activity")
    #driver.get("http://redmine.ln/projects/go/activity")
    driver.get(redmines[product])


    print "\n------------------"
    print product
    print "------------------\n"

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
        WebDriverWait(driver, 15).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'div#loggedas a.user.active'), username))

        # You should see "cheese! - Google Search"
        print "Logged in as " + driver.find_element_by_xpath("//div[@id='loggedas']/a").text


        #WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'div#content h2'), 'Действия'))
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div#content h2')))
        print("Page loaded")

    except (TimeoutException):
        print "Login failed"
        driver.quit()
        exit()


    global user_id
    try:
        user_id = driver.find_element_by_css_selector('div#loggedas a').get_attribute("href")
        print "user id: " + user_id
    except NoSuchElementException as e:
        print "Login failed"
        driver.quit()
        exit()


def read_tasks():

    raw_times = []
    raw_links = []
    raw_descr = []
    raw_users = []

    global user_id
    global user_display_name
    global my_links
    global my_descr

    if user_display_name is None:
        try:
            search_string = user_id[user_id.find("users"):]
            dn = driver.find_element_by_css_selector('span.author a[href*="' + search_string + '"]')
            user_display_name = dn.text
            print "Got displayname: " + user_display_name
        except NoSuchElementException as e:
            print("No user name found")



    try:
        tasknames = driver.find_elements_by_css_selector('div#activity dl:first-of-type dt a')
        for taskname in tasknames:
            link = taskname.get_attribute("href")
            descr = taskname.text
            print "%s\n%s" % (link,descr)
            raw_links.append(link)
            raw_descr.append(descr)
    except NoSuchElementException as e:
        print("No task names found")



    try:
        authors = driver.find_elements_by_css_selector('div#activity dl:first-of-type dd span.author a')
        for author in authors:
            userlink = author.get_attribute("href")
            print userlink
            raw_users.append(userlink)
    except NoSuchElementException as e:
        print("No task authors found")


    try:
        times = driver.find_elements_by_css_selector('div#activity dl:first-of-type dt span.time')
        #activity > dl:nth-child(2) > dt:nth-child(3) > span:nth-child(2)
        for time in times:
            usertime = time.text
            print usertime
            raw_times.append(usertime)
    except NoSuchElementException as e:
        print("No times found")



    for i in range(len(raw_links)):
        if raw_users[i] == user_id:
            my_times.append(raw_times[i])
            my_links.append(raw_links[i])
            my_descr.append(raw_descr[i])

    print "\n\nGeneral outcome"
    if len(my_links) > 0:
        print "Processed by my: ", len(my_links)
        for i in range(len(my_links)):
            print "[%i] %s" % (i,my_times[i])
            print "[%i] %s" % (i,my_descr[i])
            print "[%i] %s" % (i,my_links[i])
    else:
        print "No activity today"




    driver.quit()


def process_tasks():

    noaction_list = []
    for i in range(len(my_links)):
        if my_descr[i].find("(") == -1:
            noaction_list.append(i)
        else:
            status = my_descr[i][my_descr[i].find("(") + 1:my_descr[i].find(")")]
            my_descr[i] = status

            if my_links[i].find("#") != -1:
                trimmed_link = my_links[i][0:my_links[i].find("#")]
                my_links[i] = trimmed_link

    if len(noaction_list) is not 0:
        noaction_list.reverse()
        print "Deleting those items as non actions", noaction_list

        for i in noaction_list:
                print "deleting item ", i
                del my_times[i]
                del my_descr[i]
                del my_links[i]


    print "\n\nProcessed (step 1):"
    for i in range(len(my_links)):
        #print "[%i] %s" % (i,my_descr[i])
        print "[%i] (%s) %s - %s" % (i,my_times[i],my_links[i],my_descr[i])


    for i in range(len(my_links)):
        for j in range(len(my_links)-1):
            if my_times[j] < my_times[j+1]:
                temp_time = my_times[j]
                temp_desc = my_descr[j]
                temp_link = my_links[j]

                my_times[j] = my_times[j+1]
                my_descr[j] = my_descr[j+1]
                my_links[j] = my_links[j+1]

                my_times[j+1] = temp_time
                my_descr[j+1] = temp_desc
                my_links[j+1] = temp_link


    print "\n\nProcessed (step 2):"
    for i in range(len(my_links)):
        #print "[%i] %s" % (i,my_descr[i])
        print "[%i] (%s) %s - %s" % (i,my_times[i],my_links[i],my_descr[i])


    print "\n"
    processed_items_count = 0
    total_items = len(my_links)

    while(processed_items_count < total_items):
        duplicate_list = []
        for i in range(processed_items_count+1,len(my_links)):
            #print "[%i] (%s) %s - %s" % (i,my_times[i],my_links[i],my_descr[i])
            if (my_links[i] == my_links[processed_items_count]):
                #print "will remove [%i] (%s) %s - %s" % (i+1,my_times[i],my_links[i],my_descr[i])
                duplicate_list.append(i)

        #print duplicate_list
        duplicates_count = 0
        for i in duplicate_list:
                del my_times[i-duplicates_count]
                del my_descr[i-duplicates_count]
                del my_links[i-duplicates_count]
                duplicates_count = duplicates_count + 1


        total_items = len(my_links)
        processed_items_count = processed_items_count + 1


    print "\n\nProcessed (step 3):"
    for i in range(len(my_links)):
        #print "[%i] %s" % (i,my_descr[i])
        print "[%i] (%s) %s - %s" % (i,my_times[i],my_links[i],my_descr[i])



def translate_statuses():
    print "\n\nProcessed (step 4):"
    for i in range(len(my_links)):
        # New
        if my_descr[i] == u'\u041d\u043e\u0432\u0430\u044f':
            my_descr[i] = 'New'
        # Closed
        if my_descr[i] == u'\u0420\u0435\u0448\u0435\u043d\u0430':
            my_descr[i] = 'Closed'
        if my_descr[i] == u'\u0417\u0430\u043a\u0440\u044b\u0442\u0430':
            my_descr[i] = 'Closed'
        # Fix Again
        if my_descr[i] == u'\u041d\u0430 \u0434\u043e\u0440\u0430\u0431\u043e\u0442\u043a\u0443':
            my_descr[i] = 'Fix Again'
        # In Progress
        if my_descr[i] == u'\u0412 \u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438':
            my_descr[i] = 'Testing In Progress'

        if my_descr[i] not in ('New','Closed','Fix Again','Testing In Progress'):
            my_descr[i] = 'Hell if I know'

        print "%i. %s - %s" % (i+1,my_links[i],my_descr[i])



def store_tasks(product):
    global user_display_name
    global is_user_display_name_written

    if len(my_links) > 0:
        file_object = open(report_filename, 'a')

        if is_user_display_name_written is False:
            user_display_name = user_display_name + "."
            file_object.write(user_display_name.encode('utf8'))
            file_object.write("\n")
            is_user_display_name_written = True

        #header
        file_object.write("\n\n" + product + ":\n")

        #body
        for i in range(len(my_links)):
            file_object.write("   " + str(i+1) + ". " + my_links[i] + " - " + my_descr[i] + "\n")

        file_object.close()


def clear_tasks():
    global my_times
    global my_links
    global my_descr
    my_times = []
    my_links = []
    my_descr = []


def create_report_file():
    d = date.today()

    month_number = str(d.month)
    if len(month_number) < 2:
        month_number = "0" + month_number

    day_number = str(d.day)
    if len(day_number) < 2:
        day_number = "0" + day_number

    report_date = str(d.year) + month_number + day_number

    global report_filename
    report_filename = filename_head + report_date + filename_tail
    file_object = open(report_filename, 'w')

    report_display_date = day_number + "." + month_number + "." + str(d.year)
    report_head = u"\u041E\u0442\u0447\u0451\u0442 \u043F\u043E \u043E\u0431\u0440\u0430\u0431\u043E\u0442\u0430\u043D\u043D\u044B\u043C \u0437\u0430\u0434\u0430\u0447\u0430\u043C \u043E\u0442 "
    #report_tail = u"; \u041D\u0438\u043A\u0438\u0444\u043E\u0440\u043E\u0432 \u041F.\u041B."
    report_tail = u"; "
    report_string = u""
    report_string = report_head + report_display_date + report_tail

    file_object.write("\n")
    file_object.write(report_string.encode('utf8'))
    #file_object.write("\n")


    file_object.close()



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage:"
        print sys.argv[0] + " <login> <password>"
        sys.exit()
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        create_report_file()

    for product in products:
        login(product)
        read_tasks()
        process_tasks()
        translate_statuses()
        store_tasks(product)
        clear_tasks()
