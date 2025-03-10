import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from tqdm import tqdm
import pandas as pd
from collections import defaultdict
import random

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置随机种子，保证结果可复现
np.random.seed(42)
random.seed(42)

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

# 玩家策略
def player_strategy_fixed_threshold(hand_value, threshold=16):
    """固定阈值策略：点数小于等于阈值时要牌，否则停牌"""
    return hand_value <= threshold

# 庄家策略（固定规则：小于17点必须要牌）
def dealer_strategy(hand_value):
    """庄家策略：点数小于17点时要牌，否则停牌"""
    return hand_value < 17

# 单局游戏模拟
def play_game(deck, player_strategy, player_threshold=16):
    """模拟一局游戏
    
    参数:
    deck: 牌组
    player_strategy: 玩家策略函数
    player_threshold: 玩家策略的阈值参数
    
    返回:
    result: 游戏结果 (1: 玩家胜, -1: 玩家负, 0: 平局)
    player_hand: 玩家最终手牌
    dealer_hand: 庄家最终手牌
    """
    # 初始发牌
    player_hand = [deck.deal(), deck.deal()]
    dealer_hand = [deck.deal(), deck.deal()]
    
    # 玩家回合
    player_value = calculate_hand_value(player_hand)
    while player_strategy(player_value, player_threshold) and player_value < 21:
        player_hand.append(deck.deal())
        player_value = calculate_hand_value(player_hand)
    
    # 如果玩家爆牌，直接判定为输
    if player_value > 21:
        return -1, player_hand, dealer_hand
    
    # 庄家回合
    dealer_value = calculate_hand_value(dealer_hand)
    while dealer_strategy(dealer_value):
        dealer_hand.append(deck.deal())
        dealer_value = calculate_hand_value(dealer_hand)
    
    # 判定胜负
    if dealer_value > 21:  # 庄家爆牌
        return 1, player_hand, dealer_hand
    elif player_value > dealer_value:  # 玩家点数大于庄家
        return 1, player_hand, dealer_hand
    elif player_value < dealer_value:  # 玩家点数小于庄家
        return -1, player_hand, dealer_hand
    else:  # 平局
        return 0, player_hand, dealer_hand

# 蒙特卡洛模拟
def monte_carlo_simulation(num_games=10000, player_threshold=16):
    """使用蒙特卡洛方法模拟多局游戏，计算胜率
    
    参数:
    num_games: 模拟的游戏局数
    player_threshold: 玩家策略的阈值参数
    
    返回:
    win_rate: 玩家胜率
    loss_rate: 玩家败率
    draw_rate: 平局率
    """
    deck = Deck()
    wins = 0
    losses = 0
    draws = 0
    
    for _ in tqdm(range(num_games), desc=f"模拟 阈值={player_threshold}"):
        result, _, _ = play_game(deck, player_strategy_fixed_threshold, player_threshold)
        if result == 1:
            wins += 1
        elif result == -1:
            losses += 1
        else:
            draws += 1
    
    win_rate = wins / num_games
    loss_rate = losses / num_games
    draw_rate = draws / num_games
    
    return win_rate, loss_rate, draw_rate

# 比较不同阈值策略
def compare_thresholds(thresholds=range(11, 21), num_games=10000):
    """比较不同阈值策略的胜率
    
    参数:
    thresholds: 要比较的阈值列表
    num_games: 每个阈值模拟的游戏局数
    
    返回:
    results: 包含各阈值胜率的字典
    """
    results = {}
    
    for threshold in thresholds:
        win_rate, loss_rate, draw_rate = monte_carlo_simulation(num_games, threshold)
        results[threshold] = {
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'draw_rate': draw_rate,
            'expected_return': win_rate - loss_rate  # 期望收益（假设赢1元输1元）
        }
    
    return results

# 资本变化模拟
def simulate_capital_change(initial_capital=100, bet_amount=1, num_games=1000, player_threshold=16):
    """模拟玩家资本随游戏局数的变化
    
    参数:
    initial_capital: 初始资本
    bet_amount: 每局下注金额
    num_games: 模拟的游戏局数
    player_threshold: 玩家策略的阈值参数
    
    返回:
    capital_history: 资本变化历史
    """
    deck = Deck()
    capital = initial_capital
    capital_history = [capital]
    
    for _ in range(num_games):
        if capital <= 0:
            # 资本耗尽，游戏结束
            break
        
        # 确定本局下注金额（不超过当前资本）
        current_bet = min(bet_amount, capital)
        
        # 进行一局游戏
        result, _, _ = play_game(deck, player_strategy_fixed_threshold, player_threshold)
        
        # 更新资本
        if result == 1:  # 玩家胜
            capital += current_bet
        elif result == -1:  # 玩家负
            capital -= current_bet
        # 平局不变
        
        capital_history.append(capital)
    
    return capital_history

# 可视化函数
def plot_threshold_comparison(results):
    """绘制不同阈值策略的胜率比较图
    
    参数:
    results: compare_thresholds函数的返回结果
    
    返回:
    fig: 图形对象
    """
    thresholds = list(results.keys())
    win_rates = [results[t]['win_rate'] * 100 for t in thresholds]
    loss_rates = [results[t]['loss_rate'] * 100 for t in thresholds]
    draw_rates = [results[t]['draw_rate'] * 100 for t in thresholds]
    expected_returns = [results[t]['expected_return'] * 100 for t in thresholds]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 胜率、败率、平局率堆叠柱状图
    width = 0.8
    ax1.bar(thresholds, win_rates, width, label='胜率', color='#66b3ff')
    ax1.bar(thresholds, draw_rates, width, bottom=win_rates, label='平局率', color='#99ff99')
    ax1.bar(thresholds, loss_rates, width, bottom=[w+d for w, d in zip(win_rates, draw_rates)], label='败率', color='#ff9999')
    
    ax1.set_xlabel('策略阈值')
    ax1.set_ylabel('比率 (%)')
    ax1.set_title('不同阈值策略的胜负平局率')
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 期望收益折线图
    ax2.plot(thresholds, expected_returns, marker='o', linestyle='-', color='#ff6600')
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax2.set_xlabel('策略阈值')
    ax2.set_ylabel('期望收益 (%)')
    ax2.set_title('不同阈值策略的期望收益')
    ax2.grid(linestyle='--', alpha=0.7)
    
    # 找出最优阈值
    best_threshold = thresholds[expected_returns.index(max(expected_returns))]
    ax2.annotate(f'最优阈值: {best_threshold}',
                xy=(best_threshold, max(expected_returns)),
                xytext=(best_threshold-2, max(expected_returns)+5),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                fontsize=12)
    
    plt.suptitle('二十一点策略分析', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    return fig

def plot_capital_distribution(initial_capital=100, bet_amount=1, player_threshold=16, 
                             num_simulations=1000, max_games=1000):
    """绘制资本随游戏局数变化的概率分布图
    
    参数:
    initial_capital: 初始资本
    bet_amount: 每局下注金额
    player_threshold: 玩家策略的阈值参数
    num_simulations: 模拟次数
    max_games: 每次模拟的最大游戏局数
    
    返回:
    fig: 图形对象
    """
    # 存储每个局数的所有资本值
    all_capitals = [[] for _ in range(max_games + 1)]
    all_capitals[0] = [initial_capital] * num_simulations  # 初始资本
    
    # 记录破产情况
    bankruptcies = 0
    games_to_bankruptcy = []
    
    # 运行多次模拟
    for _ in tqdm(range(num_simulations), desc="模拟资本变化"):
        capital_history = simulate_capital_change(
            initial_capital=initial_capital, 
            bet_amount=bet_amount,
            num_games=max_games,
            player_threshold=player_threshold
        )
        
        # 记录破产情况
        if capital_history[-1] <= 0:
            bankruptcies += 1
            games_to_bankruptcy.append(len(capital_history) - 1)
        
        # 记录每个局数的资本
        for i, capital in enumerate(capital_history):
            if i <= max_games:
                all_capitals[i].append(capital)
        
        # 如果游戏提前结束，用最终资本填充剩余局数
        last_capital = capital_history[-1]
        for i in range(len(capital_history), max_games + 1):
            if i <= max_games:
                all_capitals[i].append(last_capital)
    
    # 创建图形
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 2, height_ratios=[3, 1])
    
    # 1. 资本分布热图
    ax1 = fig.add_subplot(gs[0, :])
    
    # 准备热图数据
    games_to_plot = min(max_games, 100)  # 限制显示的局数
    max_capital_to_plot = int(initial_capital * 3)  # 限制显示的最大资本
    heatmap_data = np.zeros((max_capital_to_plot + 1, games_to_plot + 1))
    
    for game_idx in range(games_to_plot + 1):
        capitals = all_capitals[game_idx]
        for capital in capitals:
            if 0 <= capital <= max_capital_to_plot:
                heatmap_data[int(capital), game_idx] += 1
    
    # 归一化每一列
    for col in range(heatmap_data.shape[1]):
        if np.sum(heatmap_data[:, col]) > 0:
            heatmap_data[:, col] = heatmap_data[:, col] / np.sum(heatmap_data[:, col])
    
    # 绘制热图
    sns.heatmap(heatmap_data, ax=ax1, cmap="viridis", cbar_kws={'label': '概率密度'})
    ax1.set_ylabel('资本 (元)')
    ax1.set_xlabel('游戏局数')
    ax1.set_title(f'资本随游戏局数变化的概率分布 (模拟{num_simulations}次)')
    
    # 添加初始资本线
    ax1.axhline(y=initial_capital, color='g', linestyle='--', alpha=0.7)
    
    # 2. 破产/存活统计饼图
    ax2 = fig.add_subplot(gs[1, 0])
    labels = ['破产', '存活']
    sizes = [bankruptcies, num_simulations - bankruptcies]
    colors = ['#ff9999', '#66b3ff']
    ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    ax2.set_title('模拟结果统计')
    
    # 3. 破产局数分布（如果有破产情况）
    ax3 = fig.add_subplot(gs[1, 1])
    if games_to_bankruptcy:
        sns.histplot(games_to_bankruptcy, ax=ax3, kde=True)
        ax3.set_xlabel('破产局数')
        ax3.set_ylabel('频次')
        ax3.set_title('破产局数分布')
    else:
        ax3.text(0.5, 0.5, '无破产情况', ha='center', va='center', fontsize=14)
        ax3.set_title('破产局数分布')
        ax3.axis('off')
    
    # 添加策略信息
    plt.suptitle(
        f"二十一点资本变化分析 - 策略阈值: {player_threshold}\n" +
        f"初始资本: {initial_capital}元, 下注金额: {bet_amount}元",
        fontsize=16
    )
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return fig

# 决策树可视化
def plot_decision_tree(max_value=21):
    """绘制二十一点的简化决策树
    
    参数:
    max_value: 最大考虑的点数
    
    返回:
    fig: 图形对象
    """
    # 创建图形
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # 计算每个点数要牌后的期望值
    current_values = range(4, max_value + 1)  # 从4点开始（最小可能是A+A+2=4）
    hit_expected_values = []
    bust_probs = []
    
    # 计算每个点数要牌的爆牌概率和期望值
    for current_value in current_values:
        # 计算爆牌概率
        safe_cards = [card for card, value in card_values.items() 
                     if current_value + min(value, 11) <= 21]  # A算1点
        safe_count = len(safe_cards) * 4  # 每种牌有4张
        total_cards = 52
        bust_prob = 1 - (safe_count / total_cards)
        bust_probs.append(bust_prob * 100)
        
        # 计算要牌后的期望值
        expected_value = 0
        for card, value in card_values.items():
            # 考虑A可以是1或11
            if card == 'A':
                if current_value + 11 <= 21:
                    new_value = current_value + 11
                else:
                    new_value = current_value + 1
            else:
                new_value = current_value + value
            
            # 如果爆牌，价值为0
            if new_value > 21:
                new_value = 0
            
            # 加权平均
            expected_value += (new_value * 4 / 52)  # 每种牌有4张
        
        hit_expected_values.append(expected_value)
    
    # 绘制爆牌概率
    ax.bar(current_values, bust_probs, alpha=0.7, color='#ff9999', label='爆牌概率 (%)')
    
    # 在右侧Y轴绘制要牌后的期望值
    ax2 = ax.twinx()
    ax2.plot(current_values, hit_expected_values, 'o-', color='#3366cc', linewidth=2, label='要牌后期望值')
    
    # 添加最优策略阈值线
    optimal_threshold = 16  # 根据蒙特卡洛模拟结果
    ax.axvline(x=optimal_threshold, color='r', linestyle='--', alpha=0.7, label=f'最优策略阈值 ({optimal_threshold})')
    
    # 添加标签和图例
    ax.set_xlabel('当前手牌点数')
    ax.set_ylabel('爆牌概率 (%)')
    ax2.set_ylabel('要牌后期望值')
    ax.set_title('二十一点决策分析：不同点数下要牌的爆牌概率与期望值')
    
    # 合并图例
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # 添加决策建议区域
    ax.fill_between(current_values, 0, 100, where=[x <= optimal_threshold for x in current_values], 
                   alpha=0.2, color='green', label='建议要牌区域')
    ax.fill_between(current_values, 0, 100, where=[x > optimal_threshold for x in current_values], 
                   alpha=0.2, color='red', label='建议停牌区域')
    
    plt.tight_layout()
    return fig

# 计算牌值概率分布
def calculate_card_probabilities():
    """计算二十一点中不同牌值的概率分布
    
    返回:
    probabilities: 包含各牌值概率的字典
    """
    # 计算各点数牌的数量
    card_counts = {}
    for card in card_values.keys():
        if card in ['J', 'Q', 'K']:
            card_counts[card] = 4  # 每种花色一张
        else:
            card_counts[card] = 4  # 每种花色一张
    
    # 计算各点数的概率
    total_cards = 52
    probabilities = {}
    
    # 点数牌概率
    for card, count in card_counts.items():
        probabilities[card] = count / total_cards
    
    # 10点牌的总概率 (10, J, Q, K)
    probabilities['10点'] = (card_counts['10'] + card_counts['J'] + card_counts['Q'] + card_counts['K']) / total_cards
    
    return probabilities

# 绘制牌值概率分布
def plot_card_probabilities():
    """绘制二十一点中不同牌值的概率分布
    
    返回:
    fig: 图形对象
    """
    probabilities = calculate_card_probabilities()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 准备数据
    cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10点']
    probs = [probabilities[card] * 100 for card in cards]
    
    # 绘制条形图
    bars = ax.bar(cards, probs, color='skyblue')
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom')
    
    # 添加标签和标题
    ax.set_xlabel('牌面值')
    ax.set_ylabel('概率 (%)')
    ax.set_title('二十一点中不同牌值的概率分布')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 添加说明
    ax.text(0.5, -0.15, "注：'10点'包括10、J、Q、K四种牌", ha='center', transform=ax.transAxes)
    
    plt.tight_layout()
    return fig

# 主函数
def main():
    print("\n===== 二十一点 (Blackjack) 数值分析与可视化 =====\n")
    
    # 1. 蒙特卡洛模拟不同阈值策略的胜率
    print("\n1. 分析不同阈值策略的胜率...")
    results = compare_thresholds(range(11, 21), num_games=10000)
    
    # 找出最优阈值
    best_threshold = max(results.items(), key=lambda x: x[1]['expected_return'])[0]
    print(f"\n最优策略阈值: {best_threshold}")
    print(f"最优策略胜率: {results[best_threshold]['win_rate']*100:.2f}%")
    print(f"最优策略期望收益: {results[best_threshold]['expected_return']*100:.2f}%")
    
    # 2. 绘制策略比较图
    print("\n2. 绘制策略比较图...")
    fig_threshold = plot_threshold_comparison(results)
    fig_threshold.savefig('/Users/djh/Desktop/gamblers\' problem/blackjack/strategy_comparison.png', dpi=300)
    plt.close(fig_threshold)
    
    # 3. 绘制资本变化分布图
    print("\n3. 绘制资本变化分布图...")
    fig_capital = plot_capital_distribution(
        initial_capital=100, 
        bet_amount=1,
        player_threshold=best_threshold,
        num_simulations=1000,
        max_games=1000
    )
    fig_capital.savefig('/Users/djh/Desktop/gamblers\' problem/blackjack/capital_distribution.png', dpi=300)
    plt.close(fig_capital)
    
    # 4. 绘制决策树分析图
    print("\n4. 绘制决策树分析图...")
    fig_decision = plot_decision_tree()
    fig_decision.savefig('/Users/djh/Desktop/gamblers\' problem/blackjack/decision_tree.png', dpi=300)
    plt.close(fig_decision)
    
    # 5. 绘制牌值概率分布图
    print("\n5. 绘制牌值概率分布图...")
    fig_probs = plot_card_probabilities()
    fig_probs.savefig('/Users/djh/Desktop/gamblers\' problem/blackjack/card_probabilities.png', dpi=300)
    plt.close(fig_probs)
    
    print("\n所有分析完成，结果已保存!")
    print("\n保存的图表文件:")
    print("1. strategy_comparison.png - 不同阈值策略的胜率比较")
    print("2. capital_distribution.png - 资本随游戏局数变化的概率分布")
    print("3. decision_tree.png - 决策树分析图")
    print("4. card_probabilities.png - 牌值概率分布图")

# 如果直接运行此脚本，则执行主函数
if __name__ == "__main__":
    main()