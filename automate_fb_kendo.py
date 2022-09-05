"""
*****REFERENCES*****
1) https://drgabrielharris.medium.com/python-how-making-facebook-api-calls-using-facebook-sdk-ea18bec973c8
2) https://developers.google.com/youtube/v3/guides/uploading_a_video
3) https://www.geeksforgeeks.org/send-message-to-telegram-user-using-python/
4) https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e
"""

import os
import logging
import requests
from asyncio import constants
import facebook
import constant
import json
import requests
import time
import send_telegram
import subprocess

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%d/%m/%y %H:%M:%S"
)

def get_long_lived_user_token():
    app_id = constant.FB_APP_ID
    app_secret = constant.FB_APP_SECRET
    user_short_token = constant.FB_USER_SHORT_TOKEN

    url = "https://graph.facebook.com/oauth/access_token"

    payload = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": user_short_token,
    }

    try:
        response = requests.get(
            url,
            params=payload,
            timeout=5,
        )
    except requests.exceptions.Timeout as e:
        logging.error("TimeoutError", e)
    else:

        try:
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logging.error("HTTPError", e)

        else:
            response_json = response.json()
            """ Example Response
            {'access_token': 'EAAPxxxx', 'token_type': 'bearer', 'expires_in': 5183614}
            """

            logging.info(response_json)
            user_long_token = response_json["access_token"]
            return user_long_token
    return ""

def get_permanent_page_access_token(long_lived_token):
    graph = facebook.GraphAPI(access_token=long_lived_token, version=constant.FB_GRAPH_API_VERSION)
    pages_data = graph.get_object("/me/accounts")
    """ Example Pages Data
        {'data': [{'access_token': 'EAAPxxx',
        'category': 'Education',
        'category_list': [{'id': '2250', 'name': 'Education'}],
        'name': 'Coding with Dr Harris',
        'id': '103361561317782',
        'tasks': ['ANALYZE', 'ADVERTISE', 'MODERATE', 'CREATE_CONTENT', 'MANAGE']}],
        'paging': {'cursors': {'before': 'MTAzMzYxNTYxMzE3Nzgy',
        'after': 'MTAzMzYxNTYxMzE3Nzgy'}}}
    """

    for data in pages_data["data"]:
        page_id = data["id"]
        if page_id == constant.FB_PAGE_ID:
            print("yes this is the correct page. name -> " + data["name"])
            return data["access_token"]

    return ""

def get_live_video_data(permanent_page_token):
    graph = facebook.GraphAPI(access_token=permanent_page_token, version=constant.FB_GRAPH_API_VERSION)
    live_video_data = graph.get_object("/me/live_videos")
    """ Example Live Video Data
    {
        "data":[
            {
                "status":"VOD",
                "embed_html":"<iframe allow=\"autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share\" allowfullscreen=\"true\" frameborder=\"0\" height=\"1280\" scrolling=\"no\" src=\"https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2F108331311905854%2Fvideos%2F584052690166512%2F&width=720\" style=\"border:none;overflow:hidden\" width=\"720\"></iframe>",
                "id":"133651572707161"
            },
            {
                "status":"VOD",
                "embed_html":"<iframe allow=\"autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share\" allowfullscreen=\"true\" frameborder=\"0\" height=\"1280\" scrolling=\"no\" src=\"https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2F108331311905854%2Fvideos%2F417690260343203%2F&width=720\" style=\"border:none;overflow:hidden\" width=\"720\"></iframe>",
                "id":"133647382707580"
            }
        ],
        "paging":{
            "cursors":{
                "before":"QVFIUmdhcG5RSThuQ3pMZAHFCUlhIMngxSlpHcU9NVnE2RTE5UGlKWVN4OEJia3VWdGJnaDRROVcwMExwcThBV09sN04ySEFGbmViV2ViRlUwY0lpQi1sWXd3",
                "after":"QVFIUm1nZAUFXeUUxbUd5anRsSnZAEbTJXbVNRMHNrbkxnRFpZAWDRQa1hHNjRlcDZALU1Ixa3hNNkpRcmZAzVmJDLXNmUmJaNTVDbzFpNDR0bDFXcmU0N1ZA2VG1B"
            }
        }
    }
    """
    """
    # TODO until here...
    1. able to get video titles, descriptions from facebook live? or self construct like "PKC Keiko 4th September 2022"?
    """
    current_video_ids = []
    for video_data in live_video_data["data"]:
        embed_url = video_data["embed_html"]
        right_video_url = embed_url.split(r"videos%2F")
        left_video_url = right_video_url[1].split(r"%2F&width")
        video_id = left_video_url[0]
        current_video_ids.append(video_id)

    unsaved_video_ids = get_unsaved_videos(current_video_ids)

    success_unsaved_video_ids = []
    for video_id in unsaved_video_ids:
        if download_videos(permanent_page_token, video_id):
            success_unsaved_video_ids.append(video_id)

    save_uploaded_video_to_json(success_unsaved_video_ids)

def download_videos(permanent_page_token, video_id):
    try:
        video_file_path = constant.VIDEO_FOLDER + video_id + ".mp4"
        if not os.path.exists(constant.VIDEO_FOLDER):
            os.makedirs(constant.VIDEO_FOLDER)

        graph = facebook.GraphAPI(access_token=permanent_page_token, version=constant.FB_GRAPH_API_VERSION)
        video_data = graph.get_object(video_id + "?fields=source")
        source = video_data["source"]
        response = requests.get(source)
        open(video_file_path, "wb").write(response.content)

        return upload_to_youtube(video_file_path, video_id)
    except BaseException as e:
        print("something wrong happened when downloading video of ID: " + video_id)
        print(e)
        return False

def upload_to_youtube(video_file_path, video_id):
    print("Querying youtube api now for this video id: " + video_id)
    
    # categories: https://techpostplus.com/youtube-video-categories-list-faqs-and-solutions/
    cmd = 'python upload_video.py --file='+video_file_path+' --title="'+video_id+'"  --description="" --keywords="PKC, Penang Kendo Club, Kendo"  --category="17" --privacyStatus="public"'
    result = str(subprocess.check_output(cmd, shell=True))
    
    success_message = r"Video id was successfully uploaded:"
    if (success_message not in result):
        print("Upload video to youtube api has returned a response with error:")
        print(result)
        return False
    
    vid_left = result.split(success_message)
    real_vid = vid_left[1].split("::::::")[0]
    send_telegram.send_telegram_message("https://www.youtube.com/watch?v=" + real_vid)
    return True

def get_unsaved_videos(current_video_ids):
    unsaved_videos = []
    try:
        # Opening JSON file
        with open(constant.STORED_VIDEO_JSON_FILE, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            video_ids_in_json = json_object[constant.JSON_VIDEO_ID_KEY]
            for video_id in current_video_ids:
                if not video_id in video_ids_in_json:
                    unsaved_videos.append(video_id)
    except:
        print("file is not created yet, stop reading. Assuming all videos are not uploaded yet")
        return current_video_ids

    return unsaved_videos

def save_uploaded_video_to_json(unsaved_video_ids):
    if (len(unsaved_video_ids) <= 0):
        return
    
    new_video_object = {
        constant.JSON_VIDEO_ID_KEY: [

        ]
    }
    json_object_from_file = json.dumps(new_video_object, indent=4)

    try:
        # Opening JSON file
        with open(constant.STORED_VIDEO_JSON_FILE, 'r') as openfile:
            # Reading from json file
            json_object_from_file = json.load(openfile)
    except:
        print("file is not created yet. Proceed writing to new file")

    try:
        video_list = json.loads(json_object_from_file)[constant.JSON_VIDEO_ID_KEY]
    except:
        video_list = json_object_from_file[constant.JSON_VIDEO_ID_KEY]
    
    video_list.extend(unsaved_video_ids)

    new_video_object = {
        constant.JSON_VIDEO_ID_KEY: video_list
    }
    json_object_from_file = json.dumps(new_video_object, indent=4)
    
    with open(constant.STORED_VIDEO_JSON_FILE, "w+") as outfile:
        outfile.write(json_object_from_file)


def main():
    long_lived_token = get_long_lived_user_token()
    if ("" == long_lived_token):
        print("gg some error occurred while getting long lived user token")
        return
    permanent_page_token = get_permanent_page_access_token(long_lived_token)
    if ("" == permanent_page_token):
        print("gg some error occurred while getting page permanent access token")
        return
    while True:
        get_live_video_data(permanent_page_token)
        time.sleep(3600) # sleep 1 hour

main()