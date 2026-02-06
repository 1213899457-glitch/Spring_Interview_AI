"""
2026春招AI模拟面试官 | 咸鱼上岸记
SaaS 全功能精修版：集成智能知识库、笔试辅助与会员系统
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

# ============ 3. SaaS 风格 CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1d1d1f 0%, #2d2d2f 100%) !important;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #f5f5f7 !important; 
    }
    .stButton > button {
        background: #32CD32 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100%;
    }
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
    if "kb_data" not in st.session_state:
        st.session_state.kb_data = [
            {"question": "请做一个简单的自我介绍", "answer": "建议包含：我是谁+我的核心优势+我为什么适合这个岗位。用1-2分钟表达完毕。", "cate": "行为面(BQ)"},
            {"question": "你最大的缺点是什么？", "answer": "避坑指南：不要说真的缺点，要说一个可以被转化为职业优势的‘缺点’，并强调你如何改进。", "cate": "行为面(BQ)"}
        ]

def get_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请在 Secrets 中配置 DEEPSEEK_API_KEY")
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
        selected = st.radio("功能导航", options, label_visibility="collapsed")
        st.session_state.current_page = page_ids[options.index(selected)]
        st.markdown("---")
        st.markdown("### 💳 激活充值")
        code = st.text_input("输入激活码", type="password")
        if st.button("立即充值"):
            if code in RECHARGE_CODES:
                st.session_state.user_credits += RECHARGE_CODES[code]
                st.success("充值成功！")
                st.rerun()
            else: st.error("无效码")

# ============ 6. 核心功能页渲染 ============

def render_page_knowledge():
    st.markdown("## 📚 智能面试知识库")
    col_search, col_cate = st.columns([2, 1])
    with col_search:
        search_q = st.text_input("🔍 搜索面试题...", placeholder="如：自我介绍")
    with col_cate:
        cate_filter = st.selectbox("分类筛选", ["全部", "行为面(BQ)", "技术基础", "项目深挖", "外贸/外语"])

    with st.expander("➕ 添加新题目（支持 AI 自动生成答案）"):
        new_q = st.text_input("题目名称")
        new_a = st.text_area("手动输入答案（留空则由 AI 生成）")
        if st.button("入库并保存"):
            if new_q:
                final_a = new_a
                if not new_a:
                    with st.spinner("AI 正在为您编写参考答案..."):
                        final_a = call_ai([{"role": "user", "content": f"请针对面试题‘{new_q}’写一个标准的专业参考答案。"}], get_client())
                st.session_state.kb_data.insert(0, {"question": new_q, "answer": final_a, "cate": "自定义"})
                st.success("入库成功！")
                st.rerun()

    st.markdown("---")
    for idx, item in enumerate(st.session_state.kb_data):
        if search_q.lower() in item["question"].lower() and (cate_filter == "全部" or item["cate"] == cate_filter):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"**Q{idx+1}:** {item['question']}")
                    st.caption(f"标签：{item['cate']}")
                with c2:
                    st.success(item["answer"])
                st.divider()

def render_page_exam():
    st.markdown("## 🖊️ 笔试辅助")
    if st.session_state.user_credits <= 0:
        st.warning("⚠️ 余额不足，请在左侧充值。")
        return
    st.markdown(f"""<div class="recharge-card"><p style="color: #32CD32; margin: 0;">每题消耗 1/2 面试额度</p>
    <h2 style="color: white; margin: 10px 0;">折合可解答 {st.session_state.user_credits * 2} 题</h2></div>""", unsafe_allow_html=True)
    st.selectbox("笔试语言", ["简体中文", "English", "C++/Java/Python"])
    st.file_uploader("上传题目截图")
    if st.button("开始 AI 解答"): st.info("正在对接截图 OCR 功能...")

def render_page_home():
    st.markdown("## 🏠 个人中心")
    st.markdown(f"""<div class="saas-card"><p style="color: #86868b; margin: 0;">当前身份</p>
    <h2 style="margin: 8px 0;">咸鱼上岸·特权会员</h2><p style="color: #1d1d1f; font-size: 1.2rem;">可用额度：<strong>{st.session_state.user_credits} 次</strong></p></div>""", unsafe_allow_html=True)
    st.write("---")
    st.success("💡 提示：您可以去【知识库】预习题目，再去【模拟面试】实战练习！")

def render_page_resume():
    st.markdown("## 📄 AI 简历神笔")
    if st.session_state.user_credits <= 0: st.warning("余额不足"); return
    job = st.text_input("目标岗位")
    raw = st.text_area("简历内容", height=200)
    if st.button("一键 STAR 法则优化"):
        if job and raw:
            st.session_state.user_credits -= 1
            with st.spinner("AI 重构中..."):
                res = call_ai([{"role": "user", "content": f"优化针对{job}的简历：\n{raw}"}], get_client())
                st.markdown(res)
        else: st.error("请填写完整")

def render_page_interview(client):
    st.markdown("## 🎤 模拟面试")
    if st.session_state.user_credits <= 0: st.warning("余额不足"); return
    if not st.session_state.started:
        pos = st.text_input("岗位")
        res = st.text_area("简历")
        with st.expander("⚙️ 面试高级设置 (参考 Offer+ 逻辑)"):
            st.selectbox("面试官性格", ["严厉毒舌", "温柔引导", "大厂HR风"])
            st.toggle("自动作答引导", value=True)
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
    else: st.info("模块开发中...")

if __name__ == "__main__":
    main()
