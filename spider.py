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
import cloudscraper
import xml.etree.ElementTree as ET
import time
import jsonlines

scraper = cloudscraper.create_scraper(
    browser={'custom': 'ScraperBot/1.0 (+https://example.com/bot)'}
)  # 自动处理 CF


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


def download_latest_ssrn_papers(count=10,download_interval=5,output_file='./ssrn/papers.json'):
    url = f"https://api.ssrn.com/content/v1/bindings/200668/papers?index=0&count={count}&sort=0"
    resp = scraper.get(url, timeout=15)

    resp.raise_for_status()
    papers = parse_ssrn_xml(resp.text)
    for paper in papers:
        paper_detail = fetch_ssrn_abstract_and_keywords(paper['url'])
        time.sleep(download_interval) 
        paper['abstract'] = paper_detail['abstract']
        paper['keywords'] = paper_detail['keywords']
        paper['summary'] = generate(prompt=summary_prompt.format(abstract=paper_detail['abstract']))[0]
        print(paper)
        with jsonlines.open(output_file,'a') as f:
            f.write(paper)
    return papers


def parse_ssrn_xml(xml_text):
    root = ET.fromstring(xml_text)
    papers = []
    for paper in root.findall(".//papers"):
        title = paper.findtext("title", default="")
        if title=='':
            continue
        abstract_type = paper.findtext("abstract_type", default="")
        publication_status = paper.findtext("publication_status", default="")
        is_paid = paper.findtext("is_paid", default="false") == "true"
        reference = paper.findtext("reference", default="")
        page_count = paper.findtext("page_count", default="")
        url = paper.findtext("url", default="")
        downloads = paper.findtext("downloads", default="")
        approved_date = paper.findtext("approved_date", default="")
        affiliations = paper.findtext("affiliations", default="")

        # 提取作者列表
        authors = []
        for author in paper.findall(".//authors"):
            author_id = author.findtext("id", default="")
            first_name = author.findtext("first_name", default="")
            if first_name=='':
                continue
            last_name = author.findtext("last_name", default="")
            author_url = author.findtext("url", default="")
            authors.append({
                "id": author_id,
                "first_name": first_name,
                "last_name": last_name,
                "url": author_url
            })

        papers.append({
            "title": title,
            "abstract_type": abstract_type,
            "publication_status": publication_status,
            "is_paid": is_paid,
            "reference": reference,
            "page_count": page_count,
            "url": url,
            "downloads": downloads,
            "approved_date": approved_date,
            "affiliations": affiliations,
            "authors": authors
        })
    return papers

def fetch_ssrn_abstract_and_keywords(url):
    response = scraper.get(url, timeout=15)
    # response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取 abstract
    abstract_div = soup.find("div", class_="abstract-text")
    abstract = ""
    if abstract_div:
        abstract_paragraphs = abstract_div.find_all("p")
        abstract = " ".join(p.get_text(strip=True) for p in abstract_paragraphs if p.get_text(strip=True))

    # 获取 keywords
    strong_tag = soup.find("strong", string=lambda s: s and s.strip().startswith("Keywords:"))
    if not strong_tag:
        keywords=''
    else:
        p_element = strong_tag.find_parent('p')
        keywords=p_element.text.replace('Keywords:', '').strip()
    
    return {
        "abstract": abstract,
        "keywords": keywords
    }





