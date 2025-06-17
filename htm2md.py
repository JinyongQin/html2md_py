"""
htm2md.py
将HTML文件(.htm .html)转换为Markdown(.md )格式。
依赖：BeautifulSoup4, lxml
使用方法：
python htm2md.py <input_file.htm> <output_file.md>
"""




from bs4 import BeautifulSoup, Tag
import re
import sys

def pre_process_html(html_content):
    """
    将HTML中直接位于<body>下、未被任何标签包裹的裸文本用<p>标签包裹。
    """
    soup = BeautifulSoup(html_content, "lxml")
    body = soup.body
    if not body:
        return html_content

    # 收集需要包裹的节点
    naked_texts = []
    for child in list(body.children):
        if isinstance(child, str) and child.strip():
            naked_texts.append(child)

    # 用<p>包裹裸文本
    for naked in naked_texts:
        new_p = soup.new_tag("p")
        new_p.string = naked
        naked.replace_with(new_p)

    return str(soup)

def html_to_markdown(html_content):
    """
    将HTML内容转换为Markdown格式。
    """
    soup = BeautifulSoup(html_content, "lxml")

    # 移除非内容标签
    for tag in soup(["head", "script", "style", "noscript", "meta"]):
        tag.decompose()

    def process_element(element):
        if not isinstance(element, Tag):
            return str(element).replace('\t', '')

        tag = element.name
        contents = ''.join(process_element(child) for child in element.children)
        match tag:
            # 标题
            case 'h1':
                return f'\n# {contents.strip()}\n'
            case 'h2':
                return f'\n## {contents.strip()}\n'
            case 'h3':
                return f'\n### {contents.strip()}\n'
            case 'h4':
                return f'\n#### {contents.strip()}\n'
            case 'h5':
                return f'\n##### {contents.strip()}\n'
            case 'h6':
                return f'\n###### {contents.strip()}\n'
            # 文本
            case 'p':
                stripped = contents.strip()
                return f'{stripped}\n'
             # 换行
            case 'br':
                return '\n'
            #强调
            case 'strong' | 'b':
                return f' **{contents.strip()}** '
            case 'em' | 'i':
                return f' *{contents.strip()}* '
            # 删除线
            case 'del' | 's':
                return f'~~{contents.strip()}~~'
            # 链接
            case 'a':
                href = element.get('href', '')
                title = element.get('title', '')
                title_str = f' "{title}"' if title else ''
                # return f'[{contents}]({href}{title_str})' if href else contents
                contents = contents.strip()
                return f'[{contents}]({title_str}) ' if href else contents
            # 图片
            case 'img':
                src = element.get('src', '')
                alt = element.get('alt', '')
                title = element.get('title', '')
                title_str = f' "{title}"' if title else ''
                return f'![{alt}]({src}{title_str}) ' if src else '\n'
            # 列表
            case 'ul'| 'ol':
                return process_list(element)
            # 列表项
            case 'li':
                return ''.join(process_element(child) for child in element.children)
            # 引用块
            case 'blockquote':
                lines = contents.strip().split('\n')
                quoted_lines = '\n'.join([f'> {line}' for line in lines])
                return f'{quoted_lines}\n\n'
            # 代码块
            case 'code':
                parent = element.parent.name if element.parent else ''
                if parent == 'pre':
                    lang = detect_code_language(contents)
                    code_block = f'```{lang}\n{contents.strip()}\n```'
                    return f'\n{code_block}\n\n'
                else:
                    return f'`{contents.strip()}`'
            case 'pre':
                code_tag = element.find('code')
                if code_tag:
                    return process_element(code_tag)
                else:
                    return f'\n```\n{element.get_text().strip()}\n```\n\n'
            # 分割线
            case 'hr':
                return '\n---\n\n'
            # 表格
            case 'table':
                return convert_table_to_markdown(element) + '\n\n'
            case _:
                return contents


    # def process_list(tag_element, depth=0):
    #     is_ordered = tag_element.name == 'ol'
    #     items = tag_element.find_all('li', recursive=False)
    #     list_items = []
    #     for i, li in enumerate(items):
    #         # 获取当前 <li> 内容（去掉子列表内容，避免重复解析）
    #         inner_content = ''
    #         for child in li.children:
    #             if child.name not in ('ul', 'ol'):
    #                 processed = process_element(child)
    #                 if processed.strip():
    #                     inner_content += processed
    #         # 构造当前项
    #         indent = '  ' * depth
    #         prefix = f'{i + 1}.' if is_ordered else '-'
    #         line = f'{indent}{prefix} {inner_content.strip()+" "}'
    #         # 查找子列表（ul/ol），如果有则递归处理
    #         sublists = li.find_all(['ul', 'ol'], recursive=False)
    #         for sublist in sublists:
    #             sublist_md = process_list(sublist, depth + 1)
    #             line += '\n' + sublist_md
    #         list_items.append(line)
    #     return '\n'.join(list_items) + '\n'

    def process_list(tag_element, depth=0):
        is_ordered = tag_element.name == 'ol'
        items = tag_element.find_all('li', recursive=False)
        list_items = []
        for i, li in enumerate(items):
            indent = '  ' * depth
            prefix = f'{i + 1}.' if is_ordered else '-'
            # 处理li的所有子节点，合并p和ul/ol
            lines = []
            for child in li.children:
                if isinstance(child, Tag) and child.name in ('ul', 'ol'):
                    # 子列表，递归处理并加一个回车
                    sublist_md = process_list(child, depth + 1)
                    if sublist_md.strip():
                        lines.append(sublist_md.rstrip() + '\n')
                elif isinstance(child, Tag) and child.name == 'p':
                    # 段落，去除多余空行
                    p_content = process_element(child).strip()
                    if p_content:
                        lines.append(p_content)
                else:
                    # 其他内容
                    content = process_element(child).strip()
                    if content:
                        lines.append(content)
            # 合并内容
            inner_content = '\n'.join(lines)
            # 首行加前缀，后续行缩进
            split_lines = inner_content.split('\n')
            first_line = f'{indent}{prefix} {split_lines[0]}'
            other_lines = [f'{indent}  {line}' if line.strip() else '' for line in split_lines[1:]]
            list_items.append('\n'.join([first_line] + other_lines))
        return '\n'.join(list_items) + '\n'

    def detect_code_language(text):
        if text.startswith('!') or 'sh' in text.lower():
            return 'bash'
        elif 'python' in text.lower():
            return 'python'
        elif 'cpp' in text.lower():
            return 'cpp'
        elif 'csharp' in text.lower():
            return 'csharp'
        else:
            return ''

    def convert_table_to_markdown(table):
        # 判断是否为复杂表格（有rowspan/colspan/嵌套表格）
        def is_complex_table(table):
            if table.find('img'):
                # print("img found!")
                return True
            for tr in table.find_all('tr'):
                for td in tr.find_all(['td', 'th']):
                    if td.has_attr('rowspan') or td.has_attr('colspan'):
                        return True
                    if td.find('table'):
                        return True
            return False

        if is_complex_table(table):
            def simplify_html(tag):
                if not isinstance(tag, Tag):
                    return str(tag)
                if tag.name in ['table', 'tr', 'td', 'th', 'img']:
                    children = ''.join(simplify_html(child) for child in tag.children)
                    if tag.name == 'img':
                        attrs = ' '.join(f'{k}="{v}"' for k, v in tag.attrs.items())
                        return f'<img {attrs}/>'
                    # 保留rowspan属性(跨行单元格)
                    attrs = ''
                    if tag.has_attr('rowspan'):
                        attrs += f' rowspan="{tag["rowspan"]}"'
                    return f'<{tag.name}{attrs}>{children}</{tag.name}>'
                else:
                    return ''.join(simplify_html(child) for child in tag.children)

            simple_html = simplify_html(table)
            return f'\n{simple_html}\n\n'
        # 简单表格，转换为Markdown
        rows = table.find_all('tr')
        if not rows:
            return ''

        markdown_rows = []
        for row in rows:
            cells = row.find_all(['td', 'th'])
            # 将单元格内的换行替换为空格，避免破坏Markdown表格
            markdown_cells = [
                cell.get_text(separator=' ', strip=True).replace('\n', ' ').replace('\r', '') + ' '
                for cell in cells
            ]
            markdown_rows.append(markdown_cells)

        if len(markdown_rows) < 1:
            return ''

        # 表头
        header = '| ' + ' | '.join(markdown_rows[0]) + ' |'

        # 分隔行
        separator = '| ' + ' | '.join(['---'] * len(markdown_rows[0])) + ' |'

        # 数据行
        body = '\n'.join(['| ' + ' | '.join(row) + ' |' for row in markdown_rows[1:]])

        return '\n\n' + '\n'.join([header, separator, body]) + '\n\n'

    markdown = process_element(soup)
    markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()
    return markdown


def post_process_markdown(md_content):
    """
    对Markdown内容进行后处理,去除1~8行无用内容
    """
    lines = md_content.split('\n')
    lines = lines[7:]
    return '\n'.join(lines).strip()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python htm2md.py <input_file.htm> <output_file.md>")
        sys.exit(1)
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'example.htm'
    if not input_file.endswith('.htm'):
        print("错误：输入文件必须是 .htm 格式！")
        sys.exit(1)
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.md'
    if not output_file.endswith('.md'):
        print("错误：输出文件必须是 .md 格式！")
        sys.exit(1)
    with open(input_file, 'r', encoding='utf-8') as f:
        html_data = f.read()
        
    html_data = pre_process_html(html_data)
    md_content = html_to_markdown(html_data)
    md_content = post_process_markdown(md_content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print("转换完成！")