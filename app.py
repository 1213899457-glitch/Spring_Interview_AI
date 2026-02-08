import streamlit as st
import openai
import random
from datetime import datetime, timedelta

# ==============================================
# 页面配置（正式、高级、商用级）
# ==============================================
st.set_page_config(
    page_title="春招AI面试助手",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==============================================
# 全局商用样式（浅色+深色自适应、高级感）
# ==============================================
st.markdown("""
<style>
/* 基础布局 */
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 800px; }
.stApp { background-color: #fafbfc; }
html[data-theme="dark"] .stApp { background-color: #1c1c1e; }

/* 标题样式 */
.main-title {
    text-align: center;
    font-size: 26px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 6px;
}
html[data-theme="dark"] .main-title { color: #f3f4f6; }

.sub-title {
    text-align: center;
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 24px;
}
html[data-theme="dark"] .sub-title { color: #9ca3af; }

/* 按钮 */
button[kind="primary"] {
    background-color: #4f46e5;
    border-color: #4f46e5;
    border-radius: 10px;
    padding: 0.6rem 0;
}
button[kind="primary"]:hover {
    background-color: #4338ca;
    border-color: #4338ca;
}

/* 顶部导航 */
.nav-bar {
    display: flex;
    justify-content: center;
    gap: 22px;
    margin-bottom: 20px;
    font-size: 15px;
    color: #4f46e5;
    font-weight: 500;
}
.nav-item { cursor: pointer; padding: 4px 0; }
.nav-item:hover { border-bottom: 2px solid #4f46e5; }

/* 会员横幅 */
.vip-banner {
    background: linear-gradient(90deg, #4f46e5, #6366f1);
    color: #fff;
    padding: 20px 16px;
    border-radius: 14px;
    text-align: center;
    margin-top: 24px;
}
.free-limit {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 10px 0;
}
html[data-theme="dark"] .free-limit {
    background: #2a241b;
    border-left-color: #d97706;
}

/* 协议卡片 */
.protocol-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-top: 12px;
}
html[data-theme="dark"] .protocol-card {
    background: #27272a;
    border-color: #3f3f46;
}
</style>
""", unsafe_allow_html=True)

# ==============================================
# API KEY（必须在 Secrets 配置）
# ==============================================
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ 系统异常，请联系管理员：maoxf03")
    st.stop()

# ==============================================
# 全局状态
# ==============================================
if "user" not in st.session_state:
    st.session_state.user = None
if "verify_code" not in st.session_state:
    st.session_state.verify_code = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# 用户数据库（内存版，正式可替换MySQL/Redis）
if "user_db" not in st.session_state:
    st.session_state.user_db = {}

MAX_FREE_USE = 3

# ==============================================
# 工具函数
# ==============================================
def is_vip(phone):
    u = st.session_state.user_db.get(phone)
    if not u or not u.get("vip"):
        return False
    try:
        exp = datetime.strptime(u["expire"], "%Y-%m-%d")
        return exp >= datetime.now()
    except:
        return False

def reset_day(phone):
    today = datetime.now().strftime("%Y-%m-%d")
    u = st.session_state.user_db[phone]
    if u.get("date") != today:
        u["today_count"] = 0
        u["date"] = today

def can_use(phone):
    if phone not in st.session_state.user_db:
        st.session_state.user_db[phone] = {
            "vip": False, "expire": "", "today_count": 0,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    reset_day(phone)
    return st.session_state.user_db[phone]["today_count"] < MAX_FREE_USE

def add_count(phone):
    reset_day(phone)
    st.session_state.user_db[phone]["today_count"] += 1

# ==============================================
# 页面路由（顶部导航）
# ==============================================
def nav():
    st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
    if st.button("首页", key="nav_home", use_container_width=False):
        st.session_state.page = "home"
    if st.button("用户协议", key="nav_agreement", use_container_width=False):
        st.session_state.page = "agreement"
    if st.button("隐私政策", key="nav_privacy", use_container_width=False):
        st.session_state.page = "privacy"
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================
# 协议页面
# ==============================================
def page_agreement():
    st.markdown('<div class="main-title">用户协议</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">User Agreement</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="protocol-card">
1. 本工具仅用于春招学习、面试辅助，不构成就业指导、培训承诺。<br>
2. 用户不得利用本站进行违法、违规、侵权、批量爬虫等行为。<br>
3. 免费用户有每日次数限制，会员服务为虚拟商品，开通后不支持退款。<br>
4. 平台有权对恶意使用、异常调用、违规账号进行限制。<br>
5. 最终解释权归平台运营方所有，保留随时调整条款、功能、价格的权利。
</div>
""", unsafe_allow_html=True)

def page_privacy():
    st.markdown('<div class="main-title">隐私政策</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Privacy Policy</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="protocol-card">
1. 平台仅收集用户手机号、使用记录，用于身份识别与服务提供。<br>
2. 简历、问答等内容仅实时用于AI生成，不用于商业用途，不随意泄露。<br>
3. 不会向第三方共享、出售、交换用户个人信息。<br>
4. 采用内存临时存储，敏感信息不长期保存。<br>
5. 用户可随时停止使用，停止使用后相关临时信息不再收集与使用。
</div>
""", unsafe_allow_html=True)

# ==============================================
# 登录页面
# ==============================================
def page_login():
    st.markdown('<div class="main-title">🎓 春招AI面试助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">面试模拟｜简历优化｜高频题库｜助力通关拿Offer</div>', unsafe_allow_html=True)
    st.subheader("账号登录")
    phone = st.text_input("手机号", placeholder="请输入11位手机号", max_chars=11)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("获取验证码", use_container_width=True):
            if len(phone) != 11:
                st.warning("请输入正确手机号")
            else:
                code = random.randint(1000, 9999)
                st.session_state.verify_code = str(code)
                st.success(f"验证码：{code}（演示模式）")
    with col2:
        code_in = st.text_input("验证码", type="password")
        if st.button("登录", type="primary", use_container_width=True):
            if st.session_state.verify_code and code_in == st.session_state.verify_code:
                st.session_state.user = phone
                if phone not in st.session_state.user_db:
                    st.session_state.user_db[phone] = {
                        "vip": False, "expire": "", "today_count": 0,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                st.rerun()
            else:
                st.error("验证码错误")
    st.caption("登录即代表同意 用户协议 与 隐私政策")

# ==============================================
# 管理员后台（手动开通会员）
# ==============================================
def admin_panel():
    with st.expander("⚙️ 管理员开通会员"):
        pwd = st.text_input("管理员密码", type="password")
        if pwd == st.secrets.get("ADMIN_PASSWORD", "admin123"):
            target = st.text_input("用户手机号")
            typ = st.radio("套餐", ["月卡19.9", "季卡49.9", "终身99"], horizontal=True)
            if st.button("确认开通"):
                if target not in st.session_state.user_db:
                    st.session_state.user_db[target] = {
                        "vip": True, "expire": "", "today_count": 0, "date": ""
                    }
                u = st.session_state.user_db[target]
                now = datetime.now()
                if typ == "月卡19.9":
                    exp = now + timedelta(days=30)
                elif typ == "季卡49.9":
                    exp = now + timedelta(days=90)
                else:
                    exp = datetime(2099, 12, 31)
                u["vip"] = True
                u["expire"] = exp.strftime("%Y-%m-%d")
                st.success(f"✅ 已开通：{typ}，到期：{u['expire']}")

# ==============================================
# 主功能页面
# ==============================================
def page_home():
    user_phone = st.session_state.user
    user_vip = is_vip(user_phone)
    can = can_use(user_phone)
    used = st.session_state.user_db[user_phone]["today_count"]

    st.markdown('<div class="main-title">春招AI面试助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">专业AI面试辅助工具 · 应届生专用</div>', unsafe_allow_html=True)

    # 账号与会员信息
    st.markdown(f"👤 账号：`{user_phone}`")
    if user_vip:
        st.success("✅ 会员已激活，可使用全部功能")
    else:
        st.info(f"🆓 免费版（今日已使用：{used}/{MAX_FREE_USE} 次）")

    # 功能Tab
    tab1, tab2, tab3 = st.tabs(["📝 岗位面经生成", "✍️ 简历智能优化", "💬 AI面试问答"])

    # ========== 1. 面经生成 ==========
    with tab1:
        st.subheader("岗位面经生成")
        c1, c2 = st.columns(2)
        with c1:
            industry = st.selectbox("行业", ["互联网", "金融", "快消", "国企/央企", "制造业", "教育", "医疗"])
        with c2:
            job = st.selectbox("岗位", ["产品经理", "运营", "市场", "人力", "财务", "开发", "测试", "数据分析", "管培生"])
        ctype = st.radio("企业类型", ["通用版", "大厂", "国企/央企"], horizontal=True)
        if st.button("🚀 生成面经", type="primary", use_container_width=True):
            if not user_vip and not can:
                st.markdown('<div class="free-limit">今日免费次数已用完，开通会员解锁无限使用</div>', unsafe_allow_html=True)
                st.stop()
            if not user_vip and ctype != "通用版":
                st.info("🔒 仅会员可查看大厂/国企专属面经，添加微信 maoxf03 开通")
                st.stop()
            with st.spinner("正在生成..."):
                prompt = f"""
你是专业春招面试导师，为应届生生成可直接背诵的面经。
行业：{industry}
岗位：{job}
企业类型：{ctype}

结构：
1. 1分钟自我介绍模板
2. 专业高频题（8题）
3. 行为面试题（4题）
4. 反问面试官问题（3题）

每题包含：答题思路 + 参考回答（1分钟内）。
""".strip()
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    ).choices[0].message.content.strip()
                    st.markdown("---")
                    st.markdown(res)
                    if not user_vip:
                        add_count(user_phone)
                except Exception as e:
                    st.error(f"错误：{str(e)}")

    # ========== 2. 简历优化 ==========
    with tab2:
        st.subheader("简历智能优化")
        resume = st.text_area("粘贴简历内容", height=240)
        target_job = st.selectbox("目标岗位", ["产品经理", "运营", "市场", "人力", "财务", "开发", "数据分析", "管培生"])
        if st.button("🔍 优化简历", type="primary", use_container_width=True):
            if not resume:
                st.warning("请输入简历")
                st.stop()
            if not user_vip and not can:
                st.markdown('<div class="free-limit">今日免费次数已用完</div>', unsafe_allow_html=True)
                st.stop()
            with st.spinner("优化中..."):
                prompt = f"""你是资深简历优化师，{'完整优化整篇简历' if user_vip else '仅优化实习/项目经历'}，贴合{target_job}岗位，突出成果与关键词。简历：{resume}"""
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.6
                    ).choices[0].message.content.strip()
                    st.markdown("---")
                    st.success("✅ 优化完成")
                    st.markdown(res)
                    if not user_vip:
                        add_count(user_phone)
                        st.info("🔒 免费版仅部分优化，会员解锁全简历深度优化")
                except Exception as e:
                    st.error(f"错误：{str(e)}")

    # ========== 3. 面试问答 ==========
    with tab3:
        st.subheader("AI面试问答")
        q = st.text_input("输入面试问题")
        if st.button("💡 获取回答思路", use_container_width=True):
            if not q:
                st.warning("请输入问题")
                st.stop()
            if not user_vip and not can:
                st.markdown('<div class="free-limit">今日免费次数已用完</div>', unsafe_allow_html=True)
                st.stop()
            with st.spinner("生成中..."):
                prompt = f"""你是春招面试导师，输出三点：1.答题框架 2.参考回答（1分钟）3.避坑提醒。问题：{q}"""
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    ).choices[0].message.content.strip()
                    st.markdown("---")
                    st.markdown(res)
                    if not user_vip:
                        add_count(user_phone)
                except Exception as e:
                    st.error(f"错误：{str(e)}")

    # ========== 底部会员转化 ==========
    st.markdown("---")
    if not user_vip:
        st.markdown(f"""
<div class="vip-banner">
    <div style="font-size:16px;font-weight:600;">解锁全部功能 · 春招快人一步</div>
    <div style="margin:8px 0; font-size:15px;">月卡19.9 ｜ 季卡49.9 ｜ 终身99 元</div>
    <div style="font-size:16px; font-weight:600; margin-top:4px;">微信：<code>maoxf03</code>（备注：春招会员）</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.success("🎉 已解锁全部会员功能，祝你春招顺利拿Offer！")

    admin_panel()

# ==============================================
# 页面路由调度
# ==============================================
nav()
if not st.session_state.user:
    page_login()
else:
    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "agreement":
        page_agreement()
    elif st.session_state.page == "privacy":
        page_privacy()

# 底部版权
st.markdown("""
<div style="text-align:center; font-size:12px; color:#9ca3af; margin-top:32px;">
© 2026 春招AI面试助手 | 仅限学习使用 | 客服微信：maoxf03
</div>
""", unsafe_allow_html=True)
