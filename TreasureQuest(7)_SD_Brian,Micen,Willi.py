import random
import time
import os

# =============================================================================
# 👤 MAHASISWA A: BAGIAN LINKED LIST (Papan Permainan)
# =============================================================================
class Node:
    def __init__(self, position, event_type=None, description=None):
        self.position = position
        self.event_type = event_type # STATIC, STACK, atau QUEUE
        self.description = description
        self.next = None

class LinkedListBoard:
    def __init__(self, size):
        self.head = None
        self.size = size
        self._build_board()

    def _build_board(self):
        events = {
            # --- ZONE A: STATIC EVENTS ---
            3: ("STATIC", "MAJU 2"),
            6: ("STATIC", "MUNDUR 3"),
            15: ("STATIC", "UNDO"),
            18: ("STATIC", "SKIP"),

            # --- ZONE B: STACK EVENTS (LOOT) ---
            4: ("STACK", "LOOT_BOX"),
            8: ("STACK", "LOOT_BOX"),
            12: ("STACK", "LOOT_BOX"),
            
            # --- ZONE C: QUEUE EVENTS (CARD) ---
            5: ("QUEUE", "MYSTERY_CARD"),
            10: ("QUEUE", "MYSTERY_CARD"),
            14: ("QUEUE", "MYSTERY_CARD"),
        }
        
        prev = None
        for i in range(1, self.size + 1):
            if i in events:
                etype, desc = events[i]
                node = Node(i, etype, desc)
            else:
                node = Node(i)
            
            if self.head is None:
                self.head = node
            else:
                prev.next = node
            prev = node

    def get_node(self, position):
        current = self.head
        while current:
            if current.position == position:
                return current
            current = current.next
        return None

    def display_board(self, players):
        print("\n" + "="*65)
        print("🗺  PETA FINAL (Linked List + Stack Loot + Queue Deck)")
        print("="*65)
        current = self.head
        row = ""
        count = 0
        
        while current:
            count += 1
            # Visualisasi
            symbol = "[_]"
            if current.event_type == "STATIC": symbol = "[❗]"
            elif current.event_type == "STACK": symbol = "[🎒]"
            elif current.event_type == "QUEUE": symbol = "[🃏]"
            elif current.position == 20: symbol = "[🏁]"
            
            occupant = ""
            for p_name, p_data in players.items():
                if p_data["pos"] == current.position:
                    occupant += p_data["icon"]
            
            row += f"{current.position:02d}{symbol}{occupant:<2} -> "
            
            if count % 5 == 0:
                print(row)
                print("      ⬇")
                row = ""
            current = current.next
        print("    [FINISH]")


# =============================================================================
# 👤 MAHASISWA B: BAGIAN STACK (Inventory & Undo)
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
# 👤 MAHASISWA C: BAGIAN QUEUE (Giliran & Deck Kartu)
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
class Game:
    def __init__(self, player_names):
        self.board = LinkedListBoard(20)
        self.turn_queue = Queue(player_names)
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

    def clear_screen(self):
        # os.system('cls' if os.name == 'nt' else 'clear')
        pass 

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

        p_data = self.players[player]
        print(f"\n🎲 GILIRAN: {player} {p_data['icon']}")
        
        # Logic B: Item
        self.manage_inventory_stack(player)

        input("   [ENTER] Lempar dadu...")
        dice = random.randint(1, 6)
        print(f"   🎲 Dadu: {dice}")

        p_data["history"].push(p_data["pos"])

        new_pos = min(20, p_data["pos"] + dice)
        p_data["pos"] = new_pos
        print(f"   🏃 Maju ke kotak {new_pos}")

        # --- CEK NODE (REKURSIF) ---
        self.check_node_event(player, new_pos)
        
        # Cek Menang
        if self.players[player]["pos"] >= 20:
             print(f"\n🏆🏆🏆 {player} MENANG! 🏆🏆🏆")
             self.game_finished = True
             return

        self.turn_queue.rotate()

    def check_node_event(self, player, pos):
        # Base Case: Posisi di luar papan atau null
        if pos > 20 or pos < 1: return
        
        node = self.board.get_node(pos)
        if not node or not node.event_type:
            return

        etype = node.event_type
        desc = node.description
        
        # 1. EVENT STATIS
        if etype == "STATIC":
            print(f"   ⚠ EVENT PAPAN: {desc}")
            if desc == "MAJU 2":
                new_pos = min(20, pos + 2)
                self.players[player]["pos"] = new_pos
                print(f"   -> 🚀 Meluncur ke kotak {new_pos}")
                self.check_node_event(player, new_pos) # <--- REKURSI

            elif desc == "MUNDUR 3":
                if self.players[player]["shield"]:
                    print("     🛡 Shield aktif! Batal mundur.")
                    self.players[player]["shield"] = False
                else:
                    new_pos = max(1, pos - 3)
                    self.players[player]["pos"] = new_pos
                    print(f"   -> 🔻 Tergelincir ke kotak {new_pos}")
                    self.check_node_event(player, new_pos) # <--- REKURSI

            elif desc == "UNDO":
                last = self.players[player]["history"].pop()
                if last: 
                    self.players[player]["pos"] = last
                    print(f"   -> 🔙 UNDO! Kembali ke posisi {last}")
                    self.check_node_event(player, last) # <--- REKURSI
                else:
                    print("   -> History kosong. Tetap di posisi.")

            elif desc == "SKIP":
                self.skipped.add(player)
                print(f"   -> 🚫 {player} akan di-SKIP 1x di putaran selanjutnya.") 

        # 2. EVENT STACK
        elif etype == "STACK":
            print(f"   🎒 {desc}: Menemukan Item Box!")
            item = random.choice(["Shield", "Boost", "Swap"])
            self.players[player]["inventory"].push(item)
            print(f"   -> **{item}** disimpan ke Stack Inventory.")

        # 3. EVENT QUEUE
        elif etype == "QUEUE":
            print(f"   🃏 {desc}: Mengambil Kartu Nasib!")
            card = self.card_deck.rotate()
            print(f"   -> 📜 {card}")
            
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
                    target_p = random.choice(others)
                    self.players[player]["pos"], self.players[target_p]["pos"] = \
                    self.players[target_p]["pos"], self.players[player]["pos"]
                    print(f"   -> 🔄 Tukar posisi dengan {target_p} (Kamu di {self.players[player]['pos']})")
                    # Cek event di posisi baru
                    self.check_node_event(player, self.players[player]["pos"]) # <--- REKURSI
            elif "LAGI" in card:
                print("   -> LEMPAR DADU LAGI!")
                # Trik: Ambil pemain dari belakang queue, taruh depan lagi
                curr = self.turn_queue.data.pop()
                self.turn_queue.data.insert(0, curr)
                
            if pos_changed:
                print(f"   -> Pindah ke {target_pos}")
                self.players[player]["pos"] = target_pos
                self.check_node_event(player, target_pos) # <--- REKURSI

    def manage_inventory_stack(self, player):
        stack = self.players[player]["inventory"]
        if not stack.is_empty():
            top_item = stack.peek()
            print(f"   🎒 Tas (Stack Teratas): [{top_item}]")
            
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
                    # Cek event setelah boost
                    self.check_node_event(player, self.players[player]["pos"])

                elif used == "Shield":
                    self.players[player]["shield"] = True
                    print("      -> Shield ON! Akan melindungi dari 1x event mundur.")

                elif used == "Swap":
                    others = [p for p in self.players if p != player]
                    if others:
                        target = random.choice(others)
                        self.players[player]["pos"], self.players[target]["pos"] = \
                        self.players[target]["pos"], self.players[player]["pos"]
                        print(f"      -> Tukar posisi dengan {target}! Posisi: {self.players[player]['pos']}")
                        # Cek event setelah swap
                        self.check_node_event(player, self.players[player]["pos"])
                    else:
                        print("      -> Tidak ada pemain lain untuk ditukar.")
            else:
                print("      -> Item disimpan.")

# =============================================================================
# 🚀 MAIN PROGRAM
# =============================================================================
if __name__ == "__main__":
    game = Game(["Brian", "Micen", "William"])
    
    while not game.game_finished:
        #game.clear_screen()
        game.board.display_board(game.players)
        game.play_turn()
        time.sleep(1) 
    time.sleep(2)
    print("\nPermainan Selesai.")