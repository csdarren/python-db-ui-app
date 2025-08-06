#ruff: noqa: FIX002
# TODO: Remove any occurence of the word ?
# required libraries
from __future__ import annotations

import json
import logging
from email.message import EmailMessage
from pathlib import Path
from smtplib import SMTP

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

import config

# Configure logging
config.logging_setup()

logger = logging.getLogger(__name__)

# directory paths for downloads, screenshots, and the storage_state cache


def send_email(body: str, screenshot_path: Path | None) -> None:
    email_subject = "ERROR - WebScraper"  # Define the email subject that is used here
    sender = config.EMAIL_SENDER
    recipient = [config.EMAIL_ONE, config.EMAIL_TWO]
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = email_subject
    msg.set_content(body)
    if screenshot_path:
        path = Path(screenshot_path)
        if path.exists():
            msg.add_attachment(path.read_bytes(), maintype="image", subtype="png", filename=path.name)
        else:
            logger.info("screenshot path does not exist")
    try:
        with SMTP("mail.smtp2go.com", 25) as smtp:
            logger.info("Sending email")
            smtp.send_message(msg, to_addrs=recipient)
    except Exception as e: # noqa: BLE001
        logger.info("Email failed to send through SMTP, Exception: %s", e)


# function to check if the user is already logged in
def is_login_success(page: Page) -> bool:
    """Checks if the user is already logged in."""

    # navigates to the check_login_url that is previously defined
    page.goto(config.CHECK_LOGIN_URL, wait_until="networkidle")
    try:
        # Looks for ITLOGIN (from .env) on the page
        user_id_element = page.get_by_text(config.ITLOGIN.upper())
        user_id_element.wait_for(state="visible", timeout=5000)
    except PlaywrightTimeoutError:
        return False  # use login verification FAILED, Exiting function

    logger.info("located text %s, Login is confirmed", config.ITLOGIN.upper())
    return True  # user login verification SUCCEEDED, Exiting function


# function to fill in the username textbox and click the submit button
def find_fill_click_username(page: Page) -> bool:
    try:
        # searches the input section for an ID with the name of pwd_userid
        username_textbox_element = page.locator('input[name="pwd_userid"]')
        username_textbox_element.wait_for(state="visible")
        logger.info("username_textbox_element is visible, filling in username")
        # fills the username_textbox_element with ITLOGIN (pulled from .env file in project directory)
        username_textbox_element.fill(config.ITLOGIN)
    except PlaywrightTimeoutError:
        logger.info("username_textbox_element was not found, pausing page")
        ss_path = config.SCREENSHOTS_PATH.joinpath("username_textbox_element_not_found.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email("username_textbox_element is not visible", ss_path)
        page.pause()

    try:
        continue_element = page.get_by_text("Continue")
        continue_element.wait_for(state="visible")  # waits for the continue_element to become visible
        logger.info("continue_element is visible, clicking")
        continue_element.click()
    except PlaywrightTimeoutError:  # if continue_element.wait_for() hits a PlaywrightTimeoutError
        logger.info("continue_element was not found, pausing page")
        ss_path = config.SCREENSHOTS_PATH.joinpath("continue_element_not_found.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email("continue_element was not found, pausing page", ss_path)
        page.pause()
    return True


# function to search the page for the login method element (asks you how you want to login, password/email)
def find_click_login_method(page: Page) -> None:
    try:
        login_method_element = page.locator("li.pwdless_options_section a", has_text="Password")
        login_method_element.wait_for(state="visible")
        logger.info("login_method_element is visible, clicking")
        login_method_element.click()

    except PlaywrightTimeoutError:
        logger.info("login_method_element is not visible, continuing on")
    except Exception:
        logger.exception("Unexpected error")
        page.pause()




# function to fill in and click the password textbox/submit
def find_fill_click_password(page: Page) -> bool:
    try:
        password_textbox_element = page.locator('input[type="password"]')
        password_textbox_element.wait_for(state="visible")
        logger.info("password_textbox_element is visible, filling in password")
        password_textbox_element.fill(config.PASSID)
    except PlaywrightTimeoutError:
        logger.info("password_textbox_element is not visible, pausing page")
        ss_path = config.SCREENSHOTS_PATH.joinpath("login_pass_element_not_found.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email("password_textbox_element is not visible, pausing page", ss_path)
        page.pause()
    except Exception:
        logger.exception("Unexpected error")
        page.pause()

    try:
        login_pass_element = page.get_by_role("button", name="Log in")
        login_pass_element.wait_for(state="visible")
        logger.info("login_pass_element is visible, clicking")
        login_pass_element.click()
    except PlaywrightTimeoutError:
        logger.info("login_pass_element is not visible, pausing page")
        ss_path = config.SCREENSHOTS_PATH.joinpath("login_pass_element_not_found.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email("login_pass_element is not visible, pausing page", ss_path)
        page.pause()
    except Exception:
        logger.exception("Unexpected error")
        page.pause()

    try:
        welcome_element = page.get_by_text(f"Welcome, {config.ACC_HOLDER_NAME}")
        welcome_element.wait_for(state="visible")
        logger.info("welcome_element is visible, continuing")
    except PlaywrightTimeoutError:
        logger.info("welcome_element is not visible")
        ss_path = config.SCREENSHOTS_PATH.joinpath("welcome_element_not_found.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email("welcome_element is not visible", ss_path)
        page.pause()
    except Exception:
        logger.exception("Unexpected error")
        page.pause()
    return True


def failed_login_password(page: Page) -> bool:
    try:
        failed_password_element = page.get_by_text("incorrect values")
        failed_password_element.wait_for(state="visible")
        logger.info("login failed due to incorrect password being entered. Check .env file in project directory")
        ss_path = config.SCREENSHOTS_PATH.joinpath("incorrect_password.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email(
            """Failed to login to the site due to incorrect password
            page has been paused
            change password value in .env to the correct value and re-run the script""",
            ss_path
        )
        page.pause()
    except PlaywrightTimeoutError:
        logger.info("Could not find failed_password_element, continuing to next check")
        ss_path = config.SCREENSHOTS_PATH.joinpath("failed_password_not_found.png")
        page.screenshot(path=ss_path, full_page=True)
    except Exception:
        logger.exception("Unexpected error")
        page.pause()

    try:
        failed_password_lastattempt_element = page.get_by_text("1 more attempt")
        failed_password_lastattempt_element.wait_for(state="visible")
        logger.info("login failed due to incorrect password being entered. Check .env file in project directory")
        ss_path = config.SCREENSHOTS_PATH.joinpath("incorrect_password_last_attempt.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email(
            """Failed to login to the site due to incorrect password
            page has been paused
            change password value in .env to the correct value and re-run the script""",
            ss_path,
        )
        page.pause()
    except PlaywrightTimeoutError:
        logger.info("Could not find failed_password_lastattempt_element, continuing to next check")
        ss_path = config.SCREENSHOTS_PATH.joinpath("failed_password_lastattempt_not_found.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email(
            """Failed to login to the site due to incorrect password
            page has been paused. This is the FINAL ATTEMPT
            change password value in .env to the correct value and re-run the script""",
            ss_path)
    except Exception:
        logger.exception("Unexpected error")
        page.pause()


    try:
        reset_password_element = page.get_by_text("Reset password")
        if reset_password_element.count() == 0:
            return False
        reset_password_element.wait_for(state="visible")
        reset_password_element.click()
        logger.info("Password reset page was found, pausing page for user input")
        ss_path = config.SCREENSHOTS_PATH.joinpath("reset_password.png")
        page.screenshot(path=ss_path, full_page=True)
        send_email(
            """Failed to login to the site due to password reset.
                Needs password reset. Page paused.
                See attached screenshot for more info.""",
            ss_path,
        )
        page.pause()
    except PlaywrightTimeoutError:
        logger.info("reset_password_element is not visible, passed password checks")
    except Exception:
        logger.exception("Unexpected error")
        page.pause()
    return True


def navigate_to_download(page: Page, phone_number: str) -> bool:
    try:
        minutes_used_element = page.get_by_text("Minutes used")
        logger.info("minutes_used_element is visible, clicking")
        minutes_used_element.wait_for(state="visible")
        minutes_used_element.click()
    except PlaywrightTimeoutError:
        logger.info("minutes_used_element is not visible, pausing page")
        ss_path = config.SCREENSHOTS_PATH.joinpath("minutes_used_element_not_found.png")
        page.screenshot(path=ss_path)
        send_email("minutes_used_element is not visible, pausing page", ss_path)
        page.pause()
    except Exception:
        logger.exception("Unexpected error")
        page.pause()

    try:
        view_more_details_element = page.get_by_text("View voice details")
        view_more_details_element.wait_for(state="visible", timeout=5000)
        logger.info("view_more_details_element is visible, clicking")
        view_more_details_element.click()
    except PlaywrightTimeoutError:
        logger.info("Skipping %s, no voice details, assuming 0 minutes", phone_number)
        return False
    except Exception:
        logger.exception("Unexpected error")
        page.pause()
    return True


def download_call_log(page: Page) -> bool:
    with page.expect_download() as download_data:
        download_element = page.get_by_title("Download", exact=True)
        download_element.click()
    download = download_data.value
    suggested_filename = download.suggested_filename
    adjusted_path = suggested_filename.replace("MinutesUsageFor", "")
    final_path = config.src_logs.joinpath(adjusted_path)
    download.save_as(final_path)
    if not final_path.exists():
        logger.error("final_path could not be found: %s", final_path)
        return False
    logger.info("Downloaded %s to %s", adjusted_path, final_path)
    return True


def get_call_log(context: BrowserContext, page: Page) -> None:
    # iterates through each number in the PHONE_NUMBERS list and downloads their voice data into config.src_logs
    for phone_number in config.PHONE_NUMBERS:
        # builds a dynamic url that places each phone_number at the end of the base url
        dynamic_url = config.BASE_URL + config.ACCOUNT_NUMBER + "/" + phone_number
        page.goto(dynamic_url, wait_until="networkidle")  # navigates to the dynamically created url
        if navigate_to_download(page, phone_number):
            if not download_call_log(page):
                logger.error("Failed to download call log exiting get_call_log")
        else:
            logger.error("Failed to navigate to the download page for %s", phone_number)


    save_storage_state(context)

# function that logs into the user, then stores storage state in config.SITECACHE_PATH
def goto_and_login(context: BrowserContext, page: Page) -> None:
    page.goto(config.BASE_LOGIN_URL, wait_until="networkidle")

    # Fill in username, click submit button, wait for networkidle, take final screenshot
    if not find_fill_click_username(page):
        logger.error("find_fill_click_username function failed")

    # Message to future me: If password needs reset, the script silently fails here for some reason, FIX!
    find_click_login_method(page)
    logger.error("find_click_login_method function failed")

    if not find_fill_click_password(page):
        logger.error("find_fill_click_password function failed")

    if not is_login_success(page):
        logger.info("Failed to verify login, checking for failed login")
        if not failed_login_password(page):
            logger.error("failed_login_password function failed")

    logger.info("Login Verification Successfull. Logged in and continuing")
    save_storage_state(context)


def save_storage_state(context: BrowserContext) -> None:
    context.storage_state(path=config.SITECACHE_PATH)
    logger.info("Saved storage state to %s", config.SITECACHE_PATH)


def is_storage_state_valid() -> bool:
    try:  # confirm the json file has usable content (non-empty dictionary or list)
        if not config.SITECACHE_PATH.exists():
            logger.info("Cache file does not exist at path")
            return False
        with Path.open(config.SITECACHE_PATH) as f:
            data = json.load(f)  # loads data to ensure there is data, throws exception if not
            _ = data  # acknowledge and discard data (removes warning)
            logger.info("json data loaded successfully")
            return True
    except (OSError, json.JSONDecodeError):  # Throws exception if json data from storage state is not valid
        logger.info("Cannot decode json data, cache file is invalid")
        return False


def load_browser(pw: Playwright) -> BrowserContext:
    browser = pw.chromium.launch(headless=False, executable_path=config.BROWSER_PATH)
    logger.info("Attempting to load storage state")
    if not is_storage_state_valid():
        logger.info("Cache file was invalid, launching new browser context")
        return browser.new_context()
    logger.info("Cache file was valid, launching new browser context with existing cache")
    return browser.new_context(storage_state=config.SITECACHE_PATH)

def main() -> None:
    with sync_playwright() as pw:  # begins playwright in sync mode

        logger.info("Starting playwright")
        context = load_browser(pw)
        page = context.new_page()  # creates a new page based on the browsers context

        if not is_login_success(page):
            logger.info("login could not be verified, proceeding with normal login")
            goto_and_login(context, page)
        get_call_log(context, page)


if __name__ == "__main__":
    main()
