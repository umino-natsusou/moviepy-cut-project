# 导入需要的库
from moviepy.editor import *
import os
import transitions as ts
import moviepy.editor as mpe
import random
import time

# 合成的视频最小时长
min_time = 80
# 开头片段动画时长
time_transition_header = 0.15
# 其他片段动画时长
time_transition_other = 0.2
# 末尾淡出时间
time_fade_out = 2


# 输入视频文件夹的路径
video_folder = "videoFolder" 
# 已被合并视频文件夹属灵
video_folder_done = "videoFolderDone"
# 输出视频文件夹路径
video_output = "videoOutput"

# 开头视频
clip_Header = VideoFileClip('videoHeader/header.mp4')


# 视频文件名列表并进行排序
video_files = sorted(os.listdir(video_folder))


# 计数器
counter = 1
# 初始化一个空列表，用于存放待合并视频
clips_to_do = []


for itemVideo in video_files:
    # 每一个视频的路径
    itemVideoPath = os.path.join(video_folder, itemVideo)
    # 每一个视频的clip对象
    itemVideoClip = VideoFileClip(itemVideoPath)
    # 将header视频放进去
    if len(clips_to_do) == 0:
        clips_to_do.append(clip_Header)
    # 添加到待合并列表
    clips_to_do.append(itemVideoClip)
    # 计算列表中视频的总时长
    total_duration = sum([c.duration for c in clips_to_do])
    # 总时长符合要求，进行合并操作
    if total_duration >= min_time:
        # 先合并headerVideo和第1个视频
        clipPartial= ts.transition_glitch(clip_Header, time_transition_header, clips_to_do[1], time_transition_header)
        # 再合并余下的视频
        left_order = 0
        for itemVideoLeft in clips_to_do[2:]:
            # 获取一个随机数
            random_int = random.randint(0, 1)
            # 要保存的图片路径
            img_save_path = "dirZoom" + "/" + str(time.time()) + ".jpg"
            clip_zoom = None
            if random_int == 0 or left_order == 0:
                # 获取第一帧的图片并保存
                ts.get_first_frame_as_img(itemVideoLeft, img_save_path)
                # 将这一张图做成缩小效果的视频片段
                clip_zoom = ts.transition_zoom(img_save_path, duration = time_transition_other, zoom_ratio = 2, is_zoom_in = False)
            else:
                # 获取最后一帧的图片并保存
                ts.get_last_frame_as_img(itemVideoLeft, img_save_path)
                clip_zoom = ts.transition_zoom(img_save_path, duration = time_transition_other, zoom_ratio = 2, is_zoom_in = True)
            # 合并视频片段
            clipPartial = mpe.concatenate_videoclips([clipPartial, clip_zoom, itemVideoLeft])
            left_order += 1
        # 视频末尾淡出
        clipPartial = clipPartial.fadeout(time_fade_out).audio_fadeout(time_fade_out)
        # 合并后的视频进行输出
        clipPartial.write_videofile(os.path.join(video_output, f"part_{counter}.mp4"))
        
        # 释放对象资源占用
        clipPartial.close()
        # 清空图片文件夹
        for image in os.listdir('dirGlitch'):
            os.remove(os.path.join('dirGlitch', image))
        for image in os.listdir('dirZoom'):
            os.remove(os.path.join('dirZoom', image))
        # 将除headerVideo外的已被合并的视频进行转移
        for c in clips_to_do[1:]:
            # 获取片段对应的文件名 
            file_name = c.filename.split(os.sep)[-1] 
            # 拼接片段对应的原始路径和目标路径 
            src_path = os.path.join(video_folder, file_name) 
            dst_path = os.path.join(video_folder_done, file_name) 
            os.rename(src_path, dst_path)
            c.close()
        # 清空视频对象
        clips_to_do.clear()
        # 计数器+1
        counter += 1

