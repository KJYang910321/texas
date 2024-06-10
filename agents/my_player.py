from game.players import BasePokerPlayer
import random
import numpy as np
import traceback

# 梅花 0 方塊 1 紅心 2 黑桃 3
color_dict = {'C': 0, 'D' : 1, 'H' : 2, 'S' : 3}

# number (let A equals 14)
num_dict = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

def is_flush(comb):
    color = [[] ,[] ,[] ,[]]
    for card in comb:
        color[color_dict[card[0]]].append(num_dict[card[1]])
    for idx in range(4):
        if len(color[idx]) >= 5:
            return 155 + max(color[idx])
    return 0

def is_straw(comb):

    numbers = [0] * 15
    for card in comb:
      numbers[num_dict[card[1]]] += 1

    #numbers[1] = numbers[14]
    
    count = 0
    maxi = 0
    for idx in range(2, 15):
      if numbers[idx] != 0:
        count += 1
        maxi = idx
      else:
        if count >= 5:
          return 135 + idx
        count = 0
        maxi = 0

    # handle 10-A and A-5
    if count >= 5 and numbers[14] != 0:
        return 135 + 14
    return 0

def is_combo(comb):

    numbers = [0] * 15
    four = []
    three = []
    two = []
    for card in comb:
      numbers[num_dict[card[1]]] += 1

    high_card = 0
    for idx in range(14,-1,-1):
        if numbers[idx] == 1:
          high_card = idx
          break

    for idx, count in enumerate(numbers):
      if count == 4:
        four.append(idx)
      elif count == 3:
        three.append(idx)
      elif count == 2:
        two.append(idx)

    if len(four) != 0 :
        return 250 + four[-1]
    elif len(three) == 2:
        return 170 + three[-1] + (0.5) * three[-2]
    elif len(three) != 0 and len(two) != 0:
        return 170 + three[-1] + two[-1]
    elif len(three) != 0 :
        return 120 + three[-1] + (0.002) * high_card
    elif len(two) >= 2:
        return 60 + two[-1] + (0.5)*two[-2] + (0.002) * high_card
    elif len(two) == 1:
        return 30 + two[-1] + (0.002) * high_card

    return high_card

def counting(comb):
    flush = is_flush(comb)
    straw = is_straw(comb)
    if flush != 0 or straw != 0:
        return flush + straw
    else:
        combo = is_combo(comb)
        return combo

def change_to_card(code):
  number_dict = {10:"T", 11:"J", 12:"Q", 13:"K", 1:"A"}
  color_dict = {0:"C", 1:"D", 2:"H", 3:"S"}
  card = ""
  card += color_dict[int(code / 13)]
  value = code % 13 + 1
  if value >= 10 or value < 2:
    card += number_dict[value]
  else:
    card += str(value)
  return card

class my_player(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
        try :
            call_action_info = valid_actions[1]
            action, amount = call_action_info["action"], call_action_info["amount"]
            
            current_round = round_state['round_count']
            
            if round_state['street'] == 'river':
                print(valid_actions[0]['action'], valid_actions[0]['amount'])
                print(valid_actions[1]['action'], valid_actions[1]['amount'])
                print(valid_actions[2]['action'], valid_actions[2]['amount'])
            
            community = round_state["community_card"]
            main_pot = round_state["pot"]["main"]["amount"]
            side_pot = round_state["pot"]["side"]
            # money left
            money = valid_actions[2]["amount"]["max"]
            min_raise = valid_actions[2]["amount"]["min"]
            
            my_id = round_state['next_player']
            stack = round_state['seats'][my_id]['stack']
            
            up = stack - 1000
            remain = 20 - current_round
            
            # absolute win
            if up > (remain * 7.5 + 2.5):
                return 'fold', 0
            
            if money != -1 and min_raise <= 300:
                slice = int((300-min_raise)/10)
                if slice == 0:
                    slice = 10
                raise_gap = [tick for tick in range(int(stack), int(min_raise)+1, -slice)]
            else:
                raise_gap = []
            
            deck = [change_to_card(i) for i in range(52)]
            player = hole_card.copy()
            
            print("**********")
            print(hole_card)
            print("**********")
            
            for p in player:
                deck.remove(p)
            
            for c in community:
                deck.remove(c)
            
            battle = [0,0,0]
            weight = 0
            for trial in range(10000):
                
                np.random.shuffle(deck)
                oppo = deck[10:12]
                
                cp_ratio = amount / main_pot
                
                public = deck[:(5-len(community))]
                
                player_comb = player.copy()
                player_comb.extend(community)
                player_comb.extend(public)

                oppo_comb = oppo.copy()
                oppo_comb.extend(community)
                oppo_comb.extend(public)
                
                player_s = counting(player_comb)
                oppo_s = counting(oppo_comb)
                
                if player_s > oppo_s :
                    battle[0] += 1
                elif player_s == oppo_s :
                    battle[0] += 0.01
                else:
                    battle[2] += 1
            
            win = (battle[0] / 10000)
            battle[1] /= 10000
            battle[2] /= 10000
            
            required_rate = amount / (main_pot + amount)
            
            if win == 0:
                print("strange fold")
                print(battle[0])
                print("")
                print("")
                print(player)
                print(community)
                print(deck)
                print("")
            
            # new add
            #if round_state['street'] == 'preflop':
            #    required_rate -= 0.15
            # end new add
            
            # define normal and danger status
            danger = 0
            danger_line = remain * 7.5 - 20
            if (1000 - stack) >= (2 * danger_line):
                # require more aggressive plays
                danger = 2
            elif (1000 - stack) >= danger_line:
                danger = 1
                
            # one shot
            one_shot = 2.5 + (remain * 7.5)
            
            # adjust for preflop
            if round_state['street'] == 'preflop':
                if amount == 5:
                    required_rate = 0.3
                elif amount == 10:
                    required_rate = 0
            
            if win <= (required_rate) or ((amount >= one_shot or amount >= 100) and win < 0.5):
                if danger == 0:
                    return valid_actions[0]["action"], valid_actions[0]["amount"]
                elif danger == 2:
                    return action, amount
            
            if round_state['street'] == 'preflop' and stack > 1065:
                if win < 0.4:
                    return valid_actions[0]["action"], valid_actions[0]["amount"]
            
            choice = [-1]
            for raise_amount in raise_gap:
                required = raise_amount / (main_pot + raise_amount)
                # new add
                #if round_state['street'] == 'preflop' :
                #    required -= 0.2
                # end new add
                if (win > required or danger == 2):
                    choice.append(raise_amount)
                    if danger >= 1:
                        choice.append(raise_amount)
                
            # should adjust win rate that higher win rate with lower raise amount
            decision = np.random.choice(choice, 1)
            if decision[0] == -1:
                return action, amount
            else:
                if money == -1:
                    return action, amount
                elif decision[0] > stack:
                    return valid_actions[2]["action"], stack
                return valid_actions[2]["action"], int(decision[0])
        
        except Exception as e: 
            print("error")
            print(e)
            traceback.print_exc()
            if money == -1 and min_raise == -1:
                return action, amount  # action returned here is sent to the poker engine
            else:
                return valid_actions[2]["action"], valid_actions[2]['amount']['max']

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def setup_ai():
    return my_player()