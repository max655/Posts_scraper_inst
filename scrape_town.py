import requests
import instaloader
import cv2
import os
import uuid
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import concurrent.futures
import pandas as pd


def contains_uppercase(input_string):
    return bool(re.search(r'[A-Z]', input_string))


def detect_faces(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(200, 200))
    return faces


def find_instagram_profiles(country):
    query = f"{country} Instagram profiles"
    google_url = f"https://www.google.com/search?q={query}"

    driver = webdriver.Chrome()
    driver.get(google_url)

    time.sleep(0.7)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.7)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    instagram_profiles = []
    try:
        links = driver.find_elements(By.XPATH, "//a[@href]")
        for link in links:
            href = link.get_attribute("href")
            if "instagram.com" in href:
                username = href.split('/')[-2]
                if not contains_uppercase(username) and username != 'reels':
                    instagram_profiles.append(username)
    except Exception as e:
        print("An error occured:", e)

    driver.quit()

    return list(set(instagram_profiles))


def find_instagram_profiles_parallel(countries):
    instagram_profiles = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(find_instagram_profiles, country): country for country in countries}
        for future in concurrent.futures.as_completed(futures):
            country = futures[future]
            try:
                profiles = future.result()
                print(f"Fetched profiles for {country}: {profiles}")
                instagram_profiles.update(profiles)
            except Exception as e:
                print(f"Error fetching profiles for {country}: {e}")
    return list(instagram_profiles)


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

    arab_countries = [
        "Algeria", "Bahrain", "Comoros", "Djibouti", "Egypt", "Iraq", "Jordan",
        "Kuwait", "Lebanon", "Libya", "Mauritania", "Morocco", "Oman", "Palestine",
        "Qatar", "Saudi Arabia", "Somalia", "Sudan", "Syria", "Tunisia", "United Arab Emirates", "Yemen"
    ]

    output_directory = "arab_faces_images"

    """if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    df = pd.read_csv('table-data.csv')

    cities = df['city'][350:500]
    all_profiles_cities = find_instagram_profiles_parallel(cities)

    with open('all_profiles.txt', 'a') as file:
        last_profile = all_profiles_cities[-1]
        for i, profile in enumerate(all_profiles_cities):
            if i != len(all_profiles_cities) - 1:
                file.write(profile + '\n')
            else:
                file.write(profile)

    for profile in profiles:
        scrape_instagram_posts(profile, output_directory)
    else:
        print("No Instagram profiles found for the given city.")

    with open('all_profiles.txt', 'r') as file:
        lines = file.readlines()

    profiles_without_duplicates = list(set(lines))

   with open('all_profiles.txt', 'w') as file:
        file.writelines(profiles_without_duplicates)"""

with open('all_profiles.txt', 'r') as file:
    lines = file.readlines()

filtered_lines = [line for line in lines if '-' not in line]

with open('all_profiles.txt', 'w') as file:
    for line in lines:
        if not re.match("^\\d+$", line.strip()):
            file.write(line)
