import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

# Setup headless Chrome browser
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Target Costco URL (Laptops section)
url = "https://www.costco.com/laptops.html"
driver.get(url)

# Scroll to load all products
SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

for _ in range(5):  # Adjust this number to scroll more or less
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Wait until at least one product tile is loaded
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-tile-set"))
    )
except:
    print("❌ Timeout: Products not loaded.")
    driver.quit()
    exit()

# Extract product data
products_data = []

products = driver.find_elements(By.CLASS_NAME, "product-tile-set")
for product in products:
    try:
        title = product.find_element(By.CLASS_NAME, "description").text.strip()
    except:
        title = "N/A"

    try:
        price = product.find_element(By.CLASS_NAME, "price").text.strip()
    except:
        price = "N/A"

    try:
        availability = "In Stock"
        if "out of stock" in product.get_attribute("innerHTML").lower():
            availability = "Out of Stock"
    except:
        availability = "Unknown"

    products_data.append({
        "Product Name": title,
        "Price": price,
        "Availability": availability
    })

driver.quit()

# Save to CSV
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)
df = pd.DataFrame(products_data)
csv_path = os.path.join(output_folder, "costco_products.csv")
df.to_csv(csv_path, index=False)

print(f"\n✅ Data scraped and saved to {csv_path}")
