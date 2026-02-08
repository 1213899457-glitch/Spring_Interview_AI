"""
2026春招AI面试助手 | 咸鱼上岸记 闲鱼/发卡联动版
流程：闲鱼下单 -> 自动发激活码 -> 网页输入激活码 -> 自动绑定手机号解锁
"""

import streamlit as st
import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============ 1. 样式与 UI 配置 ============
st.set_page_config(page_title="咸鱼上岸记 | AI教练", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    [data-testid="stSidebar"] { background-color: #1e293b !important; }
    .saas-card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px; }
    .stButton > button { background: #10b981 !important; color: white !important; font-weight: 600 !important; border-radius: 10px !important; }
    .status-vip { color: #10b981; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ============ 2. 核心激活码验证逻辑 ============
# 实际运营时，您可以预先生成一堆随机码存放在这里或数据库中
VALID_KEYS = {
    "SHANGAN777": 7,    # 周卡
    "SHANGAN30": 30,    # 月卡
    "FOREVER99": 9999   # 终身
}

def init_session():
    if "user_db" not in st.session_state:
        st.session_state.user_db = {} # {手机号: {is_vip, expire_date}}
    if "logged_user" not in st.session_state:
        st.session_state.logged_user = None

# ============ 3. 登录与充值页面 ============
def render_login():
    st.markdown("<br><h1 style='text-align:center;'>🎯 咸鱼上岸记</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        phone = st.text_input("手机号登录", placeholder="输入11位手机号", max_chars=11)
        if st.button("进入系统", type="primary"):
            if len(phone) == 11:
                if phone not in st.session_state.user_db:
                    st.session_state.user_db[phone] = {"is_vip": False, "expire": None}
                st.session_state.logged_user = phone
                st.rerun()

def render_recharge():
    st.markdown("## 💳 会员激活")
    st.info("💡 请在闲鱼搜索‘咸鱼上岸记’购买激活码，系统会自动发货。")
    
    # 引导按钮（可以替换成你的闲鱼店铺二维码链接）
    st.markdown("[点击前往闲鱼店铺购买激活码](https://m.goofish.com/your_shop_link)")
    
    st.markdown("---")
    key_input = st.text_input("请输入您收到的激活码", placeholder="例如：SHANGAN777")
    if st.button("立即激活"):
        if key_input in VALID_KEYS:
            user = st.session_state.user_db[st.session_state.logged_user]
            days = VALID_KEYS[key_input]
            user['is_vip'] = True
            # 计算到期时间
            user['expire'] = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            st.success(f"🎉 激活成功！会员有效期至：{user['expire']}")
            # 激活后可以考虑从 VALID_KEYS 中删除该码（需配合数据库实现一码一用）
            st.rerun()
        else:
            st.error("激活码错误或已被使用")

# ============ 4. 主流程逻辑 ============
def main():
    init_session()
    if not st.session_state.logged_user:
        render_login()
    else:
        phone = st.session_state.logged_user
        user = st.session_state.user_db[phone]
        
        with st.sidebar:
            st.markdown(f"### 👤 {phone[:3]}****{phone[-4:]}")
            status = f"<span class='status-vip'>💎 VIP (至{user['expire']})</span>" if user['is_vip'] else "🆓 试用用户"
            st.markdown(f"状态：{status}", unsafe_allow_html=True)
            st.markdown("---")
            nav = st.radio("导航", ["🏠 会员中心", "🎤 模拟面试", "💳 激活会员"])
            if st.button("退出登录"):
                st.session_state.logged_user = None
                st.rerun()

        if nav == "🏠 会员中心":
            st.markdown("## 🏠 个人中心")
            st.markdown(f"<div class='saas-card'><h4>绑定手机：{phone}</h4><p>账号资产已锁定</p></div>", unsafe_allow_html=True)
        elif nav == "💳 激活会员":
            render_recharge()
        elif nav == "🎤 模拟面试":
            if not user['is_vip']:
                st.warning("请先激活会员解锁全功能")
                render_recharge()
            else:
                st.write("面试官已就绪...")

if __name__ == "__main__":
    main()
