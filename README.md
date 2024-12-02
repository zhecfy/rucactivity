# rucactivity

自动化查询与报名中国人民大学形势与政策活动，并发送邮件通知。可能也适用于微人大学务中心发布的其它类型活动。

部署在服务器或类似环境中连续运行时效果最佳。

## Installation

```bash
git clone https://github.com/zhecfy/rucactivity.git
cd rucactivity
pip install -r requirements.txt
```

微人大登录基于 ruclogin 包，需参考 https://github.com/panjd123/ruclogin 的步骤进行配置。

```bash
ruclogin
```

```bash
cp .env.example .env
vim .env
# 修改 .env 中的设置
```

## Usage

```bash
python rucactivity.py
```

添加到 crontab 以自动运行：

```bash
PYTHON_PATH=$(which python)
WORKDIR=$(pwd)

CRON_JOB="*/5 * * * * $PYTHON_PATH $WORKDIR/rucactivity.py >> $WORKDIR/rucactivity.log 2>&1 || killall chromedriver chrome ; tail -n 10000 $WORKDIR/rucactivity.log > $WORKDIR/tmp.log && mv $WORKDIR/tmp.log $WORKDIR/rucactivity.log"
# 若失败则杀死残留 chrome 进程，ruclogin 使用其它浏览器时修改为相应进程名

(crontab -l | grep -v -F "$CRON_JOB"; echo "$CRON_JOB") | crontab -
```

## How it works

每次运行时：查询该类型的未开始活动，尝试报名所有未报名（即不在排除列表中）且可报名的活动，并将报名成功的活动加入排除列表。

因此，每项活动最多自动报名一次，手动取消后不会重新报名。如果无法参加活动，请将名额留给其他同学！
