import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
import pandas as pd
import base64
from PIL import Image
import io
import os
import platform
import time
from matplotlib.font_manager import FontProperties  # 导入FontProperties

# 根据操作系统设置合适的中文字体
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows的中文黑体
elif system == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['PingFang HK', 'Arial Unicode MS']
else:  # Linux
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']

plt.rcParams['axes.unicode_minus'] = False
# 设置页面配置
st.set_page_config(
    page_title="二十一点交互式模拟",
    page_icon="♠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 定义牌的值
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11  # A初始值为11，需要时可变为1
}

# 定义花色
suits = ['♠', '♥', '♦', '♣']

# 定义牌组
class Deck:
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置牌组为一副新牌"""
        self.cards = []
        for suit in suits:
            for card, _ in card_values.items():
                self.cards.append(card + suit)
        random.shuffle(self.cards)
    
    def deal(self):
        """发一张牌"""
        if not self.cards:
            self.reset()
        return self.cards.pop()

# 计算手牌点数
def calculate_hand_value(hand):
    """计算手牌的点数，考虑A可以是1或11"""
    value = 0
    aces = 0
    
    for card in hand:
        card_value = card[:-1]  # 去掉花色
        if card_value == 'A':
            aces += 1
            value += 11
        else:
            value += card_values[card_value]
    
    # 如果点数超过21且有A，则将A的值从11改为1
    while value > 21 and aces > 0:
        value -= 10  # 11 - 1 = 10
        aces -= 1
    
    return value

# 庄家策略（固定规则：小于17点必须要牌）
def dealer_strategy(hand_value):
    """庄家策略：点数小于17点时要牌，否则停牌"""
    return hand_value < 17

# 计算爆牌概率
def calculate_bust_probability(hand_value):
    """计算当前点数下要牌的爆牌概率"""
    if hand_value >= 21:
        return 100.0
    
    # 计算安全牌的数量
    safe_cards = [card for card, value in card_values.items() 
                 if hand_value + min(value, 11) <= 21]  # A算1点
    safe_count = len(safe_cards) * 4  # 每种牌有4张
    total_cards = 52
    bust_prob = 1 - (safe_count / total_cards)
    
    return bust_prob * 100

# 计算要牌后的期望值
def calculate_hit_expected_value(hand_value):
    """计算当前点数下要牌后的期望值"""
    if hand_value >= 21:
        return 0.0
    
    expected_value = 0
    for card, value in card_values.items():
        # 考虑A可以是1或11
        if card == 'A':
            if hand_value + 11 <= 21:
                new_value = hand_value + 11
            else:
                new_value = hand_value + 1
        else:
            new_value = hand_value + value
        
        # 如果爆牌，价值为0
        if new_value > 21:
            new_value = 0
        
        # 加权平均
        expected_value += (new_value * 4 / 52)  # 每种牌有4张
    
    return expected_value

# 计算胜率
def calculate_win_probability(player_value, dealer_card):
    """计算当前玩家点数和庄家明牌下的胜率"""
    if player_value > 21:  # 玩家已爆牌
        return 0.0
    
    # 庄家明牌的值
    dealer_card_value = dealer_card[:-1]  # 去掉花色
    if dealer_card_value == 'A':
        dealer_value = 11
    else:
        dealer_value = card_values[dealer_card_value]
    
    # 模拟庄家的可能结果
    wins = 0
    total_simulations = 1000
    
    for _ in range(total_simulations):
        # 创建一副新牌
        deck = Deck()
        # 移除已知的牌
        deck.cards = [card for card in deck.cards if card != dealer_card]
        
        # 庄家初始手牌
        dealer_hand = [dealer_card]
        dealer_hand.append(deck.deal())
        current_dealer_value = calculate_hand_value(dealer_hand)
        
        # 庄家按规则要牌
        while dealer_strategy(current_dealer_value):
            dealer_hand.append(deck.deal())
            current_dealer_value = calculate_hand_value(dealer_hand)
        
        # 判断胜负
        if current_dealer_value > 21 or player_value > current_dealer_value:
            wins += 1
        elif player_value == current_dealer_value:
            wins += 0.5  # 平局算半胜
    
    return (wins / total_simulations) * 100

# 显示牌的函数
def display_card(card):
    """美化显示一张牌"""
    suit = card[-1]
    value = card[:-1]
    
    # 根据花色设置颜色
    if suit in ['♥', '♦']:
        color = "red"
    else:
        color = "black"
    
    # 使用HTML和CSS美化显示
    card_html = f"""
    <div style="
        display: inline-block;
        width: 60px;
        height: 90px;
        background-color: white;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin: 5px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        position: relative;
    ">
        <div style="
            position: absolute;
            top: 5px;
            left: 5px;
            font-size: 16px;
            color: {color};
            font-weight: bold;
        ">{value}</div>
        <div style="
            position: absolute;
            bottom: 5px;
            right: 5px;
            font-size: 16px;
            color: {color};
            font-weight: bold;
        ">{value}</div>
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            color: {color};
        ">{suit}</div>
    </div>
    """
    return card_html

# 显示手牌的函数
def display_hand(hand, hide_first=False):
    """显示一组手牌"""
    html = ""
    for i, card in enumerate(hand):
        if i == 0 and hide_first:
            html += display_card("?")
        else:
            html += display_card(card)
    return html

# 生成图表的函数
def generate_probability_chart(player_value):
    """生成当前点数的概率图表"""
    bust_prob = calculate_bust_probability(player_value)
    hit_expected = calculate_hit_expected_value(player_value)
    font = FontProperties(fname='Arial Unicode MS', size=14) 
    plt.style.use('default')  # 使用默认样式
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # 绘制爆牌概率
    ax.bar(["爆牌概率"], [bust_prob], alpha=0.7, color='#ff9999', fontproperties=font)
    
    # 在右侧Y轴绘制要牌后的期望值
    ax2 = ax.twinx()
    ax2.bar(["要牌期望值"], [hit_expected], alpha=0.7, color='#3366cc', fontproperties=font)
    
    # 添加标签
    ax.set_ylabel('爆牌概率 (%)', fontsize=10, fontproperties=font)
    ax2.set_ylabel('要牌后期望值', fontsize=10, fontproperties=font)
    ax.set_title(f'当前点数 {player_value} 的决策分析', fontsize=12, pad=20, fontproperties=font)
    
    # 设置Y轴范围
    ax.set_ylim(0, 100)
    ax2.set_ylim(0, 21)
    
    # 添加数值标签
    ax.text(0, bust_prob + 2, f"{bust_prob:.1f}%", ha='center', fontsize=10)
    ax2.text(0, hit_expected + 0.5, f"{hit_expected:.1f}", ha='center', color='#3366cc', fontsize=10)
    
    plt.tight_layout()
    return fig

# 生成胜率图表
def generate_win_probability_chart(player_value, dealer_card):
    """生成当前局面的胜率图表"""
    win_prob = calculate_win_probability(player_value, dealer_card)
    font = FontProperties(fname='Arial Unicode MS', size=14) 
    plt.style.use('default')  # 使用默认样式
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # 绘制胜率
    ax.bar(["当前胜率"], [win_prob], alpha=0.7, color='#66b3ff', fontproperties=font)
    
    # 添加标签
    ax.set_ylabel('胜率 (%)', fontsize=10, fontproperties=font)
    ax.set_title(f'当前局面胜率分析', fontsize=12, pad=20, fontproperties=font)
    
    # 设置Y轴范围
    ax.set_ylim(0, 100)
    
    # 添加数值标签
    ax.text(0, win_prob + 2, f"{win_prob:.1f}%", ha='center', fontsize=10, fontproperties=font)
    
    plt.tight_layout()
    return fig

# 主应用函数
def main():
    # 设置标题和说明
    st.title("二十一点 (Blackjack) 交互式模拟")
    st.markdown("""
    这是一个二十一点游戏的交互式模拟界面，您可以体验游戏过程并观察不同决策的概率和期望收益变化。
    
    **游戏规则**：
    - 玩家和庄家各发两张牌，庄家只有一张牌可见
    - 玩家可以选择要牌（Hit）或停牌（Stand）
    - 玩家点数超过21点则爆牌，自动输掉游戏
    - 庄家必须在点数小于17时要牌
    - 点数大者获胜，庄家爆牌则玩家获胜
    """)
    
    # 侧边栏 - 游戏设置
    st.sidebar.header("游戏设置")
    initial_capital = st.sidebar.slider("初始资本 (元)", 10, 1000, 100)
    bet_amount = st.sidebar.slider("下注金额 (元)", 1, 50, 10)
    
    # 侧边栏 - 统计信息
    st.sidebar.header("游戏统计")
    
    # 初始化会话状态
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'deck' not in st.session_state:
        st.session_state.deck = Deck()
    if 'player_hand' not in st.session_state:
        st.session_state.player_hand = []
    if 'dealer_hand' not in st.session_state:
        st.session_state.dealer_hand = []
    if 'game_result' not in st.session_state:
        st.session_state.game_result = None
    if 'capital' not in st.session_state:
        st.session_state.capital = initial_capital
    if 'current_bet' not in st.session_state:  # 添加当前赌注追踪
        st.session_state.current_bet = bet_amount
    if 'can_double' not in st.session_state:  # 添加是否可以加倍的状态
        st.session_state.can_double = True
    if 'games_played' not in st.session_state:
        st.session_state.games_played = 0
    if 'games_won' not in st.session_state:
        st.session_state.games_won = 0
    if 'games_lost' not in st.session_state:
        st.session_state.games_lost = 0
    if 'games_tied' not in st.session_state:
        st.session_state.games_tied = 0
    if 'capital_history' not in st.session_state:
        st.session_state.capital_history = [initial_capital]
    
    # 显示统计信息
    st.sidebar.metric("当前资本", f"{st.session_state.capital} 元")
    st.sidebar.metric("游戏局数", st.session_state.games_played)
    win_rate = 0 if st.session_state.games_played == 0 else (st.session_state.games_won / st.session_state.games_played) * 100
    st.sidebar.metric("胜率", f"{win_rate:.1f}%")
    
    # 资本变化图表
    if len(st.session_state.capital_history) > 1:
        st.sidebar.subheader("资本变化")
        capital_df = pd.DataFrame({
            "局数": range(len(st.session_state.capital_history)),
            "资本": st.session_state.capital_history
        })
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.plot(capital_df["局数"], capital_df["资本"], marker='o', markersize=3)
        ax.set_xlabel("局数")
        ax.set_ylabel("资本 (元)")
        ax.grid(True, alpha=0.3)
        st.sidebar.pyplot(fig)
    
    # 游戏区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 游戏状态和手牌显示
        st.subheader("游戏区域")
        
        # 开始新游戏按钮
        if not st.session_state.game_active:
            if st.button("开始新游戏", key="start_game"):
                # 检查资本是否足够
                if st.session_state.capital < st.session_state.current_bet:
                    st.error("资本不足，无法下注！")
                else:
                    # 初始化游戏
                    st.session_state.deck.reset()
                    st.session_state.player_hand = [st.session_state.deck.deal(), st.session_state.deck.deal()]
                    st.session_state.dealer_hand = [st.session_state.deck.deal(), st.session_state.deck.deal()]
                    st.session_state.game_active = True
                    st.session_state.game_result = None
                    st.rerun()
        
        # 显示游戏状态
        if st.session_state.game_active:
            # 显示下注金额
            st.write(f"当前下注: {st.session_state.current_bet} 元")
            
            # 显示庄家手牌
            st.subheader("庄家手牌")
            dealer_value = calculate_hand_value(st.session_state.dealer_hand)
            
            # 如果游戏结束，显示全部手牌，否则隐藏第一张
            hide_dealer_card = st.session_state.game_result is None
            st.markdown(display_hand(st.session_state.dealer_hand, hide_first=hide_dealer_card), unsafe_allow_html=True)
            
            if not hide_dealer_card:
                st.write(f"庄家点数: {dealer_value}")
            else:
                # 只显示第二张牌的点数
                visible_card = st.session_state.dealer_hand[1]
                visible_value = card_values[visible_card[:-1]]
                st.write(f"庄家明牌点数: {visible_value}")
            
            # 显示玩家手牌
            st.subheader("玩家手牌")
            player_value = calculate_hand_value(st.session_state.player_hand)
            st.markdown(display_hand(st.session_state.player_hand), unsafe_allow_html=True)
            st.write(f"玩家点数: {player_value}")
            
            # 游戏结果显示
            if st.session_state.game_result is not None:
                if st.session_state.game_result == "win":
                    st.success("恭喜，你赢了！")
                elif st.session_state.game_result == "lose":
                    st.error("很遗憾，你输了！")
                else:  # tie
                    st.info("平局！")
                
                # 显示新游戏按钮
                if st.button("开始新游戏", key="restart_game"):
                    # 检查资本是否足够
                    if st.session_state.capital < st.session_state.current_bet:
                        st.error("资本不足，无法下注！")
                    else:
                        # 初始化游戏
                        st.session_state.deck.reset()
                        st.session_state.player_hand = [st.session_state.deck.deal(), st.session_state.deck.deal()]
                        st.session_state.dealer_hand = [st.session_state.deck.deal(), st.session_state.deck.deal()]
                        st.session_state.game_active = True
                        st.session_state.game_result = None
                        st.rerun()
            else:
                # 游戏进行中，显示操作按钮
                col_hit, col_double, col_stand = st.columns(3)  # 改为3列以容纳加倍按钮
                
                with col_hit:
                    if st.button("要牌 (Hit)", key="hit"):
                        # 玩家要牌
                        new_player_card = st.session_state.deck.deal()
                        st.session_state.player_hand.append(new_player_card)
                        st.session_state.can_double = False  # 要过牌后不能加倍
                        player_value = calculate_hand_value(st.session_state.player_hand)
                        
                        # 显示玩家新牌
                        st.markdown("玩家要牌：")
                        st.markdown(display_card(new_player_card), unsafe_allow_html=True)
                        st.write(f"玩家当前点数: {player_value}")
                        
                        # 检查是否爆牌
                        if player_value > 21:
                            # 玩家爆牌，游戏结束
                            st.session_state.game_result = "lose"
                            st.session_state.games_played += 1
                            st.session_state.games_lost += 1
                            st.session_state.capital -= st.session_state.current_bet
                            st.session_state.capital_history.append(st.session_state.capital)
                            st.error("爆牌了！")
                        
                        # 使用 spinner 来提供更好的视觉反馈
                        with st.spinner("更新游戏状态..."):
                            time.sleep(0.5)  # 给用户时间看到新牌
                            st.rerun()
                
                with col_double:
                    # 只有在第一次行动时且资金足够时才能加倍
                    can_afford_double = st.session_state.capital >= st.session_state.current_bet * 2
                    if st.button("加倍 (Double)", key="double", 
                               disabled=not (st.session_state.can_double and can_afford_double)):
                        # 加倍下注并发一张牌
                        st.session_state.current_bet *= 2
                        new_player_card = st.session_state.deck.deal()
                        st.session_state.player_hand.append(new_player_card)
                        player_value = calculate_hand_value(st.session_state.player_hand)
                        
                        # 显示玩家新牌
                        st.markdown("加倍并要牌：")
                        st.markdown(display_card(new_player_card), unsafe_allow_html=True)
                        st.write(f"玩家当前点数: {player_value}")
                        st.write(f"当前赌注已加倍至: {st.session_state.current_bet} 元")
                        
                        # 检查是否爆牌
                        if player_value > 21:
                            # 玩家爆牌，游戏结束
                            st.session_state.game_result = "lose"
                            st.session_state.games_played += 1
                            st.session_state.games_lost += 1
                            st.session_state.capital -= st.session_state.current_bet
                            st.session_state.capital_history.append(st.session_state.capital)
                            st.error("爆牌了！")
                            with st.spinner("更新游戏状态..."):
                                time.sleep(0.5)
                                st.rerun()
                        else:
                            # 加倍后自动进入庄家回合
                            st.markdown("庄家手牌：")
                            st.markdown(display_hand(st.session_state.dealer_hand), unsafe_allow_html=True)
                            dealer_value = calculate_hand_value(st.session_state.dealer_hand)
                            st.write(f"庄家当前点数: {dealer_value}")
                            
                            # 庄家按规则要牌
                            while dealer_strategy(dealer_value):
                                new_dealer_card = st.session_state.deck.deal()
                                st.session_state.dealer_hand.append(new_dealer_card)
                                dealer_value = calculate_hand_value(st.session_state.dealer_hand)
                                
                                # 显示庄家新抽到的牌
                                st.markdown("庄家要牌：")
                                st.markdown(display_card(new_dealer_card), unsafe_allow_html=True)
                                st.write(f"庄家当前点数: {dealer_value}")
                                time.sleep(0.5)
                            
                            # 判定胜负
                            if dealer_value > 21:  # 庄家爆牌
                                st.session_state.game_result = "win"
                                st.session_state.games_won += 1
                                st.session_state.capital += st.session_state.current_bet
                                st.success("庄家爆牌，你赢了！")
                            elif player_value > dealer_value:  # 玩家点数大于庄家
                                st.session_state.game_result = "win"
                                st.session_state.games_won += 1
                                st.session_state.capital += st.session_state.current_bet
                                st.success(f"你赢了！（{player_value} vs {dealer_value}）")
                            elif player_value < dealer_value:  # 玩家点数小于庄家
                                st.session_state.game_result = "lose"
                                st.session_state.games_lost += 1
                                st.session_state.capital -= st.session_state.current_bet
                                st.error(f"你输了！（{player_value} vs {dealer_value}）")
                            else:  # 平局
                                st.session_state.game_result = "tie"
                                st.session_state.games_tied += 1
                                st.info(f"平局！（{player_value} vs {dealer_value}）")
                            
                            st.session_state.games_played += 1
                            st.session_state.capital_history.append(st.session_state.capital)
                            with st.spinner("更新游戏状态..."):
                                time.sleep(1)
                                st.rerun()
                
                with col_stand:
                    if st.button("停牌 (Stand)", key="stand"):
                        # 玩家停牌，显示庄家的所有手牌
                        st.markdown("庄家手牌：")
                        st.markdown(display_hand(st.session_state.dealer_hand), unsafe_allow_html=True)
                        dealer_value = calculate_hand_value(st.session_state.dealer_hand)
                        st.write(f"庄家当前点数: {dealer_value}")
                        
                        # 庄家按规则要牌
                        while dealer_strategy(dealer_value):
                            new_dealer_card = st.session_state.deck.deal()
                            st.session_state.dealer_hand.append(new_dealer_card)
                            dealer_value = calculate_hand_value(st.session_state.dealer_hand)
                            
                            # 显示庄家新抽到的牌
                            st.markdown("庄家要牌：")
                            st.markdown(display_card(new_dealer_card), unsafe_allow_html=True)
                            st.write(f"庄家当前点数: {dealer_value}")
                            time.sleep(0.5)  # 给用户时间看清每张新牌
                        
                        # 判定胜负
                        player_value = calculate_hand_value(st.session_state.player_hand)
                        
                        if dealer_value > 21:  # 庄家爆牌
                            st.session_state.game_result = "win"
                            st.session_state.games_won += 1
                            st.session_state.capital += st.session_state.current_bet
                            st.success("庄家爆牌，你赢了！")
                        elif player_value > dealer_value:  # 玩家点数大于庄家
                            st.session_state.game_result = "win"
                            st.session_state.games_won += 1
                            st.session_state.capital += st.session_state.current_bet
                            st.success(f"你赢了！（{player_value} vs {dealer_value}）")
                        elif player_value < dealer_value:  # 玩家点数小于庄家
                            st.session_state.game_result = "lose"
                            st.session_state.games_lost += 1
                            st.session_state.capital -= st.session_state.current_bet
                            st.error(f"你输了！（{player_value} vs {dealer_value}）")
                        else:  # 平局
                            st.session_state.game_result = "tie"
                            st.session_state.games_tied += 1
                            st.info(f"平局！（{player_value} vs {dealer_value}）")
                        
                        st.session_state.games_played += 1
                        st.session_state.capital_history.append(st.session_state.capital)
                        
                        # 使用 spinner 来提供更好的视觉反馈
                        with st.spinner("更新游戏状态..."):
                            time.sleep(1)  # 给用户时间看清结果
                            st.rerun()
    
    with col2:
        # 概率和决策分析区域
        if st.session_state.game_active and st.session_state.game_result is None:
            st.subheader("决策分析")
            
            # 显示当前爆牌概率和期望值
            player_value = calculate_hand_value(st.session_state.player_hand)
            prob_fig = generate_probability_chart(player_value)
            st.pyplot(prob_fig)
            
            # 显示当前胜率
            win_fig = generate_win_probability_chart(player_value, st.session_state.dealer_hand[1])
            st.pyplot(win_fig)
            
            # 决策建议
            st.subheader("决策建议")
            bust_prob = calculate_bust_probability(player_value)
            win_prob = calculate_win_probability(player_value, st.session_state.dealer_hand[1])
            
            if player_value >= 17 and win_prob > 45:
                st.info("建议: 停牌 (Stand)")
            elif bust_prob < 30 or (player_value <= 11):
                st.info("建议: 要牌 (Hit)")
            else:
                if win_prob > 40:
                    st.info("建议: 停牌 (Stand)")
                else:
                    st.info("建议: 要牌 (Hit)")

# 运行应用
if __name__ == "__main__":
    main()