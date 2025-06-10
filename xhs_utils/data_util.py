import json
import os
import re
import time
import unicodedata
import subprocess
import openpyxl
import requests
from loguru import logger
from retry import retry
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def norm_str(text: str) -> str:
    """Normalize a string for safe filesystem usage."""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    text = text.replace('\n', '').replace('\r', '').strip()
    return text[:50]

def norm_text(text):
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
    text = ILLEGAL_CHARACTERS_RE.sub(r'', text)
    return text


def timestamp_to_str(timestamp):
    time_local = time.localtime(timestamp / 1000)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def handle_user_info(data, user_id):
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['basic_info']['nickname']
    avatar = data['basic_info']['imageb']
    red_id = data['basic_info']['red_id']
    gender = data['basic_info']['gender']
    if gender == 0:
        gender = '男'
    elif gender == 1:
        gender = '女'
    else:
        gender = '未知'
    ip_location = data['basic_info']['ip_location']
    desc = data['basic_info']['desc']
    follows = data['interactions'][0]['count']
    fans = data['interactions'][1]['count']
    interaction = data['interactions'][2]['count']
    tags_temp = data['tags']
    tags = []
    for tag in tags_temp:
        try:
            tags.append(tag['name'])
        except:
            pass
    return {
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'red_id': red_id,
        'gender': gender,
        'ip_location': ip_location,
        'desc': desc,
        'follows': follows,
        'fans': fans,
        'interaction': interaction,
        'tags': tags,
    }

def handle_note_info(data):
    note_id = data['id']
    note_url = data['url']
    note_type = data['note_card']['type']
    if note_type == 'normal':
        note_type = '图集'
    else:
        note_type = '视频'
    user_id = data['note_card']['user']['user_id']
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['note_card']['user']['nickname']
    avatar = data['note_card']['user']['avatar']
    title = data['note_card']['title']
    if title.strip() == '':
        title = f'无标题'
    desc = data['note_card']['desc']
    liked_count = data['note_card']['interact_info']['liked_count']
    collected_count = data['note_card']['interact_info']['collected_count']
    comment_count = data['note_card']['interact_info']['comment_count']
    share_count = data['note_card']['interact_info']['share_count']
    image_list_temp = data['note_card']['image_list']
    image_list = []
    for image in image_list_temp:
        try:
            image_list.append(image['info_list'][1]['url'])
            # success, msg, img_url = XHS_Apis.get_note_no_water_img(image['info_list'][1]['url'])
            # image_list.append(img_url)
        except:
            pass
    if note_type == '视频':
        video_cover = image_list[0]
        video_addr = f"https://sns-video-bd.xhscdn.com/{data['note_card']['video']['consumer']['origin_video_key']}"
        # success, msg, video_addr = XHS_Apis.get_note_no_water_video(note_id)
    else:
        video_cover = None
        video_addr = None
    tags_temp = data['note_card']['tag_list']
    tags = []
    for tag in tags_temp:
        try:
            tags.append(tag['name'])
        except:
            pass
    upload_time = timestamp_to_str(data['note_card']['time'])
    if 'ip_location' in data['note_card']:
        ip_location = data['note_card']['ip_location']
    else:
        ip_location = '未知'
    return {
        'note_id': note_id,
        'note_url': note_url,
        'note_type': note_type,
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'title': title,
        'desc': desc,
        'liked_count': liked_count,
        'collected_count': collected_count,
        'comment_count': comment_count,
        'share_count': share_count,
        'video_cover': video_cover,
        'video_addr': video_addr,
        'image_list': image_list,
        'tags': tags,
        'upload_time': upload_time,
        'ip_location': ip_location,
    }

def handle_comment_info(data):
    note_id = data['note_id']
    note_url = data['note_url']
    comment_id = data['id']
    user_id = data['user_info']['user_id']
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['user_info']['nickname']
    avatar = data['user_info']['image']
    content = data['content']
    show_tags = data['show_tags']
    like_count = data['like_count']
    upload_time = timestamp_to_str(data['create_time'])
    try:
        ip_location = data['ip_location']
    except:
        ip_location = '未知'
    pictures = []
    try:
        pictures_temp = data['pictures']
        for picture in pictures_temp:
            try:
                pictures.append(picture['info_list'][1]['url'])
                # success, msg, img_url = XHS_Apis.get_note_no_water_img(picture['info_list'][1]['url'])
                # pictures.append(img_url)
            except:
                pass
    except:
        pass
    return {
        'note_id': note_id,
        'note_url': note_url,
        'comment_id': comment_id,
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'content': content,
        'show_tags': show_tags,
        'like_count': like_count,
        'upload_time': upload_time,
        'ip_location': ip_location,
        'pictures': pictures,
    }
def save_to_xlsx(datas, file_path, type='note'):
    """Save a list of dicts to an Excel workbook.

    The directory is created if missing. If ``datas`` is empty, no file
    will be written and ``False`` is returned.
    """
    if not datas:
        logger.warning("No data to write to Excel; skipping file creation")
        return False

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    if type == 'note':
        headers = ['笔记id', '笔记url', '笔记类型', '用户id', '用户主页url', '昵称', '头像url', '标题', '描述', '点赞数量', '收藏数量', '评论数量', '分享数量', '视频封面url', '视频地址url', '图片地址url列表', '标签', '上传时间', 'ip归属地']
    elif type == 'user':
        headers = ['用户id', '用户主页url', '用户名', '头像url', '小红书号', '性别', 'ip地址', '介绍', '关注数量', '粉丝数量', '作品被赞和收藏数量', '标签']
    else:
        headers = ['笔记id', '笔记url', '评论id', '用户id', '用户主页url', '昵称', '头像url', '评论内容', '评论标签', '点赞数量', '上传时间', 'ip归属地', '图片地址url列表']
    ws.append(headers)
    for data in datas:
        data = {k: norm_text(str(v)) for k, v in data.items()}
        ws.append(list(data.values()))
    wb.save(file_path)
    logger.info(f'数据保存至 {file_path}')

def download_media(path: str, name: str, url: str, type: str, failed: list | None = None) -> bool:
    """Download an image or video file. Return True on success."""
    try:
        if type == 'image':
            content = requests.get(url).content
            with open(f"{path}/{name}.jpg", "wb") as f:
                f.write(content)
        elif type == 'video':
            res = requests.get(url, stream=True)
            chunk_size = 1024 * 1024
            with open(f"{path}/{name}.mp4", "wb") as f:
                for data in res.iter_content(chunk_size=chunk_size):
                    f.write(data)
        return True
    except Exception as e:
        logger.error(f"Download failed for {url}: {e}")
        if failed is not None:
            failed.append({"path": path, "name": name, "url": url, "type": type})
        return False

def transcode_to_h264(path: str) -> bool:
    """Transcode a video to H.264 using ffmpeg."""
    out_path = f"{os.path.splitext(path)[0]}_h264.mp4"
    cmd = [
        "ffmpeg",
        "-i",
        path,
        "-c:v",
        "libx264",
        "-c:a",
        "copy",
        "-y",
        out_path,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(path)
        os.rename(out_path, path)
        return True
    except Exception as e:
        logger.error(f"Transcode failed for {path}: {e}")
        if os.path.exists(out_path):
            os.remove(out_path)
        return False

def save_user_detail(user, path):
    with open(f'{path}/detail.txt', mode="w", encoding="utf-8") as f:
        # 逐行输出到txt里
        f.write(f"用户id: {user['user_id']}\n")
        f.write(f"用户主页url: {user['home_url']}\n")
        f.write(f"用户名: {user['nickname']}\n")
        f.write(f"头像url: {user['avatar']}\n")
        f.write(f"小红书号: {user['red_id']}\n")
        f.write(f"性别: {user['gender']}\n")
        f.write(f"ip地址: {user['ip_location']}\n")
        f.write(f"介绍: {user['desc']}\n")
        f.write(f"关注数量: {user['follows']}\n")
        f.write(f"粉丝数量: {user['fans']}\n")
        f.write(f"作品被赞和收藏数量: {user['interaction']}\n")
        f.write(f"标签: {user['tags']}\n")

def save_note_detail(note, path):
    with open(f'{path}/detail.txt', mode="w", encoding="utf-8") as f:
        # 逐行输出到txt里
        f.write(f"笔记id: {note['note_id']}\n")
        f.write(f"笔记url: {note['note_url']}\n")
        f.write(f"笔记类型: {note['note_type']}\n")
        f.write(f"用户id: {note['user_id']}\n")
        f.write(f"用户主页url: {note['home_url']}\n")
        f.write(f"昵称: {note['nickname']}\n")
        f.write(f"头像url: {note['avatar']}\n")
        f.write(f"标题: {note['title']}\n")
        f.write(f"描述: {note['desc']}\n")
        f.write(f"点赞数量: {note['liked_count']}\n")
        f.write(f"收藏数量: {note['collected_count']}\n")
        f.write(f"评论数量: {note['comment_count']}\n")
        f.write(f"分享数量: {note['share_count']}\n")
        f.write(f"视频封面url: {note['video_cover']}\n")
        f.write(f"视频地址url: {note['video_addr']}\n")
        f.write(f"图片地址url列表: {note['image_list']}\n")
        f.write(f"标签: {note['tags']}\n")
        f.write(f"上传时间: {note['upload_time']}\n")
        f.write(f"ip归属地: {note['ip_location']}\n")



@retry(tries=3, delay=1)
def download_note(note_info, path, save_choice, transcode=False, failed: list | None = None):
    note_id = note_info['note_id']
    user_id = note_info['user_id']
    title = norm_str(note_info['title'])
    nickname = norm_str(note_info['nickname'])
    if title.strip() == '':
        title = f'无标题'
    note_type = note_info['note_type']

    # flat mode: directly store media under base path
    if save_choice == 'image-flat' and note_type == '图集':
        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {
                ex.submit(download_media, path, f"{note_id}_{idx}", url, 'image', failed): url
                for idx, url in enumerate(note_info['image_list'])
            }
            for _ in tqdm(as_completed(futures), total=len(futures), desc="images"):
                pass
        return path
    if save_choice == 'video-flat' and note_type == '视频':
        download_media(path, note_id, note_info['video_addr'], 'video', failed)
        if transcode:
            transcode_to_h264(f"{path}/{note_id}.mp4")
        return path

    save_path = f'{path}/{nickname}_{user_id}/{title}_{note_id}'
    check_and_create_path(save_path)
    with open(f'{save_path}/info.json', mode='w', encoding='utf-8') as f:
        f.write(json.dumps(note_info) + '\n')
    save_note_detail(note_info, save_path)
    if note_type == '图集' and save_choice in ['media', 'media-image', 'all']:
        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {
                ex.submit(download_media, save_path, f'image_{idx}', url, 'image', failed): url
                for idx, url in enumerate(note_info['image_list'])
            }
            for _ in tqdm(as_completed(futures), total=len(futures), desc="images"):
                pass
    elif note_type == '视频' and save_choice in ['media', 'media-video', 'all']:
        download_media(save_path, 'cover', note_info['video_cover'], 'image', failed)
        download_media(save_path, 'video', note_info['video_addr'], 'video', failed)
        if transcode:
            transcode_to_h264(f"{save_path}/video.mp4")
    return save_path


def check_and_create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_failed(failed: list, file_path: str = "failed.txt"):
    """Append failed download records to a file."""
    if not failed:
        return
    with open(file_path, "a", encoding="utf-8") as f:
        for item in failed:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    logger.info(f"Saved {len(failed)} failed downloads to {file_path}")


def retry_failed(file_path: str) -> list:
    """Load failed download records from a file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]
