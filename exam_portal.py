#!/usr/bin/env python3
# exam_portal.py
# Smart Exam Portal (single-file)
# Features:
# - Tkinter GUI (dark/light theme toggle)
# - Multi-category dashboard (Aptitude, Programming, Computer Science)
# - 50 MCQs per subject (programmatically generated)
# - 5 coding problems per subject (Python problems executable via subprocess)
# - 60-minute timer
# - Session-only profile & stats (no persistent storage)
# - Designed for Python 3.10+ (Windows compatible)

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, filedialog
import tkinter.font as tkfont
import time, random, subprocess, sys, os, tempfile, threading

# ----------------------------
# Configuration
# ----------------------------
DEFAULT_THEME = "dark"
PY_EXEC_TIMEOUT = 6  # seconds per execution
WINDOW_TITLE = "Smart Exam Portal — exam_portal.py (Temporary Session)"
WINDOW_SIZE = "1100x720"
EXAM_DURATION_SECONDS = 60 * 60  # 60 minutes

# Categories and subjects
CATEGORIES = {
    "Aptitude": ["Aptitude"],
    "Programming": ["C", "Java", "Python"],
    "Computer Science": ["DBMS", "CN", "OS"]
}

# Utility: programmatic MCQ generation
def generate_mcqs_for(subject, count=50):
    mcqs = []
    templates = {
        "Aptitude": [
            ("Next in series: {a}, {b}, {c}, {d}, ?", "series"),
            ("If 5x - 3 = 2x + {k}, x = ?", "algebra"),
            ("A train {L} m long crosses a platform in {t} sec at {v} km/h. Platform length = ?", "speed"),
            ("If each side of square increased by {p}%, area increases by ?", "percent"),
            ("Profit: Bought at {c}, sold at {s}. Profit % = ?", "profit"),
        ],
        "C": [
            ("Which header file contains malloc declaration?", "c_stdlib"),
            ("What does the 'static' keyword in C do for a function or variable?", "c_keywords"),
            ("Given int x = {a}; printf(\"%d\", x++); what prints?", "postinc"),
            ("How many bytes is sizeof(char) on most platforms?", "size"),
            ("Which is true about pointer arithmetic: {i}?", "c_basic"),
        ],
        "Java": [
            ("Which keyword is used to inherit a class in Java?", "inherit"),
            ("Which interface is used to implement runnable threads?", "threads"),
            ("What is the output of: System.out.println(5/2);", "div"),
            ("Which collection is synchronized by default?", "collections"),
            ("What is the default value of boolean in Java?", "default"),
        ],
        "Python": [
            ("What does list comprehension [x*x for x in range({n})] produce?", "list_comp"),
            ("What is the output of: print(3//2)?", "floor_div"),
            ("Which keyword creates a generator?", "yield"),
            ("Which type is immutable: list or tuple?", "immut"),
            ("What does 'None' represent in Python?", "none"),
        ],
        "DBMS": [
            ("What is normalization's aim?", "normal"),
            ("Which normal form resolves partial dependency?", "2nf"),
            ("Define primary key uniqueness: True/False", "pk"),
            ("What SQL clause filters result rows?", "where"),
            ("Which operation is used for joining two relations?", "join"),
        ],
        "CN": [
            ("OSI layer that handles routing is?", "network"),
            ("What protocol ensures reliable byte stream?", "tcp"),
            ("Which device operates at data-link layer?", "switch"),
            ("IP address v4 is how many bits?", "ipv4"),
            ("What does DNS resolve?", "domain"),
        ],
        "OS": [
            ("Which scheduling is preemptive: Round Robin or FCFS?", "rr"),
            ("What is a process vs thread?", "proc_thread"),
            ("Which condition denotes deadlock?", "deadlock"),
            ("Virtual memory uses which structure?", "paging"),
            ("What is a semaphore used for?", "sync"),
        ]
    }

    diffs = ["Easy"] * (count//2) + ["Medium"] * (count//3) + ["Hard"] * (count - (count//2) - (count//3))
    random.shuffle(diffs)
    tpls = templates.get(subject, templates["Aptitude"])

    for i in range(count):
        tpl = random.choice(tpls)
        diff = diffs[i]
        # provide formatting values
        vals = {
            "a": random.randint(2,5),
            "b": random.randint(6,12),
            "c": random.randint(13,20),
            "d": random.randint(21,30),
            "k": random.randint(5,20),
            "L": random.randint(80,320),
            "t": random.randint(6,40),
            "v": random.choice([30,36,45,60]),
            "p": random.choice([5,10,12,15,20]),
            "c": random.randint(500,2000),
            "s": random.randint(1200,4000),
            "i": random.choice(["pointer arithmetic", "garbage collection", "automatic resize"]),
            "n": random.randint(3,8)
        }
        qtext = tpl[0].format(**vals)
        opts = []
        correct_index = random.randint(1,4)
        for j in range(4):
            if tpl[1] == "series":
                opts.append(str(random.choice([36,40,42,56,72,90])))
            elif tpl[1] == "algebra":
                opts.append(str(random.randint(1,20)))
            elif tpl[1] == "speed":
                opts.append(str(random.choice([80,120,200,160,240])))
            elif tpl[1] == "percent":
                opts.append(str(random.choice(["10%","20%","21%","19%"])))
            elif tpl[1] == "profit":
                opts.append(str(random.choice(["20%","25%","15%","30%"])))
            elif tpl[1] in ("c_basic","c_keywords","c_stdlib","postinc","size"):
                opts.append(random.choice(["stdio.h","stdlib.h","string.h","math.h","static-local"]))
            elif tpl[1] in ("inherit","threads","div","collections","default"):
                opts.append(random.choice(["extends","implements","synchronized","true","false","2"]))
            elif tpl[1] in ("list_comp","floor_div","yield","immut","none"):
                opts.append(random.choice(["[0,1,4]","1","generator","tuple","no value"]))
            elif tpl[1] in ("normal","2nf","pk","where","join"):
                opts.append(random.choice(["remove redundancy","2NF","true","WHERE","JOIN"]))
            elif tpl[1] in ("network","tcp","switch","ipv4","domain"):
                opts.append(random.choice(["Network","TCP","Switch","32 bits","Domain to IP"]))
            elif tpl[1] in ("rr","proc_thread","deadlock","paging","sync"):
                opts.append(random.choice(["Round Robin","Process","Mutual Exclusion","Paging","Semaphore"]))
            else:
                opts.append(str(random.randint(1,100)))
        opts = opts[:4]
        mcqs.append({
            "question": f"{subject}: {qtext} ({diff})",
            "options": opts,
            "answer": correct_index,
            "difficulty": diff
        })
    return mcqs

# Build question bank
QUESTION_BANK = {}
SUBJECTS = []
for cat, subjects in CATEGORIES.items():
    for s in subjects:
        SUBJECTS.append(s)
        QUESTION_BANK[s] = generate_mcqs_for(s, count=50)

# Coding bank (Python problems are executable)
CODING_BANK = {
    "Python": [
        {"title":"Easy: Sum of list", "desc":"Write a function solve() that reads a line of integers separated by spaces and prints their sum."},
        {"title":"Easy-Mid: Count vowels", "desc":"Write solve() that reads a line, counts vowels (a,e,i,o,u) and prints the count."},
        {"title":"Medium: Unique words", "desc":"Write solve() that reads a sentence and prints number of unique words (case-insensitive)."},
        {"title":"Hard: Longest increasing subsequence length", "desc":"Write solve() that reads integers and prints length of LIS."},
        {"title":"Harder: Evaluate expression", "desc":"Write solve() that evaluates a single-line arithmetic expression (safe eval) and prints result."}
    ],
    "C": [
        {"title":"Easy: Hello World variant", "desc":"Write a C program that prints a pattern or 'Hello from C' (for practice)."},
        {"title":"Easy-Mid: Pointers practice", "desc":"Write a C function that swaps two integers using pointers."},
        {"title":"Medium: String reverse", "desc":"Write a C program to reverse a string in place."},
        {"title":"Hard: Dynamic memory", "desc":"Write code to allocate and resize an integer array using malloc/realloc."},
        {"title":"Harder: Implement linked list", "desc":"Write code to implement a singly linked list with insert/delete."}
    ],
    "Java": [
        {"title":"Easy: Hello Java", "desc":"Write a Java program that prints 'Hello Java' and demonstrates main method."},
        {"title":"Easy-Mid: Class & Object", "desc":"Implement a simple class with attributes and a method."},
        {"title":"Medium: Array operations", "desc":"Write Java code to find second largest element in an array."},
        {"title":"Hard: Threads demo", "desc":"Create multi-threaded Java example demonstrating Runnable."},
        {"title":"Harder: Data structures", "desc":"Implement stack using linked list in Java."}
    ],
    "DBMS": [
        {"title":"Easy: SQL SELECT", "desc":"Write SQL to select top-N records from a table."},
        {"title":"Easy-Mid: JOIN query", "desc":"Write SQL to join two tables on a key."},
        {"title":"Medium: Normalization", "desc":"Explain/Show steps to normalize a table to 3NF (text answer)."},
        {"title":"Hard: Transaction", "desc":"Design transactions to avoid lost update (explain)."},
        {"title":"Harder: Query optimization", "desc":"Explain indexes and how to optimize a query."}
    ],
    "CN": [
        {"title":"Easy: Describe IP", "desc":"Explain IPv4 address structure (text)."},
        {"title":"Easy-Mid: Subnetting", "desc":"Given CIDR /24, how many hosts? (text)"},
        {"title":"Medium: Routing", "desc":"Explain how OSPF works at high level."},
        {"title":"Hard: Congestion control", "desc":"Explain TCP congestion control algorithms."},
        {"title":"Harder: Protocol design", "desc":"Design a simple reliable message protocol (text)."}
    ],
    "OS": [
        {"title":"Easy: Process vs Thread", "desc":"Explain difference between process and thread."},
        {"title":"Easy-Mid: Scheduling", "desc":"Given processes, compute turnaround time for Round Robin."},
        {"title":"Medium: Critical section", "desc":"Write pseudocode to solve mutual exclusion with semaphores."},
        {"title":"Hard: Virtual memory", "desc":"Explain demand paging and page replacement algorithms."},
        {"title":"Harder: Kernel modules", "desc":"Describe how kernel modules are loaded/unloaded (text)."}
    ],
    "Aptitude": [
        {"title":"Easy: Simple Interest", "desc":"Compute simple interest for principal, rate, time."},
        {"title":"Easy-Mid: Percentage", "desc":"Find percentage increase for given values."},
        {"title":"Medium: Series", "desc":"Find next in numeric series."},
        {"title":"Hard: Time & Work", "desc":"Solve combined work-rate problems."},
        {"title":"Harder: Combinatorics", "desc":"Counting/permutation combinatorics problem."}
    ]
}

# ----------------------------
# Session profile and helpers
# ----------------------------
class SessionProfile:
    def __init__(self, username):
        self.username = username
        self.tests_taken = []
        self.start_time = time.time()

    def record_test(self, summary):
        self.tests_taken.append(summary)

    def get_overall_accuracy(self):
        total_q = 0
        correct = 0
        for t in self.tests_taken:
            total_q += t.get("total_questions",0)
            correct += t.get("correct",0)
        if total_q == 0: return 0.0
        return (correct/total_q)*100.0

    def subject_accuracy(self):
        subj = {}
        for t in self.tests_taken:
            name = t.get("subject","Unknown")
            subj.setdefault(name, {"correct":0,"total":0})
            subj[name]["correct"] += t.get("correct",0)
            subj[name]["total"] += t.get("total_questions",0)
        out = {}
        for k,v in subj.items():
            if v["total"]==0: out[k]=0.0
            else: out[k]= (v["correct"]/v["total"])*100.0
        return out

# ----------------------------
# Main Tkinter App
# ----------------------------
class SmartExamApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(1000, 650)
        self.theme = DEFAULT_THEME
        # fonts
        self.title_font = tkfont.Font(family="Inter", size=18, weight="bold")
        self.h2_font = tkfont.Font(family="Inter", size=14, weight="bold")
        self.normal_font = tkfont.Font(family="Inter", size=11)
        self.small_font = tkfont.Font(family="Inter", size=10)

        # user login
        username = simpledialog.askstring("Login", "Enter your name for the session:", parent=self.root)
        if not username:
            username = "Guest"
        self.profile = SessionProfile(username)

        # UI frames
        self.create_menu()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        self.apply_theme()
        self.show_home()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        app_menu = tk.Menu(menubar, tearoff=0)
        app_menu.add_command(label="Home", command=self.show_home)
        app_menu.add_command(label="Profile", command=self.show_profile)
        app_menu.add_separator()
        app_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="App", menu=app_menu)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)

    def clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def toggle_theme(self):
        self.theme = "light" if self.theme=="dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "dark":
            self.bg = "#0f1720"
            self.fg = "#e6eef8"
            self.card = "#111827"
            self.control_bg = "#0b1220"
            self.btn_bg = "#0ea5a4"
            self.btn_fg = "#ffffff"
        else:
            self.bg = "#f3f4f6"
            self.fg = "#111827"
            self.card = "#ffffff"
            self.control_bg = "#ffffff"
            self.btn_bg = "#2563eb"
            self.btn_fg = "#ffffff"
        self.root.configure(bg=self.bg)
        for w in self.main_frame.winfo_children():
            try:
                w.configure(bg=self.bg)
            except:
                pass

    def show_home(self):
        self.clear_main()
        self.apply_theme()
        top = tk.Frame(self.main_frame, bg=self.bg)
        top.pack(fill="x", padx=18, pady=12)
        title = tk.Label(top, text="Smart Exam Portal", font=self.title_font, bg=self.bg, fg=self.fg)
        title.pack(side="left")
        user_lbl = tk.Label(top, text=f"User: {self.profile.username}", font=self.normal_font, bg=self.bg, fg=self.fg)
        user_lbl.pack(side="right")
        body = tk.Frame(self.main_frame, bg=self.bg)
        body.pack(fill="both", expand=True, padx=18, pady=6)
        left = tk.Frame(body, width=360, bg=self.bg)
        left.pack(side="left", fill="y", padx=(0,12))
        for cat, subs in CATEGORIES.items():
            card = tk.Frame(left, bg=self.card, bd=0, relief="ridge", padx=10, pady=8)
            card.pack(fill="x", pady=8)
            lbl = tk.Label(card, text=cat, font=self.h2_font, bg=self.card, fg=self.fg)
            lbl.pack(anchor="w")
            desc = tk.Label(card, text=f"{len(subs)} subjects", font=self.small_font, bg=self.card, fg=self.fg)
            desc.pack(anchor="w")
            for s in subs:
                btn = tk.Button(card, text=f"Open {s}", command=lambda sub=s: self.show_subject(sub),
                                bg=self.btn_bg, fg=self.btn_fg, relief="flat")
                btn.pack(side="left", padx=4, pady=6)

        right = tk.Frame(body, bg=self.bg)
        right.pack(side="left", fill="both", expand=True)
        actions = tk.Frame(right, bg=self.card, padx=12, pady=12)
        actions.pack(fill="x")
        a1 = tk.Button(actions, text="All Tests", command=self.show_all_tests, bg=self.btn_bg, fg=self.btn_fg, relief="flat")
        a1.pack(side="left", padx=6)
        a2 = tk.Button(actions, text="Profile", command=self.show_profile, bg=self.btn_bg, fg=self.btn_fg, relief="flat")
        a2.pack(side="left", padx=6)

        recent = tk.Frame(right, bg=self.card, padx=12, pady=12)
        recent.pack(fill="both", expand=True, pady=12)
        rlbl = tk.Label(recent, text="Session Summary", font=self.h2_font, bg=self.card, fg=self.fg)
        rlbl.pack(anchor="w")
        self.summary_text = tk.Text(recent, height=12, bg=self.card, fg=self.fg, bd=0)
        self.summary_text.pack(fill="both", expand=True, pady=8)
        self.update_summary_text()

    def update_summary_text(self):
        self.summary_text.delete("1.0", tk.END)
        acc = self.profile.get_overall_accuracy()
        self.summary_text.insert(tk.END, f"Overall accuracy: {acc:.2f}%\n")
        self.summary_text.insert(tk.END, f"Total tests taken: {len(self.profile.tests_taken)}\n\n")
        for t in self.profile.tests_taken[-8:]:
            self.summary_text.insert(tk.END, f"- {t.get('subject')} | {t.get('mode')} | Score: {t.get('correct')}/{t.get('total_questions')} | Time: {t.get('time_taken'):.1f}s\n")

    def show_all_tests(self):
        self.clear_main()
        self.apply_theme()
        header = tk.Frame(self.main_frame, bg=self.bg)
        header.pack(fill="x", padx=12, pady=8)
        lbl = tk.Label(header, text="All Available Tests", font=self.title_font, bg=self.bg, fg=self.fg)
        lbl.pack(anchor="w")
        container = tk.Frame(self.main_frame, bg=self.bg)
        container.pack(fill="both", expand=True, padx=12, pady=6)
        for subj in SUBJECTS:
            card = tk.Frame(container, bg=self.card, padx=10, pady=10)
            card.pack(fill="x", pady=6)
            l = tk.Label(card, text=subj, font=self.h2_font, bg=self.card, fg=self.fg)
            l.pack(side="left")
            mbtn = tk.Button(card, text="MCQ Test", command=lambda s=subj: self.start_mcq_test(s),
                             bg=self.btn_bg, fg=self.btn_fg, relief="flat")
            mbtn.pack(side="right", padx=6)
            cbtn = tk.Button(card, text="Coding Test", command=lambda s=subj: self.start_coding_test(s),
                             bg=self.btn_bg, fg=self.btn_fg, relief="flat")
            cbtn.pack(side="right", padx=6)

    def show_subject(self, subject):
        self.clear_main()
        self.apply_theme()
        header = tk.Frame(self.main_frame, bg=self.bg)
        header.pack(fill="x", padx=12, pady=8)
        tk.Label(header, text=f"{subject} — Tests", font=self.title_font, bg=self.bg, fg=self.fg).pack(anchor="w")
        body = tk.Frame(self.main_frame, bg=self.bg)
        body.pack(fill="both", expand=True, padx=12, pady=6)

        mcq_card = tk.Frame(body, bg=self.card, padx=12, pady=12)
        mcq_card.pack(fill="x", pady=6)
        tk.Label(mcq_card, text="MCQ Test", font=self.h2_font, bg=self.card, fg=self.fg).pack(anchor="w")
        tk.Label(mcq_card, text="50 MCQs covering full subject skills (mixed difficulties).", bg=self.card, fg=self.fg).pack(anchor="w")
        tk.Button(mcq_card, text="Start MCQ Test", command=lambda s=subject: self.start_mcq_test(s),
                  bg=self.btn_bg, fg=self.btn_fg, relief="flat").pack(anchor="e", pady=6)

        cod_card = tk.Frame(body, bg=self.card, padx=12, pady=12)
        cod_card.pack(fill="x", pady=6)
        tk.Label(cod_card, text="Coding Test", font=self.h2_font, bg=self.card, fg=self.fg).pack(anchor="w")
        tk.Label(cod_card, text="5 coding problems: Easy → Hard. Python problems are executable.", bg=self.card, fg=self.fg).pack(anchor="w")
        tk.Button(cod_card, text="Start Coding Test", command=lambda s=subject: self.start_coding_test(s),
                  bg=self.btn_bg, fg=self.btn_fg, relief="flat").pack(anchor="e", pady=6)

    def start_mcq_test(self, subject):
        mcqs = QUESTION_BANK.get(subject, [])[:]
        if not mcqs:
            messagebox.showerror("No questions", "No MCQs available for this subject.")
            return
        random.shuffle(mcqs)
        TestWindow(self, subject, mcqs, mode="MCQ")

    def start_coding_test(self, subject):
        problems = CODING_BANK.get(subject, [])
        if not problems:
            messagebox.showerror("No problems", "No coding problems for this subject.")
            return
        CodingWindow(self, subject, problems)

    def show_profile(self):
        self.clear_main()
        self.apply_theme()
        top = tk.Frame(self.main_frame, bg=self.bg)
        top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text="Profile Dashboard", font=self.title_font, bg=self.bg, fg=self.fg).pack(anchor="w")
        body = tk.Frame(self.main_frame, bg=self.bg)
        body.pack(fill="both", expand=True, padx=12, pady=8)
        left = tk.Frame(body, bg=self.card, padx=12, pady=12)
        left.pack(side="left", fill="y")
        tk.Label(left, text=f"User: {self.profile.username}", font=self.h2_font, bg=self.card, fg=self.fg).pack(anchor="w")
        tk.Label(left, text=f"Overall Accuracy: {self.profile.get_overall_accuracy():.2f}%", bg=self.card, fg=self.fg).pack(anchor="w", pady=6)
        tk.Label(left, text=f"Tests Taken: {len(self.profile.tests_taken)}", bg=self.card, fg=self.fg).pack(anchor="w", pady=6)
        subj_acc = self.profile.subject_accuracy()
        acc_frame = tk.Frame(body, bg=self.bg)
        acc_frame.pack(side="left", fill="both", expand=True, padx=12)
        tk.Label(acc_frame, text="Subject-wise Accuracy", font=self.h2_font, bg=self.bg, fg=self.fg).pack(anchor="w")
        for k,v in subj_acc.items():
            bar_frame = tk.Frame(acc_frame, bg=self.card)
            bar_frame.pack(fill="x", pady=6)
            tk.Label(bar_frame, text=k, bg=self.card, fg=self.fg).pack(side="left")
            val = tk.Label(bar_frame, text=f"{v:.1f}%", bg=self.card, fg=self.fg)
            val.pack(side="right")
        table = tk.Frame(body, bg=self.bg)
        table.pack(side="bottom", fill="both", padx=12, pady=8)
        tk.Label(table, text="Recent Tests", font=self.h2_font, bg=self.bg, fg=self.fg).pack(anchor="w")
        txt = tk.Text(table, height=10, bg=self.card, fg=self.fg, bd=0)
        txt.pack(fill="both", expand=True)
        for t in self.profile.tests_taken[-20:]:
            txt.insert(tk.END, f"{t.get('subject')} | {t.get('mode')} | Score: {t.get('correct')}/{t.get('total_questions')} | Time: {t.get('time_taken'):.1f}s\n")

# ----------------------------
# MCQ Test Window
# ----------------------------
class TestWindow:
    def __init__(self, app: SmartExamApp, subject, questions, mode="MCQ"):
        self.app = app
        self.subject = subject
        self.questions = questions
        self.mode = mode
        self.root = tk.Toplevel(app.root)
        self.root.title(f"{subject} — {mode} Test")
        self.root.geometry("1000x660")
        self.root.minsize(900,600)

        # session state
        self.num_q = len(questions)
        self.current = 0
        self.selected = [0]*self.num_q
        self.visited = [False]*self.num_q
        self.marked = [False]*self.num_q
        self.time_started = time.time()
        self.per_q_time = [0.0]*self.num_q
        self.q_start_time = time.time()
        self.remaining_sec = EXAM_DURATION_SECONDS

        # build UI
        self.build_ui()
        self.update_timer()
        self.display_question(0)

    def build_ui(self):
        top = tk.Frame(self.root, bg=self.app.bg)
        top.pack(fill="x")
        tk.Label(top, text=f"{self.subject} — MCQ Test", font=self.app.h2_font, bg=self.app.bg, fg=self.app.fg).pack(side="left", padx=12, pady=8)
        self.timer_lbl = tk.Label(top, text="", bg=self.app.bg, fg="#ffecd1")
        self.timer_lbl.pack(side="right", padx=12)

        main = tk.Frame(self.root, bg=self.app.bg)
        main.pack(fill="both", expand=True, padx=12, pady=6)
        left = tk.Frame(main, width=260, bg=self.app.card)
        left.pack(side="left", fill="y", padx=(0,8))
        left.pack_propagate(False)
        tk.Label(left, text="Navigator", bg=self.app.card, fg=self.app.fg).pack(pady=6)
        self.nav_frame = tk.Frame(left, bg=self.app.card)
        self.nav_frame.pack(fill="y", expand=True)
        self.nav_buttons = []
        for i in range(self.num_q):
            b = tk.Button(self.nav_frame, text=str(i+1), width=4, command=lambda idx=i: self.goto(idx), bg="#2b3440", fg=self.app.fg)
            b.grid(row=i//10, column=i%10, padx=2, pady=4)
            self.nav_buttons.append(b)

        right = tk.Frame(main, bg=self.app.bg)
        right.pack(side="left", fill="both", expand=True)
        self.q_label = tk.Label(right, text="", font=self.app.normal_font, wraplength=680, justify="left", bg=self.app.card, fg=self.app.fg)
        self.q_label.pack(fill="x", pady=10, padx=6)
        self.var = tk.IntVar(value=0)
        self.opt_rbs = []
        for i in range(4):
            rb = tk.Radiobutton(right, text="", variable=self.var, value=i+1, font=self.app.normal_font, anchor="w", justify="left",
                                command=self.on_select, bg=self.app.card, fg=self.app.fg, selectcolor=self.app.card)
            rb.pack(fill="x", pady=6, padx=12)
            self.opt_rbs.append(rb)

        footer = tk.Frame(self.root, bg=self.app.bg)
        footer.pack(fill="x", padx=12, pady=8)
        tk.Button(footer, text="Previous", command=self.prev_q, bg=self.app.btn_bg, fg=self.app.btn_fg).pack(side="left")
        tk.Button(footer, text="Save & Next", command=self.save_next, bg=self.app.btn_bg, fg=self.app.btn_fg).pack(side="left", padx=6)
        tk.Button(footer, text="Mark/Unmark Review", command=self.toggle_mark, bg=self.app.btn_bg, fg=self.app.btn_fg).pack(side="left", padx=6)
        tk.Button(footer, text="Submit Test", command=self.submit).pack(side="right")
        tk.Button(footer, text="Cancel", command=self.root.destroy).pack(side="right", padx=6)

    def update_timer(self):
        elapsed = int(time.time() - self.time_started)
        remaining = max(0, self.remaining_sec - elapsed)
        mins, secs = divmod(remaining, 60)
        self.timer_lbl.config(text=f"Time Remaining: {mins:02d}:{secs:02d}")
        if remaining <= 0:
            self.submit()
        else:
            self.root.after(1000, self.update_timer)

    def display_question(self, idx):
        # save time spent on previous before switching
        now = time.time()
        if hasattr(self, "q_start_time") and self.q_start_time:
            self.per_q_time[self.current] += now - self.q_start_time
        self.q_start_time = now
        self.current = idx
        q = self.questions[idx]
        self.q_label.config(text=f"Q{idx+1}. {q['question']}")
        self.var.set(self.selected[idx])
        for i,opt in enumerate(q["options"]):
            self.opt_rbs[i].config(text=f"{chr(65+i)}. {opt}")
        self.visited[idx] = True
        self.update_nav_colors()

    def on_select(self):
        sel = self.var.get()
        self.selected[self.current] = sel
        self.update_nav_colors()

    def goto(self, idx):
        self.display_question(idx)

    def prev_q(self):
        if self.current > 0:
            self.display_question(self.current - 1)

    def save_next(self):
        if self.current < self.num_q - 1:
            self.display_question(self.current + 1)
        else:
            messagebox.showinfo("End", "You are at the last question.")

    def toggle_mark(self):
        self.marked[self.current] = not self.marked[self.current]
        self.update_nav_colors()

    def update_nav_colors(self):
        for i,b in enumerate(self.nav_buttons):
            if self.marked[i]:
                b.config(bg="#ff9f1c")  # orange
            elif self.selected[i] != 0:
                b.config(bg="#10b981")  # green
            elif self.visited[i]:
                b.config(bg="#fbbf24")  # yellow
            else:
                b.config(bg="#2b3440")  # default

    def submit(self):
        now = time.time()
        if self.q_start_time:
            self.per_q_time[self.current] += now - self.q_start_time
        total_time = time.time() - self.time_started
        correct = 0
        attempted = 0
        for i,q in enumerate(self.questions):
            if self.selected[i] != 0:
                attempted += 1
                if self.selected[i] == q.get("answer", 1):
                    correct += 1
        total = self.num_q
        percent = (correct/total)*100.0
        avg_time = sum(self.per_q_time)/max(1,total)
        summary = {
            "subject": self.subject,
            "mode": "MCQ",
            "correct": correct,
            "attempted": attempted,
            "total_questions": total,
            "time_taken": total_time,
            "avg_time_per_question": avg_time
        }
        self.app.profile.record_test(summary)
        self.app.update_summary_text()
        ResultWindow(self.app, summary)
        self.root.destroy()

# ----------------------------
# Coding Window
# ----------------------------
class CodingWindow:
    def __init__(self, app: SmartExamApp, subject, problems):
        self.app = app
        self.subject = subject
        self.problems = problems
        self.root = tk.Toplevel(app.root)
        self.root.title(f"{subject} — Coding Test")
        self.root.geometry("1000x700")
        self.current = 0
        self.num = len(problems)
        self.answers = [""]*self.num
        self.times = [0.0]*self.num
        self.start_time = time.time()
        self.q_start = time.time()
        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root, bg=self.app.bg)
        top.pack(fill="x")
        tk.Label(top, text=f"{self.subject} — Coding Test", font=self.app.h2_font, bg=self.app.bg, fg=self.app.fg).pack(side="left", padx=10, pady=8)
        tk.Label(top, text="Note: Only Python problems are executable. For others, write code as text (no execution).", bg=self.app.bg, fg=self.app.fg).pack(side="right", padx=8)

        main = tk.Frame(self.root, bg=self.app.bg)
        main.pack(fill="both", expand=True, padx=10, pady=8)
        left = tk.Frame(main, width=260, bg=self.app.card)
        left.pack(side="left", fill="y", padx=(0,8))
        left.pack_propagate(False)
        tk.Label(left, text="Problems", bg=self.app.card, fg=self.app.fg).pack(pady=6)
        for i,p in enumerate(self.problems):
            b = tk.Button(left, text=f"{i+1}. {p['title']}", anchor="w", justify="left",
                          command=lambda idx=i: self.show_problem(idx), bg="#24303a", fg=self.app.fg)
            b.pack(fill="x", pady=4, padx=6)

        right = tk.Frame(main, bg=self.app.bg)
        right.pack(side="left", fill="both", expand=True)
        self.title_lbl = tk.Label(right, text="", font=self.app.h2_font, bg=self.app.card, fg=self.app.fg)
        self.title_lbl.pack(anchor="w", fill="x", padx=6, pady=6)
        self.desc_lbl = tk.Label(right, text="", bg=self.app.card, fg=self.app.fg, wraplength=700, justify="left")
        self.desc_lbl.pack(anchor="w", padx=6)
        self.editor = scrolledtext.ScrolledText(right, height=20, bg="#0b1220", fg="#e6eef8", insertbackground="#fff")
        self.editor.pack(fill="both", expand=True, padx=6, pady=8)

        ctrl = tk.Frame(self.root, bg=self.app.bg)
        ctrl.pack(fill="x", padx=8, pady=6)
        tk.Button(ctrl, text="Run (Python only)", command=self.run_code, bg="#06b6d4", fg="#000").pack(side="left", padx=6)
        tk.Button(ctrl, text="Save Answer", command=self.save_answer, bg=self.app.btn_bg, fg=self.app.btn_fg).pack(side="left", padx=6)
        tk.Button(ctrl, text="Submit Test", command=self.submit).pack(side="right", padx=6)
        tk.Button(ctrl, text="Cancel", command=self.root.destroy).pack(side="right", padx=6)

        outlbl = tk.Label(self.root, text="Output:", bg=self.app.bg, fg=self.app.fg)
        outlbl.pack(anchor="w", padx=12)
        self.output_area = scrolledtext.ScrolledText(self.root, height=8, bg="#02111b", fg="#bfefff")
        self.output_area.pack(fill="x", padx=12, pady=6)
        self.show_problem(0)

    def show_problem(self, idx):
        now = time.time()
        self.times[self.current] += now - self.q_start
        self.q_start = now
        self.current = idx
        p = self.problems[idx]
        self.title_lbl.config(text=f"{idx+1}. {p['title']}")
        self.desc_lbl.config(text=p['desc'])
        self.editor.delete("1.0", tk.END)
        self.editor.insert(tk.END, self.answers[idx])

    def save_answer(self):
        code = self.editor.get("1.0", tk.END).rstrip()
        self.answers[self.current] = code
        messagebox.showinfo("Saved", "Answer saved locally in session.")

    def run_code(self):
        if self.subject != "Python":
            messagebox.showwarning("Not supported", "Only Python problems are executable in this demo. For other languages, save answers as text.")
            return
        code = self.editor.get("1.0", tk.END).rstrip()
        if not code.strip():
            messagebox.showerror("No code", "Please write some Python code to run.")
            return
        tmpdir = tempfile.gettempdir()
        fname = os.path.join(tmpdir, f"exam_user_code_{int(time.time()*1000)}.py")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        def run_and_capture():
            try:
                proc = subprocess.run([sys.executable, fname], capture_output=True, text=True, timeout=PY_EXEC_TIMEOUT)
                out = proc.stdout
                err = proc.stderr
                self.output_area.delete("1.0", tk.END)
                if out:
                    self.output_area.insert(tk.END, "=== STDOUT ===\n")
                    self.output_area.insert(tk.END, out)
                if err:
                    self.output_area.insert(tk.END, "\n=== STDERR ===\n")
                    self.output_area.insert(tk.END, err)
            except subprocess.TimeoutExpired:
                self.output_area.insert(tk.END, "ERROR: Execution timed out.\n")
            except Exception as e:
                self.output_area.insert(tk.END, f"ERROR running code: {e}\n")
            finally:
                try:
                    os.remove(fname)
                except:
                    pass
        threading.Thread(target=run_and_capture, daemon=True).start()

    def submit(self):
        total = self.num
        solved = 0
        for i, ans in enumerate(self.answers):
            if ans and len(ans.strip())>20:
                solved += 1
        score = solved
        total_time = time.time() - self.start_time
        summary = {
            "subject": self.subject,
            "mode": "Coding",
            "correct": score,
            "attempted": solved,
            "total_questions": total,
            "time_taken": total_time
        }
        self.app.profile.record_test(summary)
        self.app.update_summary_text()
        ResultWindow(self.app, summary)
        self.root.destroy()

# ----------------------------
# Result Window
# ----------------------------
class ResultWindow:
    def __init__(self, app: SmartExamApp, summary: dict):
        self.app = app
        self.summary = summary
        self.root = tk.Toplevel(app.root)
        self.root.title("Test Result")
        self.root.geometry("560x420")
        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root, bg=self.app.bg)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="Test Result", font=self.app.h2_font, bg=self.app.bg, fg=self.app.fg).pack(anchor="w")
        body = tk.Frame(self.root, bg=self.app.card, padx=12, pady=12)
        body.pack(fill="both", expand=True, padx=10, pady=6)
        sbj = self.summary.get("subject","Unknown")
        mode = self.summary.get("mode","MCQ")
        tk.Label(body, text=f"Subject: {sbj}", bg=self.app.card, fg=self.app.fg).pack(anchor="w")
        tk.Label(body, text=f"Mode: {mode}", bg=self.app.card, fg=self.app.fg).pack(anchor="w")
        tk.Label(body, text=f"Score: {self.summary.get('correct')} / {self.summary.get('total_questions')}", bg=self.app.card, fg=self.app.fg).pack(anchor="w", pady=6)
        if mode == "MCQ":
            tk.Label(body, text=f"Attempted: {self.summary.get('attempted')}", bg=self.app.card, fg=self.app.fg).pack(anchor="w")
            tk.Label(body, text=f"Time Taken: {self.summary.get('time_taken'):.1f} seconds", bg=self.app.card, fg=self.app.fg).pack(anchor="w")
            tk.Label(body, text=f"Avg Time / Q: {self.summary.get('avg_time_per_question',0):.2f} seconds", bg=self.app.card, fg=self.app.fg).pack(anchor="w")
        else:
            tk.Label(body, text=f"Problems Solved (crude): {self.summary.get('correct')}", bg=self.app.card, fg=self.app.fg).pack(anchor="w")
            tk.Label(body, text=f"Time Taken: {self.summary.get('time_taken'):.1f} seconds", bg=self.app.card, fg=self.app.fg).pack(anchor="w")
        btn_frame = tk.Frame(self.root, bg=self.app.bg)
        btn_frame.pack(fill="x", pady=8)
        tk.Button(btn_frame, text="Back to Dashboard", command=self.root.destroy, bg=self.app.btn_bg, fg=self.app.btn_fg).pack(side="left", padx=8)
        tk.Button(btn_frame, text="View Profile", command=lambda: [self.root.destroy(), self.app.show_profile()]).pack(side="left", padx=8)

# ----------------------------
# Run App
# ----------------------------
def main():
    root = tk.Tk()
    app = SmartExamApp(root)
    app.apply_theme()
    root.mainloop()

if __name__ == "__main__":
    main()
