FROM python:3.12-slim
LABEL maintainer="https://github.com/pamdla"
LABEL team="victor@agent①②③⑦"
LABEL project="MindEchoAgent"
LABEL git.repo="https://github.com/pamdla/MindEchoAgent"

ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/ \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

WORKDIR /app

COPY requirements.txt .

RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main" >> /etc/apt/sources.list

RUN apt update \
    && apt install -y --no-install-recommends \
    && apt install -y git wget make gcc g++ \
    && apt install -y nodejs npm \
    && apt autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN npm config set registry https://registry.npmmirror.com

# RUN python -m spacy download zh_core_web_sm \
#     python -m spacy download en_core_web_sm

RUN pip3 install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
