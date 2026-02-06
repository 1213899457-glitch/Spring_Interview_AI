"""
2026春招AI模拟面试官 | 咸鱼上岸记
专业 SaaS 多模块布局
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 配置 ============
CORRECT_ORDER_ID = "XYSA888"

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
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { border-radius: 8px !important; border: 1px solid #d2d2d7 !important; }
    .nav-label { font-size: 0.95rem; padding: 8px 0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def get_deepseek_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key.strip() == "":
        st.error("请在 .env 文件中配置 DEEPSEEK_API_KEY")
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def call_deepseek(messages: list, client: OpenAI) -> str:
    if client is None:
        return "[API 未配置]"
    try:
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0.8)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[API 调用失败: {str(e)}]"


def init_session():
    if "verified" not in st.session_state:
        st.session_state.verified = False
    if "show_verification_success" not in st.session_state:
        st.session_state.show_verification_success = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "round" not in st.session_state:
        st.session_state.round = 0
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "started" not in st.session_state:
        st.session_state.started = False
    if "position" not in st.session_state:
        st.session_state.position = ""
    if "resume" not in st.session_state:
        st.session_state.resume = ""
    if "report" not in st.session_state:
        st.session_state.report = None


def build_system_prompt(position: str, resume: str) -> str:
    return f"""你是一位大厂资深面试官，语气略带紧张和挑剔，会针对简历细节追问。
目标岗位：{position}
候选人简历摘要：
---
{resume[:3000]}
---
请用简洁、直接的方式提问，每次只问一个问题。不要过于客气，要像真实面试那样略带压力感。"""


# ============ 验证页面 ============
def render_verification_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<h1 style="text-align: center; font-size: 2.2rem; font-weight: 600; color: #1d1d1f; margin-bottom: 32px;">'
        '🎯咸鱼上岸记 | 唯一授权验证</h1>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        order_id = st.text_input("订单号", placeholder="请输入您的订单号", key="order_id_input", label_visibility="collapsed")
        if st.button("立即激活", use_container_width=True, key="activate_btn"):
            if order_id and str(order_id).strip().upper() == CORRECT_ORDER_ID:
                st.session_state.verified = True
                st.session_state.show_verification_success = True
                st.rerun()
            else:
                st.error("订单号不正确，请核对后重试")

    st.markdown(
        '<p style="text-align: center; color: #86868b; font-size: 0.85rem; margin-top: 24px;">'
        '本工具用于【咸鱼上岸记】领取使用。尚未获取订单号？请前往小红书/咸鱼搜索领取店铺。</p>',
        unsafe_allow_html=True,
    )


# ============ 各页面内容 ============
def render_page_home():
    """个人中心"""
    st.markdown("## 🏠 个人中心")
    st.markdown(
        '<div style="background: #ffffff; border-radius: 12px; padding: 24px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.06); border: 1px solid rgba(0,0,0,0.06);">'
        '<p style="font-size: 1.1rem; margin: 0;"><strong>会员状态</strong></p>'
        '<p style="font-size: 1.5rem; color: #1d1d1f; margin: 12px 0 0 0;">咸鱼上岸特权会员</p>'
        '<p style="color: #86868b; font-size: 0.9rem; margin: 8px 0 0 0;">享有全部功能无限制使用</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("咸鱼上岸记：助你春招一跃上岸 🎯")


def render_page_resume():
    """AI 简历神笔"""
    st.markdown("## 📄 AI 简历神笔")
    st.info("功能开发中，敬请期待。")


def render_page_exam():
    """笔试辅助"""
    st.markdown("## 🖊️ 笔试辅助")
    st.info("功能开发中，敬请期待。")


def render_page_knowledge():
    """知识库"""
    st.markdown("## 📚 知识库")
    st.info("功能开发中，敬请期待。")


def render_page_history():
    """面试历史"""
    st.markdown("## ⏰ 面试历史")
    st.info("功能开发中，敬请期待。")


def render_page_interview(client):
    """模拟面试"""
    st.markdown("## 🎤 模拟面试")
    st.markdown("输入岗位、上传或粘贴简历，开始三轮追问模拟。")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        position = st.text_input("目标岗位", placeholder="例：Java 后端开发工程师 / 产品经理", key="position")
    with col2:
        resume_file = st.file_uploader("上传简历 (可选，支持 .txt)", type=["txt"], key="resume_file")

    resume_paste = st.text_area("粘贴简历内容", placeholder="将简历全文粘贴到此处…", height=180, key="resume_paste")

    resume = resume_paste or ""
    if resume_file:
        resume = resume_file.read().decode("utf-8", errors="ignore") + "\n\n" + resume

    if not st.session_state.started:
        if st.button("开始模拟面试", use_container_width=True):
            if not position or not str(position).strip():
                st.warning("请先输入目标岗位")
            elif not resume.strip():
                st.warning("请上传或粘贴简历内容")
            else:
                st.session_state.started = True
                if position and str(position).strip():
                    st.session_state.position = str(position).strip()
                if resume and str(resume).strip():
                    st.session_state.resume = str(resume).strip()
                st.session_state.round = 0
                st.session_state.conversation = []
                st.rerun()

    if st.session_state.started:
        position = st.session_state.get("position", position)
        resume = st.session_state.get("resume", resume)
        sys_prompt = build_system_prompt(position, resume)

        st.markdown("---")
        st.markdown("### 📋 面试记录")

        for item in st.session_state.conversation:
            if item["role"] == "interviewer":
                st.markdown(f'<div class="interviewer-msg"><strong>面试官</strong><br>{item["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="user-msg"><strong>我</strong><br>{item["content"]}</div>', unsafe_allow_html=True)

        if st.session_state.round < 3:
            round_names = ["第一轮", "第二轮", "第三轮"]
            r = st.session_state.round
            conv = st.session_state.conversation
            need_new_q = (len(conv) % 2 == 0) and (len(conv) // 2 == r)

            if need_new_q:
                msgs = [{"role": "system", "content": sys_prompt}]
                for x in conv:
                    role = "assistant" if x["role"] == "interviewer" else "user"
                    msgs.append({"role": role, "content": x["content"]})
                msgs.append({"role": "user", "content": "请开始第一轮提问。" if r == 0 else "请基于上一轮回答继续追问。"})

                with st.spinner(f"面试官思考中（{round_names[r]}）…"):
                    q = call_deepseek(msgs, client)
                st.session_state.conversation.append({"role": "interviewer", "content": q})
                st.rerun()

            st.markdown(f"**{round_names[r]} - 请输入你的回答：**")
            user_answer = st.text_area("你的回答", key=f"answer_{r}", placeholder="在此输入你的回答…", height=120)
            if st.button("提交并进入下一轮"):
                if not user_answer.strip():
                    st.warning("请先输入回答")
                else:
                    st.session_state.conversation.append({"role": "user", "content": user_answer.strip()})
                    st.session_state.round += 1
                    st.rerun()

        else:
            st.success("✅ 三轮面试已完成")
            if st.session_state.report is None:
                with st.spinner("正在生成复盘报告…"):
                    hist_text = "\n\n".join(
                        f"{'面试官' if x['role']=='interviewer' else '候选人'}: {x['content']}"
                        for x in st.session_state.conversation
                    )
                    report_prompt = f"""基于以下面试对话，生成一份「复盘报告」：
{hist_text}
请按以下结构输出（Markdown 格式）：
## 一、整体表现
简要评价候选人表现。
## 二、亮点
列出回答中的亮点。
## 三、待改进点
列出需要改进的地方。
## 四、答案修改建议
针对每一轮问题，给出更优的回答示例或修改建议（具体、可操作）。"""
                    report = call_deepseek(
                        [
                            {"role": "system", "content": "你是一位资深HR，擅长面试复盘和求职辅导。请用专业、具体的语言输出。"},
                            {"role": "user", "content": report_prompt},
                        ],
                        client,
                    )
                    st.session_state.report = report

            st.markdown("### 📊 复盘报告")
            st.markdown(st.session_state.report or "", unsafe_allow_html=True)

        if st.button("重新开始面试"):
            st.session_state.started = False
            st.session_state.round = 0
            st.session_state.conversation = []
            st.session_state.report = None
            st.rerun()


# ============ 主流程 ============
def main():
    init_session()

    # ============ 订单验证：未验证时只显示验证页面，无侧边栏 ============
    if not st.session_state.verified:
        render_verification_page()
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align: center; color: #86868b; font-size: 0.85rem;">'
            '© 2026 咸鱼上岸记版权所有 | 初学者学习交流</p>',
            unsafe_allow_html=True,
        )
        return

    # ============ 验证通过：显示左侧导航 + 主内容区 ============
    with st.sidebar:
        st.markdown("## 🎯 咸鱼上岸记")
        st.markdown("---")
        st.markdown("**导航**")
        options = [item[0] for item in NAV_ITEMS]
        page_ids = [item[1] for item in NAV_ITEMS]
        idx = page_ids.index(st.session_state.current_page) if st.session_state.current_page in page_ids else 0
        selected = st.radio("", options, index=idx, key="nav_radio", label_visibility="collapsed")
        sel_idx = options.index(selected)
        st.session_state.current_page = page_ids[sel_idx]
        st.markdown("---")
        st.caption("© 2026 咸鱼上岸记")

    # ============ 验证成功反馈 ============
    if st.session_state.show_verification_success:
        st.success("验证成功！祝您春招一跃上岸！")
        st.session_state.show_verification_success = False

    # ============ 根据当前页渲染主内容 ============
    page = st.session_state.current_page

    if page == "home":
        render_page_home()
    elif page == "resume":
        render_page_resume()
    elif page == "interview":
        client = get_deepseek_client()
        if client:
            render_page_interview(client)
        else:
            st.warning("请配置 DeepSeek API Key 后使用模拟面试功能")
    elif page == "exam":
        render_page_exam()
    elif page == "knowledge":
        render_page_knowledge()
    elif page == "history":
        render_page_history()
    else:
        render_page_home()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #86868b; font-size: 0.85rem;">'
        '© 2026 咸鱼上岸记版权所有 | 初学者学习交流</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
