import streamlit as st
import requests
import time
import random
import pandas as pd
import re

# ==================== 情景库（15个） ====================
SCENARIOS = [
    {
        "desc": "你刚搬到一座新城市，需要找个住处。市中心一套公寓离公司很近，步行就能上班，但租金较贵，而且周边晚上比较嘈杂。郊区一套房子租金便宜一半，环境安静，但每天通勤需要坐一个多小时的地铁，早高峰还很拥挤。",
        "A": "选择市中心公寓（贵但方便）",
        "B": "选择郊区房子（便宜但通勤长）"
    },
    {
        "desc": "你在一家公司工作五年了，最近拿到两个 offer。大公司名气响亮，薪资涨幅一般，但流程规范，晋升需要熬年限。一家初创公司邀请你加入，承诺核心岗位和期权，但团队还很小，产品还没正式上线，行业竞争也很激烈。",
        "A": "加入初创公司（高风险高潜力）",
        "B": "留在大公司（稳定可预期）"
    },
    {
        "desc": "你最好的朋友最近因为一次误会和你闹了矛盾，把你微信拉黑了。你有两个选择：主动找共同朋友从中调解，但这可能让更多人知道你们的不和；或者等一段时间，让双方冷静下来，但可能关系就此疏远。",
        "A": "请共同朋友帮忙调解（主动但可能扩大事态）",
        "B": "静静等待对方消气（被动但保全隐私）"
    },
    {
        "desc": "你一直想学一门新技能（比如钢琴或编程），现在有一个短期集训班，价格不菲，占用两个周末，但据说效果很好。你也可以在网上找免费教程自学，省钱但进度慢，而且没人督促容易中途放弃。",
        "A": "报班系统学习（花钱买效率）",
        "B": "自学摸索（省钱但耗时长）"
    },
    {
        "desc": "你在商场看到一件非常喜欢的外套，设计独特，试穿效果很好，但价格超出你本月的衣物预算。你犹豫是否要买下，因为下个月可能要参加一个重要活动，穿着它确实会加分，但这个月剩下的生活费会变紧张。",
        "A": "买下外套（即时满足）",
        "B": "放弃购买（保持预算）"
    },
    {
        "desc": "你父母希望你毕业后回老家考公务员，那里有房有车，生活安逸，还能照顾逐渐年迈的他们。但你自己更想去一线城市闯一闯，试试喜欢的互联网行业，虽然起步辛苦，租房挤地铁，但机会更多。",
        "A": "去一线城市闯荡（追求个人理想）",
        "B": "回老家考公务员（照顾家庭求稳）"
    },
    {
        "desc": "你们大学班级正在评选优秀班干部，你的好朋友也参加了竞选。他的工作能力一般，但对你一直很照顾，投他一票他大概率能当选。另一位候选人你不熟悉，但公认能力更强，组织过很多成功的活动。班主任说这次投票完全匿名。",
        "A": "投票给好友（人情义气）",
        "B": "投票给更有能力的同学（公平公正）"
    },
    {
        "desc": "你计划下个月出国玩一周，已经请好假。临行前公司突然通知有个重要项目需要你参与，如果能完成，对年底晋升很有帮助。但你不得不取消行程，机票酒店退订会损失一笔钱，而且下次有空不知道什么时候。",
        "A": "取消旅行，投入项目（职业发展优先）",
        "B": "坚持出发，旅行放松（个人生活优先）"
    },
    {
        "desc": "你发现同事在报销单上多填了一些金额，虽然数额不大，但明显是故意的。如果向领导反映，同事可能会被处分，你也可能被认为“爱打小报告”；如果装作没看见，又觉得自己在默许不诚实的行为。",
        "A": "私下提醒同事改正（给机会但可能无效）",
        "B": "直接向领导反映（维护规则但伤关系）"
    },
    {
        "desc": "你有一笔闲置存款，银行理财经理推荐一款热门基金，最近几个月涨势很好，身边也有朋友赚了钱。但你也听说市场波动较大，有不少人追高被套。你也可以选择继续存定期，利息虽然低，但晚上睡得安稳。",
        "A": "买入热门基金（追求高收益）",
        "B": "继续存定期（保证本金安全）"
    },
    {
        "desc": "周末晚上，你原本计划在家看书充电，突然几个老同学约你出去聚餐。你很久没见他们了，聚在一起肯定很开心，但这样一来你的学习计划就泡汤了，下周的考试还没完全准备好。",
        "A": "出去聚会（社交放松）",
        "B": "留在家学习（自律充电）"
    },
    {
        "desc": "你攒了一笔钱想买一台新手机，最新款旗舰机型拍照好、性能强，但价格是普通机型的近两倍。普通机型完全够用，只是缺少一些新功能。你身边不少人都换了旗舰款。",
        "A": "买最新旗舰（追求品质）",
        "B": "买性价比款（理性消费）"
    },
    {
        "desc": "你是一个团队的负责人，有个项目交付在即，但关键成员家里有急事请假，导致进度可能延误。你可以自己加班顶上，但会很累；也可以申请延期，但这可能影响团队季度考核。",
        "A": "自己加班顶上（硬扛保交付）",
        "B": "申请延期（保护个人精力）"
    },
    {
        "desc": "你暗恋一位同学很久，两人平时关系友好但没挑明。马上毕业了，你想在毕业典礼上送一份特别的礼物表白。如果对方接受，可能开始一段恋情；如果拒绝，连朋友都做不成，毕业照都会有点尴尬。",
        "A": "表白心意（抓住最后机会）",
        "B": "保持沉默（保留友谊）"
    },
    {
        "desc": "你看到一个公益项目，捐款帮助山区儿童建图书馆。捐出一笔不小的数目会让你这个月手头紧一些，但能直接改善几十个孩子的阅读条件。你也可以选择捐很少，或者下次再说。",
        "A": "捐出较大数额（慷慨助人）",
        "B": "象征性捐一点（量力而行）"
    }
]

# ==================== 自动化信任量表 ====================
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

def extract_ai_choice(ai_text):
    """从 AI 回复中提取建议选项（A 或 B），增强鲁棒性"""
    if not ai_text:
        return ""
    text = ai_text.strip()
    # 多种正则模式，按优先级尝试
    patterns = [
        r'建议[选选择]*\s*([AB])',   # 建议选A / 建议选择B
        r'推荐\s*([AB])',            # 推荐A
        r'我推荐\s*([AB])',
        r'我会选\s*([AB])',
        r'选择\s*([AB])',            # 选择A
        r'[选]\s*([AB])',            # 选A
        r'答案\s*[是为：:]\s*([AB])',# 答案是A
        r'([AB])\s*[。.]',           # 以A或B结尾的句子（谨慎）
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    # 如果都没匹配到，在文本中查找独立的 A 或 B（尽量避开单词中的AB）
    # 仅作为最后手段，并记录警告
    if re.search(r'\bA\b', text):
        return 'A'
    if re.search(r'\bB\b', text):
        return 'B'
    return ""

# ==================== 主函数 ====================
def main():
    st.set_page_config(page_title="AI决策实验", layout="centered")
    st.title("🧠 日常决策实验")

    if 'stage' not in st.session_state:
        st.session_state.stage = 'trust_scale'
        st.session_state.data = []
        st.session_state.trust_scores = []
        st.session_state.trust_total = 0
        st.session_state.trust_items = {}
        st.session_state.scenarios_no_ai = []
        st.session_state.scenarios_ai = []
        st.session_state.block_order = []
        st.session_state.block_idx = 0
        st.session_state.trial_idx = 0
        st.session_state.current_block = ''
        st.session_state.choice = ''
        st.session_state.ai_text = ''
        st.session_state.ai_choice = ''
        st.session_state.ai_shown = False
        st.session_state.countdown_start = 0.0
        st.session_state.participant = ''

    # ---------- 信任量表 ----------
    if st.session_state.stage == 'trust_scale':
        st.markdown("## 第一部分：AI 态度调查")
        st.write("请根据你的真实想法，对以下陈述打分（1 = 完全不同意，7 = 完全同意）")
        scores = []
        for i, item in enumerate(TRUST_ITEMS):
            score = st.slider(item, 1, 7, 4, key=f"trust_{i}")
            scores.append(score)
        if st.button("提交并开始实验"):
            st.session_state.trust_scores = scores
            st.session_state.trust_total = sum(scores)
            st.session_state.trust_items = {f"trust_q{i+1}": scores[i] for i in range(7)}
            st.session_state.stage = 'practice'
            st.rerun()

    # ---------- 练习 ----------
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

    # ---------- 编号与分组 ----------
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
                st.session_state.scenarios_ai = [SCENARIOS[i] for i in shuffled[6:12]]
                if int(pid) % 2 == 1:
                    st.session_state.block_order = ['no_ai', 'ai']
                else:
                    st.session_state.block_order = ['ai', 'no_ai']
                st.session_state.block_idx = 0
                st.session_state.stage = 'block_instr'
                st.rerun()

    # ---------- Block 指导语 ----------
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
            msg = f"**阶段 {idx+1}/2：AI 辅助判断**\n\n情景显示后，AI 将立即开始生成建议，随后进入 6 秒阅读倒计时，倒计时结束后 AI 建议自动出现。该AI系统已经适配于本次实验的情景（均具有完整的提示词，均是AI基于情景题实时反馈的数据）"
        st.markdown(msg)
        if st.button("开始本阶段"):
            st.session_state.stage = 'trial'
            st.session_state.trial_idx = 0
            st.session_state.ai_text = ''
            st.session_state.ai_choice = ''
            st.session_state.ai_shown = False
            st.session_state.choice = ''
            if 'countdown_start' in st.session_state:
                del st.session_state.countdown_start
            st.rerun()

    # ---------- 试次 ----------
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

        # ========== 无 AI ==========
        if block == 'no_ai':
            if st.session_state.choice == '':
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("选择 A", key=f"no_a_{idx}"):
                        st.session_state.choice = 'A'
                        st.rerun()
                with col2:
                    if st.button("选择 B", key=f"no_b_{idx}"):
                        st.session_state.choice = 'B'
                        st.rerun()
            else:
                st.markdown(f"你的选择：**{st.session_state.choice}**")
                conf = st.slider("信心评价 (1=完全不确定, 7=非常确定)", 1, 7, 4, key=f"no_conf_{idx}")
                if st.button("提交并继续", key=f"no_sub_{idx}"):
                    row = {
                        "participant": st.session_state.participant,
                        "block": "no_ai",
                        "trial": idx + 1,
                        "scenario": trial['desc'][:40] + "...",
                        "ai_response": "",
                        "ai_choice": "",
                        "adopt": "",
                        "choice": st.session_state.choice,
                        "confidence": conf,
                        "trust_total": st.session_state.trust_total,
                        **st.session_state.trust_items
                    }
                    st.session_state.data.append(row)
                    st.session_state.trial_idx += 1
                    st.session_state.choice = ''
                    st.rerun()

        # ========== 有 AI ==========
        else:
            # API 调用
            if 'ai_called' not in st.session_state:
                st.session_state.ai_called = False
            if not st.session_state.ai_called:
                with st.spinner("🤖 AI 正在准备建议，请稍候..."):
                    ai_reply = get_ai_advice(trial['desc'], trial['A'], trial['B'])
                st.session_state.ai_text = ai_reply
                st.session_state.ai_choice = extract_ai_choice(ai_reply)
                st.session_state.ai_called = True
                st.session_state.countdown_start = time.time()
                st.rerun()

            # 倒计时
            elapsed = time.time() - st.session_state.countdown_start
            remaining = max(0, 6.0 - elapsed)
            if remaining > 0:
                st.info(f"请仔细阅读情景，AI 建议将在 {remaining:.1f} 秒后显示。")
                time.sleep(0.5)
                st.rerun()

            # 显示建议
            if not st.session_state.ai_shown:
                st.markdown("---")
                choice_str = st.session_state.ai_choice if st.session_state.ai_choice else "（未识别到选项，请查看下方文本）"
                st.markdown(f"### 🤖 AI 建议选：{choice_str}")
                st.info(st.session_state.ai_text)
                if not st.session_state.ai_choice:
                    st.warning("⚠️ 未能提取到明确的选项，请根据上方完整回复自行判断。")
                else:
                    st.caption(f"[调试] 提取到的选项：{st.session_state.ai_choice}")
                st.session_state.ai_shown = True
                # 关键：不再 rerun，直接进入选择阶段

            # 选择
            if st.session_state.choice == '':
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("选择 A", key=f"ai_a_{idx}"):
                        st.session_state.choice = 'A'
                        st.rerun()
                with col2:
                    if st.button("选择 B", key=f"ai_b_{idx}"):
                        st.session_state.choice = 'B'
                        st.rerun()
            else:
                st.markdown(f"你的选择：**{st.session_state.choice}**")
                conf = st.slider("信心评价", 1, 7, 4, key=f"ai_conf_{idx}")
                if st.button("提交并继续", key=f"ai_sub_{idx}"):
                    # 计算采纳
                    ai_ch = st.session_state.ai_choice
                    if ai_ch in ['A', 'B']:
                        adopt = 1 if st.session_state.choice == ai_ch else 0
                    else:
                        adopt = ""  # 无法判断
                    row = {
                        "participant": st.session_state.participant,
                        "block": "ai",
                        "trial": idx + 1,
                        "scenario": trial['desc'][:40] + "...",
                        "ai_response": st.session_state.ai_text,
                        "ai_choice": ai_ch,
                        "adopt": adopt,
                        "choice": st.session_state.choice,
                        "confidence": conf,
                        "trust_total": st.session_state.trust_total,
                        **st.session_state.trust_items
                    }
                    st.session_state.data.append(row)
                    st.session_state.trial_idx += 1
                    st.session_state.choice = ''
                    st.session_state.ai_called = False
                    st.session_state.ai_shown = False
                    if 'countdown_start' in st.session_state:
                        del st.session_state.countdown_start
                    st.rerun()

    # ---------- 完成 ----------
    elif st.session_state.stage == 'done':
        st.success("实验完成！感谢你的参与 🎉")
        df = pd.DataFrame(st.session_state.data)

        # 个人统计
        no_ai = df[df['block'] == 'no_ai']
        ai = df[df['block'] == 'ai']
        baseline_a = (no_ai['choice'] == 'A').mean() if len(no_ai) > 0 else 0
        adopt_rate = (ai['adopt'] == 1).mean() if len(ai) > 0 else 0
        conf_no_ai = no_ai['confidence'].mean() if len(no_ai) > 0 else 0
        conf_ai = ai['confidence'].mean() if len(ai) > 0 else 0

        st.markdown("### 📋 你的实验摘要")
        st.write(f"自然 A 偏好（无 AI 条件下选 A 的比例）：{baseline_a:.2%}")
        st.write(f"AI 建议采纳率：{adopt_rate:.2%}")
        st.write(f"无 AI 阶段平均信心：{conf_no_ai:.2f}")
        st.write(f"有 AI 阶段平均信心：{conf_ai:.2f}")

        st.markdown("### 📋 信任量表得分")
        for i in range(7):
            st.write(f"题{i+1}: {st.session_state.trust_scores[i]}")
        st.write(f"**总分：{st.session_state.trust_total} / 49**")

        st.markdown("### 📊 完整数据")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("请下载实验数据返回主试 (CSV)", data=csv,
                           file_name=f"subj_{st.session_state.participant}.csv",
                           mime="text/csv")
        if st.button("重新开始"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
