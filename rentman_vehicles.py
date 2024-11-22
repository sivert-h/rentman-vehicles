from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import traceback
import os

load_dotenv()
TAB_COUNT = int(os.getenv('TAB_COUNT'))
home_dir = os.path.expanduser("~")  # Expands to the user's home directory

# Setup Chrome options for kiosk mode
chrome_options = Options()
chrome_options.add_argument("--app=https://rentmanapp.com/login")  # Opens in App Mode without URL bar or tabs
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Disable "controlled by automated software" infobar
chrome_options.add_argument(f"user-data-dir={os.path.join(home_dir, '.config/google-chrome')}")
chrome_options.add_argument("profile-directory=Default")  # Use "Profile X" if you have multiple profiles
chrome_options.add_argument("--window-position=0,1270")  # Replace with desired x,y coordinates
chrome_options.add_argument("--window-size=1080,650")  # Replace with desired width and height


# Initialize the Chrome WebDriver with options and service
driver = webdriver.Chrome(options=chrome_options)

def is_logged_in():
    """Check if already logged in by verifying if the URL contains 'dashboard'."""
    time.sleep(5)  # Brief pause to allow potential redirection
    return "dashboard" in driver.current_url

def login():
    try:
        driver.get("https://rentmanapp.com/login")

        wait = WebDriverWait(driver, 20)

        # Enter username
        username_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        username_field.send_keys(Keys.CONTROL + "a")  # Select all text
        username_field.send_keys(Keys.BACKSPACE)     # Delete the text
        username_field.send_keys(os.getenv('RENTMAN_USERNAME'))  # Use environment variable

        # Enter password
        password_field = driver.find_element(By.ID, "password")
        #password_field.clear()  # Clear any existing text
        password_field.send_keys(os.getenv('RENTMAN_PASSWORD'))  # Use environment variable

        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[normalize-space()='Login']")
        login_button.click()

        #wait = WebDriverWait(driver, 20)
        time.sleep(20)

         # Log in to workspace
        login_button = driver.find_element(By.XPATH, "//button[normalize-space()='Log in']")
        login_button.click()

        # Wait for login to complete
        wait.until(EC.url_contains('/dashboard'))

    except Exception as e:
        traceback.print_exc()
        driver.quit()
        exit()

def load_page(tab_count):
    try:
        driver.get("about:blank")
        time.sleep(1)

        # Calculate today's date and the date 3 days from today
        today = datetime.today()
        date_three_days = today + timedelta(days=3)

        # Format the dates as strings in 'YYYY-MM-DD' format
        date_format = '%Y-%m-%d'
        today_str = today.strftime(date_format)
        date_three_days_str = date_three_days.strftime(date_format)

        # Construct the URL with the dynamic dates
        base_url = 'https://audionor.rentmanapp.com/#/transport'
        date_param = f"?dates={today_str}_{date_three_days_str}"
        url = base_url + date_param

        # Load the webpage with dynamic dates
        driver.get(url)

        # Wait for the page to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(2)

        # Send "Tab" key the specified number of times
        for _ in range(tab_count):
            driver.switch_to.active_element.send_keys(Keys.TAB)
            time.sleep(0.1)  # Slight delay between tabs

        # Send "Space" key to select the checkbox
        driver.switch_to.active_element.send_keys(Keys.SPACE)
        time.sleep(1)  # Wait for the action to register

        # Remove elements from webpage
        driver.execute_script("""
        // Hide the .rm-top-bar__main element
        var topBar = document.querySelector('.rm-top-bar__main');
        if (topBar) {
            topBar.style.display = 'none';
        }

        // Hide the .rm-filters-bar__filters-container element
        var filtersBar = document.querySelector('.rm-filters-bar__filters-container');
        if (filtersBar) {
            filtersBar.style.display = 'none';
        }

        // Hide the first rm-split-pane element
        var splitPane = document.querySelector('.rm-split-pane-container--vertical > rm-split-pane:nth-child(1)');
        if (splitPane) {
            splitPane.style.display = 'none';
        }

        // Hide the .rm-split-pane-container__gutter element
        var gutter = document.querySelector('.rm-split-pane-container__gutter');
        if (gutter) {
            gutter.style.display = 'none';
        }
        """)

    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    driver.get("https://rentmanapp.com/login")

    # Check if already logged in
    if is_logged_in():
        print("Already logged in. Redirecting to target page...")
    else:
        print("Not logged in. Performing login steps...")
        login()

    while True:
        load_page(TAB_COUNT)
        time.sleep(3600)
        print("Reloading page")
