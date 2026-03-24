import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os  # [수정] 파일 경로 확인을 위해 추가

# 1. 디자인 커스텀 (CSS 적용)
st.set_page_config(page_title="DodreamAI 뉴스 분석기", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1e88e5; font-size: 40px !important; font-weight: 800; }
    h2 { color: #333333; font-size: 30px !important; }
    p, label, .stSelectbox { font-size: 20px !important; font-weight: 500; }
    .stTable { font-size: 22px !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 불러오기 및 전처리 함수
@st.cache_data
def load_and_preprocess():
    try:
        df = pd.read_csv("news_data.csv", encoding="utf-8-sig")
        return df
    except:
        return pd.DataFrame(columns=['query', 'title'])

kiwi = Kiwi()
def get_nouns(text):
    if not text: return ""
    text = re.sub(r'[^가-힣\s]', '', str(text))
    tokens = kiwi.tokenize(text)
    return " ".join([t.form for t in tokens if t.tag in ['NNG', 'NNP'] and len(t.form) > 1])

# 3. 앱 화면 구성
st.title("🌟 DodreamAI 뉴스 핵심 키워드 분석기")
st.write("선택하신 주제의 뉴스를 분석하여 가장 중요한 단어들을 보여드립니다.")
st.divider()

df = load_and_preprocess()

if not df.empty:
    topics = df['query'].unique()
    selected_topic = st.sidebar.selectbox("🎯 분석할 뉴스 주제를 선택하세요", topics)
    
    topic_df = df[df['query'] == selected_topic].copy()
    topic_df['processed'] = topic_df['title'].apply(get_nouns)
    
    all_text = " ".join(topic_df['processed'])
    
    if all_text.strip():
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader(f"🖼️ '{selected_topic}' 한눈에 보는 키워드")
            
            # --- [수정 시작: 폰트 체크 로직] ---
            font_path = 'NanumGothic.ttf'  # 깃허브에 올린 파일명과 정확히 일치해야 함
            
            if os.path.exists(font_path):
                # 파일이 있을 때만 해당 경로 사용
                use_font = font_path
            else:
                # 파일이 없으면 폰트 설정을 비워서 에러 방지 (한글은 깨지지만 앱은 실행됨)
                use_font = None
                st.error(f"⚠️ '{font_path}' 파일을 찾을 수 없습니다. 깃허브 업로드 상태를 확인해주세요!")
            # --- [수정 끝] ---

            wc = WordCloud(
                font_path=use_font,  # [수정] 확인된 폰트 경로 사용
                background_color='white', 
                width=800, height=500,
                colormap='coolwarm'
            ).generate(all_text)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

        with col2:
            st.subheader("🔝 핵심 단어 TOP 10")
            word_list = all_text.split()
            word_counts = pd.Series(word_list).value_counts().head(10).reset_index()
            word_counts.columns = ['단어', '언급 횟수']
            
            st.table(word_counts)
            st.success(f"현재 '{selected_topic}' 주제에서 가장 많이 언급된 단어는 '{word_counts.iloc[0,0]}'입니다!")
    else:
        st.warning("선택한 주제에 분석 가능한 명사가 없습니다.")
else:
    st.error("데이터 파일(news_data.csv)을 먼저 생성해 주세요.")