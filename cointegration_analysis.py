import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint, adfuller
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import os

# 设置中文字体
import platform
import matplotlib as mpl

if platform.system() == 'Windows':
    font_name = 'SimHei'
elif platform.system() == 'Darwin':  # macOS
    font_name = 'Arial Unicode MS'
else:  # Linux
    font_name = 'WenQuanYi Zen Hei'

plt.rcParams['font.sans-serif'] = [font_name, 'SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

class CointegrationAnalyzer:
    def __init__(self, futures_types: List[str] = ['if', 'ih', 'ic', 'im']):
        """
        初始化协整分析器
        
        参数:
            futures_types: 期货品种列表，如 ['if', 'ih', 'ic', 'im']
        """
        self.futures_types = [ft.lower() for ft in futures_types]
        self.results = {}
    
    def load_data(self, futures_type: str) -> pd.DataFrame:
        """加载期货价差数据"""
        file_path = f"data/{futures_type.lower()}_spread.csv"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在，请先运行 process_futures.py 生成数据")
        
        df = pd.read_csv(file_path)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df
    
    def perform_adf_test(self, series: pd.Series, series_name: str = "") -> dict:
        """
        执行ADF检验并返回结果
        
        返回:
            dict: 包含ADF统计量、p值、临界值等信息的字典
        """
        # 删除NaN值
        series = series.dropna()
        
        # 执行ADF检验
        result = adfuller(series, autolag='AIC')
        
        # 整理结果
        adf_result = {
            'series_name': series_name,
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] <= 0.05  # 5%显著性水平
        }
        
        return adf_result
    
    def analyze_spread_combinations(self, futures_type: str) -> Dict[str, dict]:
        """分析指定品种的所有价差组合"""
        df = self.load_data(futures_type)
        
        # 获取所有价差列
        spread_cols = [col for col in df.columns if col.startswith('price_spread')]
        
        results = {}
        for col in spread_cols:
            # 提取合约对，例如 price_spread_00_01 -> (00, 01)
            contracts = col.split('_')[-2:]
            pair_name = f"{contracts[0]}-{contracts[1]}"
            
            # 执行ADF检验
            result = self.perform_adf_test(df[col], pair_name)
            results[pair_name] = result
        
        return results
    
    def analyze_all_futures(self):
        """分析所有期货品种的所有价差组合"""
        all_results = {}
        
        for ft in self.futures_types:
            try:
                print(f"\n正在分析 {ft.upper()} 的价差组合...")
                results = self.analyze_spread_combinations(ft)
                all_results[ft.upper()] = results
                print(f"完成 {ft.upper()} 的分析")
            except Exception as e:
                print(f"分析 {ft.upper()} 时出错: {str(e)}")
        
        self.results = all_results
        return all_results
    
    def generate_summary_table(self) -> pd.DataFrame:
        """生成汇总表格"""
        if not self.results:
            self.analyze_all_futures()
        
        summary_data = []
        
        for ft, contracts in self.results.items():
            for pair_name, result in contracts.items():
                summary_data.append({
                    '品种': ft.upper(),
                    '合约对': pair_name,
                    'ADF统计量': f"{result['adf_statistic']:.4f}",
                    'p值': f"{result['p_value']:.4f}",
                    '1%临界值': f"{result['critical_values']['1%']:.4f}",
                    '5%临界值': f"{result['critical_values']['5%']:.4f}",
                    '10%临界值': f"{result['critical_values']['10%']:.4f}",
                    '是否平稳(5%显著性)': '是' if result['is_stationary'] else '否'
                })
        
        return pd.DataFrame(summary_data)

if __name__ == "__main__":
    # 使用示例
    analyzer = CointegrationAnalyzer()
    
    # 分析所有期货品种
    results = analyzer.analyze_all_futures()
    
    # 生成并显示汇总表格
    summary_df = analyzer.generate_summary_table()
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print("\n" + "="*80)
    print("期货价差平稳性检验结果汇总:")
    print("-"*80)
    print(summary_df)
    print("="*80 + "\n")
    
    # 保存结果到CSV
    summary_df.to_csv('cointegration_results.csv', index=False, encoding='utf-8-sig')
    print("结果已保存至: cointegration_results.csv")
