from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin  # Import cross_origin
from flask_cors import CORS
import os
import json
from youtubesearchpython import VideosSearch
from pytube import YouTube
from datetime import datetime, timedelta
import re
import openai

# Initialize the Flask app
app = Flask(__name__)
# Allow requests from geniezbase.com and set appropriate CORS headers
CORS(app, origins="https://geniezbase.com")

# Initialize OpenAI API with your provided API key
openai.api_key = "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"

# Define the search query and region code
results_per_page = 30

# Function to extract YouTube video information
def extract_yt_video_info(video_url):
    try:
        yt = YouTube(video_url)
        title = yt.title
        views = int(yt.views)
        upload_date = yt.publish_date
        return title, views, upload_date, video_url  # Include video URL
    except Exception as e:
        print(f"An error occurred while processing {video_url}: {str(e)}")
        return None, None, None, None

# Function to calculate popularity score for a video
def calculate_popularity_score(views, upload_date, current_date):
    # Calculate days since upload
    days_since_upload = (current_date - upload_date).days + 1  # Adding 1 to avoid division by zero

    # Calculate views per day
    views_per_day = views / days_since_upload

    # Higher weight for recent videos, you can adjust the weight to your preference
    recent_video_weight = 2.0

    # Calculate popularity score
    popularity_score = views_per_day * recent_video_weight

    return popularity_score

# Extract video data including views and upload date
def extract_video_data(keyword):
    video_data_list = []

    videos_search = VideosSearch(keyword, limit=results_per_page)
    results = videos_search.result()['result']

    # Current date (for calculating days since upload)
    current_date = datetime.now()

    for result in results:
        video_url = "https://www.youtube.com/watch?v=" + result['id']
        title, views, upload_date, video_url = extract_yt_video_info(video_url)
        if title and views and upload_date:
            popularity_score = calculate_popularity_score(views, upload_date, current_date)
            # Clean title from emojis and specified Unicode characters
            cleaned_title = remove_emojis_and_unicode(title)
            video_data = {
                "title": cleaned_title,
                "views": views,
                "upload_date": upload_date.strftime('%Y-%m-%d'),
                "popularity_score": popularity_score,
                "video_url": video_url  # Include video URL
            }
            video_data_list.append(video_data)

    # Save the video information to a JSON file
    output_folder = "Output Results"
    os.makedirs(output_folder, exist_ok=True)
    video_data_file = os.path.join(output_folder, "video_data.json")

    with open(video_data_file, 'w') as json_file:
        json.dump({'videos': video_data_list}, json_file, indent=4)

    return video_data_list

# Function to filter popular videos based on popularity score
def filter_popular_videos(video_data_list):
    # Sort the videos based on popularity score in descending order
    sorted_videos = sorted(video_data_list, key=lambda x: x['popularity_score'], reverse=True)
    # Return the top 5 videos (you can modify the number)
    return [video['title'] for video in sorted_videos[:5]]

# Function to remove emojis and specified Unicode characters from the title
def remove_emojis_and_unicode(data):
    # Define the Unicode escape sequences to remove
    unicode_to_remove = ["\u2013", "\u200b"]  # Add more if needed in the future

    # Create a regex pattern to match these Unicode escape sequences
    unicode_pattern = "|".join(map(re.escape, unicode_to_remove))

    # Replace the Unicode escape sequences with an empty string
    cleaned_data = re.sub(unicode_pattern, '', data)
    
    # Remove emojis
    emoj = re.compile(r"["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        u"\U0001F700-\U0001F773"  # Alchemical Symbols
        u"\U0001F780-\U0001F7D4"  # Geometric Shapes Extended
        u"\U0001F800-\U0001F80B"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Extended Smileys & Symbols
        u"\U0001F1E0-\U0001F1FF"  # Regional Indicator Symbols
        u"\U00002500-\U00002BEF"  # Chinese characters and symbols
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2"  # Circled Latin Capital Letter M
        u"\U0001F004"  # Mahjong Tile Red Dragon
        u"\U0001F0CF"  # Playing Card Black Joker
        u"\U0001F170-\U0001F251"  # Enclosed Ideographic Supplement
        u"\U0001F926-\U0001F937"  # Emoji Modifiers
        u"\U00010000-\U0010FFFF"  # Supplementary Multilingual Plane
        u"\u2640-\u2642"  # Female and Male signs
        u"\u2600-\u2B55"  # Various Weather symbols
        u"\u23F0"  # Alarm Clock
        u"\u23F3"  # Hourglass Not Done
        u"\u231A"  # Watch
        u"\u2764"  # Heavy Black Heart
        u"\U0001F49B"  # Yellow Heart
        u"\U0001F49A"  # Green Heart
        u"\U0001F499"  # Blue Heart
        u"\U0001F49C"  # Purple Heart
        u"\U0001F5A4"  # Black Heart
        u"\U0001F44C"  # OK Hand
        u"\U0001F44D"  # Thumbs Up
        u"\U0001F44E"  # Thumbs Down
        u"\U0001F44F"  # Clapping Hands
        u"\U0001F4A1"  # Light Bulb
        u"\U0001F4A3"  # Bomb
        u"\U0001F4A4"  # Zzz (Sleeping Symbol)
        u"\U0001F4AB"  # Dizzy Symbol
        u"\U0001F4AF"  # Hundred Points Symbol
        u"\U0001F347"  # Grapes
        u"\U0001F354"  # Hamburger
        u"\U0001F355"  # Pizza
        u"\U0001F367"  # Shaved Ice
        u"\U0001F40D"  # Snake
        u"\U0001F412"  # Monkey
        u"\U0001F436"  # Dog
        u"\U0001F428"  # Koala
        u"\U0001F431"  # Cat
        u"\U0001F680"  # Rocket
        u"\U0001F697"  # Car
        u"\U0001F600"  # Grinning Face
        u"\U0001F601"  # Grinning Face with Smiling Eyes
        u"\U0001F602"  # Face with Tears of Joy
        u"\U0001F603"  # Smiling Face with Open Mouth
        u"\U0001F604"  # Smiling Face with Open Mouth and Smiling Eyes
        u"\U0001F605"  # Smiling Face with Open Mouth and Cold Sweat
        u"\U0001F4A9"  # Pile of Poo
        u"\U0001F52B"  # Pistol
        u"\u2648-\u2653"  # Zodiac signs Aries to Pisces
        u"\u2654-\u265F"  # Chess pieces (King to Black Pawn)
        u"\u2600-\u26C8"  # Various Weather symbols
        u"\U0001F550-\U0001F55B"  # Clock Faces
        u"\U0001F311-\U0001F318"  # Moon Phases
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        u"\u20b9"
        u"\u092e"
        u"\u0947"
        u"\u0902"
        u"\u00a0"
                      "]+", re.UNICODE)
    cleaned_data = re.sub(emoj, '', cleaned_data)

    return cleaned_data

@app.route('/', methods=['POST'])
@cross_origin(origin='https://geniezbase.com', headers=['Content-Type', 'Access-Control-Allow-Origin'])
def home():
    keyword = request.json.get('keyword')

    # Step 1: Extract video data including views and upload date
    video_data_list = extract_video_data(keyword)

    # Step 3: Filter and get the top video titles based on popularity score
    popular_titles = filter_popular_videos(video_data_list)

    # Prepare the prompt for ChatGPT
    prompt = f"Generate 2 SEO based short YouTube Video titles about the {keyword} and the sample titles are these {popular_titles}, please just give me the titles."

    # Call OpenAI to generate video titles
    response = openai.Completion.create(
        engine="davinci",  # or "curie"
        prompt=prompt,
        max_tokens=50,  # Adjust the max tokens as needed
        n=10  # Generate 10 titles
    )

    generated_titles = response.choices[0].text.strip().split('\n')

    # Prepare the response
    response_data = {'generated_titles': generated_titles}

    # Set the CORS headers
    response = jsonify(response_data)

    return response

if __name__ == "__main__":
    app.run(debug=True)
