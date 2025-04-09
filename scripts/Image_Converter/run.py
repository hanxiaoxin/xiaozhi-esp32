from PIL import Image
import os
import tempfile
import sys
from LVGLImage import LVGLImage, ColorFormat, CompressMethod
import shutil

def clean_directory(directory):
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在。")
        return

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # 删除文件或符号链接
                print(f"已删除文件: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # 删除子目录及其内容
                print(f"已删除子目录: {item_path}")
        except Exception as e:
            print(f"删除 {item_path} 失败: {e}")


current_dir = os.getcwd()
# 拼接 images 文件夹路径
images_path = os.path.join(current_dir, "images")
output_path = os.path.join(current_dir, "output")


clean_directory(output_path)

print(images_path, output_path)

# 列出所有文件（过滤文件夹）
files = [
    (f"{images_path}/{f}") for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))
]
print(files)

def convert_images(input_files, width, height, compress):
    success_count = 0
    total_files = len(input_files)

    for idx, file_path in enumerate(input_files):
        try:
            print(f"正在处理: {os.path.basename(file_path)}")

            with Image.open(file_path) as img:
                # 调整图片大小
                img = img.resize((width, height), Image.Resampling.LANCZOS)

                # 处理颜色格式
                color_format_str = "自动识别"
                if color_format_str == "自动识别":
                    # 检测透明通道
                    has_alpha = img.mode in ("RGBA", "LA") or (
                        img.mode == "P" and "transparency" in img.info
                    )
                    if has_alpha:
                        img = img.convert("RGBA")
                        cf = ColorFormat.RGB565A8
                    else:
                        img = img.convert("RGB")
                        cf = ColorFormat.RGB565
                else:
                    if color_format_str == "RGB565A8":
                        img = img.convert("RGBA")
                        cf = ColorFormat.RGB565A8
                    else:
                        img = img.convert("RGB")
                        cf = ColorFormat.RGB565

                # 保存调整后的图片
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_image_path = os.path.join(
                    output_path, f"{base_name}_{width}x{height}.png"
                )
                # img.save(output_image_path, "PNG")

                # 创建临时文件
                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False
                ) as tmpfile:
                    temp_path = tmpfile.name
                    img.save(temp_path, "PNG")

                # 转换为LVGL C数组
                lvgl_img = LVGLImage().from_png(temp_path, cf=cf)
                output_c_path = os.path.join(output_path, f"{base_name}.c")
                lvgl_img.to_c_array(output_c_path, compress=compress)

                success_count += 1
                os.unlink(temp_path)
                print(f"成功转换: {base_name}.c\n")

        except Exception as e:
            print(f"转换失败: {str(e)}\n")

    print(f"转换完成! 成功 {success_count}/{total_files} 个文件\n")



convert_images(files, 64, 64, CompressMethod.NONE)


