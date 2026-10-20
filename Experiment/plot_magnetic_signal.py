import os
import platform
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# conf
project_name = "261014_JMAG-実験"
summary_csv_filename = 'p2p_summary.csv'
target_signal = 'Raw_P2P[mV]'  # 'Raw_P2P[mV]' または 'HPF_P2P[mV]' ('Raw', 'HPF' でも可)
plot_mode = 'all'  # 'all' (全計測回数を個別に表示) または 'mean' (ケースごとの平均値を代表点として表示)

# シグナル種別の判定
if 'HPF' in str(target_signal).upper():
    signal_col = 'HPF_P2P[mV]'
    signal_type = 'HPF'
else:
    signal_col = 'Raw_P2P[mV]'
    signal_type = 'Raw'

# プロットモードの判定 ('all' または 'mean')
is_mean_mode = str(plot_mode).lower() in ['mean', 'average', 'avg']
mode_tag = '_mean' if is_mean_mode else ''
mode_title = '平均値 (Mean)' if is_mean_mode else '全計測 (All Measurements)'

# 日本語フォントの設定 (Mac / Linux / Windows 互換)
try:
    import japanize_matplotlib
except (ImportError, ModuleNotFoundError):
    system = platform.system()
    if system == 'Darwin':
        plt.rcParams['font.family'] = 'Hiragino Sans'
    elif system == 'Windows':
        plt.rcParams['font.family'] = 'MS Gothic'
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'


def parse_measurement(filename):
    """ファイル名末尾の _0 / _1 / _2 を判定して計測回数 (1st / 2nd / 3rd) を返す"""
    fname = Path(str(filename)).name.lower()
    if '_0.' in fname or '_0csv' in fname or fname.endswith('_0'):
        return '1st'
    elif '_1.' in fname or '_1csv' in fname or fname.endswith('_1'):
        return '2nd'
    elif '_2.' in fname or '_2csv' in fname or fname.endswith('_2'):
        return '3rd'
    return 'Unknown'


def plot_magnetic_signal():
    # __file__ が存在しない環境 (Jupyter等) への対策
    try:
        script_dir = Path(__file__).parent.resolve()
    except NameError:
        script_dir = Path.cwd()

    possible_paths = [
        script_dir / 'results' / project_name / summary_csv_filename,
        Path(f'Experiment/results/{project_name}/{summary_csv_filename}'),
        Path(f'results/{project_name}/{summary_csv_filename}'),
        script_dir / summary_csv_filename,
        Path(summary_csv_filename),
    ]

    csv_path = None
    for p in possible_paths:
        if p.exists():
            csv_path = p
            break

    if csv_path is None:
        raise FileNotFoundError(f"{summary_csv_filename} が見つかりませんでした。")

    print(f"データファイルを読み込みます: {csv_path}")
    print(f"プロット対象シグナル: {signal_col} ({signal_type})")
    print(f"表示モード: {mode_title}")

    # CSVの読み込み
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # 数値変換および計測回数・ケース名 (フォルダ名) の抽出
    df['最大磁束密度 [T]'] = pd.to_numeric(df['MagneticField'], errors='coerce')
    df[signal_col] = pd.to_numeric(df[signal_col], errors='coerce')
    df['計測回数'] = df['ファイル名'].apply(parse_measurement)
    
    # ケース名（親フォルダ名またはファイル名幹）の取得
    df['Case'] = df['ファイル名'].apply(
        lambda x: Path(str(x)).parent.name if Path(str(x)).parent.name else Path(str(x)).stem
    )

    # 出力先フォルダの作成
    output_dir = script_dir / 'results' / project_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # 区間番号ごとにグルーピング
    grouped = df.groupby('区間番号')
    sections = sorted(df['区間番号'].dropna().unique())

    # 区間ごとの色定義
    section_color_pairs = {
        'D1': {'1st': '#2ca02c', '2nd': '#98df8a', '3rd': '#005a24'},
        'D2': {'1st': '#d62728', '2nd': '#ff9896', '3rd': '#8c1b1c'},
        'L1': {'1st': '#1f77b4', '2nd': '#aec7e8', '3rd': '#084594'},
        'L2': {'1st': '#ff7f0e', '2nd': '#ffbb78', '3rd': '#b35300'},
        'L3': {'1st': '#9467bd', '2nd': '#c5b0d5', '3rd': '#59357a'},
        'L4': {'1st': '#8c564b', '2nd': '#c49c94', '3rd': '#4c2e28'},
    }

    default_colors = {'1st': '#1f77b4', '2nd': '#ff7f0e', '3rd': '#2ca02c'}

    section_markers = {
        'D1': '^', 'D2': 'v', 'L1': 'o',
        'L2': 's', 'L3': 'D', 'L4': 'p',
    }

    measurements = ['1st', '2nd', '3rd']

    # -------------------------------------------------------------
    # 1. 区間番号ごとの個別散布図 (Individual Scatter Plots)
    # -------------------------------------------------------------
    print("\n区間ごとの個別散布図を作成中...")
    indiv_colors = {'1st': '#1f77b4', '2nd': '#ff7f0e', '3rd': '#2ca02c'}
    indiv_markers = {'1st': 'o', '2nd': 's', '3rd': '^'}

    for sec_name, group in grouped:
        fig, ax = plt.subplots(figsize=(7, 5))

        if is_mean_mode:
            # ケースごとの平均値を算出
            mean_group = group.groupby('Case', as_index=False).agg({
                '最大磁束密度 [T]': 'mean',
                signal_col: 'mean'
            }).dropna(subset=['最大磁束密度 [T]']).sort_values(by='最大磁束密度 [T]')

            sec_color = section_color_pairs.get(sec_name, {}).get('1st', '#1f77b4')
            ax.scatter(
                mean_group['最大磁束密度 [T]'],
                mean_group[signal_col],
                color=sec_color,
                marker='o',
                s=70,
                edgecolors='k',
                linewidth=0.6,
                label=f'Label: {sec_name} (Mean)',
                zorder=3,
            )
        else:
            for meas in measurements:
                m_group = group[group['計測回数'] == meas]
                if m_group.empty:
                    continue
                
                c = indiv_colors.get(meas, 'blue')
                m = indiv_markers.get(meas, 'o')

                ax.scatter(
                    m_group['最大磁束密度 [T]'],
                    m_group[signal_col],
                    color=c,
                    marker=m,
                    s=65,
                    edgecolors='k',
                    linewidth=0.5,
                    label=f'Label: {sec_name} ({meas} Meas.)',
                    zorder=3,
                )

        ax.set_xlim(0, 1.82)
        if signal_type == 'HPF':
            if sec_name in ['D1', 'D2']:
                ax.set_ylim(0, 10)
            else:
                ax.set_ylim(0, 15)
        else:
            if sec_name in ['D1', 'D2']:
                ax.set_ylim(0, 10)
            else:
                ax.set_ylim(0, 30)

        ax.set_xlabel('Magnetic Field [T]', fontsize=12)
        ax.set_ylabel(f'Measured Voltage ({signal_type}) [mV]', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(fontsize=11, loc='upper left')
        ax.set_title(f'伝搬波ラベル {sec_name} ({signal_type} {mode_title})', fontsize=13, fontweight='bold')

        plt.tight_layout()
        save_path = output_dir / f'scatter_section_{sec_name}_{signal_type.lower()}{mode_tag}_separate.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f'   - 保存完了: {save_path.name}')

    # -------------------------------------------------------------
    # 2. 全区間を1つのグラフに重ねた統合散布図 (Combined Overlay Scatter Plot)
    # -------------------------------------------------------------
    print(f"\n2. 全区間を1枚のグラフに重ねた散布図を作成中 ({signal_type} {mode_title})...")
    fig, ax = plt.subplots(figsize=(9.5, 6))

    for sec_name in sections:
        if sec_name not in grouped.groups:
            continue
        group = grouped.get_group(sec_name)
        color_pair = section_color_pairs.get(sec_name, default_colors)
        marker = section_markers.get(sec_name, 'o')

        if is_mean_mode:
            mean_group = group.groupby('Case', as_index=False).agg({
                '最大磁束密度 [T]': 'mean',
                signal_col: 'mean'
            }).dropna(subset=['最大磁束密度 [T]']).sort_values(by='最大磁束密度 [T]')

            c = color_pair.get('1st', '#1f77b4')

            ax.scatter(
                mean_group['最大磁束密度 [T]'],
                mean_group[signal_col],
                color=c,
                marker=marker,
                s=70,
                edgecolors='k',
                linewidth=0.6,
                label=f'Label: {sec_name} (Mean)',
                zorder=3,
            )
        else:
            group = group.sort_values(by='最大磁束密度 [T]')
            for meas in measurements:
                m_group = group[group['計測回数'] == meas]
                if m_group.empty:
                    continue
                
                c = color_pair.get(meas, 'blue')

                ax.scatter(
                    m_group['最大磁束密度 [T]'],
                    m_group[signal_col],
                    color=c,
                    marker=marker,
                    s=65,
                    edgecolors='k',
                    linewidth=0.5,
                    label=f'Label: {sec_name} ({meas})',
                    zorder=3,
                )

    ax.set_xlim(0, 1.82)
    if signal_type == 'HPF':
        ax.set_ylim(0, 15)
    else:
        ax.set_ylim(0, 30)
    ax.set_xlabel('Magnetic Field [T]', fontsize=12)
    ax.set_ylabel(f'Measured Voltage ({signal_type}) [mV]', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(fontsize=9.5, loc='upper left', bbox_to_anchor=(1.02, 1.0), ncol=1)
    ax.set_title(f'Scatter Plot - All Sections Overlay ({signal_type} {mode_title})', fontsize=13, fontweight='bold')

    plt.tight_layout()
    combined_save_path = output_dir / f'scatter_all_sections_combined_{signal_type.lower()}{mode_tag}_separate_legend.png'
    plt.savefig(combined_save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'   - 保存完了: {combined_save_path.name}')

    print("\nすべての散布図の作成・保存が正常に完了しました。")


if __name__ == '__main__':
    plot_magnetic_signal()