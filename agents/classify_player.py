from game.players import BasePokerPlayer
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import pickle
import joblib

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

    numbers[1] = numbers[14]
    
    count = 0
    maxi = 0
    for idx in range(1, 15):
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

#with open('random_forest_model.pkl', 'rb') as file:
#    model_1 = pickle.load(file)
#with open('random_forest_model_v2.pkl', 'rb') as file_2:
#    model_2 = pickle.load(file_2)
#with open('random_forest_model_v3.pkl', 'rb') as file_3:
#    model_3 = pickle.load(file_3)
#with open('random_forest_model_v4.pkl', 'rb') as file_4:
#    model_4 = pickle.load(file_4)

acts_arr = ['fold', 'call', 'raise', 'raise', 'raise', 'raise']
chips_arr = [0, 0, 0.1, 0.25, 0.5, 1]

class CallPlayer(
    BasePokerPlayer
):  # Do not forget to make parent class as "BasePokerPlayer"
    
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        
        #print(round_state)
        player_idx = round_state['next_player']
        small_blind = round_state['small_blind_pos']
        
        if player_idx == small_blind:
            blind = 0
        else:
            blind = 1
        
        
        community = round_state["community_card"]
        main_pot = round_state["pot"]["main"]["amount"]
        side_pot = round_state["pot"]["side"]
        # money left
        money = valid_actions[2]["amount"]["max"]
        min_raise = valid_actions[2]["amount"]["min"]
        
        score = counting(hole_card + community)
        combo = hole_card + community
        detail_card = []
        
        current_round = round_state['round_count']
        up = money - 1000
        remain = (20 - current_round + 1)
        if up > (remain * 7.5 + 2.5):
            return 'fold', 0
        
        #print(combo)
        
        for c in combo:
            num = num_dict[c[1]]
            if num == 14:
                num = 1
            detail_card.append(color_dict[c[0]])
            detail_card.append(num)
    
        call_amount = amount

        round = round_state['street']
        
        arr = detail_card.copy()
        arr = arr + [call_amount, main_pot, blind]
        
        #print(main_pot)
        #print(valid_actions[0]['action'], valid_actions[0]['amount'])
        #print(valid_actions[1]['action'], valid_actions[1]['amount'])
        #print(valid_actions[2]['action'], valid_actions[2]['amount'])
        
        try:
            #with open('random_forest_model_1.pkl', 'rb') as f1:
            #    model_1 = pickle.load(f1)
            #with open('random_forest_model_2.pkl', 'rb') as f2:
            #with open('random_forest_model_3.pkl', 'rb') as f3:
            #    model_3= pickle.load(f3)
            #with open('random_forest_model_4.pkl', 'rb') as f4:
            #    model_4= pickle.load(f4)
            model_1 = joblib.load('random_forest_model_1.joblib')
            model_2 = joblib.load('random_forest_model_2.joblib')
            model_3 = joblib.load('random_forest_model_3.joblib')
            model_4 = joblib.load('random_forest_model_4.joblib')
                
        except Exception as e:
            print(f"Error loading model: {e}")
            return 'fold', 0
        
        if round == 'preflop':
            action_idx = model_1.predict([arr])[0]
            
        elif round == 'flop':
            action_idx = model_2.predict([[score] + arr])[0]
            
        elif round == 'turn':
            action_idx = model_3.predict([[score] + arr])[0]

        else:
            action_idx = model_4.predict([[score] + arr])[0]
            
        #print(round, action_idx)
        
        chip = chips_arr[action_idx] * main_pot + amount
        #print(chip, main_pot, amount)
        #print(valid_actions[2]["amount"])
        if action_idx > 1 and (min_raise == -1 and money == -1):
            return action, amount # all-in
        elif chip < min_raise:
            return action, amount
            #print("all-in", money)
            
        if action_idx == 0:
            chip = 0 # fold
        
        return acts_arr[action_idx], chip  # action returned here is sent to the poker engine

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
    return CallPlayer()