from moviepy.editor import * 
import moviepy.editor as mpe
from glitch_this import ImageGlitcher
import math
from PIL import Image
import numpy


def get_last_frame_as_img(clip, img_path):
    frame_t = clip.duration - 1 # 获取最后一秒的时间
    image = clip.get_frame(frame_t) # 获取最后一帧的图像
    clip.save_frame(img_path, t=frame_t)



def get_first_frame_as_img(clip, img_path):
    frame_t = 0 
    image = clip.get_frame(frame_t) 
    clip.save_frame(img_path, t=frame_t)



def zoom_in_effect(clip, zoom_ratio):
    def effect(get_frame, t):
            img = Image.fromarray(get_frame(t))
            base_size = img.size

            new_size = [
                math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
                math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
            ]
            # The new dimensions must be even.
            new_size[0] = new_size[0] + (new_size[0] % 2)
            new_size[1] = new_size[1] + (new_size[1] % 2)

            img = img.resize(new_size, Image.LANCZOS)

            x = math.ceil((new_size[0] - base_size[0]) / 2)
            y = math.ceil((new_size[1] - base_size[1]) / 2)

            img = img.crop([
                x, y, new_size[0] - x, new_size[1] - y
            ]).resize(base_size, Image.LANCZOS)

            result = numpy.array(img)
            img.close()
            # 返回result作为新的一帧
            return result
    return clip.fl(effect)

def transition_zoom(img_path, duration, zoom_ratio = 0.04, fps = 30, is_zoom_in = True):
    """将一张图片做成一段具变焦效果的视频

    Args:
        img_path (_type_): 图片途径
        duration (_type_): 视频时间
        zoom_ratio (float, optional): 每秒缩放比例. Defaults to 0.04.
        fps (int, optional): 帧率. Defaults to 30.
        is_zoom_in (bool, optional): 是否放大（焦距拉近）. Defaults to True.

    Returns:
        _type_: 合成后的视频clip
    """
    clip = ImageClip(img_path).set_fps(fps).set_duration(duration)
    clip = zoom_in_effect(clip, zoom_ratio)
    if (is_zoom_in == False):
        # 倒放
        clip = clip.fx(vfx.time_mirror)
    return clip



def transition_glitch(video1, glitch_duration1: float, video2, glitch_duration2: float):
    """视频与视频之间添加色差故障转场效果

    Args:
        video1 (_type_): 视频1 clip
        glitch_duration1 (float): 要做成转场效果的视频1的秒数（取结尾部分）
        video2 (_type_): 视频2 clip
        glitch_duration2 (float): 要做成转场效果的视频2的秒数（取开头部分）

    Returns:
        _type_: 合并后的视频clip
    """    
    glitcher = ImageGlitcher()

    duration1 = video1.duration # 获取第一个视频的时长
    duration2 = video2.duration # 获取第二个视频的时长

    # 过度图片文件夹
    clip_dir = 'dirGlitch'
    # 过渡段
    glitch_clip1 = video1.subclip(duration1 - glitch_duration1, duration1)
    glitch_clip2 = video2.subclip(0, glitch_duration2)
    glitch_clip = concatenate_videoclips([glitch_clip1, glitch_clip2])
    # 将过度段导出为图片
    glitch_clip.write_images_sequence(clip_dir + '/transition_%04d.png', fps = 30) 

    # 排序
    images = sorted(os.listdir(clip_dir))
    middlePos = len(images) // 2    # 中间值
    stepFront = 10 / middlePos     # 前半部分步长
    stepAfter = 10 / (len(images) - len(images) // 2 - 1)  #后半部分步长
    intensity  = 0.1    # 初始值
    i = 0   # i初始化
    # 图片进行色差障碍处理
    glitched_list = []
    for image in images:
        # 改变intensity
        if i < len(images) // 2:
            # 前半部分图片
            if i == 0:
                # 第一张图片
                intensity = 0.1
            else:
                # 非第一张一张
                intensity += stepFront
        elif i == len(images) // 2:
            # 中间图片
            intensity = 10
        else:
            # 后半部分图片
            if i == len(images) - 1:
                # 最后一张图片
                intensity = 0.1
            else:
                # 非最后一张
                intensity -= stepAfter
        # 调用glitch_image方法
        print(intensity)
        glitched_img = glitcher.glitch_image(clip_dir + '/' + image, intensity, intensity, color_offset=True)
        # 获取输出文件名
        output_name = os.path.join(clip_dir, image)
        # 保存输出文件
        glitched_img.save(output_name)
        # 将输出文件名添加到列表中
        glitched_list.append(output_name)
        # i递加
        i += 1
    # 图片序列转为视频
    glitched_transition = ImageSequenceClip(glitched_list, fps=30)
    # 返回
    return concatenate_videoclips([video1.subclip(0, duration1 - glitch_duration1), glitched_transition, video2.subclip(glitch_duration2)])



