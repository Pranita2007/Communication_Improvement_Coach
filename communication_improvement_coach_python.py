# ============================================================
# COMMUNICATION IMPROVEMENT COACH
# Complete Python Project
#
# Features:
# - Login / Register
# - Proper Dashboard
# - Voice Practice
# - Selectable speaking timer (15 to 120 seconds)
# - Microphone verification
# - Voice -> Text
# - Text analysis
# - Grammar mistakes
# - Corrections
# - Vocabulary detection
# - Communication score
# - Text Practice
# - Vocabulary Practice
# - Grammar Practice
# - Sentence Practice
# - Daily Conversation
# - Pronunciation Practice
# - Progress Dashboard
# - SQLite Database
# ============================================================

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import speech_recognition as sr
import pyttsx3
import random
import re
import threading
import queue
from datetime import datetime
import time

# matplotlib is optional
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ============================================================
# SETTINGS
# ============================================================

APP_TITLE = "Communication Improvement Coach"

DB_NAME = "communication_coach.db"

# Maximum speaking time
MAX_SPEAKING_SECONDS = 30

# User must start speaking within this time
LISTEN_TIMEOUT = 10

# Speech language
SPEECH_LANGUAGE = "en-IN"


# ============================================================
# COLORS
# ============================================================

NAVY = "#17365D"
BLUE = "#2874A6"
LIGHT_BLUE = "#EAF3FA"
VERY_LIGHT_BLUE = "#F4F8FC"

GREEN = "#20A464"
LIGHT_GREEN = "#E8F8F0"

RED = "#D64545"
LIGHT_RED = "#FDECEC"

ORANGE = "#E67E22"
LIGHT_ORANGE = "#FFF3E5"

WHITE = "#FFFFFF"
BLACK = "#202124"
GREY = "#6B7280"
LIGHT_GREY = "#E5E7EB"


# ============================================================
# GLOBAL VARIABLES
# ============================================================

root = tk.Tk()

current_user = None

# Queue is used so microphone work does not freeze the GUI
voice_queue = queue.Queue()

# Prevent multiple recordings at the same time
recording_in_progress = False


# ============================================================
# DATABASE
# ============================================================

def database_connection():

    return sqlite3.connect(DB_NAME)


def create_database():

    conn = database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            module TEXT NOT NULL,
            score INTEGER NOT NULL,
            feedback TEXT,
            original_text TEXT,
            corrected_text TEXT,
            mistakes INTEGER DEFAULT 0,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_result(
    module,
    score,
    feedback="",
    original_text="",
    corrected_text="",
    mistakes=0
):

    if current_user is None:
        return

    conn = database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results
        (
            username,
            module,
            score,
            feedback,
            original_text,
            corrected_text,
            mistakes,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user,
        module,
        int(score),
        feedback,
        original_text,
        corrected_text,
        int(mistakes),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# ============================================================
# GENERAL GUI FUNCTIONS
# ============================================================

def clear_screen():

    for widget in root.winfo_children():
        widget.destroy()


def make_button(
    parent,
    text,
    command,
    color=NAVY,
    width=20,
    height=1
):

    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        width=width,
        height=height,
        bg=color,
        fg=WHITE,
        activebackground=color,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2"
    )


def page_title(parent, title, subtitle=None):

    tk.Label(
        parent,
        text=title,
        font=("Arial", 25, "bold"),
        bg=parent.cget("bg"),
        fg=NAVY
    ).pack(pady=(20, 5))

    if subtitle:

        tk.Label(
            parent,
            text=subtitle,
            font=("Arial", 12),
            bg=parent.cget("bg"),
            fg=GREY
        ).pack(pady=(0, 15))


def create_back_button(parent):

    tk.Button(
        parent,
        text="← Back to Dashboard",
        command=dashboard,
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=NAVY,
        relief="solid",
        cursor="hand2"
    ).pack(pady=15)


# ============================================================
# WELCOME PAGE
# ============================================================

def welcome_page():

    clear_screen()

    root.configure(bg=VERY_LIGHT_BLUE)

    frame = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    frame.pack(
        fill="both",
        expand=True
    )

    tk.Label(
        frame,
        text="COMMUNICATION",
        font=("Arial", 40, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=NAVY
    ).pack(pady=(100, 0))

    tk.Label(
        frame,
        text="IMPROVEMENT COACH",
        font=("Arial", 30, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=BLUE
    ).pack(pady=5)

    tk.Label(
        frame,
        text="Practice • Speak • Analyze • Improve",
        font=("Arial", 16),
        bg=VERY_LIGHT_BLUE,
        fg=GREY
    ).pack(pady=15)

    tk.Label(
        frame,
        text=(
            "Improve your English communication through\n"
            "speaking, vocabulary, grammar and conversation practice."
        ),
        font=("Arial", 13),
        bg=VERY_LIGHT_BLUE,
        fg=BLACK,
        justify="center"
    ).pack(pady=10)

    make_button(
        frame,
        "START PRACTICE",
        login_page,
        NAVY,
        25,
        2
    ).pack(pady=30)

    tk.Label(
        frame,
        text="Python • Tkinter • Speech Recognition • SQLite",
        font=("Arial", 10),
        bg=VERY_LIGHT_BLUE,
        fg=GREY
    ).pack(side="bottom", pady=20)


# ============================================================
# LOGIN
# ============================================================

def login_page():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "LOGIN",
        "Login to your Communication Coach"
    )

    card = tk.Frame(
        main,
        bg=WHITE,
        padx=45,
        pady=35,
        relief="solid",
        bd=1
    )

    card.pack()

    tk.Label(
        card,
        text="Username",
        font=("Arial", 12, "bold"),
        bg=WHITE,
        fg=BLACK
    ).pack(anchor="w")

    username = tk.Entry(
        card,
        font=("Arial", 13),
        width=32
    )

    username.pack(pady=(5, 18))

    tk.Label(
        card,
        text="Password",
        font=("Arial", 12, "bold"),
        bg=WHITE,
        fg=BLACK
    ).pack(anchor="w")

    password = tk.Entry(
        card,
        font=("Arial", 13),
        width=32,
        show="*"
    )

    password.pack(pady=(5, 20))

    def login():

        global current_user

        user = username.get().strip()
        pwd = password.get().strip()

        if not user or not pwd:

            messagebox.showwarning(
                "Missing Information",
                "Please enter username and password."
            )

            return

        conn = database_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT username
            FROM users
            WHERE username = ? AND password = ?
            """,
            (user, pwd)
        )

        result = cursor.fetchone()

        conn.close()

        if result:

            current_user = user

            dashboard()

        else:

            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )

    make_button(
        card,
        "LOGIN",
        login,
        NAVY,
        25
    ).pack(pady=5)

    tk.Button(
        card,
        text="Create New Account",
        command=signup_page,
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=BLUE,
        relief="flat",
        cursor="hand2"
    ).pack(pady=12)

    tk.Button(
        main,
        text="← Back",
        command=welcome_page,
        font=("Arial", 10),
        bg=VERY_LIGHT_BLUE,
        relief="flat"
    ).pack()


# ============================================================
# SIGNUP
# ============================================================

def signup_page():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "CREATE ACCOUNT"
    )

    card = tk.Frame(
        main,
        bg=WHITE,
        padx=45,
        pady=35,
        relief="solid",
        bd=1
    )

    card.pack()

    tk.Label(
        card,
        text="Username",
        font=("Arial", 12, "bold"),
        bg=WHITE
    ).pack(anchor="w")

    username = tk.Entry(
        card,
        font=("Arial", 13),
        width=32
    )

    username.pack(pady=8)

    tk.Label(
        card,
        text="Password",
        font=("Arial", 12, "bold"),
        bg=WHITE
    ).pack(anchor="w")

    password = tk.Entry(
        card,
        font=("Arial", 13),
        width=32,
        show="*"
    )

    password.pack(pady=8)

    def register():

        user = username.get().strip()
        pwd = password.get().strip()

        if not user or not pwd:

            messagebox.showwarning(
                "Missing Information",
                "Please enter username and password."
            )

            return

        try:

            conn = database_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users(username, password)
                VALUES (?, ?)
                """,
                (user, pwd)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Account Created",
                "Your account was created successfully."
            )

            login_page()

        except sqlite3.IntegrityError:

            messagebox.showerror(
                "Username Exists",
                "This username already exists."
            )

    make_button(
        card,
        "CREATE ACCOUNT",
        register,
        GREEN,
        25
    ).pack(pady=20)

    tk.Button(
        main,
        text="← Back to Login",
        command=login_page,
        bg=VERY_LIGHT_BLUE,
        relief="flat"
    ).pack()


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    clear_screen()

    root.configure(bg=VERY_LIGHT_BLUE)

    # ---------------- Header ----------------

    header = tk.Frame(
        root,
        bg=NAVY,
        height=75
    )

    header.pack(
        fill="x"
    )

    header.pack_propagate(False)

    tk.Label(
        header,
        text="Communication Improvement Coach",
        font=("Arial", 20, "bold"),
        bg=NAVY,
        fg=WHITE
    ).pack(
        side="left",
        padx=25
    )

    tk.Label(
        header,
        text="Welcome, " + str(current_user),
        font=("Arial", 11),
        bg=NAVY,
        fg=WHITE
    ).pack(
        side="right",
        padx=25
    )

    # ---------------- Main ----------------

    body = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    body.pack(
        fill="both",
        expand=True
    )

    tk.Label(
        body,
        text="Learning Dashboard",
        font=("Arial", 27, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=BLACK
    ).pack(pady=(22, 3))

    tk.Label(
        body,
        text="Choose a practice module",
        font=("Arial", 13),
        bg=VERY_LIGHT_BLUE,
        fg=GREY
    ).pack(pady=(0, 15))

    # ---------------- Quick Progress ----------------

    show_dashboard_summary(body)

    # ---------------- Module Grid ----------------

    grid = tk.Frame(
        body,
        bg=VERY_LIGHT_BLUE
    )

    grid.pack(pady=10)

    modules = [

        (
            "🎤",
            "Voice Practice",
            "Speak and get detailed feedback",
            voice_practice,
            NAVY
        ),

        (
            "📝",
            "Text Practice",
            "Type and analyze your English",
            text_practice,
            BLUE
        ),

        (
            "📚",
            "Vocabulary",
            "Learn useful English words",
            vocabulary_practice,
            GREEN
        ),

        (
            "📖",
            "Grammar",
            "Improve grammar knowledge",
            grammar_practice,
            ORANGE
        ),

        (
            "✍",
            "Sentence Practice",
            "Build correct sentences",
            sentence_practice,
            BLUE
        ),

        (
            "🗣",
            "Conversation",
            "Practice daily communication",
            conversation_practice,
            NAVY
        ),

        (
            "🔊",
            "Pronunciation",
            "Listen and repeat words",
            pronunciation_practice,
            GREEN
        ),

        (
            "📊",
            "My Progress",
            "View scores and improvement",
            progress_page,
            ORANGE
        )
    ]

    row = 0
    col = 0

    for icon, title, description, command, color in modules:

        card = tk.Frame(
            grid,
            bg=WHITE,
            width=230,
            height=125,
            bd=1,
            relief="solid"
        )

        card.grid(
            row=row,
            column=col,
            padx=7,
            pady=7
        )

        card.grid_propagate(False)

        tk.Label(
            card,
            text=icon,
            font=("Arial", 25),
            bg=WHITE
        ).pack(pady=(8, 0))

        tk.Button(
            card,
            text=title,
            font=("Arial", 11, "bold"),
            bg=color,
            fg=WHITE,
            width=19,
            relief="flat",
            command=command,
            cursor="hand2"
        ).pack(pady=3)

        tk.Label(
            card,
            text=description,
            font=("Arial", 8),
            bg=WHITE,
            fg=GREY
        ).pack()

        col += 1

        if col == 4:

            col = 0
            row += 1

    # ---------------- Logout ----------------

    tk.Button(
        body,
        text="Logout",
        command=logout,
        font=("Arial", 10, "bold"),
        bg=LIGHT_RED,
        fg=RED,
        relief="flat",
        width=15
    ).pack(pady=8)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

def show_dashboard_summary(parent):

    conn = database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*), AVG(score)
        FROM results
        WHERE username = ?
        """,
        (current_user,)
    )

    result = cursor.fetchone()

    conn.close()

    attempts = result[0] or 0
    average = round(result[1] or 0)

    frame = tk.Frame(
        parent,
        bg=VERY_LIGHT_BLUE
    )

    frame.pack()

    make_summary_card(
        frame,
        "PRACTICE SESSIONS",
        str(attempts),
        NAVY
    ).grid(row=0, column=0, padx=8)

    make_summary_card(
        frame,
        "AVERAGE SCORE",
        f"{average}/100",
        GREEN
    ).grid(row=0, column=1, padx=8)

    make_summary_card(
        frame,
        "SPEAKING LIMIT",
        "Selectable",
        ORANGE
    ).grid(row=0, column=2, padx=8)


def make_summary_card(parent, title, value, color):

    card = tk.Frame(
        parent,
        bg=WHITE,
        width=190,
        height=75,
        bd=1,
        relief="solid"
    )

    card.grid_propagate(False)

    tk.Label(
        card,
        text=title,
        font=("Arial", 9, "bold"),
        bg=WHITE,
        fg=GREY
    ).pack(pady=(8, 0))

    tk.Label(
        card,
        text=value,
        font=("Arial", 17, "bold"),
        bg=WHITE,
        fg=color
    ).pack()

    return card


# ============================================================
# VOICE PRACTICE
# ============================================================

def voice_practice():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "🎤 Voice Communication Practice",
        "Speak clearly and receive communication feedback"
    )

    # ---------------- Topic ----------------

    topics = [

        "Introduce yourself",

        "Talk about your college",

        "Talk about your favorite subject",

        "Talk about your hobbies",

        "Talk about your family",

        "Talk about your career goal",

        "Talk about your future plans",

        "Why do you want to improve your English?",

        "Talk about your daily routine",

        "Describe your best friend"
    ]

    topic = random.choice(topics)

    # Speaking duration can be selected for each practice session.
    duration_frame = tk.Frame(main, bg=VERY_LIGHT_BLUE)
    duration_frame.pack(pady=(0, 10))

    tk.Label(
        duration_frame,
        text="Choose speaking time:",
        font=("Arial", 11, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=NAVY
    ).pack(side="left", padx=8)

    duration_var = tk.StringVar(value="30 seconds")
    duration_menu = ttk.Combobox(
        duration_frame,
        textvariable=duration_var,
        values=("15 seconds", "30 seconds", "45 seconds", "60 seconds", "90 seconds", "120 seconds"),
        state="readonly",
        width=15,
        font=("Arial", 11)
    )
    duration_menu.pack(side="left", padx=8)

    topic_card = tk.Frame(
        main,
        bg=WHITE,
        padx=20,
        pady=12,
        relief="solid",
        bd=1
    )

    topic_card.pack(
        fill="x",
        padx=70
    )

    tk.Label(
        topic_card,
        text="TODAY'S SPEAKING TOPIC",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=BLUE
    ).pack()

    tk.Label(
        topic_card,
        text=topic,
        font=("Arial", 17, "bold"),
        bg=WHITE,
        fg=BLACK,
        wraplength=900
    ).pack(pady=5)

    tk.Label(
        topic_card,
        text="Select your speaking time above before starting.",
        font=("Arial", 10),
        bg=WHITE,
        fg=GREY
    ).pack()

    # ---------------- Timer ----------------

    timer_label = tk.Label(
        main,
        text=f"{MAX_SPEAKING_SECONDS // 60:02d}:{MAX_SPEAKING_SECONDS % 60:02d}",
        font=("Arial", 32, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=NAVY
    )

    timer_label.pack(pady=(15, 5))

    status_label = tk.Label(
        main,
        text="Ready to start. Click the microphone button.",
        font=("Arial", 12, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=GREY
    )

    status_label.pack(pady=5)

    # ---------------- Progress ----------------

    progress = ttk.Progressbar(
        main,
        orient="horizontal",
        length=650,
        mode="determinate",
        maximum=MAX_SPEAKING_SECONDS
    )

    progress.pack(pady=5)

    # ---------------- Text ----------------

    text_box = tk.Text(
        main,
        height=7,
        width=95,
        font=("Arial", 13),
        wrap="word",
        bg=WHITE
    )

    text_box.pack(
        padx=50,
        pady=10
    )

    # ---------------- Buttons ----------------

    button_frame = tk.Frame(
        main,
        bg=VERY_LIGHT_BLUE
    )

    button_frame.pack(pady=5)

    listen_button = make_button(
        button_frame,
        "🎤 START SPEAKING",
        None,
        NAVY,
        22,
        2
    )

    listen_button.grid(
        row=0,
        column=0,
        padx=7
    )

    analyze_button = make_button(
        button_frame,
        "🔍 ANALYZE MY SPEECH",
        None,
        GREEN,
        22,
        2
    )

    analyze_button.grid(
        row=0,
        column=1,
        padx=7
    )

    # ---------------- Internal State ----------------

    state = {
        "seconds": 0,
        "limit": MAX_SPEAKING_SECONDS,
        "recording": False,
        "finished": False
    }

    def update_timer():

        if not state["recording"]:
            return

        state["seconds"] += 1

        remaining = state["limit"] - state["seconds"]

        if remaining < 0:
            remaining = 0

        timer_label.config(
            text=f"{remaining // 60:02d}:{remaining % 60:02d}"
        )

        progress["value"] = state["seconds"]

        if state["seconds"] >= state["limit"]:

            state["recording"] = False

            status_label.config(
                text=f"⏰ {state['limit']} seconds completed. Processing your voice...",
                fg=ORANGE
            )

            return

        root.after(
            1000,
            update_timer
        )

    def start_recording():

        global recording_in_progress

        if recording_in_progress:

            messagebox.showwarning(
                "Recording in Progress",
                "A recording is already running."
            )

            return

        recording_in_progress = True

        state["limit"] = int(duration_var.get().split()[0])
        state["seconds"] = 0
        state["recording"] = True
        state["finished"] = False

        text_box.delete(
            "1.0",
            tk.END
        )

        timer_label.config(
            text=f"{state['limit'] // 60:02d}:{state['limit'] % 60:02d}",
            fg=NAVY
        )

        progress.configure(maximum=state["limit"])
        progress["value"] = 0

        status_label.config(
            text="🔍 Checking microphone...",
            fg=BLUE
        )

        listen_button.config(
            state="disabled"
        )

        analyze_button.config(
            state="disabled"
        )

        root.after(
            1000,
            update_timer
        )

        thread = threading.Thread(
            target=record_voice,
            args=(text_box, status_label, state, state["limit"]),
            daemon=True
        )

        thread.start()

        root.after(
            100,
            check_voice_queue
        )

    def check_voice_queue():

        global recording_in_progress

        try:

            message = voice_queue.get_nowait()

            message_type = message[0]

            if message_type == "status":

                status_label.config(
                    text=message[1],
                    fg=message[2]
                )

                root.after(
                    100,
                    check_voice_queue
                )

            elif message_type == "success":

                state["recording"] = False
                state["finished"] = True

                text = message[1]

                text_box.delete(
                    "1.0",
                    tk.END
                )

                text_box.insert(
                    tk.END,
                    text
                )

                timer_label.config(
                    text="VOICE READY",
                    fg=GREEN
                )

                progress["value"] = state["seconds"]

                status_label.config(
                    text="✅ Voice verification completed. Voice converted to text.",
                    fg=GREEN
                )

                listen_button.config(
                    state="normal"
                )

                analyze_button.config(
                    state="normal"
                )

                recording_in_progress = False

            elif message_type == "error":

                state["recording"] = False

                status_label.config(
                    text=message[1],
                    fg=RED
                )

                listen_button.config(
                    state="normal"
                )

                analyze_button.config(
                    state="normal"
                )

                recording_in_progress = False

                messagebox.showerror(
                    "Voice Error",
                    message[1]
                )

        except queue.Empty:

            if recording_in_progress:

                root.after(
                    100,
                    check_voice_queue
                )

    def analyze():

        text = text_box.get(
            "1.0",
            tk.END
        ).strip()

        if not text:

            messagebox.showwarning(
                "No Speech",
                "Please record your voice first."
            )

            return

        analyze_button.config(
            state="disabled"
        )

        status_label.config(
            text="🔍 Analyzing grammar, vocabulary and communication...",
            fg=ORANGE
        )

        root.update()

        mistakes, corrections, corrected_text, vocabulary = analyze_communication(text)

        score = calculate_score(
            text,
            mistakes
        )

        feedback = generate_feedback(
            score,
            len(mistakes),
            len(text.split())
        )

        save_result(
            "Voice Practice",
            score,
            feedback,
            text,
            corrected_text,
            len(mistakes)
        )

        show_voice_analysis(
            topic,
            text,
            mistakes,
            corrections,
            corrected_text,
            vocabulary,
            score,
            feedback
        )

    listen_button.config(
        command=start_recording
    )

    analyze_button.config(
        command=analyze
    )

    create_back_button(main)


# ============================================================
# RECORD VOICE
# ============================================================

def record_voice(text_box, status_label, state, duration_seconds):
    """Listen in short chunks until the selected speaking time ends.
    This helps capture several sentences instead of stopping after one pause.
    """
    try:
        recognizer = sr.Recognizer()
        voice_queue.put(("status", "🔍 Checking microphone...", BLUE))
        microphones = sr.Microphone.list_microphone_names()
        if not microphones:
            voice_queue.put(("error", "No microphone was detected on this computer."))
            return

        recognized_parts = []
        with sr.Microphone() as source:
            voice_queue.put(("status", "🎤 Microphone detected. Reducing background noise...", BLUE))
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            voice_queue.put(("status", f"🔴 LISTENING — Keep speaking naturally for up to {duration_seconds} seconds. Pauses are okay.", RED))
            start_time = time.monotonic()
            end_time = start_time + duration_seconds
            while time.monotonic() < end_time:
                remaining = end_time - time.monotonic()
                try:
                    audio = recognizer.listen(
                        source,
                        timeout=max(1, min(3, remaining)),
                        phrase_time_limit=max(1, min(8, remaining))
                    )
                except sr.WaitTimeoutError:
                    continue
                try:
                    part = recognizer.recognize_google(audio, language=SPEECH_LANGUAGE)
                    if part and (not recognized_parts or part.lower() != recognized_parts[-1].lower()):
                        recognized_parts.append(part.strip())
                        voice_queue.put(("status", "📝 Captured speech so far: " + " ".join(recognized_parts)[-180:], BLUE))
                except sr.UnknownValueError:
                    # Ignore one unclear chunk and keep listening for the rest.
                    continue
                except sr.RequestError:
                    voice_queue.put(("error", "Speech recognition service could not be reached. Check your internet connection."))
                    return

        state["recording"] = False
        text = " ".join(recognized_parts).strip()
        if not text:
            voice_queue.put(("error", "No clear words were recognized. Move closer to the microphone, reduce background noise, and try again."))
            return
        voice_queue.put(("status", "✅ Voice captured. Preparing the complete recognized text...", GREEN))
        voice_queue.put(("success", text))
    except OSError as error:
        state["recording"] = False
        voice_queue.put(("error", "Microphone error:\n\n" + str(error)))
    except Exception as error:
        state["recording"] = False
        voice_queue.put(("error", "Unexpected microphone error:\n\n" + str(error)))


# ============================================================
# COMMUNICATION ANALYSIS
# ============================================================

def analyze_communication(text):

    original = text.strip()

    lower = original.lower()

    mistakes = []

    corrections = []

    corrected = original

    # --------------------------------------------
    # Grammar rules
    # --------------------------------------------

    rules = [

        (
            r"\bi am go\b",
            "I am going",
            "Use 'going' after 'I am'."
        ),

        (
            r"\bi am went\b",
            "I went",
            "Do not use 'am' with 'went'."
        ),

        (
            r"\bhe go\b",
            "He goes",
            "Use 'goes' with he."
        ),

        (
            r"\bshe go\b",
            "She goes",
            "Use 'goes' with she."
        ),

        (
            r"\bthey is\b",
            "They are",
            "Use 'are' with they."
        ),

        (
            r"\bwe is\b",
            "We are",
            "Use 'are' with we."
        ),

        (
            r"\bi has\b",
            "I have",
            "Use 'have' with I."
        ),

        (
            r"\bhe have\b",
            "He has",
            "Use 'has' with he."
        ),

        (
            r"\bshe have\b",
            "She has",
            "Use 'has' with she."
        ),

        (
            r"\bhe don't\b",
            "He doesn't",
            "Use 'doesn't' with he."
        ),

        (
            r"\bshe don't\b",
            "She doesn't",
            "Use 'doesn't' with she."
        ),

        (
            r"\bdid not went\b",
            "did not go",
            "Use the base verb after 'did not'."
        ),

        (
            r"\bdidn't went\b",
            "didn't go",
            "Use the base verb after 'didn't'."
        ),

        (
            r"\bi am agree\b",
            "I agree",
            "Say 'I agree', not 'I am agree'."
        ),

        (
            r"\bmore better\b",
            "better",
            "Do not use 'more' with 'better'."
        ),

        (
            r"\bvery unique\b",
            "unique",
            "Usually 'unique' does not need 'very'."
        )
    ]

    for pattern, correction, explanation in rules:

        if re.search(
            pattern,
            lower
        ):

            mistakes.append(
                f"Grammar issue: {re.search(pattern, lower).group()}"
            )

            corrections.append(
                f"{correction} — {explanation}"
            )

            corrected = re.sub(
                pattern,
                correction,
                corrected,
                flags=re.IGNORECASE
            )

    # --------------------------------------------
    # Missing punctuation
    # --------------------------------------------

    if original:

        if original[-1] not in ".!?":

            mistakes.append(
                "Missing punctuation at the end."
            )

            corrections.append(
                "Add a full stop or appropriate punctuation."
            )

            corrected += "."

    # --------------------------------------------
    # Sentence length
    # --------------------------------------------

    words = original.split()

    if 0 < len(words) < 5:

        mistakes.append(
            "The answer is very short."
        )

        corrections.append(
            "Try to speak using a longer and more complete sentence."
        )

    # --------------------------------------------
    # Repeated words
    # --------------------------------------------

    repeated = re.findall(
        r"\b(\w+)\s+\1\b",
        lower
    )

    for word in repeated:

        mistakes.append(
            f"Repeated word: '{word}'"
        )

        corrections.append(
            f"Remove the repeated word '{word}'."
        )

    # --------------------------------------------
    # Vocabulary
    # --------------------------------------------

    vocabulary = find_vocabulary_words(
        original
    )

    return (
        mistakes,
        corrections,
        corrected,
        vocabulary
    )


# ============================================================
# VOCABULARY DATABASE
# ============================================================

VOCABULARY = {

    "communication":
        "The process of sharing information or ideas.",

    "confidence":
        "The belief in your ability to do something.",

    "improve":
        "To make something better.",

    "practice":
        "Doing something repeatedly to become better.",

    "conversation":
        "A talk between two or more people.",

    "education":
        "The process of learning knowledge and skills.",

    "knowledge":
        "Information and understanding gained through learning.",

    "opportunity":
        "A suitable chance to do something.",

    "achievement":
        "Something successfully completed.",

    "career":
        "A person's professional journey.",

    "technology":
        "Scientific knowledge used to solve practical problems.",

    "experience":
        "Knowledge gained by doing something.",

    "challenge":
        "A difficult task requiring effort.",

    "solution":
        "An answer to a problem.",

    "responsible":
        "Having a duty to take care of something.",

    "creative":
        "Having the ability to create new ideas.",

    "development":
        "The process of growth or improvement.",

    "success":
        "Achieving a desired goal.",

    "future":
        "The time that has not happened yet.",

    "professional":
        "Relating to a person's work or career."
}


# Extended beginner-friendly vocabulary bank (50+ words).
VOCABULARY.update({
    "adapt": "To change to suit a new situation.",
    "ambition": "A strong wish to achieve something.",
    "analyze": "To study something carefully.",
    "appreciate": "To understand the value of something.",
    "attitude": "The way a person thinks or feels.",
    "benefit": "A helpful or good result.",
    "collaborate": "To work together with others.",
    "communicate": "To share information with someone.",
    "compassion": "Concern for another person's difficulties.",
    "consistent": "Doing something regularly in the same way.",
    "contribute": "To give or add something to a group.",
    "curious": "Eager to learn or know something.",
    "decision": "A choice made after thinking.",
    "dedication": "Strong commitment to a task or goal.",
    "effective": "Producing the intended result.",
    "efficient": "Working well without wasting time or effort.",
    "empathy": "Understanding another person's feelings.",
    "encourage": "To give someone confidence or support.",
    "essential": "Completely necessary or very important.",
    "evaluate": "To judge the quality or value of something.",
    "flexible": "Able to change or adapt easily.",
    "goal": "Something a person wants to achieve.",
    "growth": "The process of developing or becoming better.",
    "honest": "Truthful and sincere.",
    "independent": "Able to do things without help.",
    "initiative": "The ability to act without being told.",
    "inspire": "To motivate someone to do something good.",
    "leadership": "The ability to guide or manage people.",
    "logical": "Based on clear reasoning.",
    "motivate": "To give someone a reason to act.",
    "organize": "To arrange things in a useful order.",
    "patience": "The ability to wait calmly.",
    "perspective": "A particular way of viewing something.",
    "potential": "A possibility of future development.",
    "priority": "Something that is more important than others.",
    "productive": "Achieving useful results.",
    "reliable": "Able to be trusted or depended on.",
    "resilient": "Able to recover after difficulty.",
    "respect": "To treat someone with care and value.",
    "resourceful": "Good at finding ways to solve problems.",
    "skill": "An ability gained through learning or practice.",
    "strategy": "A plan to achieve a goal.",
    "support": "To help or encourage someone.",
    "teamwork": "People working together toward a shared goal.",
    "thoughtful": "Showing care by thinking about others.",
    "valuable": "Worth a lot or very useful.",
    "versatile": "Able to do many different things.",
    "visualize": "To form a picture in your mind.",
    "willing": "Ready or happy to do something.",
    "wisdom": "The ability to make good decisions using experience."
})


def find_vocabulary_words(text):

    found = []

    lower = text.lower()

    for word in VOCABULARY:

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            lower
        ):

            found.append(word)

    return found


# ============================================================
# SCORE
# ============================================================

def calculate_score(text, mistakes):

    words = text.split()

    score = 100

    # Mistake penalty
    score -= len(mistakes) * 10

    # Reward longer speaking
    if len(words) >= 15:
        score += 5

    elif len(words) >= 10:
        score += 3

    elif len(words) < 5:
        score -= 10

    score = max(
        20,
        min(100, score)
    )

    return score


def generate_feedback(
    score,
    mistake_count,
    word_count
):

    if score >= 90:

        return (
            "Excellent communication! "
            "Your speech is clear and well structured. "
            "Keep practicing to become even more confident."
        )

    if score >= 75:

        return (
            "Very good communication. "
            "There are a few areas that can be improved."
        )

    if score >= 60:

        return (
            "Good effort. "
            "Focus on grammar, sentence formation and vocabulary."
        )

    return (
        "Keep practicing. "
        "Try speaking slowly, using complete sentences "
        "and checking your grammar."
    )


# ============================================================
# VOICE ANALYSIS RESULT PAGE
# ============================================================

def show_voice_analysis(
    topic,
    original,
    mistakes,
    corrections,
    corrected,
    vocabulary,
    score,
    feedback
):

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "📊 Speech Analysis Result",
        "Your speaking practice has been analyzed"
    )

    # ---------------- Score ----------------

    score_color = GREEN

    if score < 60:
        score_color = RED

    elif score < 75:
        score_color = ORANGE

    score_card = tk.Frame(
        main,
        bg=WHITE,
        bd=1,
        relief="solid",
        padx=25,
        pady=10
    )

    score_card.pack(
        fill="x",
        padx=70,
        pady=5
    )

    tk.Label(
        score_card,
        text=f"COMMUNICATION SCORE  {score}/100",
        font=("Arial", 22, "bold"),
        bg=WHITE,
        fg=score_color
    ).pack()

    tk.Label(
        score_card,
        text=feedback,
        font=("Arial", 11),
        bg=WHITE,
        fg=BLACK,
        wraplength=850
    ).pack(pady=5)

    # ---------------- Original ----------------

    original_box = create_result_box(
        main,
        "📝 1. YOUR SPEECH → TEXT",
        BLUE
    )

    tk.Label(
        original_box,
        text=original,
        font=("Arial", 12),
        bg=WHITE,
        fg=BLACK,
        wraplength=900,
        justify="left"
    ).pack(
        anchor="w"
    )

    # ---------------- Mistakes ----------------

    mistake_box = create_result_box(
        main,
        "❌ 2. MISTAKES FOUND",
        RED
    )

    if mistakes:

        for mistake in mistakes:

            tk.Label(
                mistake_box,
                text="• " + mistake,
                font=("Arial", 11),
                bg=WHITE,
                fg=RED,
                wraplength=900,
                justify="left"
            ).pack(
                anchor="w",
                pady=2
            )

    else:

        tk.Label(
            mistake_box,
            text="🎉 No major mistakes were detected!",
            font=("Arial", 11, "bold"),
            bg=WHITE,
            fg=GREEN
        ).pack(anchor="w")

    # ---------------- Corrections ----------------

    correction_box = create_result_box(
        main,
        "✅ 3. HOW TO CORRECT IT",
        GREEN
    )

    if corrections:

        for correction in corrections:

            tk.Label(
                correction_box,
                text="• " + correction,
                font=("Arial", 11),
                bg=WHITE,
                fg=GREEN,
                wraplength=900,
                justify="left"
            ).pack(
                anchor="w",
                pady=2
            )

    else:

        tk.Label(
            correction_box,
            text="Your grammar looks good!",
            font=("Arial", 11, "bold"),
            bg=WHITE,
            fg=GREEN
        ).pack(anchor="w")

    # ---------------- Correct sentence ----------------

    corrected_box = create_result_box(
        main,
        "✨ 4. IMPROVED VERSION",
        NAVY
    )

    tk.Label(
        corrected_box,
        text=corrected,
        font=("Arial", 12, "bold"),
        bg=WHITE,
        fg=NAVY,
        wraplength=900,
        justify="left"
    ).pack(anchor="w")

    # ---------------- Vocabulary ----------------

    vocab_box = create_result_box(
        main,
        "📚 5. VOCABULARY FOUND",
        ORANGE
    )

    if vocabulary:

        for word in vocabulary:

            tk.Label(
                vocab_box,
                text=f"• {word.title()} — {VOCABULARY[word]}",
                font=("Arial", 10),
                bg=WHITE,
                fg=BLACK,
                wraplength=900,
                justify="left"
            ).pack(
                anchor="w",
                pady=1
            )

    else:

        tk.Label(
            vocab_box,
            text="Try using more useful English vocabulary.",
            font=("Arial", 10),
            bg=WHITE,
            fg=GREY
        ).pack(anchor="w")

    # ---------------- Buttons ----------------

    buttons = tk.Frame(
        main,
        bg=VERY_LIGHT_BLUE
    )

    buttons.pack(
        pady=12
    )

    make_button(
        buttons,
        "🎤 Practice Again",
        voice_practice,
        NAVY,
        18
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    make_button(
        buttons,
        "📊 My Progress",
        progress_page,
        GREEN,
        18
    ).grid(
        row=0,
        column=1,
        padx=5
    )

    make_button(
        buttons,
        "🏠 Dashboard",
        dashboard,
        BLUE,
        18
    ).grid(
        row=0,
        column=2,
        padx=5
    )


def create_result_box(parent, title, color):

    box = tk.LabelFrame(
        parent,
        text=title,
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=color,
        padx=15,
        pady=8
    )

    box.pack(
        fill="x",
        padx=70,
        pady=4
    )

    return box


# ============================================================
# TEXT PRACTICE
# ============================================================

def text_practice():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "📝 Text Communication Practice",
        "Type your English and receive the same analysis used for speech"
    )

    tk.Label(
        main,
        text="Write 2–5 sentences about any topic.",
        font=("Arial", 12),
        bg=VERY_LIGHT_BLUE,
        fg=GREY
    ).pack()

    text_box = tk.Text(
        main,
        height=12,
        width=95,
        font=("Arial", 13),
        wrap="word"
    )

    text_box.pack(
        padx=60,
        pady=15
    )

    def analyze():

        text = text_box.get(
            "1.0",
            tk.END
        ).strip()

        if not text:

            messagebox.showwarning(
                "Empty Text",
                "Please write something first."
            )

            return

        mistakes, corrections, corrected, vocabulary = analyze_communication(
            text
        )

        score = calculate_score(
            text,
            mistakes
        )

        feedback = generate_feedback(
            score,
            len(mistakes),
            len(text.split())
        )

        save_result(
            "Text Practice",
            score,
            feedback,
            text,
            corrected,
            len(mistakes)
        )

        show_voice_analysis(
            "Text Practice",
            text,
            mistakes,
            corrections,
            corrected,
            vocabulary,
            score,
            feedback
        )

    make_button(
        main,
        "🔍 ANALYZE MY TEXT",
        analyze,
        GREEN,
        25,
        2
    ).pack(pady=10)

    create_back_button(main)


# ============================================================
# VOCABULARY PRACTICE
# ============================================================

def vocabulary_practice():
    clear_screen()
    main = tk.Frame(root, bg=VERY_LIGHT_BLUE)
    main.pack(fill="both", expand=True)
    page_title(main, "📚 Vocabulary Builder", "Study 50+ useful English words, meanings and examples")

    words = list(VOCABULARY.items())
    index = [0]
    viewed = set()
    word_label = tk.Label(main, text="", font=("Arial", 30, "bold"), bg=VERY_LIGHT_BLUE, fg=BLUE)
    word_label.pack(pady=(12, 5))
    count_label = tk.Label(main, text="", font=("Arial", 11, "bold"), bg=VERY_LIGHT_BLUE, fg=GREY)
    count_label.pack()
    meaning_label = tk.Label(main, text="Click SHOW MEANING to learn this word.", font=("Arial", 13), bg=WHITE, fg=BLACK, wraplength=850, padx=20, pady=15)
    meaning_label.pack(fill="x", padx=70, pady=15)
    example_label = tk.Label(main, text="", font=("Arial", 12, "italic"), bg=VERY_LIGHT_BLUE, fg=GREY, wraplength=850)
    example_label.pack(pady=5)
    status_label = tk.Label(main, text="Explore the words, then press SUBMIT PRACTICE.", font=("Arial", 11), bg=VERY_LIGHT_BLUE, fg=NAVY)
    status_label.pack(pady=8)

    def load_word():
        word, meaning = words[index[0]]
        word_label.config(text=word.upper())
        count_label.config(text=f"Word {index[0]+1} of {len(words)}")
        meaning_label.config(text="Click SHOW MEANING to learn this word.")
        example_label.config(text="")

    def show_meaning():
        word, meaning = words[index[0]]
        viewed.add(word)
        meaning_label.config(text=meaning)
        example_label.config(text=f"Example: I will use {word} in my daily communication.")
        status_label.config(text=f"Words studied: {len(viewed)} / {len(words)}")

    def next_word():
        if index[0] < len(words)-1:
            index[0] += 1
            load_word()
        else:
            status_label.config(text="You reached the last word. You can submit your practice now.")

    def submit():
        if not viewed:
            messagebox.showwarning("Study first", "Click SHOW MEANING for at least one word before submitting.")
            return
        score = round(len(viewed) / len(words) * 100)
        feedback = f"You studied {len(viewed)} out of {len(words)} words. Review the remaining words to improve your vocabulary."
        save_result("Vocabulary Practice", score, feedback, ", ".join(sorted(viewed)))
        clear_screen()
        result = tk.Frame(root, bg=VERY_LIGHT_BLUE)
        result.pack(fill="both", expand=True)
        page_title(result, "📊 Vocabulary Practice Result", "Your result is shown here")
        tk.Label(result, text=f"Words studied: {len(viewed)} / {len(words)}", font=("Arial", 22, "bold"), bg=VERY_LIGHT_BLUE, fg=GREEN).pack(pady=15)
        tk.Label(result, text=f"Practice score: {score}/100", font=("Arial", 18, "bold"), bg=VERY_LIGHT_BLUE, fg=NAVY).pack(pady=8)
        tk.Label(result, text=feedback, font=("Arial", 12), bg=VERY_LIGHT_BLUE, fg=BLACK, wraplength=800).pack(pady=10)
        make_button(result, "📚 Practice Again", vocabulary_practice, NAVY, 22, 2).pack(pady=8)
        make_button(result, "🏠 Go to Dashboard", dashboard, GREEN, 22, 2).pack(pady=8)

    controls = tk.Frame(main, bg=VERY_LIGHT_BLUE)
    controls.pack(pady=12)
    make_button(controls, "SHOW MEANING", show_meaning, NAVY, 17, 2).grid(row=0, column=0, padx=5)
    make_button(controls, "NEXT WORD ➜", next_word, BLUE, 17, 2).grid(row=0, column=1, padx=5)
    make_button(controls, "✅ SUBMIT PRACTICE", submit, GREEN, 20, 2).grid(row=0, column=2, padx=5)
    create_back_button(main)
    load_word()


# ============================================================
# GRAMMAR PRACTICE
# ============================================================

GRAMMAR_QUESTIONS = [
    ("She ___ to college every day.", ["go", "goes", "going"], "goes"),
    ("They ___ students.", ["is", "are", "am"], "are"),
    ("I ___ learning Python.", ["am", "is", "are"], "am"),
    ("He ___ English every day.", ["practice", "practices", "practicing"], "practices"),
    ("We ___ ready.", ["is", "are", "am"], "are"),
    ("Yesterday, she ___ a book.", ["read", "reads", "reading"], "read"),
    ("I ___ a student.", ["am", "is", "are"], "am"),
    ("They ___ playing football.", ["is", "are", "am"], "are"),
    ("He ___ a new phone.", ["have", "has", "having"], "has"),
    ("We ___ English every day.", ["practice", "practices", "practicing"], "practice"),
    ("I ___ to the library yesterday.", ["go", "went", "gone"], "went"),
    ("She has ___ her homework.", ["complete", "completed", "completing"], "completed"),
    ("There ___ many books on the table.", ["is", "are", "am"], "are"),
    ("This is ___ apple.", ["a", "an", "the"], "an"),
    ("He is taller ___ me.", ["then", "than", "that"], "than"),
    ("I have lived here ___ 2020.", ["for", "since", "from"], "since"),
    ("She ___ cooking when I arrived.", ["was", "were", "is"], "was"),
    ("If it rains, we ___ stay home.", ["will", "would", "did"], "will"),
    ("The children ___ finished their work.", ["has", "have", "is"], "have"),
    ("Neither answer ___ correct.", ["are", "is", "were"], "is"),
    ("My brother and I ___ friends.", ["am", "is", "are"], "are"),
    ("She speaks English very ___. ", ["good", "well", "best"], "well"),
    ("I am interested ___ computers.", ["on", "at", "in"], "in"),
    ("Please listen ___ the teacher.", ["to", "for", "at"], "to"),
    ("He did not ___ the answer.", ["knew", "know", "known"], "know"),
    ("They ___ dinner at 8 pm last night.", ["have", "had", "has"], "had"),
    ("This bag is ___ than that one.", ["heavy", "heavier", "heaviest"], "heavier"),
    ("Mount Everest is the ___ mountain.", ["high", "higher", "highest"], "highest"),
    ("The letter ___ written yesterday.", ["was", "were", "is"], "was"),
    ("You ___ wear a helmet while riding.", ["should", "would", "might to"], "should"),
    ("I have ___ seen that movie.", ["already", "yet", "still"], "already"),
    ("Have you finished your work ___?", ["already", "yet", "ever"], "yet"),
    ("She enjoys ___ books.", ["read", "reading", "to reading"], "reading"),
    ("I want ___ a software engineer.", ["be", "being", "to be"], "to be"),
    ("The students ___ by the teacher.", ["were praised", "praised", "praise"], "were praised"),
    ("Each student ___ a notebook.", ["have", "has", "are"], "has"),
    ("The news ___ surprising.", ["are", "were", "is"], "is"),
    ("She asked me ___ I was ready.", ["if", "what", "which"], "if"),
    ("I would travel more if I ___ time.", ["have", "had", "will have"], "had"),
    ("By next year, I ___ the course.", ["finish", "will have finished", "finished"], "will have finished"),
    ("He is good ___ mathematics.", ["in", "at", "on"], "at"),
    ("We arrived ___ the station early.", ["at", "in", "on"], "at"),
    ("The cat is hiding ___ the table.", ["under", "between", "during"], "under"),
    ("She ___ be at home; the lights are on.", ["must", "must to", "has"], "must"),
    ("I prefer tea ___ coffee.", ["than", "to", "over than"], "to"),
    ("There isn't ___ milk left.", ["many", "much", "few"], "much"),
    ("How ___ students are in your class?", ["much", "many", "little"], "many"),
    ("The man ___ lives next door is kind.", ["which", "who", "where"], "who"),
    ("Please give me ___ information.", ["an", "some", "many"], "some"),
    ("She said that she ___ tired.", ["is", "was", "were"], "was"),
]


def grammar_practice():
    clear_screen()
    main = tk.Frame(root, bg=VERY_LIGHT_BLUE)
    main.pack(fill="both", expand=True)
    page_title(main, "📖 Grammar Practice", "50 questions • Select one answer and submit your quiz")
    questions = random.sample(GRAMMAR_QUESTIONS, min(50, len(GRAMMAR_QUESTIONS)))
    index = [0]
    answers = {}
    selected = tk.StringVar()
    question_label = tk.Label(main, text="", font=("Arial", 18, "bold"), bg=VERY_LIGHT_BLUE, fg=BLACK, wraplength=900)
    question_label.pack(pady=25)
    option_frame = tk.Frame(main, bg=VERY_LIGHT_BLUE)
    option_frame.pack()
    radios = []
    for _ in range(3):
        radio = tk.Radiobutton(option_frame, text="", variable=selected, value="", font=("Arial", 13), bg=VERY_LIGHT_BLUE, fg=BLACK, anchor="w", width=35)
        radio.pack(anchor="w", pady=5)
        radios.append(radio)
    progress_label = tk.Label(main, text="", font=("Arial", 11, "bold"), bg=VERY_LIGHT_BLUE, fg=GREY)
    progress_label.pack(pady=12)
    feedback_label = tk.Label(main, text="", font=("Arial", 11), bg=VERY_LIGHT_BLUE, fg=NAVY, wraplength=800)
    feedback_label.pack(pady=5)

    def load_question():
        q, options, _ = questions[index[0]]
        question_label.config(text=q)
        progress_label.config(text=f"Question {index[0]+1} of {len(questions)}")
        selected.set(answers.get(index[0], ""))
        for i, radio in enumerate(radios):
            radio.config(text=options[i], value=options[i])
        next_btn.config(text="✅ SUBMIT QUIZ" if index[0] == len(questions)-1 else "SAVE & NEXT QUESTION ➜")
        feedback_label.config(text="")

    def finish_quiz():
        if selected.get():
            answers[index[0]] = selected.get()
        correct = sum(1 for i, (_, _, ans) in enumerate(questions) if answers.get(i) == ans)
        score = round(correct / len(questions) * 100)
        review = []
        for i, (q, _, ans) in enumerate(questions):
            chosen = answers.get(i, "Not answered")
            review.append(f"{i+1}. {q}\n   Your answer: {chosen} | Correct answer: {ans}")
        feedback = f"You answered {correct} out of {len(questions)} correctly. " + ("Excellent work!" if score >= 80 else "Review the correct answers below and try again.")
        save_result("Grammar Practice", score, feedback, "Grammar quiz", "\n".join(review), len(questions)-correct)
        clear_screen()
        result = tk.Frame(root, bg=VERY_LIGHT_BLUE)
        result.pack(fill="both", expand=True)
        page_title(result, "📊 Grammar Quiz Analysis", "Your score and answer review are shown below")
        tk.Label(result, text=f"Score: {correct}/{len(questions)}  ({score}/100)", font=("Arial", 23, "bold"), bg=VERY_LIGHT_BLUE, fg=GREEN if score >= 60 else RED).pack(pady=8)
        tk.Label(result, text=feedback, font=("Arial", 12), bg=VERY_LIGHT_BLUE, fg=BLACK).pack(pady=5)
        review_box = tk.Text(result, height=18, width=105, wrap="word", font=("Arial", 10))
        review_box.pack(fill="both", expand=True, padx=35, pady=10)
        review_box.insert("1.0", "\n\n".join(review))
        review_box.config(state="disabled")
        make_button(result, "🔁 TRY GRAMMAR AGAIN", grammar_practice, NAVY, 22, 2).pack(pady=5)
        make_button(result, "🏠 GO TO DASHBOARD", dashboard, GREEN, 22, 2).pack(pady=5)

    def next_question():
        if selected.get() == "":
            messagebox.showwarning("Choose Answer", "Please choose an answer before continuing.")
            return
        answers[index[0]] = selected.get()
        if index[0] == len(questions)-1:
            finish_quiz()
        else:
            index[0] += 1
            load_question()

    next_btn = make_button(main, "SAVE & NEXT QUESTION ➜", next_question, NAVY, 27, 2)
    next_btn.pack(pady=15)
    create_back_button(main)
    load_question()


# ============================================================
# SENTENCE PRACTICE
# ============================================================

def sentence_practice():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "✍ Sentence Practice",
        "Create a complete sentence using the given word"
    )

    # Speaking time selector for the Speak button on this page.
    duration_frame = tk.Frame(main, bg=VERY_LIGHT_BLUE)
    duration_frame.pack(pady=6)
    tk.Label(duration_frame, text="Speaking time limit:", font=("Arial", 11, "bold"),
             bg=VERY_LIGHT_BLUE, fg=NAVY).pack(side="left", padx=6)
    duration_var = tk.StringVar(value="30 seconds")
    ttk.Combobox(duration_frame, textvariable=duration_var,
                 values=["15 seconds", "30 seconds", "45 seconds", "60 seconds", "90 seconds", "120 seconds"],
                 state="readonly", width=14).pack(side="left", padx=6)

    target_word = random.choice(
        list(VOCABULARY.keys())
    )

    tk.Label(
        main,
        text="YOUR WORD",
        font=("Arial", 11, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=GREY
    ).pack(pady=10)

    tk.Label(
        main,
        text=target_word.upper(),
        font=("Arial", 30, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=BLUE
    ).pack()

    text_box = tk.Text(
        main,
        height=8,
        width=85,
        font=("Arial", 13)
    )

    text_box.pack(
        pady=20
    )

    def check():
        text = text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty", "Please write or speak a sentence first.")
            return

        contains_word = target_word.lower() in text.lower()
        score = 100 if contains_word else 50
        feedback = (f"Excellent! Your sentence includes '{target_word}'." if contains_word
                    else f"Your sentence does not include '{target_word}'. Try writing a sentence using this word.")
        save_result("Sentence Practice", score, feedback, text)

        # Display analysis directly on this page instead of using a popup.
        result_frame = tk.Frame(main, bg=WHITE, padx=18, pady=12, relief="solid", bd=1)
        result_frame.pack(fill="x", padx=65, pady=8)
        tk.Label(result_frame, text="📊 YOUR SENTENCE ANALYSIS", font=("Arial", 15, "bold"), bg=WHITE, fg=NAVY).pack(pady=4)
        tk.Label(result_frame, text=f"Your sentence: {text}", font=("Arial", 11), bg=WHITE, fg=BLACK, wraplength=850, justify="left").pack(anchor="w", pady=4)
        tk.Label(result_frame, text=f"Target word: {target_word}", font=("Arial", 11, "bold"), bg=WHITE, fg=BLUE).pack(anchor="w", pady=3)
        tk.Label(result_frame, text=f"Score: {score}/100", font=("Arial", 17, "bold"), bg=WHITE, fg=GREEN if score == 100 else ORANGE).pack(pady=3)
        tk.Label(result_frame, text=feedback, font=("Arial", 11), bg=WHITE, fg=BLACK, wraplength=850).pack(pady=4)
        make_button(result_frame, "🏠 GO TO DASHBOARD", dashboard, GREEN, 22, 2).pack(pady=7)

    def speak():

        duration_seconds = int(duration_var.get().split()[0])

        status = tk.Label(
            main,
            text="🎤 Listening...",
            font=("Arial", 11, "bold"),
            bg=VERY_LIGHT_BLUE,
            fg=BLUE
        )

        status.pack()

        def worker():

            try:

                recognizer = sr.Recognizer()

                with sr.Microphone() as source:

                    recognizer.adjust_for_ambient_noise(
                        source,
                        duration=1
                    )

                    audio = recognizer.listen(
                        source,
                        timeout=10,
                        phrase_time_limit=duration_seconds
                    )

                text = recognizer.recognize_google(
                    audio,
                    language=SPEECH_LANGUAGE
                )

                root.after(
                    0,
                    lambda: insert_spoken_text(
                        text,
                        text_box,
                        status
                    )
                )

            except Exception as error:

                root.after(
                    0,
                    lambda: status.config(
                        text="❌ " + str(error),
                        fg=RED
                    )
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    button_frame = tk.Frame(
        main,
        bg=VERY_LIGHT_BLUE
    )

    button_frame.pack()

    make_button(
        button_frame,
        "🎤 SPEAK",
        speak,
        NAVY,
        18
    ).grid(
        row=0,
        column=0,
        padx=8
    )

    make_button(
        button_frame,
        "✅ SUBMIT & ANALYZE",
        check,
        GREEN,
        18
    ).grid(
        row=0,
        column=1,
        padx=8
    )

    create_back_button(main)


def insert_spoken_text(
    text,
    text_box,
    status
):

    text_box.delete(
        "1.0",
        tk.END
    )

    text_box.insert(
        tk.END,
        text
    )

    status.config(
        text="✅ Voice converted to text.",
        fg=GREEN
    )


# ============================================================
# DAILY CONVERSATION
# ============================================================

def conversation_practice():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "🗣 Daily Conversation",
        "Answer the question naturally in English"
    )

    # Speaking time selector for the Speak Answer button on this page.
    duration_frame = tk.Frame(main, bg=VERY_LIGHT_BLUE)
    duration_frame.pack(pady=6)
    tk.Label(duration_frame, text="Answer time limit:", font=("Arial", 11, "bold"),
             bg=VERY_LIGHT_BLUE, fg=NAVY).pack(side="left", padx=6)
    duration_var = tk.StringVar(value="30 seconds")
    ttk.Combobox(duration_frame, textvariable=duration_var,
                 values=["15 seconds", "30 seconds", "45 seconds", "60 seconds", "90 seconds", "120 seconds"],
                 state="readonly", width=14).pack(side="left", padx=6)

    questions = [

        "What did you learn today?",

        "What is your favorite subject and why?",

        "What is your career goal?",

        "Tell me about your best friend.",

        "What do you do in your free time?",

        "Why do you want to improve your English?",

        "Tell me about your daily routine.",

        "What are your plans for the future?"
    ]

    question = random.choice(
        questions
    )

    card = tk.Frame(
        main,
        bg=WHITE,
        padx=25,
        pady=20,
        relief="solid",
        bd=1
    )

    card.pack(
        fill="x",
        padx=70
    )

    tk.Label(
        card,
        text="QUESTION",
        font=("Arial", 10, "bold"),
        bg=WHITE,
        fg=BLUE
    ).pack()

    tk.Label(
        card,
        text=question,
        font=("Arial", 17, "bold"),
        bg=WHITE,
        fg=BLACK,
        wraplength=850
    ).pack(pady=5)

    text_box = tk.Text(
        main,
        height=10,
        width=90,
        font=("Arial", 13),
        wrap="word"
    )

    text_box.pack(
        pady=15
    )

    status = tk.Label(
        main,
        text="Type your answer or use the microphone.",
        font=("Arial", 11),
        bg=VERY_LIGHT_BLUE,
        fg=GREY
    )

    status.pack()

    def speak():

        duration_seconds = int(duration_var.get().split()[0])

        def worker():

            try:

                recognizer = sr.Recognizer()

                with sr.Microphone() as source:

                    root.after(
                        0,
                        lambda: status.config(
                            text="🎤 Listening...",
                            fg=BLUE
                        )
                    )

                    recognizer.adjust_for_ambient_noise(
                        source,
                        duration=1
                    )

                    audio = recognizer.listen(
                        source,
                        timeout=10,
                        phrase_time_limit=duration_seconds
                    )

                text = recognizer.recognize_google(
                    audio,
                    language=SPEECH_LANGUAGE
                )

                root.after(
                    0,
                    lambda: insert_spoken_text(
                        text,
                        text_box,
                        status
                    )
                )

            except Exception as error:

                root.after(
                    0,
                    lambda: status.config(
                        text="❌ " + str(error),
                        fg=RED
                    )
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def evaluate():

        text = text_box.get(
            "1.0",
            tk.END
        ).strip()

        if not text:

            messagebox.showwarning(
                "No Answer",
                "Please answer the question."
            )

            return

        mistakes, corrections, corrected, vocabulary = analyze_communication(
            text
        )

        word_count = len(
            text.split()
        )

        score = min(
            100,
            max(
                20,
                word_count * 5 - len(mistakes) * 8
            )
        )

        feedback = generate_feedback(
            score,
            len(mistakes),
            word_count
        )

        save_result(
            "Daily Conversation",
            score,
            feedback,
            text,
            corrected,
            len(mistakes)
        )

        show_voice_analysis(
            question,
            text,
            mistakes,
            corrections,
            corrected,
            vocabulary,
            score,
            feedback
        )

    buttons = tk.Frame(
        main,
        bg=VERY_LIGHT_BLUE
    )

    buttons.pack(
        pady=10
    )

    make_button(
        buttons,
        "🎤 SPEAK ANSWER",
        speak,
        NAVY,
        20
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    make_button(
        buttons,
        "🔍 ANALYZE ANSWER",
        evaluate,
        GREEN,
        20
    ).grid(
        row=0,
        column=1,
        padx=5
    )

    create_back_button(main)


# ============================================================
# PRONUNCIATION
# ============================================================

def pronunciation_practice():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    page_title(
        main,
        "🔊 Pronunciation Practice",
        "Listen to the word and repeat it"
    )

    # Speaking time selector for the Repeat Word button on this page.
    duration_frame = tk.Frame(main, bg=VERY_LIGHT_BLUE)
    duration_frame.pack(pady=6)
    tk.Label(duration_frame, text="Repeat time limit:", font=("Arial", 11, "bold"),
             bg=VERY_LIGHT_BLUE, fg=NAVY).pack(side="left", padx=6)
    duration_var = tk.StringVar(value="15 seconds")
    ttk.Combobox(duration_frame, textvariable=duration_var,
                 values=["5 seconds", "10 seconds", "15 seconds", "30 seconds", "45 seconds"],
                 state="readonly", width=14).pack(side="left", padx=6)

    words = [
        "communication",
        "confidence",
        "opportunity",
        "technology",
        "professional",
        "achievement",
        "development",
        "conversation"
    ]

    word = random.choice(
        words
    )

    word_label = tk.Label(
        main,
        text=word,
        font=("Arial", 32, "bold"),
        bg=VERY_LIGHT_BLUE,
        fg=BLUE
    )

    word_label.pack(
        pady=30
    )

    result_label = tk.Label(
        main,
        text="",
        font=("Arial", 14, "bold"),
        bg=VERY_LIGHT_BLUE
    )

    result_label.pack(
        pady=15
    )

    def hear():

        try:

            engine = pyttsx3.init()

            engine.setProperty(
                "rate",
                145
            )

            engine.say(
                word
            )

            engine.runAndWait()

        except Exception as error:

            messagebox.showerror(
                "Voice Error",
                str(error)
            )

    def repeat():

        duration_seconds = int(duration_var.get().split()[0])

        result_label.config(
            text="🎤 Listening...",
            fg=BLUE
        )

        def worker():

            try:

                recognizer = sr.Recognizer()

                with sr.Microphone() as source:

                    recognizer.adjust_for_ambient_noise(
                        source,
                        duration=1
                    )

                    audio = recognizer.listen(
                        source,
                        timeout=10,
                        phrase_time_limit=duration_seconds
                    )

                text = recognizer.recognize_google(
                    audio,
                    language=SPEECH_LANGUAGE
                )

                if word.lower() in text.lower():

                    score = 100

                    result = (
                        "✅ Correct word recognized!\n"
                        f"You said: {text}"
                    )

                else:

                    score = 40

                    result = (
                        "❌ Try again.\n"
                        f"You said: {text}"
                    )

                save_result(
                    "Pronunciation",
                    score,
                    result
                )

                root.after(
                    0,
                    lambda: result_label.config(
                        text=result,
                        fg=GREEN if score == 100 else RED
                    )
                )

            except Exception as error:

                root.after(
                    0,
                    lambda: result_label.config(
                        text="❌ " + str(error),
                        fg=RED
                    )
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    buttons = tk.Frame(
        main,
        bg=VERY_LIGHT_BLUE
    )

    buttons.pack()

    make_button(
        buttons,
        "🔊 HEAR WORD",
        hear,
        NAVY,
        20
    ).grid(
        row=0,
        column=0,
        padx=8
    )

    make_button(
        buttons,
        "🎤 REPEAT WORD",
        repeat,
        GREEN,
        20
    ).grid(
        row=0,
        column=1,
        padx=8
    )

    create_back_button(main)


# ============================================================
# PROGRESS PAGE
# ============================================================

def progress_page():

    clear_screen()

    main = tk.Frame(
        root,
        bg=VERY_LIGHT_BLUE
    )

    main.pack(
        fill="both",
        expand=True
    )

    # Keep this button pinned to the bottom so it remains easy to find.
    make_button(
        main,
        "← BACK TO DASHBOARD",
        dashboard,
        NAVY,
        25,
        2
    ).pack(side="bottom", pady=12)

    page_title(
        main,
        "📊 My Progress",
        "Track your communication improvement"
    )

    conn = database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*), AVG(score)
        FROM results
        WHERE username = ?
        """,
        (current_user,)
    )

    summary = cursor.fetchone()

    cursor.execute(
        """
        SELECT module, AVG(score), COUNT(*)
        FROM results
        WHERE username = ?
        GROUP BY module
        ORDER BY module
        """,
        (current_user,)
    )

    module_data = cursor.fetchall()

    cursor.execute(
        """
        SELECT module, score, date
        FROM results
        WHERE username = ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (current_user,)
    )

    recent_data = cursor.fetchall()

    conn.close()

    total = summary[0] or 0

    average = round(
        summary[1] or 0,
        1
    )

    # ---------------- Summary ----------------

    summary_frame = tk.Frame(
        main,
        bg=VERY_LIGHT_BLUE
    )

    summary_frame.pack(
        pady=5
    )

    make_summary_card(
        summary_frame,
        "TOTAL PRACTICES",
        str(total),
        NAVY
    ).grid(
        row=0,
        column=0,
        padx=8
    )

    make_summary_card(
        summary_frame,
        "AVERAGE SCORE",
        f"{average}/100",
        GREEN
    ).grid(
        row=0,
        column=1,
        padx=8
    )

    # ---------------- Module table ----------------

    table_frame = tk.Frame(
        main,
        bg=WHITE,
        padx=15,
        pady=15,
        relief="solid",
        bd=1
    )

    table_frame.pack(
        fill="x",
        padx=80,
        pady=15
    )

    tk.Label(
        table_frame,
        text="Module Performance",
        font=("Arial", 15, "bold"),
        bg=WHITE,
        fg=NAVY
    ).pack(
        pady=5
    )

    tree = ttk.Treeview(
        table_frame,
        columns=(
            "module",
            "average",
            "attempts"
        ),
        show="headings",
        height=7
    )

    tree.heading(
        "module",
        text="Module"
    )

    tree.heading(
        "average",
        text="Average Score"
    )

    tree.heading(
        "attempts",
        text="Attempts"
    )

    tree.column(
        "module",
        width=350
    )

    tree.column(
        "average",
        width=180,
        anchor="center"
    )

    tree.column(
        "attempts",
        width=150,
        anchor="center"
    )

    tree.pack(
        fill="x"
    )

    for module, avg, attempts in module_data:

        tree.insert(
            "",
            tk.END,
            values=(
                module,
                f"{round(avg, 1)}/100",
                attempts
            )
        )

    if not module_data:

        tk.Label(
            table_frame,
            text="Complete your first practice to see your progress.",
            font=("Arial", 11),
            bg=WHITE,
            fg=GREY
        ).pack(pady=10)

    # ---------------- Recent attempts ----------------

    recent_frame = tk.Frame(
        main,
        bg=WHITE,
        padx=15,
        pady=10,
        relief="solid",
        bd=1
    )

    recent_frame.pack(
        fill="x",
        padx=80,
        pady=5
    )

    tk.Label(
        recent_frame,
        text="Recent Practice",
        font=("Arial", 14, "bold"),
        bg=WHITE,
        fg=NAVY
    ).pack(
        pady=5
    )

    for module, score, date in recent_data:

        tk.Label(
            recent_frame,
            text=f"{date}   |   {module}   |   {score}/100",
            font=("Arial", 10),
            bg=WHITE,
            fg=BLACK
        ).pack(
            anchor="w",
            pady=2
        )

    # ---------------- Graph ----------------

    if MATPLOTLIB_AVAILABLE and module_data:

        def show_graph():

            modules = [
                x[0]
                for x in module_data
            ]

            scores = [
                x[1]
                for x in module_data
            ]

            plt.figure(
                figsize=(10, 5)
            )

            plt.bar(
                modules,
                scores,
                color="#2874A6"
            )

            plt.title(
                "Communication Improvement Progress"
            )

            plt.ylabel(
                "Average Score"
            )

            plt.ylim(
                0,
                100
            )

            plt.xticks(
                rotation=30,
                ha="right"
            )

            plt.tight_layout()

            plt.show()

        make_button(
            main,
            "📈 VIEW PROGRESS GRAPH",
            show_graph,
            BLUE,
            25
        ).pack(pady=8)



# ============================================================
# LOGOUT
# ============================================================

def logout():

    global current_user

    current_user = None

    welcome_page()


# ============================================================
# START APPLICATION
# ============================================================

create_database()

root.title(
    APP_TITLE
)

root.geometry(
    "1200x800"
)

root.minsize(
    1000,
    700
)

root.protocol(
    "WM_DELETE_WINDOW",
    root.destroy
)

welcome_page()

root.mainloop()