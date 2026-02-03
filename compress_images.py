import os
from PIL import Image

def compress_images(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(directory, filename)
            with Image.open(filepath) as img:
                # 检查图片宽度是否大于1440
                if img.width > 1440:
                    # 计算等比例缩放的高度
                    ratio = 1440 / img.width
                    new_height = int(img.height * ratio)
                    # 调整图片大小
                    img = img.resize((1440, new_height), Image.LANCZOS)
                    # 保存压缩后的图片
                    if filename.lower().endswith('.png'):
                        img.save(filepath, optimize=True)
                    else:  # jpg, jpeg
                        img.save(filepath, optimize=True, quality=85)
                    print(f"已压缩: {filename}")
                elif img.width == 1440:
                    pass
                    # print(f"跳过: {filename} (宽度已经是1440)")
                else:
                    pass
                    # print(f"跳过: {filename} (宽度小于1440)")

if __name__ == "__main__":
    # 指定要压缩的目录
    assets_dir = 'content/assets'

    # 执行压缩
    compress_images(assets_dir)
    print("图片压缩完成")
