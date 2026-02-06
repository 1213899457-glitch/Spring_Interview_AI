"""
2026春招AI模拟面试官 | 咸鱼上岸记
升级版：全功能 SaaS 会员充值版
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 核心充值码配置 ============
# 您可以根据需要修改或增加激活码。格式为 "激活码": 增加的次数
RECHARGE_CODES = {
    "XY666": 1,          # 体验码：1次
    "VIP888": 10,        # 进阶码：10次
    "SHANGAN999": 999    # 无限码：999次
}

NAV_ITEMS = [
    ("🏠 个人中心", "home"),
    
    ("📄 AI 简历神笔", "resume"),
    
    ("🎤 模拟面试", "interview"),
    
    ("🖊️ 笔试辅助", "exam"),
    
    ("📚 知识库", "knowledge"),
    
    ("⏰ 面试历史", "history"),
]

# ============ 页面配置 ============
st.set_page_config(
    page_title="咸鱼上岸记 | 春招AI助手",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ SaaS 风格 CSS (修复文字显示) ============
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
    /* 侧边栏文字颜色增强 */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #f5f5f7 !important; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #f5f5f7 !important;
        font-size: 1rem !important;
    }
    .interviewer-msg { background: #1d1d1f; color: #f5f5f7; padding: 16px 20px; border-radius: 12px 12px 12px 4px; margin: 12px 0; }
    .user-msg { background: #e8e8ed; color: #1d1d1f; padding: 16px 20px; border-radius: 12px 12px 4px 12px; margin: 12px 0; }
    .stButton > button { background: #1d1d1f !important; color: #ffffff !important; border-radius: 8px !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ 通用函数 ============
def get_deepseek_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请配置 DEEPSEEK_API_KEY")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def call_deepseek(messages: list, client: OpenAI) -> str:
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0.8)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[API 调用失败: {str(e)}]"

def init_session():
    if "user_credits" not in st.session_state:
        st.session_state.user_credits = 0  # 初始余额为0
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "round" not in st.session_state:
        st.session_state.round = 0
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "started" not in st.session_state:
        st.session_state.started = False
    if "report" not in st.session_state:
        st.session_state.report = None

# ============ 侧边栏充值逻辑 ============
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎯 咸鱼上岸记")
        st.markdown(f"**账户余额：`{st.session_state.user_credits}` 次**")
        st.markdown("---")
        
        # 导航
        options = [item[0] for item in NAV_ITEMS]
        page_ids = [item[1] for item in NAV_ITEMS]
        selected = st.radio("功能导航", options, label_visibility="collapsed")
        st.session_state.current_page = page_ids[options.index(selected)]
        
        st.markdown("---")
        st.markdown("### 💳 会员充值")
        recharge_code = st.text_input("输入激活码", type="password", placeholder="请在此输入充值码")
        if st.button("立即充值", use_container_width=True):
            if recharge_code in RECHARGE_CODES:
                added = RECHARGE_CODES[recharge_code]
                st.session_state.user_credits += added
                st.success(f"成功充值 {added} 次额度！")
                st.rerun()
            else:
                st.error("激活码错误")

# ============ 各模块渲染 ============
def render_page_home():
    st.markdown("## 🏠 个人中心")
    st.markdown(f"""
    <div style="background: #ffffff; border-radius: 12px; padding: 24px; border: 1px solid #d2d2d7; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <p style="color: #86868b; margin: 0;">当前会员身份</p>
        <h2 style="margin: 8px 0;">咸鱼上岸·特权会员</h2>
        <p style="color: #1d1d1f; font-size: 1.2rem;">可用额度：<strong>{st.session_state.user_credits} 次</strong></p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 📢 公告栏")
    st.info("春招高峰期已到！AI简历优化与模拟面试现已全量开放。尚未获取激活码？请联系主理人。")

def render_page_resume():
    st.markdown("## 📄 AI 简历神笔")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请在左侧充值激活。")
        return
    
    col1, col2 = st.columns([1, 1])
    with col1:
        job_target = st.text_input("目标岗位", placeholder="例：互联网产品经理")
        raw_resume = st.text_area("粘贴简历内容", height=300, placeholder="将简历文字粘贴在此...")
    
    if st.button("开始一键优化（消耗 1 次额度）"):
        if job_target and raw_resume:
            st.session_state.user_credits -= 1
            with st.spinner("AI 正在深度优化中..."):
                client = get_deepseek_client()
                prompt = f"你是一位资深猎头，请针对岗位【{job_target}】，使用STAR法则深度优化以下简历内容，使其更有竞争力：\n{raw_resume}"
                result = call_deepseek([{"role": "user", "content": prompt}], client)
                with col2:
                    st.markdown("### ✨ 优化结果")
                    st.markdown(result)
                    st.balloons()
        else:
            st.error("请填入岗位和简历内容")

def render_page_interview(client):
    st.markdown("## 🎤 模拟面试")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请在左侧充值激活。")
        return
    
    # ... 此处引用您原本的模拟面试逻辑 ...
    # 记得在开始面试的那个 if st.button("开始模拟面试") 里面加一行：
    # st.session_state.user_credits -= 1 

# ============ 主程序 ============
def main():
    init_session()
    render_sidebar()
    
    page = st.session_state.current_page
    client = get_deepseek_client()
    
    if page == "home":
        render_page_home()
    elif page == "resume":
        render_page_resume()
    elif page == "interview":
        if client: render_page_interview(client)
    else:
        st.info("该模块功能正在接入中，敬请期待！")

if __name__ == "__main__":
    main()
