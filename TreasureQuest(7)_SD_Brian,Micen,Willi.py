import random
import time
import os

# =============================================================================
#   MAHASISWA A: BAGIAN LINKED LIST (Papan Permainan)
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
            # ZONE A: STATIC EVENTS (Efek Tetap)
            3: ("STATIC", "MAJU 2"),
            6: ("STATIC", "MUNDUR 3"),
            15: ("STATIC", "UNDO"),
            18: ("STATIC", "SKIP"), # <-- Logic SKIP diperbaiki di Game Controller

            # ZONE B: STACK EVENTS (Loot Box / Inventory)
            4: ("STACK", "LOOT_BOX"),
            12: ("STACK", "LOOT_BOX"),

            # ZONE C: QUEUE EVENTS (Kartu Nasib)
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
        print("🗺️  PETA FINAL (Linked List + Stack Loot + Queue Deck)")
        print("="*65)
        current = self.head
        row = ""
        count = 0

        while current:
            count += 1
            symbol = "[_]"
            # Icon Map
            if current.event_type == "STATIC": symbol = "[❗️]"
            elif current.event_type == "STACK": symbol = "[🎒]"
            elif current.event_type == "QUEUE": symbol = "[🃰]"
            elif current.position == 20: symbol = "[🏁]"

            occupant = ""
            for p_name, p_data in players.items():
                if p_data["pos"] == current.position:
                    occupant += p_data["icon"]

            row += f"{current.position:02d}{symbol}{occupant:<2} -> "

            if count % 5 == 0:
                print(row)
                print("       ⬇️")
                row = ""
            current = current.next
        print("    [FINISH]")


# =============================================================================
#   MAHASISWA B: BAGIAN STACK (Inventory & Undo)
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
#   MAHASISWA C: BAGIAN QUEUE (Giliran & Deck Kartu)
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
# 🎮 GAME CONTROLLER
# =============================================================================
class Game:
    def __init__(self, player_names):
        # SETUP A
        self.board = LinkedListBoard(20)

        # SETUP C
        self.turn_queue = Queue(player_names)
        self.card_deck = Queue([
            "KARTU: MAJU 3 LANGKAH",
            "KARTU: MUNDUR 2 LANGKAH",
            "KARTU: ZONK (KOSONG)",
            "KARTU: TUKAR POSISI",
            "KARTU: LEMPAR DADU LAGI"
        ])

        # SETUP B
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

    #def clear_screen(self):
        #os.system('cls' if os.name == 'nt' else 'clear')

    def play_turn(self):
        if self.game_finished: return

        # --- LOGIC C (Giliran) ---
        player = self.turn_queue.front()

        # 1. Cek apakah pemain sedang di-SKIP?
        if player in self.skipped:
            print(f"\n⛔ {player} sedang di-SKIP giliran ini.")
            self.skipped.remove(player) # Hapus dari daftar skip
            self.turn_queue.rotate()    # Langsung ganti giliran
            time.sleep(1.5)
            return

        p_data = self.players[player]
        print(f"\n🎲 GILIRAN: {player} {p_data['icon']}")

        # --- LOGIC B (Inventory) ---
        self.manage_inventory_stack(player)

        input("   [ENTER] Lempar dadu...")
        dice = random.randint(1, 6)
        print(f"   🎲 Dadu: {dice}")

        p_data["history"].push(p_data["pos"])

        new_pos = min(20, p_data["pos"] + dice)
        p_data["pos"] = new_pos
        print(f"   🏃 Maju ke kotak {new_pos}")

        # --- CEK EVENT ---
        self.check_node_event(player, new_pos)

        # Cek Menang
        if p_data["pos"] >= 20:
            print(f"\n🏆🏆🏆 {player} MENANG! 🏆🏆🏆")
            self.game_finished = True
            return

        self.turn_queue.rotate()

    def check_node_event(self, player, pos):
        node = self.board.get_node(pos)
        if not node or not node.event_type:
            return

        etype = node.event_type
        desc = node.description

        # 1. EVENT STATIS (Tugas A)
        if etype == "STATIC":
            print(f"   ⚠️ EVENT PAPAN: {desc}")
            if desc == "MAJU 2":
                self.players[player]["pos"] = min(20, pos + 2)

            elif desc == "MUNDUR 3":
                if self.players[player]["shield"]:
                    print("      🛡️ Shield aktif! Batal mundur.")
                    self.players[player]["shield"] = False
                else:
                    self.players[player]["pos"] = max(1, pos - 3)

            elif desc == "UNDO":
                last = self.players[player]["history"].pop()
                if last: self.players[player]["pos"] = last

            elif desc == "SKIP":
                # ✅ FIX: Logic Skip yang benar
                print(f"      🚫 {player} Terperangkap! Harus istirahat 1 putaran.")
                self.skipped.add(player)

        # 2. EVENT STACK (Tugas B)
        elif etype == "STACK":
            print(f"   🎒 {desc}: Menemukan Item Box!")
            item = random.choice(["Shield", "Boost"])
            self.players[player]["inventory"].push(item)
            print(f"      -> {item} disimpan ke Stack Inventory.")

        # 3. EVENT QUEUE (Tugas C)
        elif etype == "QUEUE":
            print(f"   🃰 {desc}: Mengambil Kartu Nasib!")
            card = self.card_deck.rotate()
            print(f"      📜 {card}")

            if "MAJU" in card:
                self.players[player]["pos"] = min(20, self.players[player]["pos"] + 3)
            elif "MUNDUR" in card:
                self.players[player]["pos"] = max(1, self.players[player]["pos"] - 2)
            elif "TUKAR" in card:
                others = [p for p in self.players if p != player]
                if others:
                    target = random.choice(others)
                    
                    pos_me = self.players[player]["pos"]
                    pos_target= self.players[target]["pos"]

                    self.players[player]["pos"] ,self.players[target]["pos"] = self.players[target]["pos"], self.players[player]["pos"]
                    print(f"Tukar posisi dengan {target}!")
                    print(f"      -> {player} ke kotak {self.players[player]['pos']}, {target} ke kotak {self.players[target]['pos']}")

    def manage_inventory_stack(self, player):
        stack = self.players[player]["inventory"]
        if not stack.is_empty():
            top_item = stack.peek()
            print(f"   🎒 Tas (Stack Teratas): [{top_item}]")
            choice = input("      Gunakan Item? (y/n): ").lower()
            if choice == 'y':
                used = stack.pop()
                print(f"      ✨ Menggunakan {used}!")

                if used == "Boost":
                    self.players[player]["pos"] = min(20, self.players[player]["pos"] + 3)
                    print("      -> Maju 3 langkah!")
                elif used == "Shield":
                    self.players[player]["shield"] = True
                    print("      -> Shield ON!")
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
        time.sleep(2)