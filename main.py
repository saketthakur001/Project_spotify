# USING SELENIUM VERSION 4

# Import the selenium webdriver module
from selenium import webdriver
# import the ChromeOptions class
from selenium.webdriver.chrome.options import Options as chromeOptions
# Import the By class for locating elements
from selenium.webdriver.common.by import By
# Import the NoSuchElementException class
from selenium.common.exceptions import NoSuchElementException


# time
import time

# Create a ChromeOptions object
options = webdriver.ChromeOptions()

# Use the default profile name in the user-data-dir argument
# options.add_argument("--user-data-dir=C:\\Users\\saket\\AppData\\Local\\Google\\Chrome\\User Data")

options.add_argument("--user-data-dir=C:\\Temp\\ChromeProfile")

# Create a webdriver object for chrome with the options
driver = webdriver.Chrome(options=options)

# Open the google.com website
# driver.get("https://trakt.tv/dashboard")


''' GOOGLE SEARCH AND CLICKING ON THE FIRST LINK '''

# Assuming the search text is a string
def generate_google_link(search_text):
  # Replace spaces with plus signs
  search_text = search_text.replace(" ", "+")
  # Add the search text to the base url
  base_url = "https://www.google.com/search?q="
  link = base_url + search_text
  # Return the link
  return link

def find_elements_by_class_name(driver, class_name):
    """Finds all elements with class `class_name`."""
    return driver.find_elements(by=By.CLASS_NAME, value=class_name)

def click_first_link(driver):
  """Clicks on the first link element on the page."""
  # Wait for the page to load and the element to be present
  driver.implicitly_wait(3)
  
  # Use a try-except block to handle possible exceptions
  try:
    # Get the first element from the list of elements with class name "yuRUbf"
    first_div = find_elements_by_class_name(driver, "yuRUbf")[0]
    # Find the child element of the div that has the tag name "a" using the find_element method
    first_link = first_div.find_element(By.TAG_NAME, "a")
    # Execute a script to change the target attribute of the link to "_self"
    driver.execute_script("arguments[0].setAttribute('target', '_self')", first_link)
    first_link.click()
    return True
  except IndexError:
    # If no element is found, return False
    return False


def click_heart(driver, value):
  """Clicks on the heart based on a given value."""
  # Check if the value is between 1 and 10
  if not 1 <= value <= 10:
    raise ValueError("Value must be between 1 and 10")
  
  # Use a try-except block to handle possible exceptions
  try:
    # Find the li element that has the class name "summary-user-rating" using the class name locator
    li_element = driver.find_element(By.CLASS_NAME, "summary-user-rating")
    # Click on the li element
    li_element.click()
    # Wait for the popup to be visible using expected conditions
    popup = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "popover")))
    # Find the input element that has the name "rating" and the value equal to the given value using XPath
    input_element = driver.find_element(By.XPATH, f"//input[@name='rating' and @value='{value}']")
    # Click on the input element
    input_element.click()
    return True
  except NoSuchElementException:
    # If the element is not found, return False
    return False



# Assuming the file name is movies.csv
import pandas as pd
df = pd.read_csv(r"C:\Users\saket\Downloads\movielens-ratings.csv")

for i in df['title'][0]:
    # search = 'site:trakt.tv '+i
    # driver.get(generate_google_link(search))
    
    # Call the click_first_link function and store the result in a variable
    # clicked = click_first_link(driver)

    # # If clicked is True, break out of the loop
    # if clicked:
    #     print(f"Link found for {i}")

    #     break
    # else:
    #     # If clicked is False, print a message and continue the loop
    #     print(f"No link found for {i}")
    #     continue

    driver.get("https://trakt.tv/movies/toy-story-5")
    # Find the element by its text content using XPath
    try:
        element = driver.find_element(By.XPATH, "//div[contains(text(), 'Add to history')]")
        # Click on the element
        element.click()
        # Find the li element that has the class name "summary-user-rating" using the class name locator
        li_element = driver.find_element(By.CLASS_NAME, "summary-user-rating")
        # Click on the li element
        # print('clicked')
        # time.sleep(10)
        # li_element.click()
        # Call the click_heart function with the desired value
        # click_heart(driver, 8) # for example
        click_heart(driver, 5)
    except NoSuchElementException:
    # If the element is not found, pass
        # pass
        print('sleeping')
        time.sleep(10)
        break
    break


# Get the title of the page
print(driver.title)

time.sleep(60000)

# Close the driver
driver.close()
