import requests
from bs4 import BeautifulSoup
import instaloader
import cv2
import os
import multiprocessing
import uuid
import time



def detect_faces(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(200, 200))
    return faces


def find_instagram_profiles(country):
    query = f"{country} Instagram profiles"
    google_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(google_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all("a")
        instagram_profiles = [link['href'] for link in links if "instagram.com" in link['href']]
        return instagram_profiles
    else:
        print("An error occurred while retrieving the web page")
        return None


def scrape_instagram_posts(profile_url, output_directory):
    L = instaloader.Instaloader()
    user, password = None, None
    with open('credentials.txt', 'r') as f:
        user = f.readline().split()
        password = f.readline().split()
    try:
        L.login(user, password)
    except instaloader.exceptions.BadCredentialsException:
        print("Invalid credentials")
    except Exception as e:
        print(f"Error occured during login: {e}")

    username = profile_url.split('/')[-2]
    with open('scraped_profiles.txt', 'r') as file:
        scraped_usernames = {line.strip() for line in file}

    if username not in scraped_usernames:
        print(f"Scraping posts from {username}")
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            for post in profile.get_posts():
                image_url = post.url
                image_data = requests.get(image_url).content
                temp_image_path = str(uuid.uuid4()) + '.jpg'

                with open(temp_image_path, "wb") as f:
                    f.write(image_data)

                faces = detect_faces(temp_image_path)

                if len(faces) > 0 and all(face[2] >= 200 and face[3] >= 200 for face in faces):
                    image_filename = f"{post.owner_username}_{post.shortcode}.jpg"
                    image_path = os.path.join(output_directory, image_filename)
                    if not os.path.exists(image_path):
                        with open(image_path, "wb") as f:
                            f.write(image_data)
                            print(f"Saved post to {image_path}")
                    time.sleep(0.7)
                else:
                    print("No faces detected, skipping post.")
                    time.sleep(0.7)

                os.remove(temp_image_path)
        except instaloader.exceptions.InstaloaderException as e:
            print(f"Error while scraping posts from {username}: {e}")


if __name__ == "__main__":

    output_directory = "arab_faces_images"
    arab_countries = [
        "Algeria",
        "Bahrain",
        "Comoros",
        "Djibouti",
        "Egypt",
        "Iraq",
        "Jordan",
        "Kuwait",
        "Lebanon",
        "Libya",
        "Mauritania",
        "Morocco",
        "Oman",
        "Palestine",
        "Qatar",
        "Saudi Arabia",
        "Somalia",
        "Sudan",
        "Syria",
        "Tunisia",
        "United Arab Emirates",
        "Yemen"
    ]
    all_profiles = []
    for country in arab_countries:
        profiles = find_instagram_profiles(country)
        for profile in profiles:
            username = profile.split('/')[-2]
            all_profiles.append(username)
    with open('all_profiles.txt', 'w') as file:
        file.write(str(len(all_profiles)) + '\n')

        for username in all_profiles:
            file.write(username + '\n')



