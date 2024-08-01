import ffmpeg
import whisper
import sys
import os


def extract_audio(video_path, audio_path):
    """
    Extract the audio from the video using FFmpeg.
    """
    ffmpeg.input(video_path).output(audio_path, acodec='pcm_s16le', ac=1, ar='16k').run(overwrite_output=True)


def generate_captions(audio_path):
    """
    Generate captions from the audio file using Whisper, including timestamps.
    """
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="English", task="transcribe_with_timestamps")
    return result['segments']


def create_subtitle_file(segments, subtitle_path):
    """
    Create a subtitle file in SRT format from the Whisper segments with limited words per subtitle.
    Each pair of words will get a proportionate amount of time based on the total duration of the segment.
    """
    with open(subtitle_path, 'w', encoding='utf-8') as f:
        index = 1
        for segment in segments:
            words = segment['text'].split()
            num_pairs = (len(words) + 1) // 2
            segment_duration = segment['end'] - segment['start']
            pair_duration = segment_duration / num_pairs

            for i in range(0, len(words), 2):
                start_time = segment['start'] + i // 2 * pair_duration
                end_time = start_time + pair_duration
                text = " ".join(words[i:i + 2])
                f.write(f"{index}\n{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n{text}\n\n")
                index += 1


def format_timestamp(seconds):
    """
    Format the timestamp from seconds to SRT format.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:06.3f}".replace('.', ',')


def burn_subtitles(video_path, subtitle_path, output_video_path, font_path):
    """
    Burn subtitles into the video using FFmpeg, with custom font settings and enhanced black outline.
    """
    subtitle_filter = (
        f"subtitles={subtitle_path}:force_style='Alignment=10,FontName=TheBoldFont-Bold,"
        f"FontSize=15.5,PrimaryColour=&H00ffffff,OutlineColour=&H00000000,"
        f"BorderStyle=1,Outline=1.3,Shadow=0'"  # Increase `Outline` as needed for thicker borders
    )
    ffmpeg.input(video_path).output(
        output_video_path,
        vf=subtitle_filter
    ).run(overwrite_output=True)


def main(video_path):
    audio_path = 'temp_audio.wav'
    subtitle_path = 'temp_subtitles.srt'
    output_video_path = 'output_video.mp4'
    font_path = "/path/to/your/font.ttf"  # Adjust this path to your font file location

    try:
        # Extract audio from video
        extract_audio(video_path, audio_path)

        # Generate captions including timestamps
        segments = generate_captions(audio_path)

        # Create a subtitle file with limited words
        create_subtitle_file(segments, subtitle_path)

        # Burn subtitles into the video, using custom font
        burn_subtitles(video_path, subtitle_path, output_video_path, font_path)
        print("Process completed. Subtitled video is available at:", output_video_path)
    except Exception as e:
        print("Error processing the video:", e)
    finally:
        # Cleanup temporary files
        try:
            os.remove(audio_path)
            os.remove(subtitle_path)
        except Exception as e:
            print("Error removing temporary files:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <path_to_video>")
    else:
        video_path = sys.argv[1]
        main(video_path)
