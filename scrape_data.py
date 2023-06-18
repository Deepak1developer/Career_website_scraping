import json
import re

from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import requests


def get_metadata(data, col):
    """Get the formatted values."""
    try:
        jd = data.get('jobAd').get('sections').get(col).get('text')
        raw_data = re.split(r"<[^>]+>", jd)
        description = [x.replace("•", "") for x in raw_data if x != '']
    except Exception as e:
        print(" Error in get_metadata {}".format(e))
    return description


def get_location(data):
    """Get the location."""
    value = None
    for i in data.get('customField'):
        if i.get('fieldId') == 'COUNTRY':
            value = i.get('valueLabel')
    return value


def check_none(value, first_key, second_key, data):
    """Check for none keys in dictionary."""
    try:
        if value is None:
            return None
        else:
            return data.get(first_key).get(second_key)
    except Exception as e:
        print(" Error in check_none {}".format(e))


def get_all_data(url):
    """Gets all the data from Job urls."""
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    all_data = dict()
    try:
        for script in soup.findAll('script', attrs={"id": "initials"}):
            for content in script.descendants:
                raw_data = json.loads(content)
                list_of_job_data = raw_data.get('smartRecruiterResult').get('content')
                for job in list_of_job_data:
                    if 'ref' in job.keys():
                        print("Processing this url {}".format(job.get('ref')))
                        data = requests.get(job.get('ref')).json()
                        dept = check_none(data.get("department"), "department", "label", data)
                        meta_data = {'title': data.get('name'),
                                     'location': get_location(data),
                                     'description': get_metadata(data, "jobDescription"),
                                     'qualification': get_metadata(data, "qualifications"),
                                     'postedBy': check_none(data.get('creator'), "creator", "name", data)}
                        if dept in all_data.keys():
                            all_data.get(dept).append(meta_data)
                        else:
                            all_data[dept] = []
                            all_data.get(dept).append(meta_data)
                        print("All data is {}".format(all_data))
        with open("solution.json", "w") as outfile:
            json.dump(all_data, outfile)
    except Exception as e:
        print("Error in get_all_url {}".format(e))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url = "https://www.cermati.com/karir"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    myLink = driver.find_element(By.PARTIAL_LINK_TEXT, 'View All Jobs')
    all_jobs_url = myLink.get_attribute('href')
    driver.get(all_jobs_url)
    get_all_data(all_jobs_url)
    driver.close()
