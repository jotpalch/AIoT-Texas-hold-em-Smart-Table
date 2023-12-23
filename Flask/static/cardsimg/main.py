import os

# mapping_table = { "ace": "A", "10": "T", "jack": "J", "queen": "Q", "king": "K" }

# for i in os.listdir(os.getcwd()):
#     if "of" in i:
#         print(i)
#         name = i.split("_")
#         rank = mapping_table.get(name[0]) if mapping_table.get(name[0]) != None else name[0]
#         if rank+name[2][0].upper()+".png" not in os.listdir(os.getcwd()):
#             os.rename(i,rank+name[2][0].upper()+".png")
#         # print(i,rank+name[2][0].upper())
#     # break
            
# mapping = ['10 Hearts', '10 Spades', '10 Trefoils', '2 Diamonds', '2 Hearts', '2 Spades', '2 Trefoils', '3 Diamonds', '3 Hearts', '3 Spades', '3 Trefoils', '4 Diamonds', '4 Hearts', '4 Spades', '4 Trefoils', '5 Diamonds', '5 Hearts', '5 Spades', '5 Trefoils', "xxx xxxxx", "10 Diamonds", '6 Diamonds', '6 Hearts', '6 Spades', '6 Trefoils', '7 Diamonds', '7 Hearts', '7 Spades', '7 Trefoils', '8 Diamonds', '8 Hearts', '8 Spades', '8 Trefoils', '9 Diamonds', '9 Hearts', '9 Spades', '9 Trefoils', 'A Diamonds', 'A Hearts', 'A Spades', 'A Trefoils', 'J Diamonds', 'J Hearts', 'J Spades', 'J Trefoils', 'K Diamonds', 'K Hearts', 'K Spades', 'K Trefoils', 'Q Diamonds', 'Q Hearts', 'Q Spades', 'Q Trefoils']

# m = []

# for i in mapping:
#     s = i.split(" ")
#     m.append( (s[0]+s[1][0]).replace("T","C") )

# print(m)

import pyautogui
import time 


pos = [
    [6671, 860],
    [429,  685]
]

for i in range(10000000000000):
    
    for i, j in pos:
        time.sleep(8)
        pyautogui.moveTo(i, j)
        pyautogui.click()
        time.sleep(2)
        pyautogui.click()
        # print(pyautogui.position())
