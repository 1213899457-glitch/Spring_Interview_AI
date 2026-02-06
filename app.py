"""
2026春招AI模拟面试官 | 咸鱼上岸记
SaaS 精修版：参考 Offer+ 界面布局与功能增强
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 1. 核心激活码配置 ============
RECHARGE_CODES = {
    "XY666": 1,          # 体验码
    "VIP888": 10,        # 进阶码
    "SHANGAN999": 999    # 无限码
}

NAV_ITEMS = [
    ("🏠 个人中心", "home"),
    ("📄 AI 简历神笔", "resume"),
    ("🎤 模拟面试", "interview"),
    ("🖊️ 笔试辅助", "exam"),
    ("📚 知识库", "knowledge"),
    ("⏰ 面试历史", "history"),
]

# ============ 2. 页面配置 ============
st.set_page_config(
    page_title="咸鱼上岸记 | 春招AI教练",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ 3. SaaS 风格 CSS (参考 Offer+ 亮绿色系) ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* 基础背景与文字 */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
    }

    /* 侧边栏：深色渐变 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1d1d1f 0%, #2d2d2f 100%) !important;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #f5f5f7 !important; 
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #f5f5f7 !important;
        font-weight: 500 !important;
    }

    /* 亮绿色按钮：参考竞品 */
    .stButton > button {
        background: #32CD32 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(50, 205, 50, 0.3);
    }

    /* 模拟竞品余额卡片 */
    .recharge-card {
        background: #1e1e1e;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #32CD32;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .saas-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #d2d2d7;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============ 4. 初始化与通用函数 ============
def init_session():
    if "user_credits" not in st.session_state: st.session_state.user_credits = 0
    if "current_page" not in st.session_state: st.session_state.current_page = "home"
    if "conversation" not in st.session_state: st.session_state.conversation = []
    if "started" not in st.session_state: st.session_state.started = False

def get_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请配置 API Key")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def call_ai(msgs, client):
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=msgs, temperature=0.7)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"AI 忙碌中：{str(e)}"

# ============ 5. 侧边栏渲染 ============
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎯 咸鱼上岸记")
        st.markdown(f"**剩余额度：`{st.session_state.user_credits}` 次**")
        st.markdown("---")
        
        options = [item[0] for item in NAV_ITEMS]
        page_ids = [item[1] for item in NAV_ITEMS]
        selected = st.radio("导航", options, label_visibility="collapsed")
        st.session_state.current_page = page_ids[options.index(selected)]
        
        st.markdown("---")
        st.markdown("### 💳 激活充值")
        code = st.text_input("激活码", type="password", placeholder="输入激活码")
        if st.button("立即激活额度"):
            if code in RECHARGE_CODES:
                st.session_state.user_credits += RECHARGE_CODES[code]
                st.success(f"充值成功！")
                st.rerun()
            else:
                st.error("无效激活码")

# ============ 6. 模块渲染 ============

def render_page_home():
    st.markdown("## 🏠 个人中心")
    st.markdown(f"""
    <div class="saas-card">
        <p style="color: #86868b; margin: 0;">当前身份</p>
        <h2 style="margin: 8px 0;">咸鱼上岸·特权会员</h2>
        <p style="color: #1d1d1f; font-size: 1.2rem;">可用额度：<strong>{st.session_state.user_credits} 次</strong></p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.markdown("### 📢 邀请好友有奖")
    st.success("分享网址给同学，好友注册并购买，您可额外获赠 3 次面试时长！")

def render_page_resume():
    st.markdown("## 📄 AI 简历神笔")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请先充值。")
        return

    job = st.text_input("目标岗位名称", placeholder="例：产品经理")
    resume_text = st.text_area("简历/项目内容", height=200)
    
    # 高级设置折叠
    with st.expander("🛠️ 高级优化选项"):
        style = st.selectbox("修改风格", ["专业商务", "技术深挖型", "STAR法则强化"])
        add_keywords = st.toggle("自动匹配行业关键词", value=True)

    if st.button("开始优化简历 (消耗 1 次额度)"):
        if job and resume_text:
            st.session_state.user_credits -= 1
            with st.spinner("AI 正在深度重构..."):
                client = get_client()
                prompt = [{"role": "user", "content": f"请以{style}风格，优化针对【{job}】岗位的简历内容：\n{resume_text}"}]
                res = call_ai(prompt, client)
                st.markdown("### ✨ 修改后建议")
                st.markdown(res)
        else:
            st.error("请填全岗位和内容")

def render_page_exam():
    st.markdown("## 🖊️ 笔试辅助")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足")
        return

    # 参考竞品额度展示卡片
    st.markdown(f"""
    <div class="recharge-card">
        <p style="color: #32CD32; margin: 0;">每题消耗 1/2 面试额度</p>
        <h2 style="color: white; margin: 10px 0;">折合可解答 {st.session_state.user_credits * 2} 题</h2>
    </div>
    """, unsafe_allow_html=True)

    st.selectbox("笔试类型", ["常规技术笔试", "逻辑/行测测试", "英文笔试"])
    st.file_uploader("点击上传题目截图或文件", type=["jpg", "png", "pdf"])
    
    if st.button("开始解答 (消耗额度)"):
        st.info("功能正在接入中，敬请期待...")

def render_page_interview(client):
    st.markdown("## 🎤 模拟面试")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足")
        return

    if not st.session_state.started:
        st.markdown("### 面试配置")
        pos = st.text_input("面试岗位")
        res = st.text_area("简历背景")
        
        # 参考图 12 的高级设置
        with st.expander("⚙️ 面试高级设置"):
            st.selectbox("面试语言", ["简体中文", "English", "混合模式"])
            st.selectbox("面试官性格", ["严厉毒舌", "温柔引导", "大厂HR风"])
            st.toggle("自动作答 (启用后 AI 会提供参考答案)", value=True)

        if st.button("开始面试 (消耗 1 次额度)"):
            if pos and res:
                st.session_state.user_credits -= 1
                st.session_state.started = True
                st.session_state.conversation = [{"role": "interviewer", "content": f"你好，我是今天的面试官。针对你申请的{pos}岗位，请先做一个自我介绍。"}]
                st.rerun()
    else:
        # 对话展示区域
        for chat in st.session_state.conversation:
            role = "面试官" if chat["role"]=="interviewer" else "我"
            st.write(f"**{role}**：{chat['content']}")
        
        user_input = st.text_input("在这里输入你的回答...")
        if st.button("发送"):
            if user_input:
                st.session_state.conversation.append({"role": "user", "content": user_input})
                # 此处省略 AI 追问逻辑，可接入 call_ai
                st.rerun()
        
        if st.button("结束面试"):
            st.session_state.started = False
            st.rerun()

# ============ 7. 主流程 ============
def main():
    init_session()
    render_sidebar()
    
    page = st.session_state.current_page
    client = get_client()
    
    if page == "home": render_page_home()
    elif page == "resume": render_page_resume()
    elif page == "interview": render_page_interview(client)
    elif page == "exam": render_page_exam()
    else: st.info("模块开发中...")

if __name__ == "__main__":
    main()
