import pandas as pd

def process_futures_data(futures_type):
    """
    处理指定品种的期货价差数据
    
    参数:
        futures_type (str): 期货品种，如 'if', 'ih', 'ic', 'im'
    
    返回:
        pd.DataFrame: 处理后的价差数据
    """
    # 读取数据
    df0 = pd.read_csv(f'{futures_type.upper()}00.csv')
    df1 = pd.read_csv(f'{futures_type.upper()}01.csv')
    df2 = pd.read_csv(f'{futures_type.upper()}02.csv')
    df3 = pd.read_csv(f'{futures_type.upper()}03.csv')
    
    # 选择需要的列并重命名
    dfs = []
    for i, df in enumerate([df0, df1, df2, df3]):
        df_selected = df[['trade_date', 'close']].rename(
            columns={'close': f'close_{futures_type}{i}'}
        )
        dfs.append(df_selected)
    
    # 合并数据
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='trade_date', how='inner')
    
    # 计算价差
    for i in range(3):
        for j in range(i+1, 4):
            col_name = f'price_spread_{futures_type}{i}_{futures_type}{j}'
            merged_df[col_name] = merged_df[f'close_{futures_type}{i}'] - merged_df[f'close_{futures_type}{j}']
    
    # 转换日期格式
    merged_df['trade_date'] = pd.to_datetime(merged_df['trade_date'], format='%Y%m%d')
    
    return merged_df

def process_all_futures():
    """处理所有期货品种的数据"""
    futures_types = ['if', 'ih', 'ic', 'im']
    results = {}
    
    for ft in futures_types:
        print(f"正在处理{ft.upper()}数据...")
        try:
            df = process_futures_data(ft)
            results[ft] = df
            print(f"{ft.upper()}描述统计:")
            print(df.describe())
            # 保存到CSV
            df.to_csv(f'{ft}_spread.csv', index=False)
            print(f"{ft.upper()}数据已保存到{ft}_spread.csv\n")
        except Exception as e:
            print(f"处理{ft.upper()}数据时出错: {e}\n")
    
    return results

if __name__ == "__main__":
    # 处理所有期货数据
    all_futures_data = process_all_futures()
