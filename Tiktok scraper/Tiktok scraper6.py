### doc: https://tiktokpy.readthedocs.io/en/latest/users/usage.html#examples
### install ให้ครบด้วยนะครับ
### tiktok มี rate limit ด้วยว่าห้ามดึงเกินเท่าไหร่ https://developers.tiktok.com/doc/tiktok-api-v2-rate-limit?enter_method=left_navigation
#pip install pytz
#pip install tqdm
#pip install tiktokapipy
#pip install tiktokapipy --upgrade
#python -m playwright install

from tiktokapipy.api import TikTokAPI
from tqdm import tqdm
from datetime import datetime, timedelta
import csv
import concurrent.futures
import time
import threading

def get_video_stat(username, start_date, end_date):
    RATE_LIMIT = 550
    RATE_LIMIT_INTERVAL = 60  # seconds
    SAFETY_MARGIN = 0.9  # 90% of the actual rate limit
    ADJUSTED_RATE_LIMIT = int(RATE_LIMIT * SAFETY_MARGIN)
    requests_made = 0
    last_request_time = datetime.now()
    start_date_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
    end_date_timestamp = datetime.strptime(end_date, "%Y-%m-%d").timestamp()

    print("Initializing...")
    with TikTokAPI() as api:
        print(f"Fetching user info for {username}...")
        user_info = api.user(username)
        #print(user_info)  # Debug print

        profile_name = username

        # Pre-filter videos based on date range
        videos_list = [video for video in user_info.videos if start_date_timestamp <= video.create_time.timestamp() <= end_date_timestamp]
        
        print(f"Number of videos to process: {len(videos_list)}")  # Debug print

        total_videos = len(videos_list)
        print(f"Processing {total_videos} videos...")
        csv_filename = f"{profile_name}_{start_date}_{end_date}.csv"
        
        video_stats_list = []
        errors = []

        def process_video(video):
            nonlocal requests_made, last_request_time
            try:
                # Rate limiting
                with rate_limit_lock:
                    current_time = datetime.now()
                    elapsed_time = (current_time - last_request_time).total_seconds()
                    if requests_made >= ADJUSTED_RATE_LIMIT and elapsed_time < RATE_LIMIT_INTERVAL:
                        sleep_time = RATE_LIMIT_INTERVAL - elapsed_time
                        time.sleep(sleep_time)
                        requests_made = 0
                        last_request_time = datetime.now() + timedelta(seconds=sleep_time)
                    else:
                        time.sleep(0.1)  # Introducing a small delay for safety
                    requests_made += 1

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
                return video_stats
            except Exception as e:
                errors.append(f"Error processing video with ID {video.id}: {e}")
                return None

        rate_limit_lock = threading.Lock()
        start_time = time.time()  # Start time for rate calculation

        with tqdm(total=total_videos, desc="Processing videos") as pbar:
            for stats in concurrent.futures.ThreadPoolExecutor().map(process_video, videos_list):
                video_stats_list.append(stats)  # Append the returned stats to the list
                elapsed_time = time.time() - start_time
                script_rate = (requests_made / elapsed_time) * 60  # Requests per minute
                remaining_requests = RATE_LIMIT - script_rate
                pbar.set_postfix(Remaining_Requests=f"{remaining_requests:.2f} req/min", Script_Rate=f"{script_rate:.2f} req/min", refresh=True)
                pbar.update(1)

        # Filter out None values (videos that had errors)
        video_stats_list = [stats for stats in video_stats_list if stats]

        #print("Video Stats List:", video_stats_list)  # Debug print

        with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
            fieldnames = ['user_id', 'username', 'nickname', 'private_account', 'verified_account', 'description', 'tags', 'challenges', 'video_id', 'video_url', 'create_time', 'music_title', 'num_comments', 'num_likes', 'num_views', 'num_shares', 'engagement_rate', 'image_post']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(video_stats_list)

        print(f"Saved data to {csv_filename}")
        for error in errors:
            print(error)

# Example usage
username = 'ondemandacademy'
start_date = '2023-01-01'
end_date = '2023-08-01'
get_video_stat(username, start_date, end_date)