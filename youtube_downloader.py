from pytube import YouTube
import concurrent.futures
from tqdm import tqdm
import os

# Global variable to store the progress bars
progress_bars = {}

def progress_function(stream, chunk, bytes_remaining):
    global progress_bars
    file_size = stream.filesize
    bytes_downloaded = file_size - bytes_remaining
    progress_bars[stream].update(len(chunk))

def download_video(video_url, stream_choice, index):
    try:
        yt = YouTube(video_url, on_progress_callback=progress_function)
        stream = yt.streams[stream_choice - 1]
        print(f"Downloading '{stream.title}'...")

        # Get the file size before starting the download
        file_size = stream.filesize

        # Create a tqdm progress bar
        progress_bars[stream] = tqdm(total=file_size, unit='B', unit_scale=True, desc=stream.title, ncols=100)

        # Generate a unique filename
        filename = f'download_{index}_{stream.title}.mp4'
        filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ' or c == '.']).rstrip()

        # Download the video
        stream.download(filename=filename)

        # Close the progress bar
        progress_bars[stream].close()

        print(f"Download of '{stream.title}' complete!")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    video_urls = []
    stream_choices = []

    while True:
        video_url = input("Enter the YouTube video URL (or 'done' to finish entering URLs): ")
        if video_url.lower() == 'done':
            break
        video_urls.append(video_url)

        print("Available video streams:")
        yt = YouTube(video_url)
        streams = yt.streams.filter(progressive=True).all()
        for i, stream in enumerate(streams):
            print(f"{i + 1}. {stream}")
        stream_choice = int(input("Enter the number of the stream you want to download: "))
        stream_choices.append(stream_choice)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for index, (video_url, stream_choice) in enumerate(zip(video_urls, stream_choices), start=1):
            futures.append(executor.submit(download_video, video_url, stream_choice, index))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

    print("All downloads complete!")

if __name__ == "__main__":
    main()
