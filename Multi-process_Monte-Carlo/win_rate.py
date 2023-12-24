import time
import random
import numpy as np
import itertools as iter
import threading
from multiprocessing import Process, Pipe 
from collections import Counter

g_runs = 0 
g_wins = 0
g_chop = 0 
g_lock = threading.Lock()

class MonteCarlo:

    def __init__(self) -> None:
        self.values = list(range(2,15)) # From 2 to 14
        self.suites = "CDHS"
        self.mapping_table = { 'A' : 14, 'K' : 13, 'Q' : 12, 'J' : 11, 'T' : 10 }

        # all straight set
        self.ranks = list(range(1,15))
        self.list_straight = [ [ self.ranks[j] for j in range(i, i+5) ] for i in range(len(self.ranks) - 4)]

        self.runs = 0
        self.wins = 0
        self.chop = 0
        self.mode = 0

    def GetRate(self) -> tuple:
        """
        ( "Win Rate w/o Chop", "Win Rate w/  Chop", "Chop Rate" )
        """
        return (
            round(self.wins*100/float(self.runs-self.chop), 2),
            round(self.wins*100/float(self.runs), 2),
            round(self.chop*100/float(self.runs), 2),
        )

    def Convert(self, cards) -> set:
        """
            Convert alphabet to rank
        """
        tmp = set()
        for i in cards:
            value = self.mapping_table.get(i[0]) if self.mapping_table.get(i[0]) != None else int(i[0])
            tmp.add( (value, i[1]) ) 
        return tmp

    def IsStraight(self, set_values) -> int:
        """
            Check if the set is straight
        \n    Yes -> Biggest rank in the straight 
        \n    No  -> 0 
        """
        for i in self.list_straight[::-1]:
            if set(i).issubset(set_values):
                return i[-1]
        return 0

    def GetScore(self, combination) -> list:
        """
        8: Straight flush
        7: 4 of a kind
        6: Full house
        5: Flush
        4: Straight
        3: 3 of a kind
        2: 2 pairs
        1: pair
        0: high card
        """
        score = [0, 0]

        count_cards = sorted(Counter(rank[0] for rank in combination).items(), key=lambda pair: (-pair[1], -pair[0]))
        
        list_ranks   = [ i[0] for i in count_cards ] # rank of cards sorted by amount of cards 
        count_values = [ i[1] for i in count_cards ] # amount of cards 

        is_flush = True if max( Counter(s[1] for s in combination).values() ) >= 5 else False
        is_straight = self.IsStraight(set(list_ranks)) # if straight return biggest rank in the straight ,if not return 0

        # 4 of a kind
        if count_values[0] == 4:
            score = [7, list_ranks[:2]]
        # full house
        elif count_values[0:2] == [3, 2] or count_values[0:2] == [3, 3]:
            score = [6, list_ranks[:2]]
        # 3 of a kind
        elif count_values[0:2] == [3, 1]:
            score = [3, list_ranks[:3]]
        # 2 pairs
        elif count_values[0:2] == [2, 2]:
            score = [2, list_ranks[:3]]
        # pair
        elif count_values[0] == 2:
            score = [1, list_ranks[:4]]
        # high card
        else:
            score = [0, list_ranks[:5]]

        if is_flush:
            flushSuit = Counter(s[1] for s in combination).most_common(1)[0][0] # get the suit of the flush
            flushHand = [h for h in combination if flushSuit in h] # [(13, 'S'), (11, 'S'), (9, 'S'), (10, 'S'), (12, 'S')]
            flushRank = [i[0] for i in flushHand]
            is_straight_flush = self.IsStraight(set(flushRank)) # if straight return biggest rank in the straight ,if not return 0

            if is_straight_flush > 0:
                score = [8, is_straight_flush]
            else:
                score = [5, sorted(flushRank, reverse=True)[:5] ]
        elif is_straight > 0:
            score = [4, is_straight]

        return score
    
    def Run(self, my_hands, op_hands, current_table_cards, PlayerAmount, maxRuns=100000, maxSecs=10, conn=0) -> None:
        timeout_start = time.time() 
        for _ in range(maxRuns):
            self.runs += 1
            
            all_cards = set(iter.product(self.values, self.suites))
        
            players_hands = []
            players_hands.append( self.Convert(my_hands) )
            all_cards -= my_hands

            table_cards = self.Convert(current_table_cards) | set(random.sample([*all_cards], k=5-len(current_table_cards)))
            all_cards -= table_cards

            if len(op_hands) > 0:
                players_hands.append( self.Convert(op_hands) )
                all_cards -= op_hands
            else:
                hands = set(random.sample([*all_cards], k=2))
                players_hands.append(hands)
                all_cards -= hands

            scores = [(i, self.GetScore(player_hands | table_cards)) for i, player_hands in enumerate(players_hands)]  
            winner = sorted(scores, key=lambda x: x[1], reverse=True)
            if  winner[0][1] == winner[1][1] and winner[0][0] == 0:
                self.chop += 1
            elif winner[0][0] == 0:
                self.wins += 1
            if time.time() > timeout_start + maxSecs:
                break
        if self.mode == 1:
            conn.send([self.chop, self.wins, self.runs])
            conn.close()
            

def Threading_Run(player1_hand, player2_hand, sim_times):
    thread_num = 10
    thread_sim_time = int(sim_times / thread_num) 
    current_table_cards = {}
    player_count = 2
    process_list = []
    process_sim_list = []
    pipe_list = []
    start_time = time.time()
    for i in range(thread_num):
        temp = MonteCarlo()
        process_sim_list.append(temp)
        temp.mode = 1 
        parent_conn, child_conn = Pipe()
        pipe_list.append(parent_conn)
        p = Process(target=temp.Run, args=(player1_hand, player2_hand, current_table_cards, player_count, thread_sim_time, 20, child_conn,))    
        process_list.append(p)
        p.start()
        # t = threading.Thread(target=temp.Run, args=(player1_hand, player2_hand, current_table_cards, player_count, thread_sim_time, 20,))
        # thread_list.append(t)
    for p in process_list:
        p.join()
    print("--- %s thread mode seconds ---" % (time.time() - start_time))
    runs = 0
    wins = 0
    chop = 0
    for _pipe in pipe_list:
        data = _pipe.recv()
        chop = chop + data[0]
        wins = wins + data[1]
        runs = runs + data[2]
    return (runs, wins, chop)
        
            

if __name__ == '__main__':
    Simulation = MonteCarlo()
    PlayerAmount = 2
    my_hands = {('Q', 'S'), ('Q', 'D')}
    op_hands = {}
    current_table_cards = {}

    start_time = time.time()
    Simulation.Run(my_hands, op_hands, current_table_cards, PlayerAmount, 200000, 20, 0)
    print("--- %s normal mode seconds ---" % (time.time() - start_time))

    total = Threading_Run(my_hands, op_hands, 200000)

    rate = Simulation.GetRate()
    print("Normal Mode:")
    print(f"Win Rate w/o Chop : {rate[0]}")
    print(f"Win Rate w/  Chop : {rate[1]}")
    print(f"Chop Rate         : {rate[2]}")
    Simulation.runs = total[0]
    Simulation.wins = total[1]
    Simulation.chop = total[2]
    rate = Simulation.GetRate()
    print("Thread Mode (with 10 thread):")
    print(f"Win Rate w/o Chop : {rate[0]}")
    print(f"Win Rate w/  Chop : {rate[1]}")
    print(f"Chop Rate         : {rate[2]}")