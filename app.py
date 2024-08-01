import datetime
from time import sleep
# Assuming main.py and upload.py are correctly implemented
from main import YouTubeSegmentDownloader
from upload import YouTubeVideoUploader
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the environment variables from `.env` file into the environment

openai_api_key = os.getenv('OPENAI_API_KEY')
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
project_path = os.getenv('PROJECT_PATH')


# Constants and Initial Setup
videos_goal = 3
videos_per_day_goal = 1 #12 max
scheduled_time_hour = 4 #starting time, for example 8, for 8AM
AM_PM = "PM"
video_id = "0pmviUS1Zac"
scheduled_increment = 2

# Initialize date and counters
today = datetime.date.today()
# Start from the next day
target_date = today + datetime.timedelta(days=1)
videos_uploaded = 0
videos_day_uploaded = 0

while videos_uploaded < videos_goal:
    try:
        if videos_day_uploaded >= videos_per_day_goal:
            # Reset daily upload count and move to the next day
            videos_day_uploaded = 0
            target_date += datetime.timedelta(days=1)
            scheduled_time_hour = 4  # Reset upload time for the new day
            AM_PM = "PM"

        # Format date and time for upload
        date_str = target_date.strftime("%b %d, %Y")  # E.g., "Apr 02, 2024"
        if scheduled_time_hour > 11:
            AM_PM = "PM"
        if scheduled_time_hour > 12:
            scheduled_time_hour -= 12  # Convert to 12-hour format
        scheduled_time = f"{scheduled_time_hour}:00{AM_PM}"
        print("----------")
        print(date_str)
        print(scheduled_time)
        print("----------")
        # Your API key, video ID, etc. setup remains the same
        api_key = openai_api_key
        downloader = YouTubeSegmentDownloader(api_key)
        video_id = video_id
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        transcript_file_path = downloader.download_transcript(video_id)

        if transcript_file_path:
            downloader.download_youtube_segment_from_chat_completion(youtube_url, transcript_file_path)
            file_path = fr"{project_path}{downloader.output_path}"
            email = email
            password = password
            uploader = YouTubeVideoUploader(email, password, file_path, date_str, scheduled_time)
            uploader.upload()

            # Increment counters
            videos_uploaded += 1
            videos_day_uploaded += 1
            scheduled_time_hour += scheduled_increment  # Increment for the next video's scheduled time

        print(f"Uploaded video {videos_uploaded} on {date_str} at {scheduled_time}")
        sleep(2)  # Adjust sleep time as needed

    except Exception as e:
        print(f"An error occurred: {e}")




