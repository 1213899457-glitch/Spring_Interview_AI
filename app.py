"""
2026春招AI模拟面试官 | 咸鱼上岸记
SaaS 终极全功能版：集成历史记录、知识库、简历优化、笔试辅助
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
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
    }

    /* 侧边栏样式与文字可见性修复 */
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

    /* 亮绿色按钮交互 */
    .stButton > button {
        background: #32CD32 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100%;
    }

    /* 统计卡片 */
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
    if "started" not in st.session_state: st.session_state.started = False
    # 初始化知识库数据
    if "kb_data" not in st.session_state:
        st.session_state.kb_data = [
            {"question": "请做一个简单的自我介绍", "answer": "建议包含：我是谁+核心优势+为什么适合。控制在1-2分钟。", "cate": "行为面(BQ)"},
            {"question": "你最大的缺点是什么？", "answer": "谈论一个已被改进的弱点，或与岗位无关的特征。", "cate": "行为面(BQ)"}
        ]
    # 初始化历史数据
    if "history_data" not in st.session_state:
        st.session_state.history_data = [
            {"id": "面试 1", "position": "Java 工程师", "time": "2026-02-05 14:30", "duration": "12分45秒", "score": 85, "summary": "专业扎实，但项目描述逻辑可优化。"}
        ]

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

# ============ 5. 侧边栏导航 ============
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
        code = st.text_input("激活码", type="password", placeholder="输入码")
        if st.button("立即充值"):
            if code in RECHARGE_CODES:
                st.session_state.user_credits += RECHARGE_CODES[code]
                st.success("成功！")
                st.rerun()
            else: st.error("无效")

# ============ 6. 核心功能页 ============

def render_page_history():
    st.markdown("## ⏰ 面试历史")
    # 统计概览
    st.markdown(f"""
    <div class="recharge-card">
        <p style="color: #f5f5f7; margin: 0;">已完成面试挑战</p>
        <h2 style="color: #32CD32; margin: 10px 0;">{len(st.session_state.history_data)} 场</h2>
    </div>
    """, unsafe_allow_html=True)

    for item in st.session_state.history_data:
        with st.container():
            st.markdown(f"""
            <div class="saas-card" style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{item['id']}</strong>
                    <span style="background: #32CD32; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold;">得分：{item['score']}</span>
                </div>
                <hr style="margin: 10px 0; border: 0.5px solid #f5f5f7;">
                <p style="font-size: 0.9rem; margin: 5px 0;"><b>岗位：</b>{item['position']} | <b>时长：</b>{item['duration']}</p>
                <p style="font-size: 0.9rem; margin: 5px 0;"><b>时间：</b>{item['time']}</p>
                <div style="background: #f5f5f7; padding: 10px; border-radius: 6px; margin-top: 10px;">
                    <p style="font-size: 0.85rem; color: #86868b; margin: 0;"><b>AI 简评：</b>{item['summary']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"查看 {item['id']} 复盘详情", key=f"hist_{item['id']}"):
                st.toast("正在生成详细报告...")

def render_page_knowledge():
    st.markdown("## 📚 智能面试知识库")
    col_search, col_cate = st.columns([2, 1])
    with col_search: search_q = st.text_input("🔍 搜索...", placeholder="如：自我介绍")
    with col_cate: cate_f = st.selectbox("筛选", ["全部", "行为面(BQ)", "技术基础", "外贸/外语"])

    with st.expander("➕ 添加新题（AI 自动补全答案）"):
        new_q = st.text_input("题目名称")
        if st.button("入库"):
            if new_q:
                with st.spinner("AI 编写答案中..."):
                    ans = call_ai([{"role": "user", "content": f"请针对面试题‘{new_q}’写个标准答案。"}], get_client())
                    st.session_state.kb_data.insert(0, {"question": new_q, "answer": ans, "cate": "自定义"})
                    st.rerun()

    st.markdown("---")
    for item in st.session_state.kb_data:
        if search_q.lower() in item["question"].lower():
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: 
                    st.markdown(f"**Q:** {item['question']}")
                    st.caption(f"标签：{item['cate']}")
                with c2: st.success(item["answer"])
                st.divider()

def render_page_exam():
    st.markdown("## 🖊️ 笔试辅助")
    if st.session_state.user_credits <= 0: st.warning("余额不足"); return
    st.markdown(f"""<div class="recharge-card"><p style="color: #32CD32; margin: 0;">1 次面试额度 = 2 道笔试题</p>
    <h2 style="color: white; margin: 10px 0;">折合可解答 {st.session_state.user_credits * 2} 题</h2></div>""", unsafe_allow_html=True)
    st.file_uploader("上传截图")
    if st.button("开始解答"): st.info("正在调取 OCR...")

def render_page_home():
    st.markdown("## 🏠 个人中心")
    st.markdown(f"""<div class="saas-card"><h2>咸鱼上岸·特权会员</h2>
    <p style="font-size: 1.2rem;">当前可用额度：<strong>{st.session_state.user_credits} 次</strong></p></div>""", unsafe_allow_html=True)
    st.write("---")
    st.success("💡 建议：先去【知识库】刷题，再去【模拟面试】实战！")

def render_page_resume():
    st.markdown("## 📄 AI 简历神笔")
    if st.session_state.user_credits <= 0: st.warning("余额不足"); return
    job = st.text_input("岗位")
    raw = st.text_area("简历内容", height=200)
    if st.button("一键优化 (消耗 1 次额度)"):
        if job and raw:
            st.session_state.user_credits -= 1
            with st.spinner("优化中..."):
                res = call_ai([{"role": "user", "content": f"优化岗位{job}的简历：\n{raw}"}], get_client())
                st.markdown(res)
        else: st.error("请填全")

def render_page_interview(client):
    st.markdown("## 🎤 模拟面试")
    if st.session_state.user_credits <= 0: st.warning("余额不足"); return
    if not st.session_state.started:
        pos = st.text_input("面试岗位")
        res = st.text_area("个人简历")
        if st.button("消耗 1 次额度开始面试"):
            if pos and res:
                st.session_state.user_credits -= 1
                st.session_state.started = True
                st.session_state.conversation = [{"role": "interviewer", "content": f"你好，我是面试官。请针对{pos}岗位做个介绍。"}]
                st.rerun()
    else:
        for chat in st.session_state.conversation:
            st.write(f"**{'面试官' if chat['role']=='interviewer' else '我'}**：{chat['content']}")
        if st.button("结束面试"): st.session_state.started = False; st.rerun()

# ============ 7. 主流程 ============
def main():
    init_session()
    render_sidebar()
    page = st.session_state.current_page
    client = get_client()
    if page == "home": render_page_home()
    elif page == "knowledge": render_page_knowledge()
    elif page == "resume": render_page_resume()
    elif page == "interview": render_page_interview(client)
    elif page == "exam": render_page_exam()
    elif page == "history": render_page_history()

if __name__ == "__main__":
    main()
