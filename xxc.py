from spider import download_latest_ssrn_papers
from markdown import transform_ssrn_paper_to_markdown


# count:下载最近多少篇
# download_interval:下载间隔时间（秒), 过快防止爬虫被封
# output_file:保存的JSON文件路径
# json_file:保存的JSON文件路径,和output_file一致
# markdown_file:转换后的Markdown文件路径
# download_latest_ssrn_papers(count=10,download_interval=5,output_file='./ssrn/papers.json')
transform_ssrn_paper_to_markdown(json_file='./ssrn/papers.json',markdown_file='./ssrn/papers.md')