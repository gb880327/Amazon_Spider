# 虚拟环境安装
* pip3 install virtualenv
* virtualenv -p /usr/local/bin/python3.6 ./venv
* 激活虚拟环境 source venv/bin/activate
* 安装模块 pip3 install -r requirements.txt

# chromedriver 安装
* Linux 需要安装 Chromium yum --enablerepo=extras install epel-release && yum install chromium
* 根据 Chromiun 版本选择对应的 chromedriver版本 https://sites.google.com/a/chromium.org/chromedriver/downloads