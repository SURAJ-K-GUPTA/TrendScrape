import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Webshare API token from .env file
WEBSHARE_TOKEN = os.getenv("WEBSHARE_TOKEN")

# ChromeDriver path
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
EMAIL = os.getenv("EMAIL")

# Get free proxy from Webshare API
def get_proxy():
    print("Getting proxy...")
    try:
        response = requests.get(
            "https://proxy.webshare.io/api/v2/proxy/list/",
            headers={"Authorization": f"Token {WEBSHARE_TOKEN}"},
            params={"mode": "backbone"}  # Use direct proxy mode
        )
        if response.status_code == 200:
            proxies = response.json().get("results", [])
            if proxies:
                # Filter for valid proxies
                valid_proxies = [proxy for proxy in proxies if proxy.get("valid", False)]
                if valid_proxies:
                    # Use the first valid proxy
                    proxy = valid_proxies[0]
                    proxy_address = proxy["proxy_address"]
                    port = proxy["port"]
                    username = proxy["username"]
                    password = proxy["password"]
                    proxy_url = f"{username}:{password}@{proxy_address}:{port}"
                    print(f"Using proxy: {proxy_url}")
                    return proxy_url
                else:
                    print("No valid proxies found.")
            else:
                print("No proxies returned in the response.")
        else:
            print(f"Failed to fetch proxies. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error while fetching proxy: {e}")
    return None

# Setup WebDriver
def setup_driver(proxy):
    print("Setting up WebDriver...")
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # Optional: Remove for GUI
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    print(f"Using proxy: {proxy}")
    # chrome_options.add_argument('--proxy-server=%s' % proxy)
    # chrome_options.add_argument(f"--proxy-server=https://{proxy}")
    print("Starting WebDriver...")
    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("WebDriver started.")
    return driver


# Fetch Twitter trends
def fetch_twitter_trends():
    print("Fetching Twitter trends...")
    # proxy = get_proxy()
    proxy="rhmaedjk-1:mhffz6nv0ook@107.172.163.27:10000"
    if not proxy:
        print("Failed to get a proxy. Exiting.")
        return None

    print(f"Using proxy: {proxy}")
    driver = setup_driver(proxy)

    try:
        print("Opening Twitter...")
        driver.get("https://x.com/i/flow/login")

        # Wait for the login form
        print("Waiting for login form...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        print("Textbox located")

        # Log in to Twitter
        username_field = driver.find_element(By.NAME, "text")
        username_field.send_keys("setubazaar@gmail.com")
        time.sleep(2)

        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'css-1jxf684') and text()='Next']"))
        )
        next_button.click()

        # Handle unusual activity check if present
        try:
            unusual_activity_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            if unusual_activity_element:
                print("Unusual activity form located")
                unusual_activity_element.send_keys("SETUBAZAAR")
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                next_button.click()
        except Exception as e:
            print("Unusual activity form not found, proceeding.")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        print("Password field located")

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(PASSWORD)
        time.sleep(2)

        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'css-1jxf684') and text()='Log in']"))
        )
        login_button.click()

        time.sleep(5)  # Allow time for redirection
        current_url = driver.current_url
        print(f"Current URL: {current_url}")

        # Check if the user is already on the home page
        if "x.com/home" not in current_url:
            print("Navigating to home...")
            driver.get("https://x.com/home")
        else:
            print("Already on the home page.")


        # Wait for trends section
        print("Waiting for trends section...")
        trends_section = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-175oi2r.r-kemksi.r-1kqtdi0.r-1867qdf.r-1phboty.r-rs99b7.r-1ifxtd0.r-1udh08x"))
        )

        if not trends_section:
            print("Trends section not found. Exiting.")
            return {"trends": [], "proxy_used": "Unknown"}

        print("Trends section located")
        elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-175oi2r.r-kemksi.r-1kqtdi0.r-1867qdf.r-1phboty.r-rs99b7.r-1ifxtd0.r-1udh08x')
        time.sleep(5)
        # Parse the HTML
        html_content = "".join([element.get_attribute('outerHTML') for element in elements])
        soup = BeautifulSoup(html_content, 'html.parser')
        trends = soup.find_all('div', {'data-testid': 'trend'})

        # Extract the trend names
        trending_topics = []
        for trend in trends:
            trend_name = trend.find('div', {'class': 'r-a023e6'})
            if trend_name:
                span = trend_name.find('span')
                if span:
                    trending_topics.append(span.text)

        print("Top 5 trends fetched successfully:", trending_topics)
        return {"trends": trending_topics, "proxy_used": proxy}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"trends": [], "proxy_used": "Unknown"}
    
    finally:
        driver.quit()
        
if __name__ == "__main__":
    result = fetch_twitter_trends()
    if result:
        print("Result:", result)
