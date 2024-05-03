import os
from youtube_search import YoutubeSearch
from pytube import YouTube
import cv2
import pytesseract
from PIL import Image
import contextlib

def ie(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
    return wrapper

# Function to search for videos on YouTube
def search_videos(query):
    results = YoutubeSearch(query, max_results=5).to_dict()
    return results

# Function to download the video
@ie
def download_video(video_id):
    yt = YouTube(f'http://www.youtube.com/watch?v={video_id}')
    yt.streams.filter(file_extension='mp4').first().download(filename='video.mp4')

# Function to play the video with ASCII art
def play_video():
    if not os.path.exists('video.mp4'):
        print("Error: Video file not found.")
        return

    # Open video stream
    video = cv2.VideoCapture('video.mp4')
    # Get console dimensions
    console_width = os.get_terminal_size().columns
    console_height = os.get_terminal_size().lines - 3  # Leave space for controls
    while video.isOpened():
        # Read frame from the video
        ret, frame = video.read()
        if ret:
            # Replace text in the frame with ASCII art
            text = replace_text_with_ascii(frame)
            # Convert frame to ASCII art
            ascii_frame = frame_to_ascii(frame, console_width, console_height)
            # Clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            # Print ASCII art frame
            print("Playing Video!")
            print("Text on screen:")
            print(text)
            print("Video ASCII art: ")
            print(ascii_frame)
            # Wait for a short duration (adjust to control frame rate)
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break
        else:
            break
    video.release()

# Function to convert a grayscale pixel value to ASCII character
def pixel_to_ascii(pixel_value):
    ascii_chars = '@%#*+=-:. '
    index = int(pixel_value[0] / 255 * len(ascii_chars))
    index = max(0, min(index, len(ascii_chars) - 1))  # Ensure index is within range
    return ascii_chars[index]

# Function to convert a frame to ASCII art
def frame_to_ascii(frame, console_width, console_height):
    # Check frame dimensions
    if frame.shape[0] == 0 or frame.shape[1] == 0:
        return ""

    # Calculate aspect ratio
    aspect_ratio = frame.shape[1] / frame.shape[0]
    # Calculate new width and height to fit within console dimensions
    new_width = int(console_height * aspect_ratio)
    new_height = console_height
    if new_width > console_width:
        new_width = console_width
        new_height = int(console_width / aspect_ratio)
    # Resize frame
    resized_frame = cv2.resize(frame, (new_width, new_height))
    ascii_art = ""
    # Convert pixels to ASCII characters
    for row in resized_frame:
        for pixel in row:
            ascii_art += pixel_to_ascii(pixel)
        ascii_art += '\n'
    return ascii_art

# Function to detect text in an image and replace it with ASCII art
def replace_text_with_ascii(frame):
    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Use Tesseract OCR to detect text
    text = pytesseract.image_to_string(Image.fromarray(gray_frame))
    return text

def main():
    query = input("Enter your search query: ")
    results = search_videos(query)

    for i, video in enumerate(results):
        print(f"{i+1}. {video['title']}")

    while True:
        try:
            choice = int(input("Enter the number of the video you want to play: ")) - 1
            selected_video = results[choice]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a number between 1 and 5.")

    video_id = selected_video['id']
    download_video(video_id)
    play_video()

if __name__ == "__main__":
    try:
        import cv2
        import pytesseract
    except ImportError:
        print("Please install the required libraries (cv2 and pytesseract) before running the script.")
    else:
        try:
          main()
        finally:
          with contextlib.suppress(Exception):
            os.remove('video.mp4')