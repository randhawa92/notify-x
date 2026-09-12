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
            return True

        except Exception:
            driver = None

    try:

        options = Options()

        # -------------------------------------------------
        # Dedicated NotifyX WhatsApp profile
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

        options.add_argument(
            "--start-maximized"
        )

        # -------------------------------------------------
        # Start Chrome
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
        print("Scan QR if required.")
        print("Waiting for WhatsApp Web...")
        print("======================================\n")

        # Small initial wait only
        time.sleep(2)

        return True

    except Exception as e:

        print(
            "WhatsApp Start Error:",
            e
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

    # Excel may convert numbers to 1234567890.0
    if phone.endswith(".0"):
        phone = phone[:-2]

    # Remove common formatting
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

def wait_for_whatsapp(timeout=30):

    global driver

    if driver is None:
        return False

    try:

        wait = WebDriverWait(
            driver,
            timeout
        )

        # Wait until page body exists
        wait.until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        return True

    except Exception as e:

        print(
            "WhatsApp Loading Error:",
            e
        )

        return False


# =========================================================
# WAIT FOR CHAT PAGE
# =========================================================

def wait_for_chat(timeout=30):

    global driver

    if driver is None:
        return False

    try:

        wait = WebDriverWait(
            driver,
            timeout
        )

        # Wait until the URL is no longer just WhatsApp home
        wait.until(
            lambda d: "/send" in d.current_url
            or "chat" in d.current_url
            or "web.whatsapp.com" in d.current_url
        )

        return True

    except Exception:

        return False


# =========================================================
# SEND SINGLE WHATSAPP MESSAGE
# =========================================================

def send_whatsapp(phone, message):

    global driver

    try:

        # -------------------------------------------------
        # Validate phone
        # -------------------------------------------------

        phone = normalize_phone(phone)

        if not phone:

            print(
                "WhatsApp Error: "
                "Phone number missing."
            )

            return False

        # -------------------------------------------------
        # Validate message
        # -------------------------------------------------

        if message is None:

            print(
                "WhatsApp Error: "
                "Message missing."
            )

            return False

        message = str(
            message
        ).strip()

        if not message:

            print(
                "WhatsApp Error: "
                "Message is empty."
            )

            return False

        # -------------------------------------------------
        # Start WhatsApp if required
        # -------------------------------------------------

        if not is_driver_alive():

            driver = None

            if not start_whatsapp():
                return False

        # -------------------------------------------------
        # Encode message
        # -------------------------------------------------

        encoded_message = urllib.parse.quote(
            message
        )

        # -------------------------------------------------
        # WhatsApp chat URL
        # -------------------------------------------------

        url = (
            "https://web.whatsapp.com/send?"
            f"phone={phone}"
            f"&text={encoded_message}"
        )

        print("\n--------------------------------------")
        print("NotifyX → WhatsApp")
        print(f"Recipient: {phone}")
        print("--------------------------------------")

        # -------------------------------------------------
        # Open chat
        # -------------------------------------------------

        driver.get(url)

        # -------------------------------------------------
        # Wait for WhatsApp page
        # -------------------------------------------------

        if not wait_for_whatsapp():

            print(
                "Unable to load WhatsApp."
            )

            return False

        # -------------------------------------------------
        # Wait for chat navigation
        # -------------------------------------------------

        wait_for_chat()

        # -------------------------------------------------
        # Find message composer
        # -------------------------------------------------

        wait = WebDriverWait(
            driver,
            20
        )

        composer = None

        try:

            composer = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@contenteditable='true']"
                    )
                )
            )

        except Exception:

            # Fallback: use body
            try:

                composer = driver.find_element(
                    By.TAG_NAME,
                    "body"
                )

            except Exception:

                print(
                    "Message composer not found."
                )

                return False

        # -------------------------------------------------
        # Send message
        # -------------------------------------------------

        composer.send_keys(
            Keys.ENTER
        )

        # -------------------------------------------------
        # Very small confirmation wait
        # -------------------------------------------------

        time.sleep(0.5)

        print(
            "Message Sent Successfully ✅"
        )

        return True

    except Exception as e:

        print(
            f"WhatsApp Send Error "
            f"for {phone}:",
            e
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
            e
        )

        driver = None

        return False