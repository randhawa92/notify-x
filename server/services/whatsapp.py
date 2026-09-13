# services/whatsapp.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import urllib.parse
import os
import time


# =========================================================
# GLOBAL WHATSAPP DRIVER
# =========================================================

driver = None


# =========================================================
# START WHATSAPP WEB
# =========================================================

def start_whatsapp():

    global driver

    # Already running
    if driver is not None:
        try:
            _ = driver.current_url
            print("WhatsApp driver already running.")
            return True

        except Exception:
            driver = None

    try:

        options = Options()

        # -------------------------------------------------
        # RENDER / LINUX COMPATIBILITY
        # -------------------------------------------------

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--window-size=1920,1080")

        # -------------------------------------------------
        # WhatsApp profile
        # -------------------------------------------------

        profile_path = os.path.join(
            os.getcwd(),
            "whatsapp_profile"
        )

        os.makedirs(
            profile_path,
            exist_ok=True
        )

        options.add_argument(
            f"--user-data-dir={profile_path}"
        )

        # -------------------------------------------------
        # Chrome
        # -------------------------------------------------

        driver = webdriver.Chrome(
            options=options
        )

        driver.get(
            "https://web.whatsapp.com"
        )

        print("\n======================================")
        print("        NOTIFYX WHATSAPP")
        print("======================================")
        print("WhatsApp Web opened.")
        print("Waiting for WhatsApp Web...")
        print("======================================\n")

        time.sleep(5)

        return True

    except Exception as e:

        print(
            "WhatsApp Start Error:",
            repr(e)
        )

        driver = None

        return False


# =========================================================
# NORMALIZE PHONE NUMBER
# =========================================================

def normalize_phone(phone):

    if phone is None:
        return ""

    phone = str(phone).strip()

    # Excel converts numbers to 1234567890.0
    if phone.endswith(".0"):
        phone = phone[:-2]

    # Remove formatting
    phone = (
        phone
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # Remove +
    if phone.startswith("+"):
        phone = phone[1:]

    return phone


# =========================================================
# CHECK DRIVER
# =========================================================

def is_driver_alive():

    global driver

    if driver is None:
        return False

    try:

        _ = driver.current_url

        return True

    except Exception:

        return False


# =========================================================
# WAIT FOR WHATSAPP
# =========================================================

def wait_for_whatsapp(timeout=40):

    global driver

    if driver is None:
        return False

    try:

        wait = WebDriverWait(
            driver,
            timeout
        )

        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        print("WhatsApp page loaded.")

        return True

    except Exception as e:

        print(
            "WhatsApp Loading Error:",
            repr(e)
        )

        return False


# =========================================================
# CHECK LOGIN STATUS
# =========================================================

def check_whatsapp_login(timeout=10):

    global driver

    if driver is None:
        return False

    try:

        wait = WebDriverWait(
            driver,
            timeout
        )

        # Chat list / search box normally appears after login
        selectors = [
            "//div[@contenteditable='true']",
            "//div[@role='textbox']",
            "//button[@aria-label='Search']",
        ]

        for selector in selectors:

            try:

                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, selector)
                    )
                )

                print(
                    "WhatsApp login/session appears active."
                )

                return True

            except Exception:
                continue

        print(
            "WhatsApp login/session not detected."
        )

        return False

    except Exception as e:

        print(
            "Login Check Error:",
            repr(e)
        )

        return False


# =========================================================
# OPEN CHAT
# =========================================================

def open_chat(phone, message):

    global driver

    encoded_message = urllib.parse.quote(
        message
    )

    url = (
        "https://web.whatsapp.com/send?"
        f"phone={phone}"
        f"&text={encoded_message}"
    )

    print(
        f"Opening WhatsApp chat for {phone}"
    )

    driver.get(url)

    time.sleep(3)

    return wait_for_whatsapp(40)


# =========================================================
# FIND MESSAGE BOX
# =========================================================

def find_message_box(timeout=30):

    global driver

    if driver is None:
        return None

    wait = WebDriverWait(
        driver,
        timeout
    )

    selectors = [

        # Current WhatsApp Web composer
        "//div[@contenteditable='true']"
        "[@data-tab]",

        # Generic composer
        "//div[@contenteditable='true']",

        # Role textbox fallback
        "//div[@role='textbox']"

    ]

    for selector in selectors:

        try:

            element = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, selector)
                )
            )

            if element.is_displayed():

                return element

        except Exception:
            continue

    return None


# =========================================================
# SEND SINGLE MESSAGE
# =========================================================

def send_whatsapp(phone, message):

    global driver

    try:

        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        phone = normalize_phone(phone)

        if not phone:

            print(
                "WhatsApp Error: Phone number missing."
            )

            return False

        # -------------------------------------------------
        # MESSAGE
        # -------------------------------------------------

        if message is None:

            print(
                "WhatsApp Error: Message missing."
            )

            return False

        message = str(message).strip()

        if not message:

            print(
                "WhatsApp Error: Message is empty."
            )

            return False

        # -------------------------------------------------
        # START DRIVER
        # -------------------------------------------------

        if not is_driver_alive():

            driver = None

            if not start_whatsapp():

                print(
                    "Could not start WhatsApp driver."
                )

                return False

        # -------------------------------------------------
        # OPEN WHATSAPP
        # -------------------------------------------------

        if not wait_for_whatsapp(40):

            print(
                "WhatsApp Web did not load."
            )

            return False

        # -------------------------------------------------
        # OPEN CHAT
        # -------------------------------------------------

        if not open_chat(
            phone,
            message
        ):

            print(
                "Could not open WhatsApp chat."
            )

            return False

        # -------------------------------------------------
        # CHECK SESSION
        # -------------------------------------------------

        time.sleep(2)

        # -------------------------------------------------
        # FIND COMPOSER
        # -------------------------------------------------

        composer = find_message_box(
            timeout=30
        )

        if composer is None:

            print(
                "Message composer not found."
            )

            print(
                "Current URL:",
                driver.current_url
            )

            return False

        # -------------------------------------------------
        # SEND
        # -------------------------------------------------

        composer.click()

        time.sleep(0.5)

        composer.send_keys(
            Keys.ENTER
        )

        # Give WhatsApp time to process
        time.sleep(2)

        print(
            f"Message Sent Successfully ✅ "
            f"→ {phone}"
        )

        return True

    except Exception as e:

        print(
            f"WhatsApp Send Error for {phone}:",
            repr(e)
        )

        return False


# =========================================================
# CLOSE WHATSAPP
# =========================================================

def close_whatsapp():

    global driver

    try:

        if driver is not None:

            driver.quit()

            driver = None

            print(
                "NotifyX WhatsApp session closed."
            )

        return True

    except Exception as e:

        print(
            "WhatsApp Close Error:",
            repr(e)
        )

        driver = None

        return False