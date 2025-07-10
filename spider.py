import os.path
from llm import *
import json
from datetime import date
import datetime
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from const import ROOT
import re


summary_prompt = """
请用简洁的语言根据摘要概括文章解决的问题，使用的技术等关键信息，不超100个字。
摘要如下:
{abstract}
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_arxiv_papers():
    url = "https://arxiv.org/list/cs.SE/new"

    # 发送 GET 请求
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return

    # 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 查找 h3 标签中包含 "new listings" 的元素
    title_element = soup.find("h3", string=lambda text: "Showing new listings for" in text)
    if title_element:
        that_day = title_element.get_text(strip=True).replace("Showing new listings for", "").strip()
    else:
        that_day = None

    # 找到 id="articles" 的元素
    articles_div = soup.find(id="articles")
    if not articles_div:
        print("未找到 id=articles 的元素")
        return

    # 提取所有 dt 和 dd 对
    papers = []
    for dt, dd in zip(articles_div.find_all("dt"), articles_div.find_all("dd")):
        if not dt or not dd:
            continue

        # 提取论文 ID
        paper_id = dt.find("a", href=True).get("id", "N/A")

        # 提取标题
        title_tag = dd.find("div", class_="list-title")
        title = title_tag.text.strip() if title_tag else "N/A"

        # 提取作者
        authors_tag = dd.find("div", class_="list-authors")
        authors = [a.text.strip() for a in authors_tag.find_all("a")] if authors_tag else ["N/A"]

        # 提取主题
        subjects_tag = dd.find("div", class_="list-subjects")
        subjects = subjects_tag.text.strip() if subjects_tag else "N/A"

        # 提取摘要
        abstract_tag = dd.find("p", class_="mathjax")
        abstract = abstract_tag.text.strip() if abstract_tag else "N/A"

        # 提取链接
        links = {
            "pdf": dt.find("a", id=lambda x: x and x.startswith("pdf-"))["href"] if dt.find("a", id=lambda
                x: x and x.startswith("pdf-")) else None,
            "html": dt.find("a", id=lambda x: x and x.startswith("html-"))["href"] if dt.find("a", id=lambda
                x: x and x.startswith("html-")) else None,
            "other": dt.find("a", id=lambda x: x and x.startswith("oth-"))["href"] if dt.find("a", id=lambda
                x: x and x.startswith("oth-")) else None
        }

        # 存入结果
        papers.append({
            "id": paper_id,
            "title": title,
            "authors": authors,
            "subjects": subjects,
            "abstract": abstract,
            "links": links
        })

    return that_day, papers

def parse_ssrn_papers():
    url='https://www.ssrn.com/index.cfm/en/mrn/'
    # 发送 GET 请求
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return

    # 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser")
    today_str = datetime.today().strftime("%d %b %Y")   # e.g. '10 Jul 2025'

    papers_today = []
    for info in soup.select("div.paper-info"):
        # —— 标题 & 下载地址 ——
        a_tag = info.select_one(".title a")
        title = a_tag.text.strip() if a_tag else ""
        url   = a_tag["href"] if a_tag and a_tag.has_attr("href") else ""

        # —— 发布日期 ——（形如 'Posted 10 Jul 2025'）
        stats = info.select_one(".stats")
        date_text = ""
        if stats:
            m = re.search(r"Posted\s+(\d{1,2}\s+\w{3}\s+\d{4})", stats.text)
            date_text = m.group(1) if m else ""

        # 只保留今日文章
        if date_text != today_str:
            continue

        # —— 发表状态 ——
        status_tag = info.select_one(".type.status span:nth-of-type(2)")
        status = status_tag.text.strip() if status_tag else ""

        # —— 作者列表 ——
        authors = [a.text.strip() for a in info.select(".authors a")]

        # —— 单位 / 机构 ——
        aff_tag = info.select_one(".affiliations")
        affiliation = aff_tag.text.strip() if aff_tag else ""

        papers_today.append({
            "title": title,
            "date": date_text,
            "authors": authors,
            "status": status,
            "affiliation": affiliation,
            "download_url": url
        })

    return papers_today


def download_latest_arxiv_papers():
    today = date.today()
    # 格式化输出（自定义格式）
    formatted_date = today.strftime("%Y-%m-%d")
    output_path = f'{ROOT}/json/arxiv-paper-{formatted_date}.json'
    if os.path.exists(output_path):
        return

    that_day, arxiv_papers = parse_arxiv_papers()
    for paper in arxiv_papers:
        abstract = paper['abstract']
        summary = generate(prompt=summary_prompt.format(abstract=abstract))[0]
        paper['summary'] = summary

    data = {
        'date': that_day,
        'papers': arxiv_papers
    }

    with open(output_path, 'w', encoding='utf8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


def download_latest_ssrn_papers():
    today = date.today()
    # 格式化输出（自定义格式）
    formatted_date = today.strftime("%Y-%m-%d")
    output_path = f'{ROOT}/json/ssrn-paper-{formatted_date}.json'
    if os.path.exists(output_path):
        return
    
    latest_ssrn_papers = parse_ssrn_papers()
    print(latest_ssrn_papers)

def __main__():
    download_latest_ssrn_papers()