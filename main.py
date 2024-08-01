import re
import random
import os
from moviepy.config import change_settings
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from openai import OpenAI
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import time

class YouTubeSegmentDownloader:
    def __init__(self, api_key, imagemagick_binary_path=r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"):
        self.api_key = api_key
        change_settings({"IMAGEMAGICK_BINARY": imagemagick_binary_path})
        self.client = OpenAI(api_key=self.api_key)
        self.output_path = None



    def segment_transcript(self, full_transcript, max_length=500):
        words = full_transcript.split()  # Split the transcript into words
        segments = []
        current_segment = []

        for word in words:
            current_segment.append(word)
            if len(current_segment) >= max_length:  # Check if the current segment reaches the max_length
                segments.append(" ".join(current_segment))  # Join the words to form a segment
                current_segment = []  # Reset for the next segment

        # Add the last segment if there are any remaining words
        if current_segment:
            segments.append(" ".join(current_segment))

        return segments

    def download_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            formatter = SRTFormatter()
            srt = formatter.format_transcript(transcript)
            transcript_file_path = f"{video_id}_transcript.srt"
            with open(transcript_file_path, "w", encoding="utf-8") as file:
                file.write(srt)
            print(f"Transcript for video ID {video_id} downloaded successfully.")
            return transcript_file_path
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def crop_clip_to_9_16(self, clip):
        target_width = 1080
        target_height = 1920
        clip_aspect_ratio = clip.w / clip.h
        target_aspect_ratio = target_width / target_height

        if clip_aspect_ratio > target_aspect_ratio:
            new_width = int(clip.h * target_aspect_ratio)
            crop_x1 = (clip.w - new_width) // 2
            crop_clip = clip.crop(x1=crop_x1, width=new_width, height=clip.h)
        else:
            new_height = int(clip.w / target_aspect_ratio)
            crop_y1 = (clip.h - new_height) // 2
            crop_clip = clip.crop(y1=crop_y1, width=clip.w, height=new_height)

        return crop_clip.resize(newsize=(target_width, target_height))

    def download_youtube_segment_from_chat_completion(self, youtube_url, transcript_file_path):
        segment_duration = 0
        while segment_duration <= 25:
            with open(transcript_file_path, 'r') as file:
                full_transcript = file.read()

            segments = self.segment_transcript(full_transcript)
            if segments:
                random_segment = random.choice(segments)
                # Splitting the string into words
                words = random_segment.split()

            else:
                print("No segments found.")
                return

            response = self.client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        Your Mission as a YouTube Virality Expert:

                        Your unique talent lies in identifying those golden moments within YouTube videos that are just waiting to become viral sensations. Dive into the provided video script and unearth a 25-30 second clip that encapsulates the essence of clickbait glory. This clip should be the heartbeat of the video, capturing a moment, highlight, or key idea that viewers can't resist clicking on.

                        Instructions:

                        1. Segment Selection: Choose a segment that is at least 25 seconds long but no more than 30 seconds. Ensure it starts and ends with complete sentences or thoughts for smooth viewing. If there's a question that the segment is answering or posing, make sure it's included.

                        2. Title Creation: Craft a click-worthy title for this segment, keeping it under 6 words. Your title should scream "watch me!" Avoid formats like '<title> :/- <sub title>'. Go straight for the jugular with a title that grabs attention. The title should only include words, no unwanted characters.

                        Output Format:

                        Provide your chosen segment in the format: (start-time,___ --> end-time,___)

                        Accompany it with your captivating title encapsulated in curly braces, like so: {Your Clickbait Title Here}

                        Example: (00:41:30,800 --> 00:41:55,020) {How to Get 100 Million Views!}

                        Remember, the magic is in the moment and the title. Unleash your inner clickbait guru and let's make this segment irresistible!
                        """
                    },
                    {
                        "role": "user",
                        "content": random_segment
                    }
                ],
                temperature=0.7,
                max_tokens=64,
                top_p=1
            )

            segment_str = response.choices[0].message.content
            print(segment_str)

            time_pattern = r'\((\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\)'
            match = re.match(time_pattern, segment_str)
            title_pattern = r"\{(.+?)\}"

            # Search for the title using the regular expression
            title_match = re.search(title_pattern, segment_str)
            if title_match:
                title = title_match.group(1)  # Extract the title from the matched pattern
            else:
                print("Title not found or invalid format.")

            if match:
                start_time_str, end_time_str = match.groups()
                start_time = sum(x * float(t) for x, t in zip([3600, 60, 1, 0.001], re.split('[:,]', start_time_str)))
                end_time = sum(x * float(t) for x, t in zip([3600, 60, 1, 0.001], re.split('[:,]', end_time_str)))
            else:
                start_time = 0
                end_time = 0
                print("No match found")

            segment_duration = end_time - start_time

        def get_filename(url, ydl_opts):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return ydl.prepare_filename(info)
        print("Fetching video")
        print(youtube_url)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': '%(title)s.%(ext)s'
        }

        try:
            # Get the filename without downloading
            video_path = get_filename(youtube_url, ydl_opts)

            if os.path.exists(video_path):
                print(f'Video already exists at: {video_path}')
            else:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
                print(f'Video downloaded successfully to: {video_path}')
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        start_time = start_time-1
        print("Cropping")
        # Load the video clip and crop to 9:16 aspect ratio
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        clip_cropped = self.crop_clip_to_9_16(clip)  # Cropping to 9:16


        # Replace spaces with underscores and remove characters that might be invalid for filenames
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title).replace(' ', '_')
        # Format the output path using the title
        output_path = f"{safe_title}.mp4"
        print("Writing video file.")
        # Write the video file using the new output path
        clip_cropped.write_videofile(output_path, codec="libx264")
        self.output_path = output_path
        print(f"Segment saved as {output_path}")
        os.system(f"python captions.py {output_path}")
        time.sleep(20)
        print("Added Captions!")
