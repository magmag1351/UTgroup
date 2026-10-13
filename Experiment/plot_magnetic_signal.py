import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# 日本語フォントの設定 (Mac / Linux / Windows 互換)
try:
    import japanize_matplotlib
except (ImportError, ModuleNotFoundError):
    plt.rcParams['font.family'] = 'Hiragino Sans'


def parse_measurement(filename):
    """ファイル名末尾の _0 / _1 を判定して計測回数 (1st / 2nd) を返す"""
    fname = str(filename)
    if '_0.' in fname or fname.endswith('_0'):
        return '1st'
    elif '_1.' in fname or '_1csv.' in fname or fname.endswith('_1'):
        return '2nd'
    return 'Unknown'


def plot_magnetic_signal():
    script_dir = Path(__file__).parent.resolve()

    possible_paths = [
        script_dir / 'magnetic-signal.csv',
        Path('Experiment/source/261009_JMAG-実験データの比較/magnetic-signal.csv'),
        Path('source/261009_JMAG-実験データの比較/magnetic-signal.csv'),
        Path('magnetic-signal.csv'),
    ]

    csv_path = None
    for p in possible_paths:
        if p.exists():
            csv_path = p
            break

    if csv_path is None:
        raise FileNotFoundError("magnetic-signal.csv が見つかりませんでした。")

    print(f"データファイルを読み込みます: {csv_path}")

    # CSVの読み込み
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # 数値変換および計測回数の抽出
    df['最大磁束密度 [T]'] = pd.to_numeric(df['最大磁束密度 [T]'], errors='coerce')
    df['Raw_P2P[mV]'] = pd.to_numeric(df['Raw_P2P[mV]'], errors='coerce')
    df['計測回数'] = df['ファイル名'].apply(parse_measurement)

    # 出力先フォルダの作成
    output_dir = Path('results/261009_JMAG-実験データの比較')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 区間番号ごとにグルーピング
    grouped = df.groupby('区間番号')
    sections = sorted(df['区間番号'].dropna().unique())

    # 区間ごとの色定義 (1st / 2nd で濃淡・色合いを変えて区分)
    # 1st: 濃い色 (主色), 2nd: 明るい/異なる色 (副色)
    section_color_pairs = {
        'D1': {'1st': '#2ca02c', '2nd': '#98df8a'},  # 緑 (濃 / 薄)
        'D2': {'1st': '#d62728', '2nd': '#ff9896'},  # 赤 (濃 / 薄)
        'L1': {'1st': '#1f77b4', '2nd': '#aec7e8'},  # 青 (濃 / 薄)
        'L2': {'1st': '#ff7f0e', '2nd': '#ffbb78'},  # オレンジ (濃 / 薄)
        'L3': {'1st': '#9467bd', '2nd': '#c5b0d5'},  # 紫 (濃 / 薄)
        'L4': {'1st': '#8c564b', '2nd': '#c49c94'},  # 茶 (濃 / 薄)
    }

    # デフォルト用色設定
    default_colors = {'1st': '#1f77b4', '2nd': '#ff7f0e'}

    # マーカー形状 (区間ごとに識別しやすいマーカーを設定)
    section_markers = {
        'D1': '^',
        'D2': 'v',
        'L1': 'o',
        'L2': 's',
        'L3': 'D',
        'L4': 'p',
    }

    # -------------------------------------------------------------
    # 1. 区間番号ごとの個別散布図 (Individual Scatter Plots)
    # -------------------------------------------------------------
    print("\n1. 区間ごとの個別散布図を作成中...")
    # 個別プロット専用の1回目・2回目の強調色 (青 / オレンジ)
    indiv_colors = {'1st': '#1f77b4', '2nd': '#ff7f0e'}
    indiv_markers = {'1st': 'o', '2nd': 's'}

    for sec_name, group in grouped:
        fig, ax = plt.subplots(figsize=(7, 5))

        for meas in ['1st', '2nd']:
            m_group = group[group['計測回数'] == meas]
            if m_group.empty:
                continue
            
            c = indiv_colors.get(meas, 'blue')
            m = indiv_markers.get(meas, 'o')

            ax.scatter(
                m_group['最大磁束密度 [T]'],
                m_group['Raw_P2P[mV]'],
                color=c,
                marker=m,
                s=65,
                edgecolors='k',
                linewidth=0.5,
                label=f'Label: {sec_name} ({meas} Meas.)',
                zorder=3,
            )

        ax.set_xlim(0, 1.8)
        if sec_name in ['D1', 'D2']:
            ax.set_ylim(0, 4)
        else:
            ax.set_ylim(0, 20)
        ax.set_xlabel('Magnetic Field [T]', fontsize=12)
        ax.set_ylabel('Measured Voltage [V]', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(fontsize=11, loc='upper left')
        ax.set_title(f'伝搬波ラベル {sec_name}', fontsize=13, fontweight='bold')

        plt.tight_layout()
        save_path = output_dir / f'scatter_section_{sec_name}_separate.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f'   - 保存完了: [scatter_section_{sec_name}_separate.png]({save_path})')

    # -------------------------------------------------------------
    # 2. 全区間を1つのグラフに重ねた統合散布図 (Combined Overlay Scatter Plot)
    # -------------------------------------------------------------
    print("\n2. 全区間を1枚のグラフに重ねた散布図を作成中...")
    fig, ax = plt.subplots(figsize=(9.5, 6))

    for sec_name in sections:
        group = grouped.get_group(sec_name).sort_values(by='最大磁束密度 [T]')
        color_pair = section_color_pairs.get(sec_name, default_colors)
        marker = section_markers.get(sec_name, 'o')

        for meas in ['1st', '2nd']:
            m_group = group[group['計測回数'] == meas]
            if m_group.empty:
                continue
            
            c = color_pair.get(meas, 'blue')

            ax.scatter(
                m_group['最大磁束密度 [T]'],
                m_group['Raw_P2P[mV]'],
                color=c,
                marker=marker,
                s=65,
                edgecolors='k',
                linewidth=0.5,
                label=f'Label: {sec_name} ({meas})',
                zorder=3,
            )

    ax.set_xlim(0, 1.8)
    ax.set_ylim(0, 20)
    ax.set_xlabel('Magnetic Field [T]', fontsize=12)
    ax.set_ylabel('Measured Voltage [V]', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(fontsize=9.5, loc='upper left', bbox_to_anchor=(1.02, 1.0), ncol=1)
    ax.set_title('Scatter Plot - All Sections Overlay (Color-coded by Measurement)', fontsize=13, fontweight='bold')

    plt.tight_layout()
    combined_save_path = output_dir / 'scatter_all_sections_combined_separate_legend.png'
    plt.savefig(combined_save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'   - 保存完了: [scatter_all_sections_combined.png]({combined_save_path})')

    print("\nすべての散布図の作成・保存が正常に完了しました。")


if __name__ == '__main__':
    plot_magnetic_signal()
