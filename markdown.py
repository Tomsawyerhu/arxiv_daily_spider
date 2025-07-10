import json
import os.path
from datetime import date, datetime
import jsonlines
from const import ROOT


def json_to_markdown(json_data, output_file="output.md"):
    with open(output_file, "w", encoding="utf-8") as f:
        # 写入日期标题
        f.write(f"# {json_data['date']}\n\n")

        for paper in json_data["papers"]:
            title = paper["title"].replace("Title:\n          ", "").strip()
            authors = ", ".join(paper["authors"])
            summary = paper["summary"]

            # 写入论文标题和基本信息
            f.write(f"## {title}\n\n")
            f.write(f"### 作者\n{authors}\n\n")
            f.write(f"### 摘要\n{paper['abstract']}\n\n")
            f.write(f"### 总结\n{summary}\n\n")

            # 写入链接
            if "html" in paper["links"].keys():
                f.write("### 下载链接\n")
                f.write(f"- [HTML]({paper['links']['html']})\n")

            f.write("-" * 60 + "\n\n")

    print(f"✅ Markdown 文件已保存为 {output_file}")


# 示例调用（假设你的 JSON 存在变量中）
def transform_arxiv_paper_to_json():
    # 假设你的 JSON 数据已经加载到 `data` 变量中
    today = date.today()
    # 格式化输出（自定义格式）
    formatted_date = today.strftime("%Y-%m-%d")
    target_file = f"{ROOT}/json/arxiv-paper-{formatted_date}.json"
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    date_str = data["date"]
    # 使用 strptime 解析字符串为 datetime 对象
    date_obj = datetime.strptime(date_str, "%A, %d %B %Y").date()

    output_file = f'{ROOT}/markdown/arxiv-paper-{date_obj}.md'
    if os.path.exists(output_file):
        pass
    else:
        json_to_markdown(data,output_file)


def transform_ssrn_paper_to_markdown(json_file='',markdown_file=''):

    """
    将文章JSON数据转换为美观的Markdown格式字符串
    
    参数:
        article_json: 包含单篇文章信息的JSON字典
    
    返回:
        str: 转换后的Markdown字符串
    """
    markdown_str=''
    with jsonlines.open(json_file,'r') as f:
        for line in f:
            article_json = line
            # 构建Markdown内容列表
            md_parts = []
            
            # 添加标题（一级标题）
            title = article_json.get('title', '无标题')
            md_parts.append(f"# {title}\n")
            
            # 添加基本信息（二级标题 + 列表）
            md_parts.append("## 基本信息")
            info_list = []
            
            # 作者信息
            authors = article_json.get('authors', [])
            author_names = [f"{a.get('first_name', '')} {a.get('last_name', '')}" for a in authors]
            info_list.append(f"- 作者: {', '.join(author_names)}")
            
            # 机构信息
            affiliations = article_json.get('affiliations', '未提供')
            info_list.append(f"- 机构: {affiliations.replace('<i>', '*').replace('</i>', '*')}")
            
            # 发表状态
            pub_status = article_json.get('publication_status', '未知')
            info_list.append(f"- 状态: {pub_status}")
            
            # 页面数量
            page_count = article_json.get('page_count', '未知')
            info_list.append(f"- 页数: {page_count}")
            
            # 下载量
            downloads = article_json.get('downloads', '未知')
            info_list.append(f"- 下载量: {downloads}")
            
            # 批准日期
            approved_date = article_json.get('approved_date', '未知')
            info_list.append(f"- 批准日期: {approved_date}")
            
            # 访问链接
            url = article_json.get('url', '')
            if url:
                info_list.append(f"- 链接: [查看原文]({url})")
            
            # 添加信息列表
            md_parts.extend(info_list)
            md_parts.append("")  # 空行分隔
            
            # 添加关键词（二级标题 + 标签样式）
            keywords = article_json.get('keywords', '')
            if keywords:
                md_parts.append("## 关键词")
                keywords_list = keywords.split(', ')
                # 使用粗体和竖线分隔的标签样式
                md_parts.append(f"**{' | '.join(keywords_list)}**\n")
            
            # 添加摘要（二级标题 + 引用块）
            abstract = article_json.get('abstract', '无摘要')
            md_parts.append("## 摘要")
            # 使用引用块突出显示摘要
            md_parts.append(f"> {abstract}\n")
            
            # 添加中文摘要（如果有）
            summary = article_json.get('summary', '')
            if summary:
                md_parts.append("## 中文摘要")
                md_parts.append(f"> {summary}\n")
            
            # 合并所有部分，返回最终Markdown
            markdown_str+= '\n'.join(md_parts)+'\n***\n\n\n'
    with open(markdown_file,'w') as ff:
        ff.write(markdown_str)
    