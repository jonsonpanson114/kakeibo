import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
import chardet
from io import StringIO
import json
from pathlib import Path
from datetime import datetime
import calendar

# Page configuration
st.set_page_config(
    page_title="家計簿 - CFO陣内",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# ☀️ LIGHT THEME - 明るく見やすい家計簿デザイン
# ═══════════════════════════════════════════════════════════════════════════════

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@400;600;700&display=swap');

:root {
    /* 明るいカラーパレット */
    --bg-main: #f5f2eb;
    --bg-white: #ffffff;
    --bg-card: #fafaf8;
    --text-dark: #2d2d2d;
    --text-gray: #666666;
    --text-light: #999999;

    /* アクセントカラー */
    --accent-gold: #d4a574;
    --accent-blue: #5b8db8;
    --accent-green: #7d9483;
    --accent-red: #c9696d;
    --accent-purple: #9b88a3;

    /* ボーダー */
    --border-light: #e8e5dc;
    --border-medium: #d4d1c8;
}

/* ベース背景 */
html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif !important;
    background: var(--bg-main) !important;
    color: var(--text-dark);
}

[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(90deg, var(--border-light) 1px, transparent 1px),
        linear-gradient(var(--border-light) 1px, transparent 1px),
        var(--bg-main);
    background-size: 50px 50px, 50px 50px, 100%;
}

.stApp {
    background: transparent !important;
}

.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px;
}

#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* ═══════════════════════════════════════════════════════════════════════════════
   ヘッダー
   ═══════════════════════════════════════════════════════════════════════════════ */

.page-header {
    background: linear-gradient(135deg, #ffffff 0%, #fafaf8 100%);
    padding: 2.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    border: 1px solid var(--border-light);
}

.header-title {
    font-family: 'Noto Serif JP', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
    letter-spacing: 0.05em;
}

.header-subtitle {
    font-size: 0.9rem;
    color: var(--text-gray);
    letter-spacing: 0.1em;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   KPIカード
   ═══════════════════════════════════════════════════════════════════════════════ */

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin-bottom: 2rem;
}

@media (max-width: 1200px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

.kpi-card {
    background: var(--bg-white);
    padding: 1.8rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid var(--border-light);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
}

.kpi-card.gold::before { background: var(--accent-gold); }
.kpi-card.blue::before { background: var(--accent-blue); }
.kpi-card.green::before { background: var(--accent-green); }
.kpi-card.purple::before { background: var(--accent-purple); }

.kpi-icon {
    font-size: 1.8rem;
    margin-bottom: 0.8rem;
    opacity: 0.8;
}

.kpi-label {
    font-size: 0.85rem;
    color: var(--text-gray);
    margin-bottom: 0.6rem;
    font-weight: 500;
}

.kpi-value {
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 0.4rem;
}

.kpi-sub {
    font-size: 0.85rem;
    color: var(--text-light);
}

.kpi-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    padding: 0.3rem 0.7rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-warning {
    background: #fee;
    color: #c33;
}

.badge-good {
    background: #efe;
    color: #3a3;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   カレンダー
   ═══════════════════════════════════════════════════════════════════════════════ */

.calendar-section {
    background: var(--bg-white);
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid var(--border-light);
}

.calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-light);
}

.calendar-title {
    font-family: 'Noto Serif JP', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-dark);
}

.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    margin-bottom: 1.5rem;
}

.calendar-weekday {
    text-align: center;
    font-size: 0.8rem;
    color: var(--text-gray);
    padding: 0.6rem;
    font-weight: 600;
}

.calendar-weekday:first-child { color: var(--accent-red); }
.calendar-weekday:last-child { color: var(--accent-blue); }

.calendar-day {
    aspect-ratio: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: var(--bg-card);
    border-radius: 8px;
    padding: 0.6rem;
    min-height: 80px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 2px solid transparent;
}

.calendar-day:hover {
    background: #f0f0f0;
    transform: scale(1.05);
}

.calendar-day.empty {
    background: transparent;
    cursor: default;
}

.calendar-day.empty:hover {
    transform: none;
}

.calendar-day.today {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border-color: var(--accent-blue);
}

.calendar-day.has-expense {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
}

.calendar-day.high-expense {
    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    border-color: var(--accent-red);
}

.day-number {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-dark);
    margin-bottom: 0.3rem;
}

.calendar-day.today .day-number {
    color: var(--accent-blue);
}

.day-amount {
    font-size: 0.8rem;
    color: var(--accent-gold);
    font-weight: 600;
}

.calendar-day.high-expense .day-amount {
    color: var(--accent-red);
}

.calendar-summary {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 2px solid var(--border-light);
}

.summary-box {
    text-align: center;
    padding: 1.2rem;
    background: var(--bg-card);
    border-radius: 8px;
    border: 1px solid var(--border-light);
}

.summary-label {
    font-size: 0.8rem;
    color: var(--text-gray);
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.summary-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-dark);
}

/* ═══════════════════════════════════════════════════════════════════════════════
   セクションカード
   ═══════════════════════════════════════════════════════════════════════════════ */

.section-card {
    background: var(--bg-white);
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid var(--border-light);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-light);
}

.section-title {
    font-family: 'Noto Serif JP', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-dark);
}

.section-icon {
    font-size: 1.5rem;
}

/* カテゴリリスト */
.category-list {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}

.category-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.2rem;
    background: var(--bg-card);
    border-radius: 8px;
    transition: all 0.2s ease;
    border: 1px solid var(--border-light);
}

.category-item:hover {
    background: #f0f0f0;
    transform: translateX(4px);
}

.category-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    flex-shrink: 0;
}

.category-name {
    flex: 1;
    font-weight: 500;
    color: var(--text-dark);
}

.category-amount {
    font-weight: 700;
    color: var(--text-dark);
}

.category-percent {
    font-size: 0.85rem;
    color: var(--text-gray);
    min-width: 50px;
    text-align: right;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   CFOアドバイス
   ═══════════════════════════════════════════════════════════════════════════════ */

.cfo-advice {
    background: linear-gradient(135deg, #fff8f0 0%, #fff 100%);
    border: 2px solid var(--accent-gold);
    border-radius: 12px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 4px 12px rgba(212, 165, 116, 0.15);
}

.cfo-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--accent-gold);
}

.cfo-avatar {
    font-size: 2.5rem;
}

.cfo-name {
    font-family: 'Noto Serif JP', serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-dark);
}

.cfo-title {
    font-size: 0.8rem;
    color: var(--text-gray);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.cfo-body {
    font-size: 1rem;
    line-height: 1.8;
    color: var(--text-dark);
}

.cfo-body strong {
    color: var(--accent-red);
    background: linear-gradient(transparent 60%, rgba(201, 106, 109, 0.2) 60%);
    padding: 0 0.2rem;
}

/* ═══════════════════════════════════════════════════════════════════════════════
   ボタン & 入力
   ═══════════════════════════════════════════════════════════════════════════════ */

.stButton > button {
    font-family: 'Noto Sans JP', sans-serif !important;
    font-weight: 600;
    background: var(--bg-white) !important;
    color: var(--text-dark) !important;
    border: 2px solid var(--border-medium) !important;
    border-radius: 8px;
    padding: 0.7rem 2rem;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: var(--bg-card) !important;
    border-color: var(--accent-gold) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-gold) 0%, #e5b96a 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(212, 165, 116, 0.3);
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(212, 165, 116, 0.4);
}

/* データエディタ */
[data-testid="stDataFrame"] {
    background: var(--bg-white) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 8px !important;
}

/* サイドバー */
[data-testid="stSidebar"] {
    background: #fafaf8 !important;
    border-right: 1px solid var(--border-light);
}

.stTextInput input {
    background: var(--bg-white) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 6px !important;
    color: var(--text-dark) !important;
}

.stTextInput input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 2px rgba(91, 141, 184, 0.2) !important;
}

/* スクロールバー */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--bg-card);
}

::-webkit-scrollbar-thumb {
    background: var(--border-medium);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-gray);
}

/* アップロード */
.upload-area {
    background: var(--bg-white);
    border: 3px dashed var(--accent-gold);
    border-radius: 12px;
    padding: 4rem 2rem;
    text-align: center;
    margin: 3rem auto;
    max-width: 600px;
    transition: all 0.3s ease;
}

.upload-area:hover {
    border-color: #e5b96a;
    background: #fffbf5;
}

.upload-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.upload-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 0.5rem;
}

.upload-desc {
    font-size: 0.9rem;
    color: var(--text-gray);
}

.stFileUploader > div { display: none; }
.stFileUploader label { display: none !important; }

</style>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# DATA PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

DATA_DIR = Path(__file__).parent
CSV_ARCHIVE_DIR = DATA_DIR / "csv_archive"
CSV_ARCHIVE_DIR.mkdir(exist_ok=True)
LEARNED_FILE = DATA_DIR / "learned_categories.json"
LOG_FILE = DATA_DIR / "analysis_log.json"
ACTION_PLAN_FILE = DATA_DIR / "action_plans.json"


def load_learned_categories():
    if LEARNED_FILE.exists():
        try:
            return json.loads(LEARNED_FILE.read_text(encoding='utf-8'))
        except:
            return {}
    return {}


def save_learned_categories(data):
    LEARNED_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def load_analysis_log():
    if LOG_FILE.exists():
        try:
            return json.loads(LOG_FILE.read_text(encoding='utf-8'))
        except:
            return []
    return []


def save_analysis_log(log_entry):
    logs = load_analysis_log()
    logs.insert(0, log_entry)
    logs = logs[:100]
    LOG_FILE.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding='utf-8')


def load_action_plans():
    if ACTION_PLAN_FILE.exists():
        try:
            return json.loads(ACTION_PLAN_FILE.read_text(encoding='utf-8'))
        except:
            return []
    return []


def save_action_plan(plan):
    plans = load_action_plans()
    plans.insert(0, {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'plan': plan
    })
    plans = plans[:20]
    ACTION_PLAN_FILE.write_text(json.dumps(plans, ensure_ascii=False, indent=2), encoding='utf-8')


def save_monthly_csv(df, year, month):
    """月ごとにCSVを保存"""
    filename = f"{year:04d}-{month:02d}.csv"
    filepath = CSV_ARCHIVE_DIR / filename
    df.to_csv(filepath, index=False, encoding='utf-8-sig')


def load_monthly_csv(year, month):
    """月ごとにCSVを読み込み"""
    filename = f"{year:04d}-{month:02d}.csv"
    filepath = CSV_ARCHIVE_DIR / filename
    if filepath.exists():
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        # 日付列をdatetime型に変換
        for date_col in ['date', '日付']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        return df
    return None


def get_available_months():
    """保存されている月のリストを取得"""
    csv_files = sorted(CSV_ARCHIVE_DIR.glob("*.csv"), reverse=True)
    months = []
    for file in csv_files:
        try:
            year, month = file.stem.split('-')
            months.append((int(year), int(month)))
        except:
            pass
    return months


# ═══════════════════════════════════════════════════════════════════════════════
# カテゴリ設定
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORY_CONFIG = {
    '昼ご飯': {'color': '#FF6B6B'},      # 鮮やかな赤
    '晩御飯': {'color': '#4ECDC4'},      # ターコイズ
    '朝食・軽食': {'color': '#FFE66D'},  # 明るい黄色
    '日用品': {'color': '#95E1D3'},      # ミントグリーン
    '交通': {'color': '#5B9BD5'},        # 明るい青
    '交際費': {'color': '#E84393'},      # マゼンタピンク
    'エンタメ': {'color': '#FD79A8'},    # ピンク
    '教育・教養': {'color': '#A29BFE'},  # 薄紫
    '美容・衣服': {'color': '#FAB1A0'},  # サーモンピンク
    '医療・健康': {'color': '#74B9FF'},  # 水色
    '通信': {'color': '#6C5CE7'},        # インディゴ
    '水道・光熱': {'color': '#00CEC9'},  # シアン
    '住まい': {'color': '#D4A574'},      # ゴールデンブラウン
    '保険': {'color': '#DDA0DD'},        # プラム
    '税金': {'color': '#E74C3C'},        # 濃い赤
    '投資・貯蓄': {'color': '#F39C12'},  # オレンジゴールド
    '大型出費': {'color': '#555555'},    # ダークグレー
    'その他': {'color': '#95A5A6'},      # グレー
}

CATEGORIES = list(CATEGORY_CONFIG.keys())

MEAL_TIME_KEYWORDS = {
    '昼ご飯': ['ランチ', '昼食', '昼ごはん', '昼ご飯', '定食', 'LUNCH'],
    '晩御飯': ['ディナー', '夕食', '夕飯', '晩ごはん', '晩御飯', '晩酌', 'DINNER', '居酒屋', 'バル', '酒場'],
    '朝食・軽食': ['モーニング', '朝食', '朝ごはん', 'カフェ', 'コーヒー', 'CAFE', 'パン屋', 'ベーカリー', 'おやつ', 'スイーツ'],
}

FOOD_KEYWORDS = [
    'スーパー', 'イオン', 'イトーヨーカドー', 'ライフ', 'マルエツ', 'OK',
    'コープ', '西友', 'マックスバリュ', 'ドンキ', '業務スーパー',
    'マクドナルド', 'すき家', '吉野家', '松屋', 'なか卯', 'CoCo壱',
    'スタバ', 'ドトール', 'タリーズ', 'コメダ', 'サンマルク',
    '弁当', 'カフェ', 'レストラン', '食堂', 'ラーメン',
    'セブン', 'ローソン', 'ファミマ', 'ファミリーマート', 'ミニストップ',
    'デニーズ', 'ガスト', 'サイゼリヤ', 'ジョナサン', 'ココス',
    'ケンタッキー', 'モスバーガー', 'バーガーキング', 'フレッシュネス'
]

KEYWORDS_DB = {
    '日用品': ['ドラッグストア', 'マツキヨ', 'ウエルシア', 'ツルハ', 'サンドラッグ', 'ダイソー', '無印', 'ニトリ', '100均'],
    '交通': ['SUICA', 'ICOCA', 'PASMO', 'ETC', 'タクシー', '電車', 'バス', 'JR', '地下鉄', 'ガソリン'],
    '交際費': ['居酒屋', 'バル', '酒場', 'ビール', '鳥貴族', '和民', 'プレゼント', 'ギフト'],
    'エンタメ': ['映画', 'Netflix', 'Amazon Prime', 'Spotify', 'ゲーム', '旅行', 'ホテル'],
    '教育・教養': ['本屋', 'KINDLE', '書店', 'UDEMY', '習い事', 'スクール'],
    '美容・衣服': ['美容院', 'ヘアサロン', 'ユニクロ', 'GU', 'ZARA', 'クリーニング'],
    '医療・健康': ['病院', 'クリニック', '薬局', 'ジム', 'フィットネス'],
    '通信': ['DOCOMO', 'AU', 'SOFTBANK', '楽天モバイル', 'インターネット'],
    '水道・光熱': ['電気', 'ガス', '水道', '東京電力', '東京ガス'],
    '住まい': ['家賃', '管理費', '家具', '家電', 'IKEA'],
    '保険': ['保険', '生命保険', '医療保険'],
    '投資・貯蓄': ['NISA', 'iDeCo', '株式', '投資信託', '証券'],
}


def classify_meal_time(row, search_text):
    for meal_type, keywords in MEAL_TIME_KEYWORDS.items():
        if any(kw.upper() in search_text for kw in keywords):
            return meal_type
    amount = row.get('支出', 0)
    if pd.isna(amount):
        amount = 0
    if amount >= 1500:
        return '晩御飯'
    elif amount >= 600:
        return '昼ご飯'
    else:
        return '朝食・軽食'


def classify_expense(row, learned_categories):
    amount = row.get('支出', 0)
    if pd.isna(amount):
        amount = 0

    search_text = ''
    for col in ['お店', 'メモ', '品名', 'name', 'place', 'カテゴリ', 'category']:
        if col in row and pd.notna(row.get(col)):
            search_text += str(row[col]) + ' '
    search_text = search_text.upper().strip()

    for shop, category in learned_categories.items():
        if shop.upper() in search_text:
            return category

    zaim_cat = str(row.get('カテゴリ', '') or row.get('category', '')).strip()
    if zaim_cat:
        zaim_mapping = {
            '食費': None, '食料品': None, '外食': None,
            'カフェ': '朝食・軽食',
            '日用雑貨': '日用品', '日用品': '日用品',
            '交通': '交通', '交通費': '交通',
            '交際費': '交際費', '飲み会': '交際費',
            'エンタメ': 'エンタメ', '娯楽': 'エンタメ',
            '教育': '教育・教養', '書籍': '教育・教養',
            '美容': '美容・衣服', '衣服': '美容・衣服',
            '医療': '医療・健康', '健康': '医療・健康',
            '通信': '通信', '水道・光熱': '水道・光熱',
            '住まい': '住まい', '保険': '保険', '税金': '税金',
            '投資': '投資・貯蓄', '大型出費': '大型出費',
        }
        for key, cat in zaim_mapping.items():
            if key in zaim_cat:
                if cat is None:
                    return classify_meal_time(row, search_text)
                return cat

    if any(kw.upper() in search_text for kw in FOOD_KEYWORDS):
        return classify_meal_time(row, search_text)

    for category, keywords in KEYWORDS_DB.items():
        if any(kw.upper() in search_text for kw in keywords):
            if category == '交際費' and amount < 3000:
                return '晩御飯'
            return category

    if amount >= 50000:
        return '大型出費'
    elif 300 <= amount <= 2000:
        return classify_meal_time(row, search_text)

    return 'その他'


def load_data(file):
    content = file.read()
    detected = chardet.detect(content)
    detected_encoding = detected.get('encoding', 'utf-8')

    encodings = ['shift_jis', 'utf-8', 'cp932']
    if detected_encoding and detected_encoding.lower() not in [e.lower() for e in encodings]:
        encodings.insert(0, detected_encoding)

    df = None
    for encoding in encodings:
        try:
            df = pd.read_csv(StringIO(content.decode(encoding)))
            break
        except:
            continue

    if df is None:
        raise ValueError("CSVの読み込みに失敗しました")

    for date_col in ['date', '日付']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    if 'method' in df.columns:
        df = df[df['method'] == 'payment'].copy()

    drop_cols = ['通貨', '振替', '残高調整', '入金先', 'id', 'from_account_id', 'to_account_id']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

    learned = load_learned_categories()
    df['分類'] = df.apply(lambda r: classify_expense(r, learned), axis=1)

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# CFO ADVICE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_cfo_advice(df, api_key):
    genai.configure(api_key=api_key)

    category_summary = df.groupby('分類')['支出'].sum().sort_values(ascending=False)
    total_expense = df['支出'].sum()

    prompt = f"""あなたは陣内。『陽気なギャングが地球を回す』の登場人物。冷静で論理的。皮肉屋だが正論を言う。無駄が嫌い。

家計簿データを見て、CFOとして所見と改善案を述べろ。精神論はいらない。数字で語れ。
「まあ、そういうことだ」「つまり」「要するに」といった口調で。簡潔に、しかし的確に。
余計な気遣いはいらない。事実を突きつけ、解決策を示せ。遠回しな言い方はするな。

【データ】
{category_summary.to_string()}

総支出: ¥{total_expense:,.0f}

【出力フォーマット】

**所見**
(現状を2-3行で。皮肉も交えつつ、事実ベースで。「まあ」「つまり」「要するに」などの口調で)

**処方**
1. [具体的な改善策。数字付きで]
2. [具体的な改善策。数字付きで]
3. [具体的な改善策。数字付きで]

**効能**
(月間・年間の削減見込み額を明示)

— 陣内"""

    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"エラー: {str(e)}"


# ═══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

def create_donut_chart(df):
    category_data = df.groupby('分類')['支出'].sum().sort_values(ascending=False).head(8).reset_index()
    category_data.columns = ['分類', '金額']

    colors = [CATEGORY_CONFIG.get(cat, {}).get('color', '#999999') for cat in category_data['分類']]

    fig = go.Figure(data=[go.Pie(
        labels=category_data['分類'],
        values=category_data['金額'],
        hole=0.65,
        marker=dict(colors=colors, line=dict(color='#ffffff', width=3)),
        textposition='outside',
        textfont=dict(size=14, color='#2d2d2d', family='Noto Sans JP', weight=600),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>¥%{value:,.0f}<br>%{percent}<extra></extra>',
        sort=False,
        pull=[0.05] * len(category_data)  # 少し外側に引き出して見やすく
    )])

    total = df['支出'].sum()
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=40, l=80, r=80),
        height=450,
        annotations=[
            dict(
                text=f'<b>¥{total:,.0f}</b>',
                x=0.5, y=0.55,
                font=dict(size=28, color='#2d2d2d', family='Noto Sans JP', weight=700),
                showarrow=False
            ),
            dict(
                text='総支出',
                x=0.5, y=0.42,
                font=dict(size=14, color='#666666', family='Noto Sans JP'),
                showarrow=False
            )
        ]
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

def render_calendar(df, year, month):
    date_col = 'date' if 'date' in df.columns else '日付'
    if date_col not in df.columns:
        return

    df_month = df[
        (df[date_col].dt.year == year) &
        (df[date_col].dt.month == month)
    ].copy()

    daily_totals = df_month.groupby(df_month[date_col].dt.day)['支出'].sum().to_dict()
    monthly_total = df_month['支出'].sum()
    avg_daily = monthly_total / max(len(daily_totals), 1)
    max_daily = max(daily_totals.values()) if daily_totals else 0

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    today = datetime.now()

    weekdays = ['日', '月', '火', '水', '木', '金', '土']

    html = f'''
    <div class="calendar-section">
        <div class="calendar-header">
            <div class="calendar-title">{year}年 {month}月 カレンダー</div>
        </div>
        <div class="calendar-grid">
    '''

    for wd in weekdays:
        html += f'<div class="calendar-weekday">{wd}</div>'

    for week in month_days:
        for day in week:
            if day == 0:
                html += '<div class="calendar-day empty"></div>'
            else:
                amount = daily_totals.get(day, 0)
                is_today = (today.year == year and today.month == month and today.day == day)
                has_expense = amount > 0
                high_expense = amount > avg_daily * 1.5 if avg_daily > 0 else False

                classes = ['calendar-day']
                if is_today:
                    classes.append('today')
                if has_expense:
                    classes.append('has-expense')
                if high_expense:
                    classes.append('high-expense')

                amount_html = f'<div class="day-amount">¥{amount:,.0f}</div>' if has_expense else ''

                html += f'<div class="{" ".join(classes)}">'
                html += f'<div class="day-number">{day}</div>'
                html += amount_html
                html += '</div>'

    html += f'''
        </div>
        <div class="calendar-summary">
            <div class="summary-box">
                <div class="summary-label">月間合計</div>
                <div class="summary-value">¥{monthly_total:,.0f}</div>
            </div>
            <div class="summary-box">
                <div class="summary-label">日平均</div>
                <div class="summary-value">¥{avg_daily:,.0f}</div>
            </div>
            <div class="summary-box">
                <div class="summary-label">最高額</div>
                <div class="summary-value">¥{max_daily:,.0f}</div>
            </div>
        </div>
    </div>
    '''

    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ 設定")
    api_key = st.text_input("Gemini API Key", type="password")

    st.markdown("---")
    st.markdown("### 📅 表示月")

    # 保存済みの月を取得
    available_months = get_available_months()

    if available_months:
        # 保存済みの月から選択
        month_options = [f"{year}年{month}月" for year, month in available_months]
        today = datetime.now()

        # デフォルトは今月（あれば）、なければ最新の月
        default_idx = 0
        for idx, (year, month) in enumerate(available_months):
            if year == today.year and month == today.month:
                default_idx = idx
                break

        selected = st.selectbox("保存済みの月", month_options, index=default_idx)
        view_year, view_month = available_months[month_options.index(selected)]
    else:
        # 保存済みデータがない場合は手動選択
        today = datetime.now()
        col_y, col_m = st.columns(2)
        with col_y:
            view_year = st.selectbox("年", range(today.year - 2, today.year + 1), index=2)
        with col_m:
            view_month = st.selectbox("月", range(1, 13), index=today.month - 1)

    st.markdown("---")
    st.markdown("### 📊 分析履歴")
    logs = load_analysis_log()
    if logs:
        for log in logs[:5]:
            st.markdown(f"**{log.get('date', '')}**  \n¥{log.get('total', 0):,.0f}")

    st.markdown("---")
    st.markdown("### 📚 過去のCFO監査")
    plans = load_action_plans()
    if plans:
        for i, plan in enumerate(plans[:10]):
            with st.expander(f"🔍 {plan.get('date', '')}"):
                st.markdown(plan.get('plan', ''))

# CSVアップロード処理
uploaded_file = st.file_uploader("CSV", type=['csv'], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        with st.spinner('読み込み中...'):
            df_uploaded = load_data(uploaded_file)

            # 日付列を確認
            date_col = 'date' if 'date' in df_uploaded.columns else '日付'
            if date_col in df_uploaded.columns:
                # 年月ごとに分割して保存
                df_uploaded[date_col] = pd.to_datetime(df_uploaded[date_col], errors='coerce')
                saved_months = []

                for (year, month), group_df in df_uploaded.groupby([df_uploaded[date_col].dt.year, df_uploaded[date_col].dt.month]):
                    if pd.notna(year) and pd.notna(month):
                        save_monthly_csv(group_df, int(year), int(month))
                        saved_months.append(f"{int(year)}年{int(month)}月")

                if saved_months:
                    st.success(f"✅ 保存完了: {', '.join(saved_months)}")
            else:
                st.error("日付列が見つかりません")
    except Exception as e:
        st.error(f"エラー: {e}")

# 選択された年月のデータを読み込む
df = load_monthly_csv(view_year, view_month)

if df is None:
    st.markdown("""
    <div class="page-header">
        <div class="header-title">💰 家計簿アプリ - CFO陣内</div>
        <div class="header-subtitle">Personal Finance Management System</div>
    </div>
    """, unsafe_allow_html=True)

    available_months = get_available_months()
    if available_months:
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">📅</div>
            <div class="upload-title">データがありません</div>
            <div class="upload-desc">サイドバーで別の月を選択するか、新しいCSVをアップロード</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📊 保存済みの月")
        cols = st.columns(4)
        for idx, (year, month) in enumerate(available_months[:12]):
            with cols[idx % 4]:
                st.button(f"{year}年{month}月", key=f"month_{year}_{month}")
    else:
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">📂</div>
            <div class="upload-title">家計簿CSVをアップロード</div>
            <div class="upload-desc">ZaimのエクスポートデータをドラッグDrop</div>
        </div>
        """, unsafe_allow_html=True)

    plans = load_action_plans()
    if plans:
        st.markdown("""
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">📋</span>
                <span class="section-title">過去のアドバイス</span>
            </div>
        """, unsafe_allow_html=True)

        for plan in plans[:3]:
            st.markdown(f"""
            <div style="padding: 1rem; background: var(--bg-card); border-radius: 8px; margin-bottom: 0.8rem; border-left: 3px solid var(--accent-gold);">
                <div style="font-size: 0.8rem; color: var(--text-gray); margin-bottom: 0.5rem;">{plan.get('date', '')}</div>
                <div style="font-size: 0.9rem; color: var(--text-dark);">{plan.get('plan', '')[:100]}...</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ここから先はデータがある場合の処理
else:

    # ヘッダー
    st.markdown("""
    <div class="page-header">
        <div class="header-title">💰 家計簿アプリ - CFO陣内</div>
        <div class="header-subtitle">Personal Finance Management System</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI計算
    total_expense = df['支出'].sum()
    total_other = df[df['分類'] == 'その他']['支出'].sum()
    entry_count = len(df)

    meal_categories = ['昼ご飯', '晩御飯', '朝食・軽食']
    total_meal = df[df['分類'].isin(meal_categories)]['支出'].sum()
    lunch_total = df[df['分類'] == '昼ご飯']['支出'].sum()
    dinner_total = df[df['分類'] == '晩御飯']['支出'].sum()

    meal_ratio = (total_meal / total_expense * 100) if total_expense > 0 else 0
    other_ratio = (total_other / total_expense * 100) if total_expense > 0 else 0

    # バッジクラスを事前に計算
    badge_class_meal = 'badge-warning' if meal_ratio > 40 else 'badge-good'
    badge_class_other = 'badge-warning' if other_ratio > 10 else 'badge-good'

    # KPIカード - st.columns()を使用
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

    kpi_cols = st.columns(4)

    with kpi_cols[0]:
        st.markdown(f"""
        <div class="kpi-card gold">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">総支出</div>
            <div class="kpi-value">¥{total_expense:,.0f}</div>
            <div class="kpi-sub">{entry_count}件の取引</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[1]:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div class="kpi-badge {badge_class_meal}">{meal_ratio:.0f}%</div>
            <div class="kpi-icon">🍚</div>
            <div class="kpi-label">食費合計</div>
            <div class="kpi-value">¥{total_meal:,.0f}</div>
            <div class="kpi-sub">昼 ¥{lunch_total:,.0f} / 夜 ¥{dinner_total:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[2]:
        st.markdown(f"""
        <div class="kpi-card green">
            <div class="kpi-badge {badge_class_other}">{other_ratio:.0f}%</div>
            <div class="kpi-icon">❓</div>
            <div class="kpi-label">未分類</div>
            <div class="kpi-value">¥{total_other:,.0f}</div>
            <div class="kpi-sub">要確認</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[3]:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div class="kpi-icon">📊</div>
            <div class="kpi-label">日平均</div>
            <div class="kpi-value">¥{total_expense / 30:,.0f}</div>
            <div class="kpi-sub">月30日換算</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # カレンダー
    render_calendar(df, view_year, view_month)

    # チャートとカテゴリ
    col_chart, col_categories = st.columns([2, 1])

    with col_chart:
        st.markdown("""
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">📈</span>
                <span class="section-title">支出内訳</span>
            </div>
        """, unsafe_allow_html=True)

        fig = create_donut_chart(df)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("</div>", unsafe_allow_html=True)

    with col_categories:
        st.markdown("""
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">📋</span>
                <span class="section-title">カテゴリ一覧</span>
            </div>
            <div class="category-list">
        """, unsafe_allow_html=True)

        category_counts = df.groupby('分類')['支出'].sum().sort_values(ascending=False)
        for cat, amount in category_counts.head(8).items():
            color = CATEGORY_CONFIG.get(cat, {}).get('color', '#999999')
            percent = (amount / total_expense * 100) if total_expense > 0 else 0
            st.markdown(f"""
            <div class="category-item">
                <div class="category-color" style="background: {color};"></div>
                <div class="category-name">{cat}</div>
                <div class="category-amount">¥{amount:,.0f}</div>
                <div class="category-percent">{percent:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    # データエディタ
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <span class="section-icon">📝</span>
            <span class="section-title">明細帳</span>
        </div>
    """, unsafe_allow_html=True)

    display_cols = ['分類']
    for col in ['日付', 'date', 'お店', 'place', '品名', 'name', '支出']:
        if col in df.columns and col not in display_cols:
            display_cols.append(col)

    edited_df = st.data_editor(
        df[display_cols],
        column_config={
            '分類': st.column_config.SelectboxColumn('分類', options=CATEGORIES, required=True),
            '支出': st.column_config.NumberColumn('支出', format='¥%d'),
        },
        use_container_width=True,
        hide_index=True,
        height=400,
        key='data_editor'
    )

    df['分類'] = edited_df['分類']
    st.session_state['df'] = df

    st.markdown("</div>", unsafe_allow_html=True)

    # ボタン
    col_save, col_audit = st.columns(2)

    with col_save:
        if st.button("💾 学習を保存", use_container_width=True):
            learned = load_learned_categories()
            shop_col = next((c for c in ['お店', 'place'] if c in df.columns), None)
            if shop_col:
                for _, row in df.iterrows():
                    shop = row.get(shop_col)
                    if pd.notna(shop) and shop:
                        learned[str(shop)] = row['分類']
                save_learned_categories(learned)
                st.success("保存しました")

    with col_audit:
        if st.button("🔍 CFO監査", type="primary", use_container_width=True):
            if not api_key:
                st.warning("サイドバーでAPIキーを入力してください")
            else:
                with st.spinner('陣内が監査中...'):
                    advice = generate_cfo_advice(df, api_key)
                    st.session_state['advice'] = advice
                    save_action_plan(advice)
                    save_analysis_log({
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'total': int(total_expense),
                        'count': len(df)
                    })

    # CFOアドバイス
    if 'advice' in st.session_state:
        st.markdown(f"""
        <div class="cfo-advice">
            <div class="cfo-header">
                <div class="cfo-avatar">👔</div>
                <div>
                    <div class="cfo-name">陣内</div>
                    <div class="cfo-title">Chief Financial Officer</div>
                </div>
            </div>
            <div class="cfo-body">
                {st.session_state['advice'].replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 過去のCFO監査記録
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    st.markdown("### 📚 過去のCFO監査記録")

    past_plans = load_action_plans()
    if past_plans:
        # 現在のアドバイスは除外（最初の要素）
        display_plans = past_plans[1:11] if 'advice' in st.session_state else past_plans[:10]

        for plan in display_plans:
            with st.expander(f"🔍 {plan.get('date', '')}"):
                st.markdown(f"""
                <div class="cfo-advice">
                    <div class="cfo-header">
                        <div class="cfo-avatar">👔</div>
                        <div>
                            <div class="cfo-name">陣内</div>
                            <div class="cfo-title">Chief Financial Officer</div>
                        </div>
                    </div>
                    <div class="cfo-body">
                        {plan.get('plan', '').replace(chr(10), '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("まだCFO監査を実行していません。上の「🔍 CFO監査」ボタンを押してください。")
