import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os  # [수정 1] 파일이 있는지 확인하기 위해 이 한 줄이 꼭 필요합니다!

# 1. 디자인 커스텀 (CSS 적용)
st.set_page_config(page_title="DodreamAI 뉴스 분석기", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경색 및 폰트 크기 설정 */
    .main { background-color: #f8f9fa; }
    h1 { color: #1e88e5; font-size: 40px !important; font-weight: 800; }
    h2 { color: #333333; font-size: 30px !important; }
    p, label, .stSelectbox { font-size: 20px !important; font-weight: 500; }
    
    /* 표 디자인 강조 */
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
    # 불필요한 기호 제거 및 명사 추출
    text = re.sub(r'[^가-힣\s]', '', str(text))
    tokens = kiwi.tokenize(text)
    # 일반명사(NNG), 고유명사(NNP) 중 2글자 이상만 선택
    return " ".join([t.form for t in tokens if t.tag in ['NNG', 'NNP'] and len(t.form) > 1])

# 3. 앱 화면 구성
st.title("🌟 DodreamAI 뉴스 핵심 키워드 분석기")
st.write("선택하신 주제의 뉴스를 분석하여 가장 중요한 단어들을 보여드립니다.")
st.divider()

df = load_and_preprocess()

if not df.empty:
    # 기능 1: 드롭다운으로 주제 선택
    topics = df['query'].unique()
    selected_topic = st.sidebar.selectbox("🎯 분석할 뉴스 주제를 선택하세요", topics)
    
    # 데이터 필터링
    topic_df = df[df['query'] == selected_topic].copy()
    topic_df['processed'] = topic_df['title'].apply(get_nouns)
    
    all_text = " ".join(topic_df['processed'])
    
    if all_text.strip():
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            # 기능 2: 워드클라우드 표시
            st.subheader(f"🖼️ '{selected_topic}' 한눈에 보는 키워드")
            
            # --- [수정 2: 폰트 파일 이름을 대표님이 확인해주신 이름과 똑같이 맞췄습니다] ---
            font_file = 'NanumGothic.ttf' 
            
            # 파일이 깃허브에 실제로 있는지 확인하는 안전장치입니다.
            if os.path.exists(font_file):
                final_font_path = font_file
            else:
                final_font_path = None
                st.error(f"⚠️ 깃허브 저장소에 '{font_file}' 파일이 보이지 않습니다. 파일을 올려주세요!")
            # --------------------------------------------------------------------------

            wc = WordCloud(
                font_path=final_font_path, # 수정된 경로를 사용합니다.
                background_color='white', 
                width=800, height=500,
                colormap='coolwarm'
            ).generate(all_text)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

        with col2:
            # 기능 3: TOP 10 키워드 테이블
            st.subheader("🔝 핵심 단어 TOP 10")
            # 단어 빈도 계산
            word_list = all_text.split()
            word_counts = pd.Series(word_list).value_counts().head(10).reset_index()
            word_counts.columns = ['단어', '언급 횟수']
            
            # 가독성 높은 표 출력
            st.table(word_counts)
            
            st.success(f"현재 '{selected_topic}' 주제에서 가장 많이 언급된 단어는 '{word_counts.iloc[0,0]}'입니다!")
    else:
        st.warning("선택한 주제에 분석 가능한 명사가 없습니다.")
else:
    st.error("데이터 파일(news_data.csv)을 먼저 생성해 주세요.")