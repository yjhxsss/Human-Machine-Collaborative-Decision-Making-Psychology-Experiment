import streamlit as st
import requests
import time
import random
import pandas as pd

# ========== 10 个风险情景 ==========
SCENARIOS = [
    {
        "desc": (
            "你继承了一笔 50,000 元的遗产。理财顾问推荐将这笔钱投入一只高风险的科技基金，"
            "历史数据显示有 65% 的概率在 5 年内翻倍，但有 35% 的概率损失 40% 的本金。"
            "你也可以选择将其存入年利率 3% 的定期存款，保证安全但收益较低。"
        ),
        "A": "投资科技基金（高风险）",
        "B": "存入定期存款（保守）"
    },
    {
        "desc": (
            "你是一家初创公司的联合创始人，公司目前估值 200 万元。一家大公司提出以 150 万元收购你们的全部股权，"
            "立即变现离场。但如果你继续经营，有 50% 的概率在两年内估值达到 500 万元，50% 的概率因竞争倒闭只值 30 万元。"
        ),
        "A": "拒绝收购，继续经营（冒险）",
        "B": "接受收购，安全退出（保守）"
    },
    {
        "desc": (
            "你的医生发现你体内有一个良性肿瘤，目前不影响健康，但有 5% 的概率在未来 10 年转为恶性。"
            "医生建议可以进行一次手术切除，手术成功率 98%，但有 2% 的风险导致轻微后遗症。"
            "你也可以选择暂不手术，每年定期复查监控。"
        ),
        "A": "立即手术切除（冒险干预）",
        "B": "暂不手术，定期复查（保守监控）"
    },
    {
        "desc": (
            "你是一名大四学生，已经获得一家稳定国企的录用函，月薪 8,000 元，福利完善。"
            "同时，你也有机会加入一家处于 A 轮的 AI 创业公司，月薪 12,000 元并许诺期权，"
            "但公司未来两年存活率只有 60%，如果倒闭你将面临重新求职的压力。"
        ),
        "A": "选择创业公司（高回报高风险）",
        "B": "选择稳定国企（低风险稳收益）"
    },
    {
        "desc": (
            "你的好友向你借 20,000 元，承诺一年后归还 22,000 元。你知道他为人诚实，"
            "但近期他所在行业不景气，有 30% 的可能他会因失业而无法按时还款。"
            "如果你不借，这笔钱可以放在理财产品中获取 4% 的无风险收益。"
        ),
        "A": "借出 20,000 元（信任高风险）",
        "B": "婉拒并自行理财（保护本金）"
    },
    {
        "desc": (
            "你准备参加一场专业资格证考试，目前水平通过率约 70%。如果你请假两周全职备考，"
            "通过率可提高到 95%，但会扣掉当月绩效奖金 2,000 元。如果不请假，正常边工作边复习，"
            "有一成多的失败风险需要明年重考，重考费时费力。"
        ),
        "A": "请假两周备考（冒险投入金钱换确定性）",
        "B": "正常边工边考（节省金钱，接受风险）"
    },
    {
        "desc": (
            "你在一个陌生城市旅游，预订了当晚的航班回家。距离起飞还有 5 小时，你犹豫是否去一个距离机场 60 公里的网红景点。"
            "公共交通来回需要 3 小时，但可能遇到堵车延误。如果误机，需要多花 1,500 元改签并滞留一晚。"
            "如果顺利，你将收获难得的美景和体验。"
        ),
        "A": "前往景点（冒险赶飞机）",
        "B": "留在机场附近休息（保守保证航班）"
    },
    {
        "desc": (
            "你发现了一个法律灰色地带的投资机会：通过复杂的交易结构可以绕过资本管制将资金转至海外高息账户，"
            "年化收益可达 12%，但存在被监管部门调查的风险。完全合规的国内投资年化收益仅为 3.5%。"
            "一旦被查处，可能面临罚款 20% 本金及声誉损失。行业经验表明被查概率约 10%。"
        ),
        "A": "尝试灰色投资（高收益违法风险）",
        "B": "选择合规投资（安全合法）"
    },
    {
        "desc": (
            "你暗恋一位同学已半年，两人平时关系友好但无明显暧昧。你有冲动想在情人节送一份精心准备的礼物表白心意。"
            "如果对方接受，你们可能开启一段恋情；但如果被拒，双方关系可能变得尴尬，甚至疏远。"
            "你也可以选择维持现状，继续做朋友，但可能错过最佳时机。"
        ),
        "A": "送礼物表白（冒险争取关系改变）",
        "B": "保持现状（保守维持友谊）"
    },
    {
        "desc": (
            "你是一名导演，手头有两个剧本可选。剧本A是商业喜剧片，成本 3,000 万，预计票房 1 亿的概率 80%，"
            "有 20% 概率遭遇口碑崩盘仅收 2,000 万。剧本B是现实主义文艺片，成本 1,500 万，50% 概率获得大奖并收获 2 亿票房，"
            "50% 概率无人问津仅收 500 万。你的声誉和公司资金周转都与此片捆绑。"
        ),
        "A": "选择文艺片（高风险高荣誉）",
        "B": "选择商业喜剧（稳扎稳打）"
    }
]

# ---------- 调用 DeepSeek API ----------
def call_deepseek(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个冷静的AI决策助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"[API错误 {r.status_code}]"

# ---------- 主界面 ----------
def main():
    st.set_page_config(page_title="AI决策实验", layout="centered")
    st.title("🧠 AI 建议对风险决策的影响")

    # 初始化会话状态
    if 'stage' not in st.session_state:
        st.session_state.stage = 'id_input'   # id_input, block_instr, trial, done
        st.session_state.data = []
        st.session_state.scenarios = []
        st.session_state.block_order = []
        st.session_state.block_idx = 0
        st.session_state.trial_idx = 0
        st.session_state.block_type = ''
        st.session_state.start_time = 0.0
        st.session_state.ai_advice = ''
        st.session_state.ai_shown = False
        st.session_state.choice_made = False
        st.session_state.current_choice = ''

    # ---------- 阶段1：输入被试编号 ----------
    if st.session_state.stage == 'id_input':
        pid = st.text_input("请输入被试编号（任意数字）")
        if st.button("开始实验"):
            if not pid.strip():
                st.warning("请输入被试编号")
            else:
                try:
                    int(pid)
                except:
                    st.warning("被试编号必须是数字")
                    return
                # 初始化实验
                random.seed(int(pid))
                shuffled = random.sample(SCENARIOS, len(SCENARIOS))
                mid = len(shuffled) // 2
                if int(pid) % 2 == 1:
                    st.session_state.block_order = ['direct', 'explain']
                else:
                    st.session_state.block_order = ['explain', 'direct']
                st.session_state.scenarios = shuffled
                st.session_state.block_idx = 0
                st.session_state.stage = 'block_instr'
                st.rerun()

    # ---------- 阶段2：block 指导语 ----------
    elif st.session_state.stage == 'block_instr':
        idx = st.session_state.block_idx
        if idx >= 2:
            st.session_state.stage = 'done'
            st.rerun()
        block = st.session_state.block_order[idx]
        st.session_state.block_type = block
        msg = (
            "**阶段 {}/2：{}**\n\n".format(idx+1, "直接建议" if block=='direct' else "解释性建议")
            + ("在本阶段，AI 将直接给出建议，不会解释理由。" if block=='direct' else "在本阶段，AI 会给出建议并附上一两句简要解释。")
        )
        st.markdown(msg)
        if st.button("准备就绪，开始答题"):
            st.session_state.stage = 'trial'
            st.session_state.trial_idx = 0
            st.rerun()

    # ---------- 阶段3：试次 ----------
    elif st.session_state.stage == 'trial':
        idx = st.session_state.trial_idx
        mid = len(st.session_state.scenarios) // 2
        if st.session_state.block_idx == 0:
            current_trials = st.session_state.scenarios[:mid]
        else:
            current_trials = st.session_state.scenarios[mid:]

        if idx >= len(current_trials):
            # 当前 block 结束
            st.session_state.block_idx += 1
            st.session_state.stage = 'block_instr'
            st.rerun()

        trial = current_trials[idx]
        st.markdown(f"### 第 {idx+1}/{len(current_trials)} 题")
        st.write(trial['desc'])
        st.markdown(f"**A.** {trial['A']}  \n**B.** {trial['B']}")

        # 显示 AI 建议（如果请求过）
        if st.session_state.get('ai_shown'):
            st.info(f"🤖 AI 建议：{st.session_state.ai_advice}")

        # 按钮区
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("A", key=f"a_{idx}"):
                st.session_state.choice_made = True
                st.session_state.current_choice = 'A'
                st.session_state.start_time = time.time()
                st.rerun()
        with col2:
            if st.button("B", key=f"b_{idx}"):
                st.session_state.choice_made = True
                st.session_state.current_choice = 'B'
                st.session_state.start_time = time.time()
                st.rerun()
        with col3:
            if st.button("🤖 咨询 AI", key=f"ai_{idx}"):
                # 构造 prompt
                block = st.session_state.block_type
                if block == 'direct':
                    prompt = f"用户面临以下决策：{trial['desc']} 选项A：{trial['A']}，选项B：{trial['B']}。请直接建议选A还是选B，不要添加任何解释或理由。"
                else:
                    prompt = f"用户面临以下决策：{trial['desc']} 选项A：{trial['A']}，选项B：{trial['B']}。请给出你的建议（选A或选B），并用1-2句话简洁解释你的理由。"
                with st.spinner("AI 思考中..."):
                    reply = call_deepseek(prompt)
                st.session_state.ai_advice = reply
                st.session_state.ai_shown = True
                st.rerun()

        # 选择后显示信心滑条
        if st.session_state.choice_made:
            st.markdown(f"你的选择：**{st.session_state.current_choice}**")
            conf = st.slider("信心评价 (1=完全不确定, 7=非常确定)", 1, 7, 4, key=f"conf_{idx}")
            if st.button("提交并下一题", key=f"submit_{idx}"):
                rt = time.time() - st.session_state.start_time
                row = {
                    "trial": idx+1,
                    "block": st.session_state.block_type,
                    "scenario": trial['desc'][:40] + "...",
                    "ai_requested": 1 if st.session_state.ai_shown else 0,
                    "ai_response": st.session_state.ai_advice if st.session_state.ai_shown else "",
                    "choice": st.session_state.current_choice,
                    "rt": round(rt, 2),
                    "confidence": conf
                }
                st.session_state.data.append(row)
                # 重置
                st.session_state.trial_idx += 1
                st.session_state.ai_shown = False
                st.session_state.ai_advice = ''
                st.session_state.choice_made = False
                st.session_state.current_choice = ''
                st.rerun()

    # ---------- 阶段4：完成 ----------
    elif st.session_state.stage == 'done':
        st.success("实验完成！感谢你的参与 🎉")
        df = pd.DataFrame(st.session_state.data)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下载实验数据 (CSV)",
            data=csv,
            file_name=f"data.csv",
            mime="text/csv"
        )
        if st.button("重新开始（会清空数据）"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()