import json
import os.path
from datetime import date, datetime

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
