### install ให้ครบด้วยนะครับ
### tiktok มี rate limit ด้วยว่าห้ามดึงเกินเท่าไหร่ https://developers.tiktok.com/doc/tiktok-api-v2-rate-limit?enter_method=left_navigation
#pip install pytz
#pip install tqdm
#pip install tiktokapipy
#python -m playwright install

###
from tiktokapipy.api import TikTokAPI
import pandas as pd
from tqdm import tqdm
import time
from datetime import datetime

def get_video_stat(username, start_date, end_date):
    stats = []
    start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=None)
    end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=None)

    with TikTokAPI() as api:
        user_info = api.user(username)
        profile_name = username

        # Convert iterator to list and get its length
        videos_list = []
        for video in user_info.videos:
            try:
                # Your video processing code here
                videos_list.append(video)
            except Exception as e:
                print(f"Error processing video with ID {video.id}: {e}")
                continue
        total_videos = len(videos_list)

        # Initialize progress bar with total length
        pbar = tqdm(total=total_videos, desc="Processing videos", dynamic_ncols=True, bar_format='{l_bar}{bar} [{elapsed}<{remaining}, {rate_fmt}{postfix}]')

        for video in videos_list:
            create_time = video.create_time.replace(tzinfo=None)  # Convert to UTC

            # Filter videos by date range
            if start_date <= create_time <= end_date:
                num_comments = video.stats.comment_count
                num_likes = video.stats.digg_count
                num_views = video.stats.play_count
                num_shares = video.stats.share_count
                engagement_rate = ((num_comments + num_likes + num_shares) / num_views) * 100 if num_views > 0 else 0

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
                    'create_time': create_time,
                    'music_title': video.music.title if video.music else None,
                    'num_comments': num_comments,
                    'num_likes': num_likes,
                    'num_views': num_views,
                    'num_shares': num_shares,
                    'engagement_rate': engagement_rate,
                    'image_post': str(video.image_post) if video.image_post else None
                }
                stats.append(video_stats)

            # Update progress bar
            pbar.update(1)

            # Delay for 2 seconds
            time.sleep(1)

        # Close progress bar
        pbar.close()

    # Convert the list of dictionaries into a pandas DataFrame
    df = pd.DataFrame(stats)

    # Save the DataFrame to a CSV file with the specified encoding, profile name, and date range
    csv_filename = f"{profile_name}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

    print(f"Saved data to {csv_filename}")

    return df

# Example usage
#ondemandacademy
#kokoabassplayer0
#zarutt_malai
#thestandardth
username = 'ondemandacademy'
start_date = '2022-01-01'
end_date = '2022-12-31'
video_stats_df = get_video_stat(username, start_date, end_date)
###
