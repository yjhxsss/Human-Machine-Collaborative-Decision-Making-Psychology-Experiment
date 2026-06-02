import streamlit as st
import requests
import time
import random
import pandas as pd

# ==================== 情景库（不变） ====================
SCENARIOS = [
    # ... （与你之前版本完全相同，此处省略以节省篇幅）
]

# ==================== 自动化信任量表（不变） ====================
TRUST_ITEMS = [
    "我认为 AI 决策系统是可靠的。",
    "我相信 AI 系统能给出正确的建议。",
    "我信任 AI 系统提供的信息。",
    "即使 AI 系统偶尔出错，我仍然相信它。",
    "我对 AI 系统的能力有信心。",
    "即使我不完全理解 AI 系统，我也愿意相信它的输出。",
    "我依赖 AI 系统来帮助我做决策。"
]

# ==================== DeepSeek API 调用 ====================
def get_ai_advice(scenario_desc, option_a, option_b):
    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = (
        f"面对以下情景，请给出你的建议（选A或选B），并用1-2句话简单说明理由。\n"
        f"情景：{scenario_desc}\n"
        f"A. {option_a}\n"
        f"B. {option_b}"
    )
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个理性且富有洞察力的决策助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"[AI 暂时无法回应（状态码 {r.status_code}）]"
    except Exception as e:
        return f"[连接失败：{e}]"

# ==================== 主函数 ====================
def main():
    st.set_page_config(page_title="AI决策实验", layout="centered")
    st.title("🧠 日常决策实验")

    # ---------- 初始化会话状态 ----------
    if 'stage' not in st.session_state:
        st.session_state.stage = 'trust_scale'
        st.session_state.data = []
        st.session_state.trust_total = 0
        st.session_state.block_order = []
        st.session_state.block_idx = 0
        st.session_state.trial_idx = 0
        st.session_state.current_block = ''
        st.session_state.choice = ''
        st.session_state.waiting_choice = False
        st.session_state.ai_text = ''
        st.session_state.countdown = 6
        st.session_state.participant = ''

    # ---------- 阶段1：信任量表 ----------
    if st.session_state.stage == 'trust_scale':
        st.markdown("## 第一部分：AI 态度调查")
        st.write("请根据你的真实想法，对以下陈述打分（1 = 完全不同意，7 = 完全同意）")
        scores = []
        for i, item in enumerate(TRUST_ITEMS):
            score = st.slider(item, 1, 7, 4, key=f"trust_{i}")
            scores.append(score)
        if st.button("提交并开始实验"):
            st.session_state.trust_total = sum(scores)
            st.session_state.stage = 'practice'
            st.rerun()

    # ---------- 阶段2：练习 ----------
    elif st.session_state.stage == 'practice':
        st.markdown("## 练习：熟悉实验流程")
        st.write("下面是一个示例情景，请像正式实验那样做出选择。本阶段没有 AI 建议。")
        practice = {
            "desc": "你想买一本专业书籍，实体书店售价 80 元，网上售价 50 元但需要等 3 天快递。你会怎么选？",
            "A": "马上在书店购买",
            "B": "网上购买等三天"
        }
        st.write(practice['desc'])
        st.markdown(f"**A.** {practice['A']}  \n**B.** {practice['B']}")
        if 'practice_choice' not in st.session_state:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("选择 A", key="prac_a"):
                    st.session_state.practice_choice = 'A'
                    st.rerun()
            with col2:
                if st.button("选择 B", key="prac_b"):
                    st.session_state.practice_choice = 'B'
                    st.rerun()
        else:
            st.write(f"你选择了 {st.session_state.practice_choice}。练习结束。")
            if st.button("进入正式实验"):
                st.session_state.stage = 'id_input'
                st.rerun()

    # ---------- 阶段3：编号与随机分组 ----------
    elif st.session_state.stage == 'id_input':
        pid = st.text_input("请输入被试编号（数字）")
        if st.button("确定"):
            if not pid.strip():
                st.warning("请输入被试编号")
            else:
                try:
                    int(pid)
                except:
                    st.warning("被试编号必须是数字")
                    return
                st.session_state.participant = pid
                random.seed(int(pid))
                shuffled = random.sample(range(len(SCENARIOS)), 12)
                st.session_state.scenarios_no_ai = [SCENARIOS[i] for i in shuffled[:6]]
                st.session_state.scenarios_ai = [SCENARIOS[i] for i in shuffled[6:]]
                # 顺序平衡
                if int(pid) % 2 == 1:
                    st.session_state.block_order = ['no_ai', 'ai']
                else:
                    st.session_state.block_order = ['ai', 'no_ai']
                st.session_state.block_idx = 0
                st.session_state.stage = 'block_instr'
                st.rerun()

    # ---------- 阶段4：Block 指导语 ----------
    elif st.session_state.stage == 'block_instr':
        idx = st.session_state.block_idx
        if idx >= 2:
            st.session_state.stage = 'done'
            st.rerun()
        block = st.session_state.block_order[idx]
        st.session_state.current_block = block
        if block == 'no_ai':
            msg = f"**阶段 {idx+1}/2：自主判断（无 AI 建议）**\n\n请阅读情景后直接做出选择。"
        else:
            msg = f"**阶段 {idx+1}/2：AI 辅助判断**\n\n情景显示后，AI 将立即开始生成建议（可能需要几秒），随后会进入 6 秒阅读倒计时，倒计时结束后 AI 建议自动出现。"
        st.markdown(msg)
        if st.button("开始本阶段"):
            st.session_state.stage = 'trial'
            st.session_state.trial_idx = 0
            st.session_state.ai_text = ''
            st.session_state.countdown = 6
            st.session_state.choice = ''
            st.session_state.waiting_choice = False
            st.rerun()

    # ---------- 阶段5：试次 ----------
    elif st.session_state.stage == 'trial':
        block = st.session_state.current_block
        trials = st.session_state.scenarios_no_ai if block == 'no_ai' else st.session_state.scenarios_ai
        idx = st.session_state.trial_idx
        if idx >= len(trials):
            st.session_state.block_idx += 1
            st.session_state.stage = 'block_instr'
            st.rerun()

        trial = trials[idx]
        st.markdown(f"### 第 {idx+1}/{len(trials)} 题")
        st.write(trial['desc'])
        st.markdown(f"**A.** {trial['A']}  \n**B.** {trial['B']}")

        # ========== 无 AI 条件 ==========
        if block == 'no_ai':
            if not st.session_state.waiting_choice:
                st.session_state.waiting_choice = True
                st.rerun()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("选择 A", key=f"no_a_{idx}"):
                    st.session_state.choice = 'A'
                    st.rerun()
            with col2:
                if st.button("选择 B", key=f"no_b_{idx}"):
                    st.session_state.choice = 'B'
                    st.rerun()
            if st.session_state.choice != '':
                st.markdown(f"你的选择：**{st.session_state.choice}**")
                conf = st.slider("信心评价 (1=完全不确定, 7=非常确定)", 1, 7, 4, key=f"no_conf_{idx}")
                if st.button("提交并继续", key=f"no_sub_{idx}"):
                    st.session_state.data.append({
                        "participant": st.session_state.participant,
                        "block": "no_ai",
                        "trial": idx + 1,
                        "scenario": trial['desc'][:40] + "...",
                        "ai_response": "",
                        "choice": st.session_state.choice,
                        "confidence": conf,
                        "trust_total": st.session_state.trust_total
                    })
                    st.session_state.trial_idx += 1
                    st.session_state.waiting_choice = False
                    st.session_state.choice = ''
                    st.rerun()

        # ========== 有 AI 条件 ==========
        else:
            # ---- 第一阶段：如果尚未调用 API，立即调用 ----
            if 'ai_called' not in st.session_state:
                st.session_state.ai_called = False
            if not st.session_state.ai_called:
                with st.spinner("🤖 AI 正在准备建议，请稍候..."):
                    ai_reply = get_ai_advice(trial['desc'], trial['A'], trial['B'])
                st.session_state.ai_text = ai_reply
                st.session_state.ai_called = True
                st.session_state.countdown_start = time.time()
                st.rerun()

            # ---- 第二阶段：倒计时 ----
            elapsed = time.time() - st.session_state.countdown_start
            remaining = max(0, 6.0 - elapsed)
            if remaining > 0:
                st.info(f"请仔细阅读情景，AI 建议将在 {remaining:.1f} 秒后显示。")
                # 每 0.5 秒刷新一次倒计时
                time.sleep(0.5)
                st.rerun()

            # ---- 第三阶段：显示建议并允许选择 ----
            st.markdown("---")
            st.markdown("### 🤖 AI 的建议")
            st.info(st.session_state.ai_text)

            if not st.session_state.waiting_choice:
                st.session_state.waiting_choice = True
                st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                if st.button("选择 A", key=f"ai_a_{idx}"):
                    st.session_state.choice = 'A'
                    st.rerun()
            with col2:
                if st.button("选择 B", key=f"ai_b_{idx}"):
                    st.session_state.choice = 'B'
                    st.rerun()

            if st.session_state.choice != '':
                st.markdown(f"你的选择：**{st.session_state.choice}**")
                conf = st.slider("信心评价", 1, 7, 4, key=f"ai_conf_{idx}")
                if st.button("提交并继续", key=f"ai_sub_{idx}"):
                    st.session_state.data.append({
                        "participant": st.session_state.participant,
                        "block": "ai",
                        "trial": idx + 1,
                        "scenario": trial['desc'][:40] + "...",
                        "ai_response": st.session_state.ai_text,
                        "choice": st.session_state.choice,
                        "confidence": conf,
                        "trust_total": st.session_state.trust_total
                    })
                    # 清理本试次的状态
                    st.session_state.trial_idx += 1
                    st.session_state.waiting_choice = False
                    st.session_state.choice = ''
                    st.session_state.ai_called = False
                    if 'countdown_start' in st.session_state:
                        del st.session_state.countdown_start
                    st.rerun()

    # ---------- 阶段6：结束 ----------
    elif st.session_state.stage == 'done':
        st.success("实验完成！感谢你的参与 🎉")
        df = pd.DataFrame(st.session_state.data)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("下载数据 (CSV)", data=csv,
                           file_name=f"subj_{st.session_state.participant}.csv",
                           mime="text/csv")
        if st.button("清除数据并重新开始"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()