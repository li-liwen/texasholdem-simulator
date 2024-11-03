import random

# Define suits and ranks
suits = ['s', 'h', 'd', 'c']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
deck = [rank + suit for rank in ranks for suit in suits]
rank_values = {'2': 2, '3': 3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9,
               'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
hand_rank_names = {
    9: 'Straight Flush',
    8: 'Four of a Kind',
    7: 'Full House',
    6: 'Flush',
    5: 'Straight',
    4: 'Three of a Kind',
    3: 'Two Pair',
    2: 'One Pair',
    1: 'High Card'
}
simulations = 100000  # You can increase this number for more accurate results
from_file = True

def get_input():
    if not from_file:
        num_players = int(input("Enter number of players (including you): "))
        your_hand_input = input("Enter your hole cards (e.g., 'As Kd'): ")
        your_hand = your_hand_input.strip().split()
        community_cards_input = input("Enter community cards (e.g., 'Jh Tc 2c'): ")
        community_cards = community_cards_input.strip().split()
    else:
        with open("./input_file") as file:
            num_players = int(file.readline())
            your_hand = list(file.readline().split())
            community_cards = list(file.readline().split())
    return num_players, your_hand, community_cards

def remove_cards_from_deck(deck, cards_to_remove):
    for card in cards_to_remove:
        deck.remove(card)

def evaluate_hand(hand):
    # hand: list of 7 cards, each card is a string like 'As', 'Td', etc.

    # Convert hand to ranks and suits
    ranks_in_hand = []
    suits_in_hand = []
    for card in hand:
        rank = card[0]
        suit = card[1]
        ranks_in_hand.append(rank)
        suits_in_hand.append(suit)

    # Convert ranks to numeric values
    rank_nums = [rank_values[rank] for rank in ranks_in_hand]

    # Count occurrences of each rank
    rank_counts = {}
    for num in rank_nums:
        rank_counts[num] = rank_counts.get(num, 0) + 1

    # Count occurrences of each suit
    suit_counts = {}
    for suit in suits_in_hand:
        suit_counts[suit] = suit_counts.get(suit, 0) + 1

    # Check for flush
    flush_suit = None
    for suit, count in suit_counts.items():
        if count >= 5:
            flush_suit = suit
            break

    # Get sorted list of rank numbers
    rank_nums_sorted = sorted(rank_nums, reverse=True)

    # Check for straight
    rank_nums_set = set(rank_nums)
    # Special case for Ace low straight
    if set([14, 2, 3, 4, 5]).issubset(rank_nums_set):
        straight_high = 5  # 5-high straight
    else:
        straight_high = None
        for i in range(14, 4, -1):
            if set(range(i - 4, i + 1)).issubset(rank_nums_set):
                straight_high = i
                break

    # Check for straight flush
    if flush_suit:
        # Get cards of the flush suit
        flush_cards = [card for card in hand if card[1] == flush_suit]
        flush_ranks = [rank_values[card[0]] for card in flush_cards]
        flush_ranks_set = set(flush_ranks)
        # Special case for Ace low straight flush
        if set([14, 2, 3, 4, 5]).issubset(flush_ranks_set):
            straight_flush_high = 5
        else:
            straight_flush_high = None
            for i in range(14, 4, -1):
                if set(range(i - 4, i + 1)).issubset(flush_ranks_set):
                    straight_flush_high = i
                    break
    else:
        straight_flush_high = None

    # Determine hand rank
    # Hand ranks:
    # 9: Straight Flush
    # 8: Four of a Kind
    # 7: Full House
    # 6: Flush
    # 5: Straight
    # 4: Three of a Kind
    # 3: Two Pair
    # 2: One Pair
    # 1: High Card

    # Check for Straight Flush
    if straight_flush_high:
        return (9, [straight_flush_high])
    # Check for Four of a Kind
    for rank, count in rank_counts.items():
        if count == 4:
            kicker = max([r for r in rank_nums if r != rank])
            return (8, [rank, kicker])
    # Check for Full House
    three_of_kind_ranks = [rank for rank, count in rank_counts.items() if count == 3]
    pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
    if three_of_kind_ranks and (pair_ranks or len(three_of_kind_ranks) > 1):
        three_rank = max(three_of_kind_ranks)
        if len(three_of_kind_ranks) > 1:
            pair_rank = min(three_of_kind_ranks)
        else:
            pair_rank = max(pair_ranks) if pair_ranks else max([rank for rank in rank_counts if rank_counts[rank] == 3 and rank != three_rank])
        return (7, [three_rank, pair_rank])
    # Check for Flush
    if flush_suit:
        flush_cards = [card for card in hand if card[1] == flush_suit]
        flush_ranks = sorted([rank_values[card[0]] for card in flush_cards], reverse=True)
        return (6, flush_ranks[:5])
    # Check for Straight
    if straight_high:
        return (5, [straight_high])
    # Check for Three of a Kind
    if three_of_kind_ranks:
        rank = max(three_of_kind_ranks)
        kickers = sorted([r for r in rank_nums if r != rank], reverse=True)
        return (4, [rank] + kickers[:2])
    # Check for Two Pair
    if len(pair_ranks) >= 2:
        high_pair = max(pair_ranks)
        low_pair = min(pair_ranks)
        kicker = max([r for r in rank_nums if r != high_pair and r != low_pair])
        return (3, [high_pair, low_pair, kicker])
    # Check for One Pair
    if pair_ranks:
        rank = max(pair_ranks)
        kickers = sorted([r for r in rank_nums if r != rank], reverse=True)
        return (2, [rank] + kickers[:3])
    # High Card
    return (1, sorted(rank_nums, reverse=True)[:5])

def compare_hands(hand1_eval, hand2_eval):
    # hand1_eval and hand2_eval are tuples returned from evaluate_hand
    if hand1_eval[0] > hand2_eval[0]:
        return 1  # hand1 wins
    elif hand1_eval[0] < hand2_eval[0]:
        return -1  # hand2 wins
    else:
        # Same hand rank, compare tiebreaker_info
        for v1, v2 in zip(hand1_eval[1], hand2_eval[1]):
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0  # Tie

def simulate(num_players, your_hand, community_cards, simulations=10000):
    win_count = 0
    tie_count = 0
    loss_count = 0
    hand_rank_counts = {rank: 0 for rank in range(1, 10)}  # Ranks 1 to 9

    # Remove known cards from deck
    current_deck = [rank + suit for rank in ranks for suit in suits]
    remove_cards_from_deck(current_deck, your_hand + community_cards)

    for _ in range(simulations):
        # Shuffle deck
        random.shuffle(current_deck)
        # Deal hole cards to other players
        other_players_hands = []
        index = 0
        for _ in range(num_players - 1):
            hole_cards = [current_deck[index], current_deck[index + 1]]
            other_players_hands.append(hole_cards)
            index += 2
        # Deal remaining community cards
        total_community_cards = community_cards[:]
        num_community_cards_needed = 5 - len(community_cards)
        total_community_cards += current_deck[index:index + num_community_cards_needed]
        index += num_community_cards_needed

        # Evaluate your hand
        your_total_hand = your_hand + total_community_cards
        your_hand_eval = evaluate_hand(your_total_hand)
        hand_rank_counts[your_hand_eval[0]] += 1

        # Evaluate other players' hands
        win = True
        tie = False
        for opp_hand in other_players_hands:
            opp_total_hand = opp_hand + total_community_cards
            opp_hand_eval = evaluate_hand(opp_total_hand)
            result = compare_hands(your_hand_eval, opp_hand_eval)
            if result == -1:
                win = False
                break
            elif result == 0:
                tie = True
        if win:
            if tie:
                tie_count += 1
            else:
                win_count += 1
        else:
            loss_count += 1

    total = win_count + tie_count + loss_count
    win_rate = win_count / total * 100
    tie_rate = tie_count / total * 100
    loss_rate = loss_count / total * 100

    # Calculate hand value probabilities
    hand_value_probs = {}
    for rank in range(1, 10):
        hand_value_probs[rank] = hand_rank_counts[rank] / simulations * 100

    return win_rate, tie_rate, loss_rate, hand_value_probs

def main():
    num_players, your_hand, community_cards = get_input()
    win_rate, tie_rate, loss_rate, hand_value_probs = simulate(num_players, your_hand, community_cards, simulations)

    print(f"\nAfter {simulations} simulations:")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Tie rate: {tie_rate:.2f}%")
    print(f"Loss rate: {loss_rate:.2f}%\n")

    print("Probability of achieving each hand value:")
    for rank in range(9, 0, -1):
        prob = hand_value_probs[rank]
        print(f"{hand_rank_names[rank]}: {prob:.2f}%")

if __name__ == "__main__":
    main()
