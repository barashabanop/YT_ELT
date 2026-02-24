import requests 
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')
API_KEY=os.getenv('API_KEY')
CHANNEL_HANDLE = 'MrBeast'

maxResults = 50

def get_playlist_id():
    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'



        response = requests.get(url=url)

        response.raise_for_status()

        data = response.json()

        channel_items = data["items"][0]

        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]['uploads']

        return channel_playlistId


    except requests.exceptions.RequestException as e:
        raise e
    except Exception as e :
        pass


videos_list=[]
def get_all_channel_video_ids(playlistId):

    base_url =f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"
    pageToken = None
    try:
        while True:
            url = base_url

            if pageToken:
                url += f'&pageToken={pageToken}'
            response = requests.get(url=url)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items',[]):
                videoId = item['contentDetails']['videoId']
                videos_list.append(videoId)

            pageToken = data.get('nextPageToken')
            

            if not pageToken:
                break
        
        return videos_list
    except requests.exceptions.RequestException as e:
        raise e
    
    
    





def get_videos_info(videoIds):
    def batch_list(original_list,batch_size):
        for batch in range(0,len(original_list),batch_size):
            yield original_list[batch:batch+batch_size]


    videoIdsBatches = batch_list(videoIds,50)
    videosData=[]
    try:
        for batch in videoIdsBatches:
            videoIdsStr = ','.join(batch)
            
            url =f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=statistics&part=snippet&id={videoIdsStr}&key={API_KEY}'
            
            response = requests.get(url=url)
            
            response.raise_for_status()
            
            data = response.json()

            for item in data.get('items',[]):
                videoId = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                videoData = {
                    'video_id':videoId,
                    'title':snippet['title'],
                    'published_at':snippet['publishedAt'],
                    'duration':contentDetails['duration'],
                    'view_count':statistics.get('viewCount',None),
                    'like_count':statistics.get('likeCount',None),
                    'comment_count':statistics.get('commentCount',None)
                }
                videosData.append(videoData)
        return videosData
    except requests.exceptions.RequestException as e:
        raise e


if __name__ =='__main__':
    playlistId = get_playlist_id()
    #print(get_all_channel_videos(playlistId=playlistId))
    channelIds = get_all_channel_video_ids(playlistId=playlistId)
    videosInfo = get_videos_info(channelIds)
    print(videosInfo)