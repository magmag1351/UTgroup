from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# 日本語フォントの設定 (Mac / Linux / Windows 互換)
try:
    import japanize_matplotlib
except (ImportError, ModuleNotFoundError):
    plt.rcParams['font.family'] = 'Hiragino Sans'

def generate_scatter_plots():
    excel_path = Path('./印可磁場とガイド波信号強度の関係.xlsx')
    if not excel_path.exists():
        excel_path = Path('./Experiment/印可磁場とガイド波信号強度の関係.xlsx')
    
    xl = pd.ExcelFile(excel_path)
    
    output_dir = Path('./results/260911_歪-励磁磁場')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sheets = ['キャンセルコイルなし', 'キャンセルコイルあり']
    genres = {
        'Raw': {'L1_col': 2, 'D1_col': 4},
        'HPF': {'L1_col': 8, 'D1_col': 10}
    }
    
    plot_info = []
    
    # 1. 各条件の純粋な散布図を作成・保存 (計4つ)
    for sheet_name in sheets:
        df_raw = xl.parse(sheet_name, header=None)
        data = df_raw.iloc[2:].reset_index(drop=True)
        mag_field = pd.to_numeric(data[1], errors='coerce')
        
        for genre_name, col_dict in genres.items():
            l1_vals = pd.to_numeric(data[col_dict['L1_col']], errors='coerce')
            d1_vals = pd.to_numeric(data[col_dict['D1_col']], errors='coerce')
            
            fig, ax = plt.subplots(figsize=(7, 5))
            
            # 純粋な散布図 (線なし)
            ax.scatter(mag_field, l1_vals, label='L1', color='#1f77b4', s=60, marker='o', edgecolors='k', linewidth=0.5, zorder=3)
            ax.scatter(mag_field, d1_vals, label='D1', color='#ff7f0e', s=60, marker='s', edgecolors='k', linewidth=0.5, zorder=3)
            
            # タイトルなし
            ax.set_xlabel('MagneticField [T]', fontsize=12)
            ax.set_ylabel('Measured Voltage [mV]', fontsize=12)
            
            # x軸リミット: [0, 2.1], y軸リミット: [0, 20.0]
            ax.set_xlim(0, 2.1)
            ax.set_ylim(0, 20.0)
            
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(fontsize=11, loc='best')
            
            plt.tight_layout()
            filename = output_dir / f'scatter_{sheet_name}_{genre_name}.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            plot_info.append({
                'sheet': sheet_name,
                'genre': genre_name,
                'mag_field': mag_field,
                'l1': l1_vals,
                'd1': d1_vals,
                'filename': filename
            })
            print(f'グラフを保存しました: {filename}')
            
    # 2. 4つの純粋な散布図を1枚にまとめた2x2統合図の作成
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for idx, p in enumerate(plot_info):
        r, c = divmod(idx, 2)
        ax = axes[r, c]
        
        ax.scatter(p['mag_field'], p['l1'], label='L1', color='#1f77b4', s=50, marker='o', edgecolors='k', linewidth=0.5, zorder=3)
        ax.scatter(p['mag_field'], p['d1'], label='D1', color='#ff7f0e', s=50, marker='s', edgecolors='k', linewidth=0.5, zorder=3)
        
        # タイトルなし
        ax.set_xlabel('MagneticField [T]', fontsize=11)
        ax.set_ylabel('Measured Voltage [mV]', fontsize=11)
        
        # x軸リミット: [0, 2.1], y軸リミット: [0, 20.0]
        ax.set_xlim(0, 2.1)
        ax.set_ylim(0, 20.0)
        
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(fontsize=10, loc='best')
        
    plt.tight_layout()
    summary_filename = output_dir / 'scatter_plots_summary_2x2.png'
    plt.savefig(summary_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'2x2統合グラフを保存しました: {summary_filename}')

if __name__ == '__main__':
    generate_scatter_plots()
