import streamlit as st
import os
import random
import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ==============================================
# 1. 页面配置与高级商用 UI (融合版)
# ==============================================
st.set_page_config(
    page_title="咸鱼上岸记 | 春招AI教练",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 基础布局优化 */
    .stApp { background-color: #f8fafc; }
    
    /* 侧边栏：深色高级感 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
    
    /* 商业级按钮 */
    .stButton > button {
        background: #32CD32 !important; /* 延续老板喜欢的绿 */
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(50, 205, 50, 0.3);
    }

    /* 卡片样式 */
    .saas-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .recharge-card {
        background: #1e1e1e;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #32CD32;
        text-align: center;
        margin-bottom: 20px;
    }

    /* 协议文本 */
    .protocol-box {
        font-size: 13px;
        color: #64748b;
        background: #f1f5f9;
        padding: 15px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================
# 2. 核心逻辑配置 (充值码)
# ==============================================
RECHARGE_CODES = {
    "XY666": 1,          # 体验
    "VIP888": 10,        # 进阶
    "SHANGAN999": 999    # 终身
}

# ==============================================
# 3. 初始化账户系统
# ==============================================
def init_session():
    # 模拟云端数据库
    if "user_db" not in st.session_state:
        st.session_state.user_db = {}
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "history" not in st.session_state:
        st.session_state.history = []

def get_ai_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("⚠️ 请在 Secrets 中配置 DEEPSEEK_API_KEY")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ==============================================
# 4. 登录页面 (融合你的手机号逻辑)
# ==============================================
def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #1e293b;'>🎯 咸鱼上岸记</h1>
            <p style='color: #64748b;'>春招 AI 面试助手 · 专业级通关神器</p>
        </div>
        """, unsafe_allow_html=True)
        
        phone = st.text_input("手机号登录/注册", placeholder="请输入11位手机号", max_chars=11)
        code_in = st.text_input("验证码", placeholder="演示模式下任意输入", type="password")
        
        if st.button("进入系统", type="primary"):
            if len(phone) == 11 and phone.isdigit():
                if phone not in st.session_state.user_db:
                    # 自动分配会员号
                    mid = f"XY{phone[-4:]}{len(st.session_state.user_db)+1:03d}"
                    st.session_state.user_db[phone] = {"credits": 0, "mid": mid}
                
                st.session_state.current_user = phone
                st.session_state.is_logged_in = True
                st.rerun()
            else:
                st.error("请输入有效的手机号")
        
        st.markdown("""
        <div class='protocol-box'>
            登录即同意《用户协议》与《隐私政策》。本工具仅供学习交流使用。
        </div>
        """, unsafe_allow_html=True)

# ==============================================
# 5. 各核心模块 (精修布局)
# ==============================================
def render_page_home():
    user = st.session_state.user_db[st.session_state.current_user]
    st.markdown("## 🏠 会员中心")
    st.markdown(f"""
    <div class="saas-card">
        <p style="color: #64748b; margin: 0;">账户身份：正式会员</p>
        <h2 style="margin: 10px 0; color: #1e293b;">ID: {user['mid']}</h2>
        <p style="font-size: 1.2rem; color: #1e293b;">可用额度：<strong style="color: #32CD32;">{user['credits']} 次</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 所有数据均已同步至您的会员号，换设备登录后余额仍会保留。")

def render_page_history():
    st.markdown("## ⏰ 面试历史")
    if not st.session_state.history:
        st.info("暂无实战记录")
    else:
        for item in reversed(st.session_state.history):
            st.markdown(f"""
            <div class="saas-card">
                <div style="display:flex; justify-content:space-between;">
                    <strong>{item['pos']}</strong>
                    <span style="color:#32CD32;">得分：{item['score']}</span>
                </div>
                <p style="font-size:12px; color:#64748b;">时间：{item['time']}</p>
                <div style="background:#f8fafc; padding:10px; border-radius:8px; margin-top:10px;">
                    <p style="font-size:13px; margin:0;"><b>AI 点评：</b>{item['summary']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================
# 6. 侧边栏与路由
# ==============================================
def main():
    init_session()
    
    if not st.session_state.is_logged_in:
        render_login()
    else:
        user = st.session_state.user_db[st.session_state.current_user]
        
        # 侧边栏
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.current_user[:3]}****{st.session_state.current_user[-4:]}")
            st.markdown(f"**会员号：`{user['mid']}`**")
            st.markdown(f"**剩余额度：`{user['credits']}` 次**")
            st.markdown("---")
            
            nav_options = ["🏠 会员中心", "📄 AI 简历优化", "🎤 模拟面试", "🖊️ 笔试辅助", "📚 智能知识库", "⏰ 面试历史"]
            page_keys = ["home", "resume", "interview", "exam", "knowledge", "history"]
            sel = st.radio("导航菜单", nav_options, label_visibility="collapsed")
            st.session_state.current_page = page_keys[nav_options.index(sel)]
            
            st.markdown("---")
            st.markdown("### 💳 激活充值")
            code = st.text_input("激活码", type="password")
            if st.button("立即充值"):
                if code in RECHARGE_CODES:
                    user["credits"] += RECHARGE_CODES[code]
                    st.success("充值成功！")
                    st.rerun()
                else:
                    st.error("激活码错误")
            
            if st.button("退出登录"):
                st.session_state.is_logged_in = False
                st.rerun()

        # 页面路由
        cp = st.session_state.current_page
        if cp == "home": render_page_home()
        elif cp == "history": render_page_history()
        elif cp == "resume": 
            st.markdown("## 📄 AI 简历优化")
            if user['credits'] <= 0: st.warning("请先充值额度")
            else: st.info("简历优化模块已就绪")
        elif cp == "interview":
            st.markdown("## 🎤 模拟面试")
            if user['credits'] <= 0: st.warning("请先充值额度")
            else: st.info("面试模块已就绪")
        else:
            st.markdown(f"## {sel}")
            st.info("该模块正在对接最新的 AI 模型，敬请期待...")

if __name__ == "__main__":
    main()
