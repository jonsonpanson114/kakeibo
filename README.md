# 家計簿アプリ - CFO陣内

CFO陣内による家計簿監査システム。

## 起動方法
1. 依存関係のインストール:
   ```bash
   pip install -r requirements.txt
   ```
2. アプリの起動:
   ```bash
   streamlit run app.py
   ```

## 技術スタック
- Python 3.x
- Streamlit
- Pandas / Plotly
- Google Gemini API (2.5-flash)

## 注意事項
- 起動時にサイドバーで **Gemini API Key** を入力してください。
- ZaimからエクスポートしたCSVをアップロードして使用します。
