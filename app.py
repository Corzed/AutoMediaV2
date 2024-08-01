import datetime
import subprocess
from time import sleep

import upload
from main import YouTubeSegmentDownloader
from upload import YouTubeVideoUploader
from dotenv import load_dotenv
import os
import traceback  # For logging stack traces

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
project_path = os.getenv('PROJECT_PATH')

# Check if critical environment variables are missing
if not all([openai_api_key, email, password, project_path]):
    raise ValueError("Critical environment variables are missing. Please check your .env file.")

videos_goal = 30
videos_per_day_goal = 2
scheduled_time_hour1 = 6
AM_PM = "AM"
video_id = "c8VcUnz3nVc"
scheduled_increment = 9
#GfUf5OBbUz4 Starwars
#O6syLHOGwrE Minecraft 1000 Days
#0pmviUS1Zac Neil deGrasse Tyson Interview w/ joe rogan
#vGc4mg5pul4 Neil deGrasse Tyson Interview w/ joe rogan old
#c8VcUnz3nVc colin and samir mrbeast interview

scheduled_time_hour = scheduled_time_hour1
today = datetime.date.today()
target_date = today + datetime.timedelta(days=1)
videos_uploaded = 0
videos_day_uploaded = 0

while videos_uploaded < videos_goal:
    try:
        if videos_day_uploaded >= videos_per_day_goal:
            videos_day_uploaded = 0
            target_date += datetime.timedelta(days=1)
            scheduled_time_hour = scheduled_time_hour1
            AM_PM = "AM"

        date_str = target_date.strftime("%b %d, %Y")

        if scheduled_time_hour >= 12:
            if AM_PM == "AM":
                AM_PM = "PM"
            else:
                AM_PM = "AM"
                target_date += datetime.timedelta(days=1)
                date_str = target_date.strftime("%b %d, %Y")
            scheduled_time_hour = scheduled_time_hour % 12

        scheduled_time = f"{scheduled_time_hour}:00 {AM_PM}"

        print("----------")
        print(date_str)
        print(scheduled_time)
        print("----------")

        api_key = openai_api_key
        downloader = YouTubeSegmentDownloader(api_key)
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        transcript_file_path = downloader.download_transcript(video_id)

        if transcript_file_path:
            downloader.download_youtube_segment_from_chat_completion(youtube_url, transcript_file_path)
            file_path = f"{project_path}{downloader.output_path}"
            uploader = YouTubeVideoUploader(email, password, file_path, date_str, scheduled_time)
            uploader.upload()

            videos_uploaded += 1
            videos_day_uploaded += 1
            scheduled_time_hour += scheduled_increment

        print(f"Uploaded video {videos_uploaded} on {date_str} at {scheduled_time}")
        sleep(2)

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'])
