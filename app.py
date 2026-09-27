"""CrossBorder AI public portfolio demo. No external API or business data."""

import streamlit as st

from profit_calculator import ProfitInput, calculate
from workflow_demo import ProjectInput, STEPS, new_run, run_next


st.set_page_config(page_title="CrossBorder AI Showcase", page_icon="🌍", layout="wide")
st.title("CrossBorder AI · 跨境项目工作台")
st.caption("公开展示版 · Mock 工作流 · 无需 API Key · 不包含商业数据")

overview, workflow, profit = st.tabs(["项目概览", "AI 工作流", "利润测算"])

with overview:
    st.subheader("把零散 AI 功能组织成可恢复、可审计的业务工作流")
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            - 项目级数据隔离与生命周期管理
            - 八步 AI 工作流与输入快照
            - 失败检查点、断点续跑与防重复执行
            - OpenAI-compatible 模型服务抽象
            """
        )
    with right:
        st.markdown(
            """
            - 利润等关键指标由本地 Python 计算
            - Streamlit 多页面交互与后台任务状态
            - 结构化日志、调用指标和回归测试
            - 公开版仅展示架构和代表性实现
            """
        )
    st.info("完整工程版本保存在私有仓库；此仓库用于招聘作品展示。")

with workflow:
    st.subheader("可追踪的分步工作流")
    c1, c2 = st.columns(2)
    name = c1.text_input("项目名称", "便携咖啡研磨机 US")
    product = c2.text_input("产品", "便携咖啡研磨机")
    c3, c4, c5 = st.columns(3)
    platform = c3.selectbox("平台", ["Amazon", "TikTok Shop", "Independent Site"])
    marketplace = c4.selectbox("站点", ["US", "UK", "DE", "AE"])
    price = c5.number_input("售价（USD）", min_value=0.01, value=29.99, step=1.0)

    if st.button("新建演示运行", type="primary"):
        st.session_state.demo_run = new_run(
            ProjectInput(name, product, platform, marketplace, price)
        )
    state = st.session_state.get("demo_run")
    if state:
        st.progress(state["progress"] / 100, text=f"进度 {state['progress']}%")
        a, b = st.columns(2)
        if a.button("执行下一步", disabled=state["status"] == "completed"):
            st.session_state.demo_run = run_next(state)
            st.rerun()
        if b.button("执行全部", disabled=state["status"] == "completed"):
            while state["status"] != "completed":
                state = run_next(state)
            st.session_state.demo_run = state
            st.rerun()

        labels = dict(STEPS)
        for key in state["completed_steps"]:
            with st.expander(f"✅ {labels[key]}", expanded=key == state["completed_steps"][-1]):
                st.write(state["outputs"][key])
        with st.expander("运行事件（Audit Events）"):
            st.json(state["events"])
    else:
        st.caption("创建后可逐步执行，观察进度、结构化输出与审计事件。")

with profit:
    st.subheader("确定性利润计算")
    st.caption("LLM 负责生成建议，金额计算坚持使用可测试的 Python 公式。")
    cols = st.columns(4)
    p = cols[0].number_input("售价", min_value=0.01, value=29.99)
    cost = cols[1].number_input("采购成本", min_value=0.0, value=8.0)
    shipping = cols[2].number_input("头程物流", min_value=0.0, value=2.5)
    fulfillment = cols[3].number_input("履约费用", min_value=0.0, value=3.5)
    cols2 = st.columns(3)
    commission = cols2[0].number_input("佣金率（%）", min_value=0.0, max_value=100.0, value=15.0)
    ad_cost = cols2[1].number_input("单件广告成本", min_value=0.0, value=0.0)
    other = cols2[2].number_input("其他费用", min_value=0.0, value=0.0)
    result = calculate(ProfitInput(p, cost, shipping, commission, fulfillment, ad_cost, other))
    m1, m2, m3 = st.columns(3)
    m1.metric("单件利润", f"${result.profit:.2f}")
    m2.metric("利润率", f"{result.profit_margin:.1f}%")
    m3.metric("盈亏平衡 ACOS", f"{result.break_even_acos:.1f}%")
    for warning in result.warnings:
        st.warning(warning)

