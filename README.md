# 大乐透历史数据采集工具

这是一个用于采集中国体育彩票大乐透开奖历史数据的Python工具。

## 功能特点

- 自动采集大乐透历史开奖数据
- 支持增量更新，避免重复采集
- 数据保存为Excel格式
- 包含完整的开奖信息（开奖号码、奖金、奖池等）
- 自动调整Excel列宽，方便查看

## 安装说明

1. 克隆仓库 

bash
git clone https://github.com/yourusername/lottery_crawler.git
cd lottery_crawler

2. 安装依赖
bash
pip install -r requirements.txt

## 使用方法

直接运行爬虫程序：
bash
python src/crawler.py


数据将保存在 `data` 目录下，格式为：`大乐透历史数据_YYYYMMDD.xlsx`

## 数据说明

采集的数据包含以下字段：
- 期号
- 开奖日期
- 前区号码（5个）
- 后区号码（2个）
- 奖池奖金
- 一等奖注数及奖金
- 二等奖注数及奖金
- 总投注额

## 注意事项

- 本工具仅用于学习交流
- 请合理控制采集频率
- 数据仅供参考，以官方开奖为准

## 许可证

