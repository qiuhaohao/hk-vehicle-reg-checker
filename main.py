from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import click
import re
from datetime import datetime
import os
from pathlib import Path

def setup_driver(headless=False):
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    
    # Set up the Chrome driver with automatic driver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def open_query_page(headless=False):
    try:
        driver = setup_driver(headless)
        driver.get("https://www.gov.hk/en/apps/tdvehicleregmark.htm")
        wait = WebDriverWait(driver, 30)
        wait.until(lambda driver: "repoes/td-es-app515/Instruction.do" in driver.current_url)
        submit_form(driver)
        
        print("Successfully reached the target page!")
        return driver
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

def submit_form(driver):
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//form[1]")))
        driver.execute_script("document.forms[0].submit()")
    except Exception as e:
        print(f"An error occurred while submitting the form: {str(e)}")

def query(driver, prefix, digit):
    try:
        wait = WebDriverWait(driver, 10)
        prefix_input = wait.until(EC.presence_of_element_located((By.ID, "rmPrefixId")))
        digit_input = wait.until(EC.presence_of_element_located((By.ID, "rmDigitId")))

        prefix_input.clear()
        prefix_input.send_keys(prefix)
        
        digit_input.clear()
        digit_input.send_keys(digit)
        
        submit_form(driver)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Checking Result')]")))
        
    except Exception as e:
        print(f"An error occurred while populating the form: {str(e)}")
        
def navigate_to_new_search(driver):
    try:
        driver.execute_script("window.location.href='/repoes/td-es-app515/InputEnquireTVRM.do'")
    except Exception as e:
        print(f"An error occurred while navigating to New Search: {str(e)}")

def validate_plate_number(plate):
    pattern = r'^[A-Z]{2}\d{4}$'
    return re.match(pattern, plate) is not None

def is_prefix_available(prefix):
    invalid_prefixes = {'AM', 'LC', 'ZG', 'ZV', 'ZW', 'ZX', 'ZY', 'ZZ'}
    if prefix in invalid_prefixes:
        return False
    if 'I' in prefix or 'O' in prefix or 'Q' in prefix:
        return False
    return True

def plate_to_string(plate):
    return f"{plate['prefix']}{plate['digits']}"

def save_page_content(driver, plate, output_dir):
    filename = f"{plate_to_string(plate)}.html"
    filepath = Path(output_dir) / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f"Saved result to {filepath}")

@click.command()
@click.argument('plates', nargs=-1, required=True)
@click.option('--output', '-o', default='output', 
              help='Directory to save HTML results', 
              type=click.Path())
@click.option('--skip-unavailable', is_flag=True,
              help='Skip checking plates that are not available for reservation')
@click.option('--headless', is_flag=True,
              help='Run Chrome in headless mode')
def main(plates, output, skip_unavailable, headless):
    """Query vehicle registration marks and save results.
    
    PLATES: One or more plate numbers in format XX9999 (e.g., BD8374 ZZ1234)
    """
    # Validate all plates first
    invalid_plates = [p for p in plates if not validate_plate_number(p)]
    if invalid_plates:
        click.echo(f"Error: Invalid plate format: {', '.join(invalid_plates)}")
        click.echo("Plate numbers must be in format XX9999 (e.g., BD8374)")
        return
    
    parsed_plates = [{'prefix': p[:2], 'digits': p[2:]} for p in plates]
    unavailable_plates = [p for p in parsed_plates if not is_prefix_available(p['prefix'])]
    if unavailable_plates:
        unavailable_plates_str = ', '.join([plate_to_string(p) for p in unavailable_plates])
        if skip_unavailable:
            click.echo(f"Skipping plate numbers with unavailable prefixes: {unavailable_plates_str}")
        else:
            click.echo(f"Error: Plate numbers with unavailable prefixes: {unavailable_plates_str}")
            return
    
    available_plates = [p for p in parsed_plates if is_prefix_available(p['prefix'])]

    print(f"Querying {len(available_plates)} plates")
    
    os.makedirs(output, exist_ok=True)

    driver = open_query_page(headless)
    if driver:
        try:
            for _, plate in enumerate(available_plates):
                query(driver, plate['prefix'], plate['digits'])
                save_page_content(driver, plate, output)
                navigate_to_new_search(driver)
        finally:
            driver.quit()

if __name__ == "__main__":
    main()