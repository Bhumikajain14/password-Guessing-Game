import tkinter as tk
from tkinter import messagebox
import random
import winsound
import os
import threading

# ---------------- DATA ----------------
easy_words = ["apple", "train", "tiger", "money", "india"]
medium_words = ["python", "bottle", "monkey", "laptop", "planet"]
hard_words = ["elephant", "diamond", "umbrella", "computer", "mountain"]

secret = ""
attempts = 0
max_attempts = 5
time_left = 50
game_active = False
username = ""
bg_music_thread = None
STOP_MUSIC = False

SCORE_FILE = "scores.txt"

# ---------------- SOUND ----------------
def play_sound(file):
    if os.path.exists(file):
        winsound.PlaySound(file, winsound.SND_FILENAME | winsound.SND_ASYNC)

def welcome_sound():
    winsound.Beep(600,200)
    winsound.Beep(800,200)

def bg_music_loop():
    global STOP_MUSIC
    while not STOP_MUSIC:
        if os.path.exists("bg_music.wav"):
            winsound.PlaySound("bg_music.wav", winsound.SND_FILENAME)
        else:
            break

def win_sound():
    winsound.Beep(1200,300)
    winsound.Beep(1400,300)

def lose_sound():
    winsound.Beep(400,600)

# ---------------- UTIL ----------------
def show_frame(frame):
    frame.tkraise()

def save_score(name, score):
    scores = get_top_scores()
    scores.append((name,score))
    scores.sort(key=lambda x:x[1],reverse=True)
    scores = scores[:5]  # keep top 5
    with open(SCORE_FILE,"w") as f:
        for n,s in scores:
            f.write(f"{n}:{s}\n")

def get_top_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    with open(SCORE_FILE) as f:
        scores=[]
        for line in f:
            try:
                n,s=line.strip().split(":")
                scores.append((n,int(s)))
            except: pass
        scores.sort(key=lambda x:x[1], reverse=True)
        return scores[:5]

# ---------------- HINT LETTERS ----------------
def generate_hint_letters(word):
    letters = list(word)
    random.shuffle(letters)
    return "  ".join(letters)

# ---------------- GAME ----------------
def start_game():
    global secret, attempts, time_left, game_active, username, bg_music_thread, STOP_MUSIC

    username = name_entry.get().strip()
    if not username:
        messagebox.showwarning("Name required","Enter your name")
        return

    level = level_var.get()
    if not level:
        messagebox.showwarning("Level required","Select difficulty")
        return

    show_frame(game_frame)

    secret = random.choice(
        easy_words if level=="Easy" else
        medium_words if level=="Medium" else hard_words
    )

    attempts = 0
    time_left = 50
    game_active = True
    STOP_MUSIC = False

    hint_letters = generate_hint_letters(secret)
    hint_label.config(text=f"Hint: {len(secret)} letters. Letters: {hint_letters}")
    attempts_label.config(text="Attempts: 0 / 5")
    timer_label.config(text=f"⏳ {time_left}s")
    user_label.config(text=f"Player: {username}")
    guess_entry.delete(0, tk.END)
    result_label.config(text="")

    welcome_sound()

    # start background music in separate thread
    bg_music_thread = threading.Thread(target=bg_music_loop,daemon=True)
    bg_music_thread.start()

    countdown()

def check_guess():
    global attempts, game_active, STOP_MUSIC

    if not game_active:
        return

    guess = guess_entry.get().lower().strip()
    if not guess: return

    attempts += 1
    attempts_label.config(text=f"Attempts: {attempts} / 5")

    if guess == secret:
        game_active=False
        STOP_MUSIC = True
        win_sound()
        save_score(username, time_left)
        update_leaderboard()
        end_msg.config(text=f"🎉 YOU WON!\nScore: {time_left}", fg="#00ff99")
        show_frame(end_frame)
        return

    if attempts >= max_attempts:
        game_active=False
        STOP_MUSIC = True
        lose_sound()
        save_score(username,0)
        update_leaderboard()
        end_msg.config(text=f"❌ YOU LOST\nAnswer: {secret}", fg="red")
        show_frame(end_frame)
        return

    result_label.config(text=f"Try again! ❌")
    guess_entry.delete(0, tk.END)

def countdown():
    global time_left, game_active, STOP_MUSIC
    if not game_active: return
    if time_left > 0:
        timer_label.config(text=f"⏳ {time_left}s")
        time_left -= 1
        root.after(1000,countdown)
    else:
        game_active=False
        STOP_MUSIC = True
        lose_sound()
        save_score(username,0)
        update_leaderboard()
        end_msg.config(text=f"⏰ TIME UP\nAnswer: {secret}", fg="red")
        show_frame(end_frame)

def restart():
    show_frame(start_frame)

def update_leaderboard():
    scores = get_top_scores()
    board_text=""
    for idx,(n,s) in enumerate(scores,1):
        board_text += f"{idx}. {n}: {s}\n"
    leaderboard_label.config(text=board_text)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Password Guessing Game")
root.geometry("520x650")
root.config(bg="#0f172a")

# ---------------- FRAMES ----------------
start_frame = tk.Frame(root, bg="#0f172a")
game_frame = tk.Frame(root, bg="#0f172a")
end_frame = tk.Frame(root, bg="#0f172a")
for f in (start_frame, game_frame, end_frame): f.place(relwidth=1,relheight=1)

def card(parent):
    frame = tk.Frame(parent,bg="#111827")
    frame.place(relx=0.5,rely=0.5,anchor="center", width=450,height=500)
    return frame

# ---------------- PAGE 1 ----------------
c1 = card(start_frame)
tk.Label(c1,text="🔐 PASSWORD GAME", font=("Segoe UI",20,"bold"), bg="#111827", fg="#38bdf8").pack(pady=25)
name_entry = tk.Entry(c1,font=("Segoe UI",14),justify="center")
name_entry.pack(pady=10)
name_entry.insert(0,"Enter your name")
level_var = tk.StringVar()
tk.OptionMenu(c1,level_var,"Easy","Medium","Hard").pack(pady=10)
tk.Button(c1,text="START GAME",command=start_game, bg="#22c55e", fg="white",
          font=("Segoe UI",14,"bold"), width=18).pack(pady=20)

# ---------------- PAGE 2 ----------------
c2 = card(game_frame)
user_label = tk.Label(c2,text="Player:", bg="#111827", fg="white")
user_label.pack(pady=5)
timer_label = tk.Label(c2,text=f"⏳ {time_left}s", bg="#111827", fg="red")
timer_label.pack()
hint_label = tk.Label(c2,text="Hint letters:", bg="#111827", fg="yellow")
hint_label.pack(pady=10)
guess_entry = tk.Entry(c2,font=("Segoe UI",16), justify="center")
guess_entry.pack(pady=10)
tk.Button(c2,text="SUBMIT", command=check_guess, bg="#3b82f6", fg="white", font=("Segoe UI",12,"bold"), width=15).pack(pady=10)
attempts_label = tk.Label(c2,text="Attempts: 0 / 5", bg="#111827", fg="white")
attempts_label.pack()
result_label = tk.Label(c2,text="", font=("Courier",16), bg="#111827", fg="#00ff99")
result_label.pack(pady=10)

# ---------------- PAGE 3 ----------------
c3 = card(end_frame)
end_msg = tk.Label(c3,text="", font=("Segoe UI",20,"bold"), bg="#111827")
end_msg.pack(pady=20)
tk.Label(c3,text="🏆 LEADERBOARD 🏆", font=("Segoe UI",16,"bold"), bg="#111827", fg="#facc15").pack()
leaderboard_label = tk.Label(c3,text="", font=("Segoe UI",14), bg="#111827", fg="white")
leaderboard_label.pack(pady=10)
tk.Button(c3,text="PLAY AGAIN", command=restart, bg="#f59e0b", fg="black", font=("Segoe UI",13,"bold"), width=16).pack(pady=20)

# ---------------- NAME ----------------
tk.Label(root, text="Made by Bhumika Jain 💙", bg="#0f172a", fg="gray", font=("Segoe UI",9)).place(relx=0.98, rely=0.98, anchor="se")

# ---------------- START ----------------
root.after(500,welcome_sound)
show_frame(start_frame)
root.mainloop()
