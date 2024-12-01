# originate by https://python.plainenglish.io/scrape-everythings-from-instagram-using-python-39b5a8baf2e5
# modified by Nuttapong Buttprom (https://kokoabassplayer.github.io/)
# อย่าลืม pip3 install instaloader
# อย่าลืม pip install tqdm

import instaloader
from datetime import datetime
from itertools import dropwhile, takewhile
import csv
import time
from tqdm import tqdm
import re

class GetInstagramProfile():
    def __init__(self) -> None:
        self.L = instaloader.Instaloader()

    def download_users_profile_picture(self,username):
        self.L.download_profile(username, profile_pic_only=True)

    def download_users_posts_with_periods(self, username, since, until):
        posts = instaloader.Profile.from_username(self.L.context, username).get_posts()
        SINCE = datetime.strptime(since, "%Y-%m-%d")
        UNTIL = datetime.strptime(until, "%Y-%m-%d")

        for post in takewhile(lambda p: p.date > SINCE, dropwhile(lambda p: p.date > UNTIL, posts)):
            self.L.download_post(post, username)

    def download_hastag_posts(self, hashtag):
        for post in instaloader.Hashtag.from_name(self.L.context, hashtag).get_posts():
            self.L.download_post(post, target='#'+hashtag)

    def get_users_followers(self,user_name):
        '''Note: login required to get a profile's followers.'''
        self.L.login(input("input your username: "), input("input your password: ") ) 
        profile = instaloader.Profile.from_username(self.L.context, user_name)
        file = open("follower_names.txt","a+")
        for followee in profile.get_followers():
            username = followee.username
            file.write(username + "\n")
            print(username)

    def get_users_followings(self,user_name):
        '''Note: login required to get a profile's followings.'''
        self.L.login(input("input your username: "), input("input your password: ") ) 
        profile = instaloader.Profile.from_username(self.L.context, user_name)
        file = open("following_names.txt","a+")
        for followee in profile.get_followees():
            username = followee.username
            file.write(username + "\n")
            print(username)

    def get_post_comments(self,username):
        posts = instaloader.Profile.from_username(self.L.context, username).get_posts()
        for post in posts:
            for comment in post.get_comments():
                print("comment.id  : "+str(comment.id))
                print("comment.owner.username  : "+comment.owner.username)
                print("comment.text  : "+comment.text)
                print("comment.created_at_utc  : "+str(comment.created_at_utc))
                print("************************************************")

    def get_post_info_csv(self, username, since, until):
        SINCE = datetime.strptime(since, "%Y-%m-%d")
        UNTIL = datetime.strptime(until, "%Y-%m-%d")

        # Get the profile object for the given username
        profile = instaloader.Profile.from_username(self.L.context, username)
        posts = profile.get_posts()

        # Determine the total number of posts within the specified date range
        total_posts_in_range = sum(1 for _ in takewhile(lambda p: p.date > SINCE, dropwhile(lambda p: p.date > UNTIL, profile.get_posts())))

        # Open a CSV file for writing post information with UTF-8 encoding
        with open(username + '.csv', 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)

            # Write the header row in the CSV file, including the "Image URL" field
            writer.writerow(["Type", "ID", "Profile", "Caption", "Date", "Location", "URL", "TypeName", "MediaCount", "Likes", "Comments", "Video Views", "Is Video", "Engagement Rate", "Hashtags", "Mentions", "Tagged Users", "Followers", "Following", "Image URL"])

            # Get the total followers and following count for the profile
            total_followers = profile.followers
            total_following = profile.followees

            # Define an iterator to filter posts within the date range
            post_iterator = takewhile(lambda p: p.date > SINCE, dropwhile(lambda p: p.date > UNTIL, posts))

            # Iterate through posts with a progress bar using tqdm
            for post in tqdm(post_iterator, total=total_posts_in_range, desc="Processing posts"):
                # Extract various details from the post, including the image URL
                image_url = post.url
                caption = post.caption if post.caption else ""
                hashtags = " ".join(re.findall(r'#[^\s]+', caption))
                posturl = "https://www.instagram.com/p/" + post.shortcode
                likes = post.likes
                comments = post.comments
                video_views = post.video_view_count if post.is_video else ""
                is_video = post.is_video
                engagement_rate = (likes + comments) / total_followers * 100
                mentions = " ".join(post.caption_mentions)
                location = post.location.name if post.location else ""

                # Check if tagged_users is a list of objects or strings and join them
                tagged_users = " ".join([user.username if hasattr(user, 'username') else user for user in post.tagged_users])

                # Write all the extracted information to the CSV file, including the image URL
                writer.writerow(["post", post.mediaid, profile.username, caption, post.date, location, posturl, post.typename, post.mediacount, likes, comments, video_views, is_video, engagement_rate, hashtags, mentions, tagged_users, total_followers, total_following, image_url])

                time.sleep(1)  # Add a delay between requests to be courteous to the server

        print(f"Data for {username} has been successfully written to {username}.csv.") # Print a success message


if __name__=="__main__":
    cls = GetInstagramProfile()
    #cls.download_users_profile_picture("best_gadgets_2030")
    #cls.download_users_posts_with_periods(username="kokoabassplayer_rubikk", since="2023-07-01", until="2023-08-01")
    #cls.download_hastag_posts("ondemandacademy")
    #cls.get_users_followers("best_gadgets_2030")
    #cls.get_users_followings("best_gadgets_2030")
    #cls.get_post_comments("laydline")

    ### วิธีใช้: เปลี่ยน username และ ระยะเวลาที่ด้านล่าง → กดปุ่มรันที่มุมขวาบน → ไฟล์จะถูกวางลงที่โฟลเดอร์เดียวกับที่ไฟล์ของโค๊ดนี้อยู่
    cls.get_post_info_csv(username="enconcept_tothemax", since="2023-01-01", until="2023-07-01")