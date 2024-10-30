import requests
import pandas as pd
from datetime import datetime
import os
import logging
from pathlib import Path
import time

class DLTCrawler:
    """大乐透历史数据爬虫"""
    
    def __init__(self):
        self.base_url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
        self.setup_logging()
        self.setup_paths()

    def setup_logging(self):
        """配置日志"""
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    log_dir / f'dlt_crawler_{datetime.now().strftime("%Y%m%d")}.log', 
                    encoding='utf-8'
                )
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_paths(self):
        """设置文件路径"""
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / f"大乐透历史数据_{datetime.now().strftime('%Y%m%d')}.xlsx"

    def get_history_data(self, page_no):
        """获取历史数据"""
        params = {
            "gameNo": 85,
            "provinceId": 0,
            "pageSize": 30,
            "isVerify": 1,
            "pageNo": page_no,
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()['value']['list']
        except Exception as e:
            self.logger.error(f"获取数据失败: {e}")
            return None

    def parse_draw_result(self, draw_result):
        """解析开奖结果"""
        try:
            return {
                '期号': draw_result['lotteryDrawNum'],
                '开奖日期': draw_result['lotteryDrawTime'],
                '前区1': draw_result['lotteryDrawResult'].split(' ')[0],
                '前区2': draw_result['lotteryDrawResult'].split(' ')[1],
                '前区3': draw_result['lotteryDrawResult'].split(' ')[2],
                '前区4': draw_result['lotteryDrawResult'].split(' ')[3],
                '前区5': draw_result['lotteryDrawResult'].split(' ')[4],
                '后区1': draw_result['lotteryDrawResult'].split(' ')[5],
                '后区2': draw_result['lotteryDrawResult'].split(' ')[6],
                '奖池奖金(元)': draw_result['poolBalanceAmt'],
                '一等奖注数': draw_result['prizeLevelInfo'][0]['stakeCount'],
                '一等奖奖金(元)': draw_result['prizeLevelInfo'][0]['stakeAmount'],
                '二等奖注数': draw_result['prizeLevelInfo'][1]['stakeCount'],
                '二等奖奖金(元)': draw_result['prizeLevelInfo'][1]['stakeAmount'],
                '总投注额(元)': draw_result['totalSaleAmount']
            }
        except Exception as e:
            self.logger.error(f"解析数据失败: {e}")
            return None

    def get_latest_draw_num(self):
        """获取最新一期期号"""
        try:
            if self.file_path.exists():
                df = pd.read_excel(self.file_path)
                return df['期号'].iloc[0]
        except Exception as e:
            self.logger.error(f"读取现有文件失败: {e}")
        return None

    def save_to_excel(self, df):
        """保存数据到Excel"""
        try:
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                self._adjust_column_width(writer.sheets['Sheet1'])
            self.logger.info(f"数据已保存到: {self.file_path}")
        except Exception as e:
            self.logger.error(f"保存文件失败: {e}")

    def _adjust_column_width(self, worksheet):
        """调整Excel列宽"""
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

    def run(self):
        """运行爬虫"""
        self.logger.info("开始获取大乐透历史数据...")
        latest_draw_num = self.get_latest_draw_num()
        all_data = []
        page_no = 1

        while True:
            self.logger.info(f"正在获取第{page_no}页数据...")
            data = self.get_history_data(page_no)
            
            if not data:
                break
                
            for draw_result in data:
                if latest_draw_num and int(draw_result['lotteryDrawNum']) <= int(latest_draw_num):
                    break
                    
                parsed_result = self.parse_draw_result(draw_result)
                if parsed_result:
                    all_data.append(parsed_result)
                
            if latest_draw_num and len(data) > 0 and int(data[-1]['lotteryDrawNum']) <= int(latest_draw_num):
                break
                
            page_no += 1
            time.sleep(1)  # 添加延时，避免请求过快

        if not all_data:
            self.logger.info("没有新数据需要更新")
            return

        if latest_draw_num and self.file_path.exists():
            old_df = pd.read_excel(self.file_path)
            new_df = pd.DataFrame(all_data)
            df = pd.concat([new_df, old_df], ignore_index=True)
        else:
            df = pd.DataFrame(all_data)

        self.save_to_excel(df)
        self.logger.info("数据获取完成！")

def main():
    """主函数"""
    try:
        crawler = DLTCrawler()
        crawler.run()
    except Exception as e:
        logging.error(f"程序运行出错: {e}")

if __name__ == "__main__":
    main() 