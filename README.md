## Introduction
爬取每天ARXIV上最新paper(以软工SE为例)，整理成Markdown自动上传到GitHub

## Config
+ json目录存放Arxiv paper的json文件
+ markdown目录存放Arxiv paper的markdown文件
+ config/token.txt下存放GitHub API Key
+ const.py设置项目绝对路径
+ main.py设置
  + GitHub用户名
  + GitHub邮箱
  + GitHub远程仓库
  + 本地仓库

## Run
```shell
python main.py
```