"""
2026春招AI面试助手 | 咸鱼上岸记 SaaS 旗舰版
集成：手机号体系、管理员后台、隐私协议、次数限制、深色模式
"""

import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ==============================================
# 1. 商业级页面配置与 CSS
# ==============================================
st.set_page_config(
    page_title="咸鱼上岸记 | 春招AI面试教练",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 全局背景与字体 */
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    
    /* 侧边栏 SaaS 风格 */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #cbd5e1 !important; }
    
    /* 苹果系圆角卡片 */
    .saas-card {
        background: #1e293b;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    
    /* 亮绿色按钮 - 引导付费色 */
    .stButton > button {
        background: #10b981 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100%;
    }
    
    /* 协议文本 */
    .protocol-box {
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.6;
        padding: 15px;
        background: #0f172a;
        border-radius: 8px;
    }
    
    /* 会员状态标签 */
    .status-vip { color: #10b981; font-weight: bold; }
    .status-free { color: #f59e0b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================
# 2. 核心逻辑初始化
# ==============================================
def init_session():
    # 模拟云端数据库 (手机号: {余额, 是否VIP, 到期时间, 今日使用次数})
    if "user_db" not in st.session_state:
        st.session_state.user_db = {}
    if "logged_user" not in st.session_state:
        st.session_state.logged_user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

def get_ai_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# ==============================================
# 3. 业务逻辑函数 (付费转化核心)
# ==============================================
MAX_FREE_TRIES = 3

def check_permission(phone):
    user = st.session_state.user_db.get(phone)
    if not user: return False
    # 如果是 VIP 且未过期
    if user['is_vip']:
        return True
    # 否则检查免费次数
    return user['used_today'] < MAX_FREE_TRIES

# ==============================================
# 4. 流程模块：登录 / 首页 / 协议
# ==============================================

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>🎯 咸鱼上岸记</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#94a3b8;'>专业的 AI 面试提分系统 · 助你春招逆袭</p>", unsafe_allow_html=True)
        
        phone = st.text_input("手机号注册/登录", placeholder="请输入11位手机号", max_chars=11)
        if st.button("进入系统", type="primary"):
            if len(phone) == 11 and phone.isdigit():
                if phone not in st.session_state.user_db:
                    st.session_state.user_db[phone] = {
                        "is_vip": False, "used_today": 0, "mid": f"XY{phone[-4:]}"
                    }
                st.session_state.logged_user = phone
                st.rerun()
            else:
                st.error("请输入有效的手机号")
        
        st.markdown("""
        <div class='protocol-box'>
            登录即代表您同意《用户协议》与《隐私政策》。我们承诺严格保护您的简历隐私，数据仅用于实时 AI 模型生成。
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    phone = st.session_state.logged_user
    user = st.session_state.user_db[phone]
    with st.sidebar:
        st.markdown(f"### 👤 {phone[:3]}****{phone[-4:]}")
        status = "<span class='status-vip'>VIP 会员</span>" if user['is_vip'] else "<span class='status-free'>免费试用</span>"
        st.markdown(f"状态：{status}", unsafe_allow_html=True)
        st.markdown(f"会员编号：`{user['mid']}`")
        st.markdown("---")
        
        # 顶部导航
        nav_items = ["🏠 首页中心", "📄 AI 简历神笔", "🎤 模拟面试", "📚 智能知识库", "📜 用户协议"]
        page_keys = ["home", "resume", "interview", "knowledge", "agreement"]
        sel = st.radio("导航菜单", nav_items, label_visibility="collapsed")
        st.session_state.current_page = page_keys[nav_options.index(sel)] if 'nav_options' in locals() else page_keys[nav_items.index(sel)]
        
        st.markdown("---")
        if not user['is_vip']:
            st.warning(f"今日免费额度：{MAX_FREE_TRIES - user['used_today']}/{MAX_FREE_TRIES}")
            st.markdown("### 💎 开通全能 VIP")
            st.markdown("1. 加微信：`maoxf03`")
            st.markdown("2. 发送会员编号开通")
        
        if st.button("退出登录"):
            st.session_state.logged_user = None
            st.rerun()

def render_admin():
    """秘密管理员后台：由你手动操作"""
    with st.expander("🛠️ 内部管理后台 (学生不可见)"):
        pwd = st.text_input("管理员密码", type="password")
        if pwd == "shangan2026": # 你可以修改这个密码
            target_phone = st.text_input("待开通手机号")
            if st.button("手动开通 VIP 权限"):
                if target_phone in st.session_state.user_db:
                    st.session_state.user_db[target_phone]['is_vip'] = True
                    st.success(f"已成功开通 {target_phone} 的永久权限！")
                else:
                    st.error("该用户尚未注册登录")

# ==============================================
# 5. 主程序调度
# ==============================================
def main():
    init_session()
    
    if not st.session_state.logged_user:
        render_login()
    else:
        render_sidebar()
        user_phone = st.session_state.logged_user
        user = st.session_state.user_db[user_phone]
        
        page = st.session_state.current_page
        
        if page == "home":
            st.markdown("## 🏠 会员中心")
            st.markdown(f"""
            <div class='saas-card'>
                <h3>欢迎回来，主理人！</h3>
                <p>当前可用功能：模拟面试、简历优化、全库面经。</p>
            </div>
            """, unsafe_allow_html=True)
            render_admin() # 管理员入口放在首页底部

        elif page == "interview":
            st.markdown("## 🎤 AI 模拟面试")
            if not check_permission(user_phone):
                st.error("❌ 免费次数已用完，请联系主理人开通 VIP")
            else:
                st.info("面试官已就绪...")
                if st.button("开始对话（消耗额度）"):
                    user['used_today'] += 1
                    st.write("面试官：请介绍一下你自己。")

        elif page == "agreement":
            st.markdown("## 📜 用户协议与隐私政策")
            st.markdown("""
            <div class='saas-card'>
                <h4>1. 隐私安全</h4>
                <p>我们采用内存级存储，您的简历文件不会在服务器长期保存，仅用于 AI 模型分析。</p>
                <h4>2. 会员权利</h4>
                <p>付费后享有无限次面试、简历深度修改及专属大厂知识库权限。</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
