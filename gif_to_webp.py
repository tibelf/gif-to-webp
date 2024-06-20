import os
import imageio
from PIL import Image
import argparse

def resize_and_crop_image(img, max_width=800, min_aspect_ratio=1, max_aspect_ratio=1):
    # 获取原始图像尺寸
    width, height = img.size

    # 计算当前图像的宽高比
    aspect_ratio = width / height

    # 如果宽高比在指定范围内，则直接返回原始图像
    if min_aspect_ratio <= aspect_ratio <= max_aspect_ratio and width <= max_width:
        return img

    # 计算调整后的宽度和高度
    if aspect_ratio < min_aspect_ratio:
        # 宽高比过小，进行裁剪
        target_width = int(height * min_aspect_ratio)
        img = img.crop(((width - target_width) // 2, 0, (width + target_width) // 2, height))
        width, height = img.size

    # 如果宽高比超过最大允许值，则进行裁剪
    if aspect_ratio > max_aspect_ratio:
        target_height = int(width / max_aspect_ratio)
        img = img.crop((0, (height - target_height) // 2, width, (height + target_height) // 2))
        width, height = img.size

    # 计算等比例缩放后的高度
    target_height = int(height * max_width / width)

    # 缩放图像
    resized_img = img.resize((max_width, target_height), Image.LANCZOS)

    return resized_img

def convert_gif_to_webp(gif_path, webp_path, max_size_mb=20):
    # 逐帧读取GIF文件
    gif_reader = imageio.get_reader(gif_path)
    frames = []
    durations = []

    for frame in gif_reader:
        # 将每一帧从imageio格式转换为Pillow格式
        img = Image.fromarray(frame)
        # 调整图像尺寸并裁剪
        resized_img = resize_and_crop_image(img)
        frames.append(resized_img)
    
    # 尝试获取GIF的元数据中的持续时间
    try:
        meta = gif_reader.get_meta_data()
        duration = meta['duration'] if 'duration' in meta else 100  # 默认100毫秒
    except KeyError:
        duration = 100  # 如果获取不到元数据，则使用默认值

    # 使用获取到的元数据持续时间填充每帧的持续时间
    durations = [duration] * len(frames)

    # 设置初始质量值
    quality = 85
    target_size_bytes = max_size_mb * 1024 * 1024  # 将 MB 转换为字节

    # 尝试生成 WebP 文件，调整质量以控制文件大小
    while True:
        # 将帧保存为动画WebP文件
        frames[0].save(
            webp_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,  # 使用GIF的帧持续时间
            loop=0,  # 循环次数，0表示无限循环
            quality=quality  # 设置压缩质量
        )

        # 检查生成的文件大小
        if os.path.getsize(webp_path) <= target_size_bytes:
            break
        
        # 调整质量，以尝试使文件大小在指定范围内
        quality -= 5
        if quality <= 0:
            break

def batch_convert_gif_to_webp(folder_path):
    # 获取文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.gif'):
            gif_path = os.path.join(folder_path, filename)
            webp_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.webp")
            print(f"Converting {gif_path} to {webp_path}...")
            convert_gif_to_webp(gif_path, webp_path)
            print(f"Conversion complete: {webp_path}")

if __name__ == "__main__":
    # 使用argparse解析命令行参数
    parser = argparse.ArgumentParser(description="Convert GIF files to WebP format.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing GIF files.")
    args = parser.parse_args()

    # 批量转换GIF文件为WebP格式
    batch_convert_gif_to_webp(args.folder_path)

