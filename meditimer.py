# FULL UPDATED MEDITIMER CODE WITH FIELD LABELS (MEDICINE NAME, DOSAGE, TIME HH:MM, TYPE, DURATION)
# Clean, modern UI + fresh entry page + labels for each field
# ----------------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import time
from datetime import datetime, timedelta
from plyer import notification
import pyttsx3
import re

# ------------------------ ENGINE ------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 160)


def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


# ------------------------ FILES ------------------------
USERS_FILE = "users.json"
REM_FILE = "reminders.json"

# ------------------------ HELPERS ------------------------
TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def normalize_time(t: str):
    """Convert '7:7' or '7:07' -> '07:07'. Return None if invalid."""
    if not t:
        return None
    t = t.strip()
    if ":" not in t:
        return None
    parts = t.split(":")
    if len(parts) != 2:
        return None
    h, m = parts
    if not (h.isdigit() and m.isdigit()):
        return None
    return f"{int(h):02d}:{int(m):02d}"


def load_json(file):
    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                data = json.load(f)
                return data
    except Exception:
        pass
    return {}


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


# Ensure reminders structure is a dict of lists
def normalize_reminders_structure(rem):
    if not isinstance(rem, dict):
        return {}
    changed = False
    for k, v in list(rem.items()):
        if not isinstance(v, list):
            rem[k] = [] if v is None else [v] if isinstance(v, dict) else []
            changed = True
    return rem


# ------------------------ MAIN APP ------------------------
class MediTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("MediTimer")
        self.root.geometry("430x700")
        self.root.configure(bg="#0a0f24")

        self.users = load_json(USERS_FILE)
        self.reminders = normalize_reminders_structure(load_json(REM_FILE))
        self.current_user = None
        self.current_user_type = None   # <-- track Elder / Normal choice

        self.show_login()
        self.start_reminder_thread()

    # ==================================================
    # LOGIN PAGE
    # ==================================================
    def show_login(self):
        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text="MediTimer", fg="cyan", bg="#0a0f24",
                 font=("Helvetica", 28, "bold")).pack(pady=20)

        frame = tk.Frame(self.root, bg="#111935", bd=0)
        frame.pack(pady=20)

        tk.Label(frame, text="Username", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        self.username_entry = tk.Entry(frame, font=("Arial", 14), width=25)
        self.username_entry.pack(pady=5)

        tk.Label(frame, text="Password", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        self.password_entry = tk.Entry(frame, font=("Arial", 14), width=25, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", bg="cyan", fg="black", width=18, height=2,
                  command=self.login).pack(pady=10)
        tk.Button(self.root, text="Signup", bg="#00ffaa", fg="black", width=18, height=2,
                  command=self.show_signup).pack()

    def login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()

        if u in self.users and self.users[u] == p:
            self.current_user = u
            messagebox.showinfo("Success", "Login Successful!")
            self.select_type_page()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    # ==================================================
    # SIGNUP PAGE
    # ==================================================
    def show_signup(self):
        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text="Create Account", fg="cyan", bg="#0a0f24", font=("Helvetica", 26)).pack(pady=20)

        frame = tk.Frame(self.root, bg="#111935")
        frame.pack(pady=20)

        tk.Label(frame, text="New Username", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        user_e = tk.Entry(frame, font=("Arial", 14), width=25)
        user_e.pack(pady=5)

        tk.Label(frame, text="New Password", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        pass_e = tk.Entry(frame, font=("Arial", 14), width=25, show="*")
        pass_e.pack(pady=5)

        def register():
            u = user_e.get().strip(); p = pass_e.get().strip()
            if not u or not p:
                messagebox.showwarning("Missing", "All fields required!")
                return
            self.users[u] = p
            save_json(USERS_FILE, self.users)
            messagebox.showinfo("Done", "Signup Successful!")
            self.show_login()

        tk.Button(self.root, text="Create Account", bg="cyan", fg="black",
                  width=18, height=2, command=register).pack(pady=10)

        tk.Button(self.root, text="Back", bg="#00ffaa", fg="black",
                  width=18, height=2, command=self.show_login).pack()

    # ==================================================
    # SELECT USER TYPE
    # ==================================================
    def select_type_page(self):
        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text="Select User Type", fg="cyan", bg="#0a0f24",
                 font=("Helvetica", 26)).pack(pady=30)

        # set current_user_type when selecting
        tk.Button(self.root, text="Elder", bg="#00ffaa", fg="black", width=20, height=3,
                  command=lambda: self.start_dashboard("elder")).pack(pady=20)

        tk.Button(self.root, text="Normal", bg="cyan", fg="black", width=20, height=3,
                  command=lambda: self.start_dashboard("normal")).pack()

    # ==================================================
    # DASHBOARD
    # ==================================================
    def start_dashboard(self, user_type):
        # store the user's preference (elder / normal)
        self.current_user_type = user_type

        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text=f"Welcome, {self.current_user}", fg="cyan",
                 bg="#0a0f24", font=("Helvetica", 23)).pack(pady=20)

        # When buttons are clicked we keep the same user_type stored in self.current_user_type.
        tk.Button(self.root, text="Add New Reminder", bg="#00ffaa", fg="black", width=20, height=3,
                  command=self.add_reminder_page).pack(pady=15)

        tk.Button(self.root, text="Show All Reminders", bg="cyan", fg="black", width=20, height=3,
                  command=self.show_all_reminders).pack(pady=15)

        tk.Button(self.root, text="Logout", bg="#ff4444", fg="white", width=20, height=3,
                  command=self.show_login).pack(pady=15)

    # ==================================================
    # ADD REMINDER PAGE (WITH LABELS ADDED ✔)
    # ==================================================
    def add_reminder_page(self):
        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text="Add Medicine Reminder", fg="cyan", bg="#0a0f24",
                 font=("Helvetica", 24)).pack(pady=20)

        frame = tk.Frame(self.root, bg="#111935")
        frame.pack(pady=10)

        # ------------------ LABELS FOR EACH FIELD ✔ ------------------
        tk.Label(frame, text="Medicine Name", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        medicine_e = tk.Entry(frame, font=("Arial", 14), width=25)
        medicine_e.pack(pady=5)

        tk.Label(frame, text="Dosage", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        dosage_e = tk.Entry(frame, font=("Arial", 14), width=25)
        dosage_e.pack(pady=5)

        tk.Label(frame, text="Time (HH:MM)", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        time_e = tk.Entry(frame, font=("Arial", 14), width=25)
        time_e.pack(pady=5)

        tk.Label(frame, text="Type (Tablet/Syrup)", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        type_e = tk.Entry(frame, font=("Arial", 14), width=25)
        type_e.pack(pady=5)

        tk.Label(frame, text="Duration (Days)", fg="white", bg="#111935", font=("Arial", 13)).pack(anchor='w')
        duration_e = tk.Entry(frame, font=("Arial", 14), width=25)
        duration_e.insert(0, "30")  # default 30 days
        duration_e.pack(pady=5)

        def save_rem():
            m = medicine_e.get().strip()
            d = dosage_e.get().strip()
            t = time_e.get().strip()
            tp = type_e.get().strip()
            dr = duration_e.get().strip()

            if not (m and d and t and tp and dr):
                messagebox.showwarning("Missing", "All fields are required!")
                return

            nt = normalize_time(t)
            if nt is None:
                messagebox.showerror("Error", "Enter time in HH:MM format")
                return

            if self.current_user not in self.reminders:
                self.reminders[self.current_user] = []

            # store normalized time string
            self.reminders[self.current_user].append({
                "medicine": m,
                "dosage": d,
                "time": nt,
                "type": tp,
                "duration": int(dr),
                "start": datetime.now().strftime("%Y-%m-%d")
            })

            save_json(REM_FILE, self.reminders)
            messagebox.showinfo("Saved", "Reminder Added Successfully!")
            # return to dashboard preserving the chosen user_type
            self.start_dashboard(self.current_user_type)

        tk.Button(self.root, text="Save Reminder", bg="#00ffaa", fg="black", width=20, height=3,
                  command=save_rem).pack(pady=15)

        tk.Button(self.root, text="Back", bg="#ff4444", fg="white", width=20, height=3,
                  command=lambda: self.start_dashboard(self.current_user_type)).pack(pady=10)

    # ==================================================
    # SHOW ALL REMINDERS
    # ==================================================
    def show_all_reminders(self):
        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text="Your Reminders", fg="cyan", bg="#0a0f24",
                 font=("Helvetica", 24)).pack(pady=20)

        frame = tk.Frame(self.root, bg="#111935")
        frame.pack(pady=10)

        if self.current_user not in self.reminders or len(self.reminders[self.current_user]) == 0:
            tk.Label(frame, text="No reminders added yet.", fg="white", bg="#111935",
                     font=("Arial", 14)).pack(pady=20)
            tk.Button(self.root, text="Back", bg="#00ffaa", fg="black", width=20, height=3,
                      command=lambda: self.start_dashboard(self.current_user_type)).pack(pady=10)
            return

        for i, rem in enumerate(self.reminders[self.current_user]):
            # defensive: ensure rem is a dict and has time
            if not isinstance(rem, dict):
                continue

            card = tk.Frame(frame, bg="#1e2a47", bd=2, relief="ridge")
            card.pack(pady=10, fill="x")

            tk.Label(card, text=f"Medicine: {rem.get('medicine','')}", fg="cyan", bg="#1e2a47",
                     font=("Arial", 14)).pack(anchor='w')
            tk.Label(card, text=f"Dosage: {rem.get('dosage','')}", fg="white", bg="#1e2a47",
                     font=("Arial", 13)).pack(anchor='w')
            tk.Label(card, text=f"Time: {rem.get('time','')}", fg="white", bg="#1e2a47",
                     font=("Arial", 13)).pack(anchor='w')
            tk.Label(card, text=f"Type: {rem.get('type','')}", fg="white", bg="#1e2a47",
                     font=("Arial", 13)).pack(anchor='w')
            tk.Label(card, text=f"Duration: {rem.get('duration','')} days", fg="white", bg="#1e2a47",
                     font=("Arial", 13)).pack(anchor='w')

            tk.Button(card, text="Delete", bg="#ff4444", fg="white",
                      command=lambda idx=i: self.delete_reminder(idx)).pack(side="right", padx=5, pady=5)

        tk.Button(self.root, text="Back", bg="#00ffaa", fg="black", width=20, height=3,
                  command=lambda: self.start_dashboard(self.current_user_type)).pack(pady=10)

    def delete_reminder(self, index):
        if self.current_user in self.reminders and 0 <= index < len(self.reminders[self.current_user]):
            self.reminders[self.current_user].pop(index)
            save_json(REM_FILE, self.reminders)
        self.show_all_reminders()

    # ==================================================
    # REMINDER THREAD
    # ==================================================
    def start_reminder_thread(self):
        def run():
            while True:
                time.sleep(30)
                now = datetime.now().strftime("%H:%M")

                # iterate users safely
                for user, rems in list(self.reminders.items()):
                    if not isinstance(rems, list):
                        continue
                    for r in rems:
                        if not isinstance(r, dict):
                            continue
                        t = r.get("time")
                        if not t:
                            continue
                        # match normalized form (we store normalized)
                        try:
                            if t == now:
                                # Only fire according to the currently logged-in user's preference:
                                # - If logged-in user is the owner and selected 'elder' -> voice-only
                                # - If logged-in user is the owner and selected 'normal' -> popup-only
                                if user == self.current_user:
                                    if self.current_user_type == "elder":
                                        # voice only
                                        speak(f"Time to take {r.get('medicine','medicine')}")
                                    else:
                                        # normal -> popup only
                                        try:
                                            notification.notify(
                                                title="Medicine Reminder",
                                                message=f"Take {r.get('medicine','')} ({r.get('dosage','')})",
                                                timeout=5
                                            )
                                        except Exception:
                                            pass
                                else:
                                    # For other users (if multiple users exist) default to popup
                                    try:
                                        notification.notify(
                                            title="Medicine Reminder",
                                            message=f"Take {r.get('medicine','')} ({r.get('dosage','')})",
                                            timeout=5
                                        )
                                    except Exception:
                                        pass
                        except Exception:
                            # defensive: ignore malformed entries
                            continue

        threading.Thread(target=run, daemon=True).start()


# ------------------------ RUN APP ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    MediTimer(root)
    root.mainloop()