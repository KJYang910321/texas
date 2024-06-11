import json
from game.game import setup_config, start_poker
from agents.call_player import setup_ai as call_ai
from agents.random_player import setup_ai as random_ai
from agents.console_player import setup_ai as console_ai
from agents.my_player import setup_ai as my_ai
from agents.classify_player import setup_ai as classify_ai
from agents.my_player_v2 import setup_ai as my_player_v2_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai

'''
from baseline0 import setup_ai as baseline0_ai
from baseline1 import setup_ai as baseline1_ai
from baseline2 import setup_ai as baseline2_ai
from baseline3 import setup_ai as baseline3_ai
from baseline4 import setup_ai as baseline4_ai
from baseline5 import setup_ai as baseline5_ai
from baseline6 import setup_ai as baseline6_ai
from baseline7 import setup_ai as baseline7_ai
'''

config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=5)
config.register_player(name="baseline_1", algorithm=baseline2_ai())
#config.register_player(name="p2", algorithm=console_ai())
#config.register_player(name="testing_my", algorithm=my_ai())
#config.register_player(name="random", algorithm=random_ai())

## Play in interactive mode if uncomment
config.register_player(name="my_v2", algorithm=my_player_v2_ai())
game_result = start_poker(config, verbose=1)

print(json.dumps(game_result, indent=4))
