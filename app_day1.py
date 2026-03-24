import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os  # [수정] 파일 존재 확인을 위해 반드시 필요합니다

# 1. 디자인 커스텀
st.set_page_config(page_title="DodreamAI 뉴스 분석기", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1e88e5; font-size: 40px !important; font-weight: 800; }
    p, label, .stSelectbox { font-size: 20px !important; font-weight: 500; }
    .stTable { font-size: 22px !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 불러오기 (안전장치 추가)
@st.cache_data
def load_and_preprocess():
    try:
        # 파일이 있는지 먼저 확인
        if os.path.exists("news_data.csv"):
            return pd.read_csv("news_data.csv", encoding="utf-8-sig")
        else:
            return pd.DataFrame(columns=['query', 'title'])
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
            st.subheader(f"🖼️ '{selected_topic}' 키워드 지도")
            
            # --- [수정: 폰트 에러 완벽 차단 로직] ---
            font_name = 'NanumGothic.ttf' # 👈 깃허브에 올린 파일명과 대소문자까지 똑같아야 함
            
            if os.path.exists(font_name):
                final_font = font_name
            else:
                final_font = None # 파일이 없으면 기본 폰트 사용 (에러 방지)
                st.error(f"⚠️ '{font_name}' 파일을 찾을 수 없습니다. 깃허브에 파일을 올려주세요!")
            
            try:
                # 워드클라우드 생성 시도
                wc = WordCloud(
                    font_path=final_font, 
                    background_color='white', 
                    width=800, height=500,
                    colormap='coolwarm'
                ).generate(all_text)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            except Exception as e:
                st.error(f"워드클라우드 생성 중 문제가 발생했습니다: {e}")
            # --- [수정 끝] ---

        with col2:
            st.subheader("🔝 핵심 단어 TOP 10")
            word_list = all_text.split()
            word_counts = pd.Series(word_list).value_counts().head(10).reset_index()
            word_counts.columns = ['단어', '언급 횟수']
            st.table(word_counts)
            st.success(f"현재 '{selected_topic}'의 1위 키워드는 '{word_counts.iloc[0,0]}'입니다!")
    else:
        st.warning("선택한 주제에 분석 가능한 단어가 없습니다.")
else:
    # [수정] 데이터가 없을 때 더 친절하게 안내
    st.error("❗ 'news_data.csv' 파일이 없거나 비어 있습니다. 깃허브 저장소를 확인해 주세요.")