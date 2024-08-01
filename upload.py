from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import subprocess
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the environment variables from `.env` file into the environment
chrome_profile = os.getenv('CHROME_PROFILE_PATH')



class YouTubeVideoUploader:
    def __init__(self, email, password, file_path, date, time):
        self.email = email
        self.password = password
        self.file_path = file_path
        self.time = time
        self.date = date
        self.driver = None

    def setup_driver(self):

        print("Starting driver setup...")
        # Setup Chrome options as needed, e.g., for headless mode
        chrome_options = Options()
        # Uncomment the next line to run in headless mode
        # chrome_options.add_argument("--headless")
        print("Configuring Chrome options...")
        os.remove(self.file_path)
        os.rename('output_video.mp4', self.file_path)
        # Specifying the path to the user's Chrome profile
        user_profile_path = chrome_profile
        chrome_options.add_argument(f'user-data-dir={user_profile_path}')
        print(f"Chrome profile path set to: {user_profile_path}")

        # Initialize undetected_chromedriver with the specified options
        print("Initializing Chrome driver...")
        self.driver = uc.Chrome(options=chrome_options)
        print("Chrome driver setup completed.")

    def login_to_google(self):
        self.driver.get("https://accounts.google.com/signin")
        email_input = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "identifierId")))
        email_input.click()
        email_input.send_keys(self.email)
        sleep(10)
        next_button = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "identifierNext")))
        next_button.click()
        sleep(20)
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.NAME, "Passwd")))
        password_input = self.driver.find_element(By.NAME, "Passwd")
        password_input.send_keys(self.password)
        pass_next_button = WebDriverWait(self.driver, 100).until(
            EC.presence_of_element_located((By.ID, "passwordNext")))
        pass_next_button.click()

    def upload_video(self):
        print("Starting the upload process...")
        sleep(5)
        print("Navigating to YouTube Studio...")
        self.driver.get("https://studio.youtube.com")
        sleep(10)

        print("Looking for the Create button...")
        create_button = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "create-icon")))
        print("Clicking the Create button...")
        create_button.click()
        sleep(3)

        print("Looking for the Upload Videos option...")
        upload_videos = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "text-item-0")))
        print("Clicking the Upload Videos option...")
        upload_videos.click()

        print("Looking for the file upload element...")
        file_upload = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.NAME, "Filedata")))
        print(f"Uploading the file from path: {self.file_path}")
        file_upload.send_keys(self.file_path)

        sleep(10)
        print("Looking for the Next button...")
        next_btn = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "next-button")))
        for _ in range(3):  # Click next button three times
            print("Clicking Next button...")
            next_btn.click()
            self.driver.implicitly_wait(1)
        #sleep(60)

        print("Trying to schedule...")
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="second-container-expand-button"]/tp-yt-iron-icon'))).click()
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="datepicker-trigger"]/ytcp-dropdown-trigger'))).click()
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))).clear()
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))).send_keys(self.date)
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))).send_keys(Keys.ENTER)
        sleep(5)
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))).click()
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))).clear()

        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))).send_keys(self.time)

        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located(
            (By.XPATH,
             '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/div[2]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'))).send_keys(Keys.ENTER)
        print("Looking for the Done button...")
        DONE = WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "done-button")))
        print("Clicking the Done button to finish upload...")
        DONE.click()
        print("Upload process completed.")

    def quit_driver(self):
        print("Closing the Selenium WebDriver session...")
        self.driver.close()
        print("Quitting the driver and closing all associated windows...")
        self.driver.quit()

        print("Attempting to kill any remaining Chrome processes...")
        subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'])
        print("Chrome processes terminated.")

    def login_to_google_with_retry(self, attempts=3):
        for attempt in range(attempts):
            try:
                print(f"Attempt {attempt + 1} of {attempts}")
                self.login_to_google()
                print("Success!")
                break  # If login_to_google succeeds, exit the loop
            except WebDriverException as e:
                print(f"Login attempt failed: {e}")
                if attempt < attempts - 1:
                    print("Retrying...")
                else:
                    raise  # Re-raise the last exception if all attempts fail

    def upload(self):
        print("[INFO] Initializing the WebDriver and setting up the browser...")
        self.setup_driver()
        print("[INFO] WebDriver setup complete. Browser is ready.")

        # Including a delay here can help ensure that any necessary resources are loaded. Adjust as needed.
        sleep(5)

        # This section is commented out, but if you decide to implement login functionality, it can be useful.
        # print("[INFO] Attempting to log in to Google...")
        # self.login_to_google_with_retry()
        # print("[INFO] Login successful.")

        print("[INFO] Starting the video upload process. This may take some time depending on the video size...")
        self.upload_video()
        print("[SUCCESS] Video upload completed successfully.")

        # It's often a good idea to include a brief pause here to ensure all tasks are fully complete before closing.
        sleep(5)

        print("[INFO] Closing the browser and quitting the driver. Please wait...")
        self.quit_driver()
        print("[COMPLETE] Process finished. The driver has been successfully terminated.")