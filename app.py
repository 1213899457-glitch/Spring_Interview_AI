"""
2026春招AI模拟面试官
Streamlit + DeepSeek API | Mac极简风格
"""

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 中的 DEEPSEEK_API_KEY
load_dotenv()

# ============ 页面配置 ============
st.set_page_config(
    page_title="2026春招AI模拟面试官 | 咸鱼上岸记出品",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============ Mac 极简风格 CSS ============
st.markdown("""
<style>
    /* 全局 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
    }
    
    /* 主标题 */
    h1 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        color: #1d1d1f !important;
        font-size: 2rem !important;
    }
    
    /* 卡片容器 */
    .mac-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px 28px;
        margin: 16px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.06);
    }
    
    /* 面试官消息 */
    .interviewer-msg {
        background: #1d1d1f;
        color: #f5f5f7;
        padding: 16px 20px;
        border-radius: 12px 12px 12px 4px;
        margin: 12px 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* 用户回答 */
    .user-msg {
        background: #e8e8ed;
        color: #1d1d1f;
        padding: 16px 20px;
        border-radius: 12px 12px 4px 12px;
        margin: 12px 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* 按钮 */
    .stButton > button {
        background: #1d1d1f !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: opacity 0.2s !important;
    }
    
    .stButton > button:hover {
        opacity: 0.85 !important;
    }
    
    /* 输入框 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid #d2d2d7 !important;
    }
    
    /* 隐藏 Streamlit 默认边栏装饰 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def get_deepseek_client():
    """从 .env 读取 API Key 并返回 DeepSeek 客户端"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key.strip() == "":
        st.error("请在 .env 文件中配置 DEEPSEEK_API_KEY")
        st.stop()
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def call_deepseek(messages: list, client: OpenAI) -> str:
    """调用 DeepSeek API"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.8,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[API 调用失败: {str(e)}]"


def init_session():
    if "round" not in st.session_state:
        st.session_state.round = 0
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "started" not in st.session_state:
        st.session_state.started = False


def build_system_prompt(position: str, resume: str) -> str:
    return f"""你是一位大厂资深面试官，语气略带紧张和挑剔，会针对简历细节追问。
目标岗位：{position}

候选人简历摘要：
---
{resume[:3000]}
---

请用简洁、直接的方式提问，每次只问一个问题。
不要过于客气，要像真实面试那样略带压力感。"""


def main():
    init_session()
    client = get_deepseek_client()

    # ============ 顶部标题与品牌 ============
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 🎯 2026春招AI模拟面试官 | 咸鱼上岸记出品")
    st.markdown(
        '<div style="background: linear-gradient(135deg, #1d1d1f 0%, #424245 100%); color: #f5f5f7; padding: 12px 20px; border-radius: 8px; margin: 12px 0 20px 0; font-size: 1.05rem; font-weight: 500;">'
        '咸鱼上岸记：助你春招一跃上岸</div>',
        unsafe_allow_html=True,
    )
    st.markdown("输入岗位、上传或粘贴简历，开始三轮追问模拟。")
    st.markdown("<br>", unsafe_allow_html=True)

    # ============ 输入区 ============
    col1, col2 = st.columns([1, 1])
    with col1:
        position = st.text_input(
            "目标岗位",
            placeholder="例：Java 后端开发工程师 / 产品经理",
            key="position",
        )
    with col2:
        resume_file = st.file_uploader(
            "上传简历 (可选，支持 .txt)",
            type=["txt"],
            key="resume_file",
        )

    resume_paste = st.text_area(
        "粘贴简历内容",
        placeholder="将简历全文粘贴到此处…",
        height=180,
        key="resume_paste",
    )

    # 合并简历来源
    resume = resume_paste or ""
    if resume_file:
        resume = resume_file.read().decode("utf-8", errors="ignore") + "\n\n" + resume

    # ============ 开始面试 ============
    if not st.session_state.started:
        if st.button("开始模拟面试", use_container_width=True):
            if not position:
                st.warning("请先输入目标岗位")
            elif not resume.strip():
                st.warning("请上传或粘贴简历内容")
            else:
                st.session_state.started = True
                st.session_state.position = position
                st.session_state.resume = resume
                st.session_state.round = 0
                st.session_state.conversation = []
                st.rerun()

    # ============ 面试进行中 ============
    if st.session_state.started:
        position = st.session_state.get("position", position)
        resume = st.session_state.get("resume", resume)
        sys_prompt = build_system_prompt(position, resume)

        st.markdown("---")
        st.markdown("### 📋 面试记录")

        # 显示已有对话
        for item in st.session_state.conversation:
            if item["role"] == "interviewer":
                st.markdown(
                    f'<div class="interviewer-msg">'
                    f'<strong>面试官</strong><br>{item["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="user-msg">'
                    f'<strong>我</strong><br>{item["content"]}</div>',
                    unsafe_allow_html=True,
                )

        # 三轮面试
        if st.session_state.round < 3:
            round_names = ["第一轮", "第二轮", "第三轮"]
            r = st.session_state.round
            conv = st.session_state.conversation
            need_new_q = (len(conv) % 2 == 0) and (len(conv) // 2 == r)

            if need_new_q:
                # 构建消息历史
                msgs = [{"role": "system", "content": sys_prompt}]
                for x in conv:
                    role = "assistant" if x["role"] == "interviewer" else "user"
                    msgs.append({"role": role, "content": x["content"]})
                msgs.append(
                    {"role": "user", "content": "请开始第一轮提问。" if r == 0 else "请基于上一轮回答继续追问。"}
                )

                with st.spinner(f"面试官思考中（{round_names[r]}）…"):
                    q = call_deepseek(msgs, client)
                st.session_state.conversation.append({"role": "interviewer", "content": q})
                st.rerun()

            # 用户回答输入
            st.markdown(f"**{round_names[r]} - 请输入你的回答：**")
            user_answer = st.text_area(
                "你的回答",
                key=f"answer_{r}",
                placeholder="在此输入你的回答…",
                height=120,
            )
            if st.button("提交并进入下一轮"):
                if not user_answer.strip():
                    st.warning("请先输入回答")
                else:
                    st.session_state.conversation.append(
                        {"role": "user", "content": user_answer.strip()}
                    )
                    st.session_state.round += 1
                    st.rerun()

        else:
            # 三轮结束，生成复盘报告
            st.success("✅ 三轮面试已完成")
            if "report" not in st.session_state:
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
            st.markdown(st.session_state.report, unsafe_allow_html=True)

        if st.button("重新开始"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.rerun()


if __name__ == "__main__":
    main()
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #86868b; font-size: 0.85rem;">'
        '© 2026 咸鱼上岸记版权所有 | 初学者学习交流</p>',
        unsafe_allow_html=True,
    )

