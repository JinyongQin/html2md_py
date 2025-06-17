"""
 htms2mds.py
批量将 HTML 文件转换为 Markdown 格式。
依赖文件: htm2md.py
使用方法:
 python htms2mds.py <input_folder> <output_folder> [<count>]
"""

import os
import sys
from htm2md import html_to_markdown,post_process_markdown,pre_process_html

def batch_convert_html_to_md(input_folder, output_folder, count = -1):
    """
    批量转换 HTML 文件到 Markdown 格式。
    input_folder: 输入文件夹路径，包含 HTML 文件。
    output_folder: 输出文件夹路径，转换后的 Markdown 文件将保存到此处。
    count: 转换的文件数量，默认为 -1，表示转换所有文件。
           如果指定为正整数，则转换指定数量的文件。
           如果为 0，则不进行任何转换。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    i = 0
    for root, _, files in os.walk(input_folder):
        for file in files:
            if count > 0:
                if i >= count:
                    print(f"已转换 {count} 个文件，停止转换。")
                    return
                i += 1
            if file.lower().endswith(('.htm', '.html')):
                input_path = os.path.join(root, file)
                output_name = os.path.splitext(file)[0] + '.md'
                output_path = os.path.join(output_folder, output_name)

                print(f"正在转换: \t{input_path}...")

                with open(input_path, 'r', encoding='utf-8') as f:
                    html_data = f.read()
                html_data = pre_process_html(html_data)
                md_content = html_to_markdown(html_data)
                md_content = post_process_markdown(md_content)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                print(f"文件已保存: \t{output_path} !")



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python htms2mds.py <input_folder> <output_folder> [<count>]")
        sys.exit(1)
    htm_path = sys.argv[1]
    md_path = sys.argv[2]
    count = int(sys.argv[3]) if len(sys.argv) > 3 else -1
    batch_convert_html_to_md(htm_path, md_path , count)