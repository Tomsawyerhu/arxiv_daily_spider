import cloudscraper
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import requests
import time

scraper = cloudscraper.create_scraper(
    browser={'custom': 'ScraperBot/1.0 (+https://example.com/bot)'}
)  # 自动处理 CF


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

url = "https://api.ssrn.com/content/v1/bindings/200668/papers?index=0&count=10&sort=0"
resp = scraper.get(url, timeout=15)

resp.raise_for_status()
papers = parse_ssrn_xml(resp.text)
for paper in papers:
    paper_detail = fetch_ssrn_abstract_and_keywords(paper['url'])
    time.sleep(5)
    print(paper_detail)

print(papers)
