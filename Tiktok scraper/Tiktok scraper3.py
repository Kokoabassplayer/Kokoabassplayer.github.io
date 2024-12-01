### install ให้ครบด้วยนะครับ
### tiktok มี rate limit ด้วยว่าห้ามดึงเกินเท่าไหร่ https://developers.tiktok.com/doc/tiktok-api-v2-rate-limit?enter_method=left_navigation
#pip install pytz
#pip install tqdm
#pip install tiktokapipy
#python -m playwright install

from tiktokapipy.api import TikTokAPI
from tqdm import tqdm
import time
from datetime import datetime
import csv
import warnings
from tiktokapipy.util.deferred_collectors import TikTokAPIWarning

# Suppress the TikTokAPIWarning
warnings.simplefilter("ignore", TikTokAPIWarning)

def get_video_stat(username, start_date, end_date):
    RATE_LIMIT = 600  # Number of requests per minute
    requests_made = 0

    start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=None)
    end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=None)

    print("Initializing...")

    with TikTokAPI() as api:
        print(f"Fetching user info for {username}...")
        user_info = api.user(username)
        profile_name = username

        # Pre-filter videos based on date range
        videos_list = []
        for video in user_info.videos:
            try:
                create_time = video.create_time.replace(tzinfo=None)
                if start_date <= create_time <= end_date:
                    videos_list.append(video)
            except Exception as e:
                print(f"Error processing video with ID {video.id}: {e}")
                continue

        total_videos = len(videos_list)
        print(f"Processing {total_videos} videos...")

        csv_filename = f"{profile_name}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
            fieldnames = ['user_id', 'username', 'nickname', 'private_account', 'verified_account', 'description', 'tags', 'challenges', 'video_id', 'video_url', 'create_time', 'music_title', 'num_comments', 'num_likes', 'num_views', 'num_shares', 'engagement_rate', 'image_post']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            with tqdm(total=total_videos, desc="Processing videos") as pbar:
                for video in videos_list:
                    try:
                        video_stats = {
                            'user_id': user_info.id,
                            'username': profile_name,
                            'nickname': user_info.nickname,
                            'private_account': user_info.private_account,
                            'verified_account': user_info.verified,
                            'description': video.desc,
                            'tags': ", ".join(video.diversification_labels) if video.diversification_labels else None,
                            'challenges': ", ".join([challenge.title for challenge in video.challenges]) if video.challenges else None,
                            'video_id': video.id,
                            'video_url': video.url,
                            'create_time': video.create_time.replace(tzinfo=None),
                            'music_title': video.music.title if video.music else None,
                            'num_comments': video.stats.comment_count,
                            'num_likes': video.stats.digg_count,
                            'num_views': video.stats.play_count,
                            'num_shares': video.stats.share_count,
                            'engagement_rate': ((video.stats.comment_count + video.stats.digg_count + video.stats.share_count) / video.stats.play_count) * 100 if video.stats.play_count > 0 else 0,
                            'image_post': str(video.image_post) if video.image_post else None
                        }
                        writer.writerow(video_stats)

                        requests_made += 1
                        remaining_requests = RATE_LIMIT - (requests_made % RATE_LIMIT)
                        pbar.set_postfix(remaining_requests=remaining_requests, refresh=True)
                        pbar.update(1)

                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Error processing video with ID {video.id}: {e}")
                        continue

    print(f"Saved data to {csv_filename}")

# Example usage
username = 'ondemandacademy'
start_date = '2023-01-01'
end_date = '2023-08-01'
get_video_stat(username, start_date, end_date)
