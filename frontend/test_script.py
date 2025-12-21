from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize WebDriver
driver = webdriver.Chrome()
driver.maximize_window()

# Step 1: Open IRCTC website
driver.get("https://www.irctc.co.in/nget/train-search")

# Step 2: Wait for elements to load
wait = WebDriverWait(driver, 10)

# Step 3: Enter From Station
from_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='From*']")))
from_input.send_keys("Mumbai")
time.sleep(1)
from_input.send_keys(Keys.ENTER)

# Step 4: Enter To Station
to_input = driver.find_element(By.XPATH, "//input[@placeholder='To*']")
to_input.send_keys("Delhi")
time.sleep(1)
to_input.send_keys(Keys.ENTER)

# Step 5: Pick a date (select future date)
date_picker = driver.find_element(By.XPATH, "//input[@placeholder='Journey Date(dd-mm-yyyy)*']")
date_picker.click()
# You may need to handle calendar widget depending on site's structure
# Example: choose 15 days ahead
date_picker.send_keys("20-10-2025")
date_picker.send_keys(Keys.ENTER)

# Step 6: Click on Search button
search_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Search')]")
search_btn.click()

# Step 7: Verify results are shown
try:
    results = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'train_avl_enq_box')]")))
    print("✅ Train results displayed successfully.")
except:
    print("❌ Train results not displayed or search failed.")

# Close browser
driver.quit()
