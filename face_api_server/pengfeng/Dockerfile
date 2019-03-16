FROM python
RUN mkdir -p /pengfeng/site/code && mkdir -p /pengfeng/site/code/log && mkdir -p /pengfeng/site/static && mkdir -p /pengfeng/site/media && mkdir -p /pengfeng/site/postgresql/data && mkdir -p /pengfeng/site/log && touch /pengfeng/site/code/log/pengfeng.log
WORKDIR	/pengfeng/site/code
COPY ./requirements.txt /pengfeng/site/code/requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . /pengfeng/site/code/