import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import platform
import os

# 设置中文字体
if platform.system() == 'Windows':
    font_name = 'SimHei'
elif platform.system() == 'Darwin':  # macOS
    font_name = 'Arial Unicode MS'  # macOS系统通常自带这个字体
else:  # Linux
    font_name = 'WenQuanYi Zen Hei'  # 文泉驿正黑

# 设置matplotlib使用中文字体
plt.rcParams['font.sans-serif'] = [font_name, 'SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']
# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

def load_futures_data(futures_type):
    """加载期货数据"""
    file_path = f"{futures_type.lower()}_spread.csv"
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在，请先运行 process_futures.py 生成数据")
        return None
    df = pd.read_csv(file_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    return df

# 定义不同期货品种的颜色
FUTURES_COLORS = {
    'if': '#1f77b4',  # 蓝色
    'ih': '#ff7f0e',  # 橙色
    'ic': '#2ca02c',  # 绿色
    'im': '#d62728'   # 红色
}

def plot_futures_spreads(futures_type):
    """绘制指定品种的价差图"""
    df = load_futures_data(futures_type)
    if df is None:
        return
    
    # 获取所有价差列
    spread_cols = [col for col in df.columns if col.startswith('price_spread')]
    if not spread_cols:
        print(f"未找到 {futures_type} 的价差数据列")
        return
    
    # 创建子图
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    fig.suptitle(f'{futures_type.upper()} 各合约价差走势', fontsize=16)
    
    # 获取当前品种的颜色
    color = FUTURES_COLORS.get(futures_type.lower(), '#1f77b4')  # 默认蓝色
    
    # 展平axes数组以便于迭代
    axes = axes.flatten()
    
    # 绘制每个价差
    for i, col in enumerate(spread_cols):
        if i >= len(axes):  # 防止数组越界
            break
            
        ax = axes[i]
        ax.plot(df['trade_date'], df[col], 
                label=col.replace('_', ' ').upper(),
                color=color,
                linewidth=1.5)
        ax.set_title(f'{col.replace("_", " ").upper()}')
        ax.set_xlabel('日期')
        ax.set_ylabel('价差')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.tick_params(axis='x', rotation=45)
    
    # 如果子图数量不是6的倍数，隐藏多余的子图
    for j in range(len(spread_cols), len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout()
    plt.savefig(f'{futures_type.lower()}_spreads.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_futures_distributions(futures_type):
    """绘制指定品种的价差分布直方图"""
    df = load_futures_data(futures_type)
    if df is None:
        return
    
    # 获取所有价差列
    spread_cols = [col for col in df.columns if col.startswith('price_spread')]
    if not spread_cols:
        print(f"未找到 {futures_type} 的价差数据列")
        return
    
    # 创建子图
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    fig.suptitle(f'{futures_type.upper()} 各合约价差分布', fontsize=16)
    
    # 获取当前品种的颜色
    color = FUTURES_COLORS.get(futures_type.lower(), '#1f77b4')  # 默认蓝色
    
    # 展平axes数组以便于迭代
    axes = axes.flatten()
    
    # 绘制每个价差的分布
    for i, col in enumerate(spread_cols):
        if i >= len(axes):  # 防止数组越界
            break
            
        ax = axes[i]
        ax.hist(df[col], 
                bins='auto', 
                color=color, 
                edgecolor='white', 
                alpha=0.7,
                density=True)  # 显示密度而不是计数
        
        # 添加核密度估计(KDE)曲线
        import seaborn as sns
        sns.kdeplot(df[col].dropna(), color=color, ax=ax, linewidth=2)
        
        ax.set_title(f'{col.replace("_", " ").upper()}')
        ax.set_xlabel('价差')
        ax.set_ylabel('密度')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加均值和标准差标注
        mean = df[col].mean()
        std = df[col].std()
        ax.axvline(mean, color='red', linestyle='dashed', linewidth=1)
        ax.text(0.7, 0.9, f'均值: {mean:.2f}\n标准差: {std:.2f}',
                transform=ax.transAxes, fontsize=9)
    
    # 如果子图数量不是6的倍数，隐藏多余的子图
    for j in range(len(spread_cols), len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout()
    plt.savefig(f'{futures_type.lower()}_distributions.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_all_futures_spreads():
    """绘制所有期货品种的价差图"""
    futures_types = ['if', 'ih', 'ic', 'im']
    
    for ft in futures_types:
        print(f"正在生成 {ft.upper()} 的价差图...")
        plot_futures_spreads(ft)
        plot_futures_distributions(ft)

if __name__ == "__main__":
    plot_all_futures_spreads()
