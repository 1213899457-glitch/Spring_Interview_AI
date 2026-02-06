"""
2026春招AI模拟面试官 | 咸鱼上岸记
升级版：会员额度充值模式
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 核心商业配置 ============
# 充值码数据库：您可以随时修改这些码发给客户
# 格式为 "激活码": 增加的面试次数
RECHARGE_CODES = {
    "XY666": 1,      # 体验码：1次
    "VIP888": 10,    # 进阶码：10次
    "SHANGAN999": 999 # 无限码：999次
}

NAV_ITEMS = [
    ("🏠 个人中心", "home"),
    ("📄 AI 简历神笔", "resume"),
    ("🎤 模拟面试", "interview"),
    ("📚 知识库", "knowledge"),
    ("⏰ 面试历史", "history"),
]

# ============ 页面配置 ============
st.set_page_config(
    page_title="咸鱼上岸记 | 会员版",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ SaaS 风格 CSS ============
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
    [data-testid="stSidebar"] .stMarkdown { color: #f5f5f7 !important; }
    .interviewer-msg { background: #1d1d1f; color: #f5f5f7; padding: 16px 20px; border-radius: 12px 12px 12px 4px; margin: 12px 0; font-size: 0.95rem; line-height: 1.6; }
    .user-msg { background: #e8e8ed; color: #1d1d1f; padding: 16px 20px; border-radius: 12px 12px 4px 12px; margin: 12px 0; font-size: 0.95rem; line-height: 1.6; }
    .stButton > button { background: #1d1d1f !important; color: #ffffff !important; border: none !important; border-radius: 8px !important; padding: 10px 24px !important; font-weight: 500 !important; }
    .stButton > button:hover { opacity: 0.85 !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def get_deepseek_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请在 Streamlit Secrets 中配置 DEEPSEEK_API_KEY")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def call_deepseek(messages: list, client: OpenAI) -> str:
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0.8)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[API 调用失败: {str(e)}]"

def init_session():
    # 初始化会员余额
    if "user_credits" not in st.session_state:
        st.session_state.user_credits = 0
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "started" not in st.session_state:
        st.session_state.started = False
    if "report" not in st.session_state:
        st.session_state.report = None

# ============ 会员充值模块 ============
def render_recharge_section():
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💳 会员充值**")
    recharge_code = st.sidebar.text_input("输入激活码", type="password", placeholder="请输入充值码")
    if st.sidebar.button("立即充值", use_container_width=True):
        if recharge_code in RECHARGE_CODES:
            added_credits = RECHARGE_CODES[recharge_code]
            st.session_state.user_credits += added_credits
            st.sidebar.success(f"成功充值 {added_credits} 次面试额度！")
            st.rerun()
        else:
            st.sidebar.error("激活码无效")

# ============ 页面渲染 ============
def render_page_home():
    st.markdown("## 🏠 个人中心")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background: #ffffff; border-radius: 12px; padding: 24px; border: 1px solid #d2d2d7;">
            <p style="color: #86868b; margin-bottom: 4px;">当前可用面试额度</p>
            <h1 style="margin: 0; color: #1d1d1f;">{st.session_state.user_credits} 次</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 💡 如何获取额度？")
    st.write("1. 前往【咸鱼上岸记】小红书/咸鱼店铺下单。")
    st.write("2. 获取您的专属激活码。")
    st.write("3. 在左侧边栏输入激活码进行充值。")

def render_page_resume():
    st.markdown("## 📄 AI 简历神笔")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请先在左侧充值激活。")
        return
    
    st.write("输入岗位并粘贴简历，AI 将为您进行 STAR 法则优化。")
    job_target = st.text_input("目标岗位")
    raw_resume = st.text_area("原始简历内容", height=200)
    
    if st.button("开始优化（消耗 1 次额度）"):
        if job_target and raw_resume:
            st.session_state.user_credits -= 1
            with st.spinner("AI 神笔修改中..."):
                client = get_deepseek_client()
                prompt = f"请根据以下目标岗位：{job_target}，对这份简历进行深度优化，增强专业性，符合STAR法则：\n{raw_resume}"
                result = call_deepseek([{"role": "user", "content": prompt}], client)
                st.markdown("### ✨ 优化建议")
                st.markdown(result)
        else:
            st.error("请填全信息")

def render_page_interview(client):
    st.markdown("## 🎤 模拟面试")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请先在左侧充值激活。")
        return

    if not st.session_state.started:
        pos = st.text_input("目标岗位")
        res = st.text_area("简历内容")
        if st.button("开始面试（消耗 1 次额度）"):
            if pos and res:
                st.session_state.user_credits -= 1 # 扣除额度
                st.session_state.started = True
                st.session_state.pos = pos
                st.session_state.res = res
                st.session_state.conversation = []
                st.session_state.round = 0
                st.rerun()
            else:
                st.error("请填写岗位和简历")
    else:
        # 这里保留您之前的面试对话逻辑 (省略部分重复的对话 UI 代码以保持长度)
        st.write(f"正在面试：{st.session_state.pos}")
        # 对话循环和 call_deepseek 逻辑...
        if st.button("结束面试并返回"):
            st.session_state.started = False
            st.rerun()

# ============ 主程序 ============
def main():
    init_session()
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("## 🎯 咸鱼上岸记")
        st.markdown(f"**欢迎，主理人！**")
        st.markdown(f"账户余额：`{st.session_state.user_credits}` 次")
        
        options = [item[0] for item in NAV_ITEMS]
        page_ids = [item[1] for item in NAV_ITEMS]
        selected = st.radio("功能导航", options, label_visibility="collapsed")
        st.session_state.current_page = page_ids[options.index(selected)]
        
        render_recharge_section()

    # 主内容渲染
    page = st.session_state.current_page
    if page == "home":
        render_page_home()
    elif page == "resume":
        render_page_resume()
    elif page == "interview":
        c = get_deepseek_client()
        render_page_interview(c)
    else:
        st.info("功能开发中...")

if __name__ == "__main__":
    main()
