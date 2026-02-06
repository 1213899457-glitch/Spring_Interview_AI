"""
2026春招AI模拟面试官 | 咸鱼上岸记
终极修复商业版：全功能会员制 + 自动扣费 + 界面优化
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 1. 核心激活码配置 ============
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

# ============ 3. SaaS 风格 CSS (修复文字显示与布局) ============
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
    /* 侧边栏文字强制显现 */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #f5f5f7 !important; 
    }
    /* 调整单选框样式 */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #f5f5f7 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    .saas-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #d2d2d7;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stButton > button { background: #1d1d1f !important; color: #ffffff !important; border-radius: 8px !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ 4. 初始化 ============
def init_session():
    if "user_credits" not in st.session_state:
        st.session_state.user_credits = 0
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

def get_deepseek_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("⚠️ 请在 Streamlit Secrets 中配置 API Key")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def call_deepseek(messages, client):
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0.7)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"调用失败：{str(e)}"

# ============ 5. 侧边栏渲染 ============
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎯 咸鱼上岸记")
        st.markdown(f"**账户余额：`{st.session_state.user_credits}` 次**")
        st.markdown("---")
        
        options = [item[0] for item in NAV_ITEMS]
        page_ids = [item[1] for item in NAV_ITEMS]
        selected = st.radio("导航菜单", options, label_visibility="collapsed")
        st.session_state.current_page = page_ids[options.index(selected)]
        
        st.markdown("---")
        st.markdown("### 💳 会员充值")
        code = st.text_input("输入激活码", type="password", placeholder="请输入充值码")
        if st.button("立即充值", use_container_width=True):
            if code in RECHARGE_CODES:
                added = RECHARGE_CODES[code]
                st.session_state.user_credits += added
                st.success(f"成功充值 {added} 次！")
                st.rerun()
            else:
                st.error("激活码无效")

# ============ 6. 核心功能页 ============
def render_page_home():
    st.markdown("## 🏠 个人中心")
    st.markdown(f"""
    <div class="saas-card">
        <p style="color: #86868b; margin: 0;">当前会员身份</p>
        <h2 style="margin: 8px 0;">咸鱼上岸·特权会员</h2>
        <p style="color: #1d1d1f; font-size: 1.2rem;">可用额度：<strong>{st.session_state.user_credits} 次</strong></p>
    </div>
    """, unsafe_allow_html=True)
    st.info("提示：模拟面试或简历优化均会消耗 1 次额度。")

def render_page_resume():
    st.markdown("## 📄 AI 简历神笔")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请先充值。")
        return

    col1, col2 = st.columns(2)
    with col1:
        target_job = st.text_input("目标岗位", placeholder="例：后端开发工程师")
        resume_text = st.text_area("简历原始内容", height=300, placeholder="粘贴简历文字...")
        if st.button("开始优化（消耗 1 次额度）"):
            if target_job and resume_text:
                st.session_state.user_credits -= 1
                client = get_deepseek_client()
                with st.spinner("AI 正在为您改写简历..."):
                    prompt_msg = [{"role": "user", "content": f"请针对岗位【{target_job}】，优化这份简历内容：\n{resume_text}"}]
                    result = call_deepseek(prompt_msg, client)
                    with col2:
                        st.markdown("### ✨ 优化建议")
                        st.markdown(result)
            else:
                st.error("请填全信息")

# ============ 7. 主逻辑 ============
def main():
    init_session()
    render_sidebar()
    
    page = st.session_state.current_page
    if page == "home":
        render_page_home()
    elif page == "resume":
        render_page_resume()
    elif page == "interview":
        st.markdown("## 🎤 模拟面试")
        st.write("面试模块正在加载您的简历数据...")
        # 后续可继续丰富面试逻辑
    else:
        st.info("该模块正在对接中...")

if __name__ == "__main__":
    main()
