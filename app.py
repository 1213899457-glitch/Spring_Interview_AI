"""
2026春招AI模拟面试官 | 咸鱼上岸记
正式商业版：会员激活码充值模式
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 1. 核心激活码配置 (老板在这里发货) ============
# 格式为 "激活码": 充值次数
RECHARGE_CODES = {
    "XY666": 1,          # 1次体验码
    "VIP888": 10,        # 10次进阶码
    "SHANGAN999": 999    # 无限次超级码
}

NAV_ITEMS = [
    ("🏠 个人中心", "home"),
    ("📄 AI 简历神笔", "resume"),
    ("🎤 模拟面试", "interview"),
    ("📚 知识库", "knowledge"),
    ("⏰ 面试历史", "history"),
]

# ============ 2. 页面配置 ============
st.set_page_config(
    page_title="咸鱼上岸记 | 春招AI助手",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ 3. SaaS 风格 CSS (修复文字显示) ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1d1d1f 0%, #2d2d2f 100%) !important;
    }
    /* 侧边栏文字颜色强制修正为白色 */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { 
        color: #f5f5f7 !important; 
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #f5f5f7 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    /* 卡片样式 */
    .saas-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #d2d2d7;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .interviewer-msg { background: #1d1d1f; color: #f5f5f7; padding: 16px 20px; border-radius: 12px 12px 12px 4px; margin: 12px 0; }
    .user-msg { background: #e8e8ed; color: #1d1d1f; padding: 16px 20px; border-radius: 12px 12px 4px 12px; margin: 12px 0; }
    .stButton > button { background: #1d1d1f !important; color: #ffffff !important; border-radius: 8px !important; width: 100%; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ 4. 逻辑初始化 ============
def init_session():
    if "user_credits" not in st.session_state:
        st.session_state.user_credits = 0
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "started" not in st.session_state:
        st.session_state.started = False

def get_deepseek_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("⚠️ 请在 Streamlit Secrets 中配置您的 API Key")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def call_deepseek(messages, client):
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0.7)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"调用失败：{str(e)}"

# ============ 5. 侧边栏布局 ============
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎯 咸鱼上岸记")
        st.markdown(f"**账户余额：`{st.session_state.user_credits}` 次**")
        st.markdown("---")
        
        # 导航菜单
        options = [item[0] for item in NAV_ITEMS]
        page_ids = [item[1] for item in NAV_ITEMS]
        selected = st.radio("功能导航", options, label_visibility="collapsed")
        st.session_state.current_page = page_ids[options.index(selected)]
        
        # 充值区
        st.markdown("---")
        st.markdown("### 💳 会员充值")
        code = st.text_input("输入激活码", type="password", placeholder="请输入充值激活码")
        if st.button("立即激活"):
            if code in RECHARGE_CODES:
                added = RECHARGE_CODES[code]
                st.session_state.user_credits += added
                st.success(f"成功充值 {added} 次额度！")
                st.rerun()
            else:
                st.error("激活码无效，请咨询主理人")

# ============ 6. 模块渲染 ============
def render_page_home():
    st.markdown("## 🏠 个人中心")
    st.markdown(f"""
    <div class="saas-card">
        <p style="color: #86868b; margin: 0;">当前会员身份</p>
        <h2 style="margin: 8px 0;">咸鱼上岸·特权会员</h2>
        <p style="color: #1d1d1f; font-size: 1.2rem;">可用额度：<strong>{st.session_state.user_credits} 次</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📢 如何获取额度？")
    st.info("在小红书/咸鱼店铺下单后，联系主理人获取您的专属激活码。")

def render_page_resume():
    st.markdown("## 📄 AI 简历神笔")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请在侧边栏充值后使用。")
        return

    col1, col2 = st.columns(2)
    with col1:
        target_job = st.text_input("目标岗位")
        resume_text = st.text_area("简历原始内容", height=300)
        if st.button("一键优化 (消耗 1 次额度)"):
            if target_job and resume_text:
                st.session_state.user_credits -= 1
                client = get_deepseek_client()
                with st.spinner("AI 正在使用 STAR 法则修改..."):
                    prompt = [{"role": "user", "content": f"请针对岗位【
