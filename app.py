"""
2026春招AI模拟面试官 | 咸鱼上岸记
SaaS 自动存档版：面试结束自动进入历史记录
"""

import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 1. 核心激活码配置 ============
RECHARGE_CODES = {"XY666": 1, "VIP888": 10, "SHANGAN999": 999}

NAV_ITEMS = [
    ("🏠 个人中心", "home"),
    ("📄 AI 简历神笔", "resume"),
    ("🎤 模拟面试", "interview"),
    ("🖊️ 笔试辅助", "exam"),
    ("📚 知识库", "knowledge"),
    ("⏰ 面试历史", "history"),
]

# ============ 2. 页面配置 ============
st.set_page_config(page_title="咸鱼上岸记 | 春招AI教练", page_icon="🎯", layout="wide")

# ============ 3. SaaS 风格 CSS ============
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1d1d1f 0%, #2d2d2f 100%) !important; }
    [data-testid="stSidebar"] * { color: #f5f5f7 !important; }
    .stButton > button { background: #32CD32 !important; color: #000 !important; font-weight: 600 !important; border-radius: 10px !important; }
    .saas-card { background: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #d2d2d7; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .recharge-card { background: #1e1e1e; padding: 20px; border-radius: 12px; border: 1px solid #32CD32; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ============ 4. 初始化 ============
def init_session():
    if "user_credits" not in st.session_state: st.session_state.user_credits = 0
    if "current_page" not in st.session_state: st.session_state.current_page = "home"
    if "started" not in st.session_state: st.session_state.started = False
    if "history_data" not in st.session_state: st.session_state.history_data = []
    if "kb_data" not in st.session_state:
        st.session_state.kb_data = [{"question": "自我介绍", "answer": "1-2分钟，突出核心优势。", "cate": "行为面"}]

def get_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def call_ai(msgs, client):
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=msgs)
        return resp.choices[0].message.content.strip()
    except: return "AI 接口连接中..."

# ============ 5. 核心功能页 ============

def render_page_history():
    st.markdown("## ⏰ 面试历史")
    if not st.session_state.history_data:
        st.info("还没有面试记录，快去开启一场实战吧！")
        return
    
    st.markdown(f'<div class="recharge-card"><h2 style="color:#32CD32;">{len(st.session_state.history_data)} 场实战记录</h2></div>', unsafe_allow_html=True)
    
    for item in reversed(st.session_state.history_data): # 最新的在上面
        st.markdown(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between;">
                <strong>{item['position']}</strong>
                <span style="color: #32CD32; font-weight: bold;">得分：{item['score']}</span>
            </div>
            <p style="font-size: 0.8rem; color: #86868b;">时间：{item['time']}</p>
            <div style="background: #f5f5f7; padding: 10px; border-radius: 6px; margin-top: 5px;">
                <p style="font-size: 0.85rem; margin: 0;"><b>AI 点评：</b>{item['summary']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_page_interview(client):
    st.markdown("## 🎤 模拟面试")
    if st.session_state.user_credits <= 0:
        st.warning("余额不足"); return

    if not st.session_state.started:
        pos = st.text_input("目标岗位", placeholder="例：后端开发")
        res = st.text_area("个人简历")
        if st.button("开始面试 (消耗 1 次额度)"):
            if pos and res:
                st.session_state.user_credits -= 1
                st.session_state.started = True
                st.session_state.current_pos = pos
                st.session_state.conversation = [{"role": "interviewer", "content": f"你好，我是面试官。请针对{pos}岗位做个介绍。"}]
                st.rerun()
    else:
        # 对话区
        for chat in st.session_state.conversation:
            st.write(f"**{'面试官' if chat['role']=='interviewer' else '我'}**：{chat['content']}")
        
        # 底部操作
        if st.button("🏁 结束面试并生成复盘"):
            # 1. 自动生成一个简单的存档数据
            new_entry = {
                "position": st.session_state.current_pos,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "score": 88, # 实际可由 AI 评分
                "summary": "表现不错，建议在项目细节描述上再深挖一下。" # 实际可由 AI 总结
            }
            # 2. 存入历史数据
            st.session_state.history_data.append(new_entry)
            # 3. 重置面试状态
            st.session_state.started = False
            st.success("面试记录已自动存档至【面试历史】！")
            st.rerun()

# ============ 6. 侧边栏与主控 ============
def main():
    init_session()
    with st.sidebar:
        st.markdown(f"### 剩余额度：{st.session_state.user_credits}")
        options = [i[0] for i in NAV_ITEMS]
        page_ids = [i[1] for i in NAV_ITEMS]
        sel = st.radio("导航", options, label_visibility="collapsed")
        st.session_state.current_page = page_ids[options.index(sel)]
        code = st.text_input("激活码", type="password")
        if st.button("充值"):
            if code in RECHARGE_CODES:
                st.session_state.user_credits += RECHARGE_CODES[code]
                st.rerun()

    page = st.session_state.current_page
    client = get_client()
    if page == "home":
        st.markdown("## 🏠 个人中心")
        st.markdown(f'<div class="saas-card"><h3>可用额度：{st.session_state.user_credits} 次</h3></div>', unsafe_allow_html=True)
    elif page == "history": render_page_history()
    elif page == "interview": render_page_interview(client)
    elif page == "knowledge":
        st.markdown("## 📚 知识库")
        for item in st.session_state.kb_data:
            st.write(f"**Q:** {item['question']}")
            st.success(item['answer'])

if __name__ == "__main__":
    main()
