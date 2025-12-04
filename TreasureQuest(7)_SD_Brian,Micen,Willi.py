import random
import time
import os

# =============================================================================
# MICEN: BAGIAN LINKED LIST (Papan Permainan)
# =============================================================================
class Node:
    def __init__(self, position, event_type=None, description=None):
        self.position = position
        self.event_type = event_type # NODE, STACK, atau QUEUE
        self.description = description
        self.next = None

class LinkedListBoard:
    def __init__(self, size):
        self.head = None
        self.size = size
        self._build_board()

    def _build_board(self):
        curr = None
        for i in range(1, self.size + 1):
            # Default node kosong
            new_node = Node(i)
            
            # --- Zone A: Papan ---
            if i == 3:
                new_node.event_type = "NODE"
                new_node.description = "MAJU 2" 
            elif i == 6:
                new_node.event_type = "NODE"
                new_node.description = "MUNDUR 3"
            elif i == 15:
                new_node.event_type = "NODE"
                new_node.description = "UNDO"
            elif i == 18:
                new_node.event_type = "NODE"
                new_node.description = "SKIP"
            
            # --- Zone B: Item (Stack) ---
            elif i in [4, 8, 12]:
                new_node.event_type = "POWERUPS"
                new_node.description = "LOOT_BOX"
            
            # --- Zone C: Kartu (Queue) ---
            elif i in [7, 10, 14]: 
                new_node.event_type = "CARDS"
                new_node.description = "MYSTERY_CARD"

            # Nyambungin node (Linked List logic)
            if self.head is None:
                self.head = new_node
                curr = new_node
            else:
                curr.next = new_node
                curr = new_node

    def get_node(self, position):
        curr = self.head
        while curr:
            if curr.position == position:
                return curr
            curr = curr.next
        return None

    def display_board(self, players):
        print("\n" + "="*65)
        print("TREASURE QUEST MAP")
        print("="*65)
        current = self.head
        row = ""
        count = 0
        
        while current:
            count += 1
            symbol = "[_]"
            if current.event_type == "NODE": 
                symbol = "[❓]"
            elif current.event_type == "POWERUPS": 
                symbol = "[⬆️ ]"
            elif current.event_type == "CARDS": 
                symbol = "[🃏]"
            elif current.position == 20: 
                symbol = "[🏁]"
            
            occupant = ""
            for player_name, player_data in players.items():
                if player_data["pos"] == current.position:
                    occupant += player_data["icon"]
            
            row += f"{current.position:02d}{symbol}{occupant:<2} -> "
            
            if count % 5 == 0:
                print(row)
                print("      ⬇")
                row = ""
            current = current.next
        print("    [FINISH]")

# =============================================================================
# WILLI: BAGIAN STACK (Inventory & Undo)
# =============================================================================
class Stack:
    def __init__(self):
        self.data = []

    def push(self, item):
        self.data.append(item)

    def pop(self):
        if not self.is_empty():
            return self.data.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.data[-1]
        return "Kosong"

    def is_empty(self):
        return len(self.data) == 0

# =============================================================================
# BRIAN: BAGIAN QUEUE (Giliran & Deck Kartu)
# =============================================================================
class Queue:
    def __init__(self, items=None):
        self.data = list(items) if items else []

    def enqueue(self, item):
        self.data.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.data.pop(0)
        return None

    def rotate(self):
        if not self.is_empty():
            item = self.data.pop(0)
            self.data.append(item)
            return item
        return None

    def front(self):
        return self.data[0] if not self.is_empty() else None

    def is_empty(self):
        return len(self.data) == 0

# =============================================================================
# 🎮 GAME CONTROLLER (LOGIC GABUNGAN)
# =============================================================================
# MICEN, WILLI, BRIAN
class Game:
    def __init__(self, player_names): #MICEN
        self.board = LinkedListBoard(20)
        self.turn_queue = Queue(player_names) #BRIAN
        self.card_deck = Queue([
            "KARTU: MAJU 3 LANGKAH",
            "KARTU: MUNDUR 2 LANGKAH",
            "KARTU: ZONK (KOSONG)",
            "KARTU: TUKAR POSISI",
            "KARTU: LEMPAR DADU LAGI"
        ])
        
        self.players = {}
        icons = ["🔴", "🔵", "🟢"]
        for i, name in enumerate(player_names):
            self.players[name] = {
                "pos": 1,
                "icon": icons[i],
                "history": Stack(),
                "inventory": Stack(),
                "shield": False
            }
        
        self.skipped = set()
        self.game_finished = False 

    def play_turn(self):
        if self.game_finished: return

        player = self.turn_queue.front()
        
        # Cek Skip
        if player in self.skipped:
            print(f"\n⛔ {player} sedang di-SKIP giliran ini.")
            self.skipped.remove(player)
            self.turn_queue.rotate()
            time.sleep(1)
            return

        player_data = self.players[player]
        print(f"\n🎲 GILIRAN: {player} {player_data['icon']}")
        
        # Logic B: Item
        self.manage_inventory(player) #WILLI

        input("   [ENTER] Lempar dadu...")
        dice = random.randint(1, 6)
        print(f"   🎲 Dadu: {dice}")

        player_data["history"].push(player_data["pos"])

        new_pos = min(20, player_data["pos"] + dice)
        player_data["pos"] = new_pos
        print(f"   🏃 Maju ke kotak {new_pos}")

        # --- CEK NODE (REKURSIF) ---
        self.check_node_event(player, new_pos)
        
        # Cek Menang
        if self.players[player]["pos"] >= 20:
             print(f"\n🏆🏆🏆 {player} MENANG! 🏆🏆🏆")
             self.game_finished = True
             return

        self.turn_queue.rotate()

    def check_node_event(self, player, pos): #MICEN
        # Base Case: Posisi di luar papan atau null
        if pos > 20 or pos < 1: 
            return
        
        node = self.board.get_node(pos)
        if not node or not node.event_type:
            return

        eventType = node.event_type
        desc = node.description
        
        # 1. EVENT STATIS
        if eventType == "NODE":
            print(f"   EVENT PAPAN: {desc}")
            if desc == "MAJU 2":
                new_pos = min(20, pos + 2)
                self.players[player]["pos"] = new_pos
                print(f"   -> ⏩ Meluncur ke kotak {new_pos}")
                self.check_node_event(player, new_pos) # <--- REKURSI

            elif desc == "MUNDUR 3":
                if self.players[player]["shield"]:
                    print("     🛡️ Shield sedang aktif! Batal mundur.")
                    self.players[player]["shield"] = False
                else:
                    new_pos = max(1, pos - 3)
                    self.players[player]["pos"] = new_pos
                    print(f"   -> ⏪ Termundur ke kotak {new_pos}")
                    self.check_node_event(player, new_pos) # <--- REKURSI

            elif desc == "UNDO":
                # --- LOGIKA BARU: SHIELD VS UNDO ---
                if self.players[player]["shield"]:
                    print("     🛡️ Shield aktif! Selamat dari efek UNDO.")
                    self.players[player]["shield"] = False 
                else:
                    last_position = self.players[player]["history"].pop()
                    if last_position: 
                        self.players[player]["pos"] = last_position
                        print(f"   -> UNDO! Balik ke posisi {last_position}")
                        self.check_node_event(player, last_position)
                    else:
                        print("   -> History kosong.")

            elif desc == "SKIP":
                self.skipped.add(player)
                print(f"   -> 🚫 {player} akan di-SKIP 1x di giliran selanjutnya.") 

        # 2. EVENT STACK
        elif eventType == "POWERUPS": #WILLI
            print(f"   🎒 {desc}: Menemukan Item!")
            item = random.choice(["Shield", "Boost", "Swap"])
            self.players[player]["inventory"].push(item)
            print(f"   -> **{item}** disimpan ke Inventory.")

        # 3. EVENT QUEUE
        elif eventType == "CARDS": #BRIAN
            print(f"   🃏 {desc}: Mengambil Kartu Misteri!")
            card = self.card_deck.rotate()
            print(f"   -> 🃏 {card}")
            
            target_pos = self.players[player]["pos"]
            pos_changed = False

            if "MAJU" in card:
                target_pos = min(20, target_pos + 3)
                pos_changed = True
            elif "MUNDUR" in card:
                target_pos = max(1, target_pos - 2)
                pos_changed = True
            elif "TUKAR" in card:
                others = [p for p in self.players if p != player]
                if others:
                    target_p = others[0]
                    max_pos = self.players[target_p]["pos"]
                    
                    for musuh in others:
                        pos_musuh = self.players[musuh]["pos"]
                        if pos_musuh > max_pos:
                            max_pos = pos_musuh
                            target_p = musuh

                    if self.players[target_p]["shield"]:
                        print(f"   -> 🚫 TUKAR GAGAL! {target_p} menggunakan SHIELD!")
                        print(f"      (Shield {target_p} hancur)")
                        self.players[target_p]["shield"] = False # Shield hancur
                    else:
                        # Lakukan Swap
                        self.players[player]["pos"], self.players[target_p]["pos"] = \
                        self.players[target_p]["pos"], self.players[player]["pos"]
                        
                        print(f"   -> 🔄 TUKAR! Bertukar dengan ({target_p})!")
                        print(f"      (Kamu ke {self.players[player]['pos']}, Dia ke {self.players[target_p]['pos']})")
                        self.check_node_event(player, self.players[player]["pos"])

            elif "LAGI" in card:
                print("   -> LEMPAR DADU LAGI!")
                # Trik: Ambil pemain dari belakang queue, taruh depan lagi
                curr = self.turn_queue.data.pop()
                self.turn_queue.data.insert(0, curr)
                
            if pos_changed:
                print(f"   -> Pindah ke {target_pos}")
                self.players[player]["pos"] = target_pos
                self.check_node_event(player, target_pos) # <--- REKURSI

    def manage_inventory(self, player): #WILLI
        stack = self.players[player]["inventory"]
        if not stack.is_empty():
            top_item = stack.peek()
            print(f"   🎒 Inventory : [{top_item}]")
            
            try:
                choice = input("      Gunakan Item? (y/n): ").lower()
            except EOFError:
                choice = 'n'

            if choice == 'y':
                used = stack.pop()
                print(f"      ✨ Menggunakan **{used}**!")
                
                if used == "Boost":
                    self.players[player]["pos"] = min(20, self.players[player]["pos"] + 3)
                    print(f"      -> Maju 3 langkah! Posisi: {self.players[player]['pos']}")
                    self.check_node_event(player, self.players[player]["pos"])

                elif used == "Shield":
                    self.players[player]["shield"] = True
                    print("      -> Shield ON! Akan melindungi dari 1x event mundur, undo, dan swap.")

                elif used == "Swap":
                    others = [p for p in self.players if p != player]
                    if others:
                        # --- LOGIKA PENGGANTI LAMBDA (MANUAL) ---
                        target = others[0]
                        max_pos = self.players[target]["pos"]
                        
                        for musuh in others:
                            pos_musuh = self.players[musuh]["pos"]
                            if pos_musuh > max_pos:
                                max_pos = pos_musuh
                                target = musuh
                        
                        if self.players[target]["shield"]:
                            print(f"      -> 🚫 SWAP GAGAL! {target} terlindungi SHIELD!")
                            print(f"         (Shield {target} hancur, Item Swap terpakai)")
                            self.players[target]["shield"] = False # Shield hancur
                        else:
                            # Lakukan Swap
                            self.players[player]["pos"], self.players[target]["pos"] = \
                            self.players[target]["pos"], self.players[player]["pos"]
                            
                            print(f"      -> SWAP! Bertukar dengan ({target})!")
                            print(f"         (Sekarang di posisi: {self.players[player]['pos']})")
                            self.check_node_event(player, self.players[player]["pos"])
                    else:
                        print("      -> Tidak ada lawan.")
            else:
                print("      -> Item disimpan.")

# =============================================================================
# 🚀 MAIN PROGRAM
# =============================================================================
if __name__ == "__main__":
    game = Game(["Brian", "Micen", "William"])
    
    while not game.game_finished:
        game.board.display_board(game.players)
        game.play_turn()
        time.sleep(1) 
    
    print("\nPermainan Selesai.")