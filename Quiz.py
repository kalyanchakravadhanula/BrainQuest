import tkinter as tk
from tkinter import messagebox, simpledialog, font
import random
import time

# ----------------------------
# CONFIG
# ----------------------------
TOTAL_TIME_SECONDS = 30 * 60  # 30 minutes (change if you want)
# If you want a shorter trial time while testing, set e.g. TOTAL_TIME_SECONDS = 120

# ----------------------------
# DATA: 25 Aptitude & Reasoning MCQs
# (Answers are 1-based indices)
# ----------------------------
exam_data = [
    {"question": "1) Next in series: 2, 6, 12, 20, 30, ?", "options": ["36", "40", "42", "56"], "answer": 3},
    {"question": "2) If 5x - 3 = 2x + 12, x = ?", "options": ["3", "5", "7", "15"], "answer": 2},
    {"question": "3) Find odd one out: 3, 5, 8, 13, 21", "options": ["3", "5", "8", "21"], "answer": 3},
    {"question": "4) A train 160 m long crosses a platform in 20 sec at 36 km/h. Platform length = ?", "options": ["80 m", "120 m", "200 m", "160 m"], "answer": 2},
    {"question": "5) If A is twice as good as B, they complete the work in 10 days together. If A alone takes x days, find x.", "options": ["15", "20", "24", "30"], "answer": 1},
    {"question": "6) Percentage: 15% of 200 is ?", "options": ["15", "20", "30", "40"], "answer": 4},
    {"question": "7) If 8 men can do a job in 6 days, 12 women can do the same in 4 days. Ratio of a man's work to a woman's work is ?", "options": ["2:3", "3:2", "4:3", "3:4"], "answer": 1},
    {"question": "8) Logical analogy: Book is to Reading as Fork is to ?", "options": ["Drawing", "Writing", "Eating", "Stirring"], "answer": 3},
    {"question": "9) If each side of a square is increased by 10%, area increases by ?", "options": ["10%", "21%", "19%", "20%"], "answer": 2},
    {"question": "10) Data Interpretation: If sales in Q1=120, Q2=150, Q3=180, Q4=210; total = ?", "options": ["650", "660", "680", "700"], "answer": 2},
    {"question": "11) Choose the next: 5, 11, 23, 47, ?", "options": ["95", "96", "97", "99"], "answer": 3},
    {"question": "12) A clock gains 5 minutes in 24 hours. How much does it gain in 6 hours?", "options": ["1.25 min", "1.5 min", "2 min", "0.5 min"], "answer": 1},
    {"question": "13) Profit & Loss: Bought at 1200, sold at 1500. Profit % = ?", "options": ["20%", "25%", "15%", "30%"], "answer": 2},
    {"question": "14) If log10(1000) = x, x = ?", "options": ["2", "3", "10", "100"], "answer": 2},
    {"question": "15) Directions: If you face North and turn 135° clockwise, you face ?", "options": ["SE", "SW", "NW", "NE"], "answer": 2},
    {"question": "16) Seating arrangement: Five friends A-E sit in a row; A sits left of B, C sits right of D. Which can't be determined?", "options": ["A's position", "B's position", "E's position", "None of these"], "answer": 3},
    {"question": "17) Ratio: If x:y = 3:4 and y:z = 8:5, find x:z", "options": ["3:5", "6:5", "9:5", "24:25"], "answer": 2},
    {"question": "18) Venn Diagram: If 40 like A, 50 like B, 20 like both and total 70, how many like neither?", "options": ["0", "10", "20", "30"], "answer": 2},
    {"question": "19) Simple interest for Rs.1000 at 5% per annum for 3 years = ?", "options": ["150", "115", "105", "1500"], "answer": 1},
    {"question": "20) Statement & Assumption: If statement 'All apples are fruits', assumption?", "options": ["All fruits are apples", "Some fruits are apples", "No fruit is apple", "None"], "answer": 2},
    {"question": "21) Binary puzzle: 1010 (base 2) in decimal = ?", "options": ["8", "10", "12", "16"], "answer": 2},
    {"question": "22) Cube puzzle: How many faces does a cuboid have?", "options": ["4", "6", "8", "12"], "answer": 2},
    {"question": "23) Permutation: Number of ways to arrange 'ABC' = ?", "options": ["3", "6", "9", "12"], "answer": 2},
    {"question": "24) If ratio of speeds is 3:4 and time to cover same distance is t1 and t2, t1:t2 = ?", "options": ["4:3", "3:4", "16:9", "9:16"], "answer": 1},
    {"question": "25) If day after tomorrow is two days before Saturday, today is ?", "options": ["Sunday", "Monday", "Tuesday", "Wednesday"], "answer": 4},
]

# shuffle questions for exam variation each run
random.shuffle(exam_data)  # comment this line out if you want fixed order

# ----------------------------
# MAIN APP
# ----------------------------
class ExamPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Aptitude & Reasoning — MCQ Exam Portal")
        self.root.geometry("1000x640")
        self.root.minsize(920, 600)

        # styling fonts
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.q_font = font.Font(family="Helvetica", size=13)
        self.opt_font = font.Font(family="Helvetica", size=12)

        # user & timer
        self.username = simpledialog.askstring("Login", "Enter your name for the exam:")
        if not self.username:
            self.username = "Guest"
        self.total_seconds = TOTAL_TIME_SECONDS
        self.time_started = time.time()

        # exam state
        self.num_q = len(exam_data)
        self.current_q = 0
        self.selected_answers = [0] * self.num_q  # 0 means unanswered, else 1-4
        self.visited = [False] * self.num_q
        self.marked_review = [False] * self.num_q

        # theme
        self.theme = "light"

        # UI setup
        self.create_widgets()
        self.update_timer()
        self.display_question(0)

    def create_widgets(self):
        # Header Frame
        header = tk.Frame(self.root, height=60, bd=1, relief="flat")
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        self.user_label = tk.Label(header, text=f"User: {self.username}", font=("Arial", 12))
        self.user_label.pack(side="left", padx=12)

        self.timer_label = tk.Label(header, text="", font=("Arial", 14), fg="red")
        self.timer_label.pack(side="right", padx=20)

        self.toggle_btn = tk.Button(header, text="🌗 Toggle Theme", command=self.toggle_theme)
        self.toggle_btn.pack(side="right", padx=10)

        title_lbl = tk.Label(header, text="Aptitude & Reasoning Test — 25 Questions", font=self.title_font)
        title_lbl.pack(side="top", pady=4)

        # Main area (left nav, right question)
        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=8, pady=8)

        # Left navigation panel
        nav_frame = tk.Frame(main, width=180, bd=1, relief="groove")
        nav_frame.pack(side="left", fill="y", padx=(0,8))
        nav_frame.pack_propagate(False)

        nav_title = tk.Label(nav_frame, text="Question Navigator", font=("Arial", 12, "bold"))
        nav_title.pack(pady=6)

        self.nav_buttons = []
        btns_frame = tk.Frame(nav_frame)
        btns_frame.pack(padx=6, pady=4, fill="y", expand=True)

        # create grid of 1..num_q buttons
        rows = (self.num_q + 4) // 5
        idx = 0
        for r in range(rows):
            rowf = tk.Frame(btns_frame)
            rowf.pack(fill="x", pady=2)
            for c in range(5):
                if idx >= self.num_q:
                    break
                b = tk.Button(rowf, text=str(idx+1), width=3,
                              command=lambda i=idx: self.jump_to_question(i))
                b.config(bg="#d3d3d3")  # default not visited color
                b.pack(side="left", padx=4)
                self.nav_buttons.append(b)
                idx += 1

        # Right question panel
        q_frame = tk.Frame(main, bd=1, relief="flat")
        q_frame.pack(side="left", fill="both", expand=True)

        self.question_label = tk.Label(q_frame, text="", font=self.q_font, wraplength=720, justify="left")
        self.question_label.pack(pady=(20,10), padx=12)

        self.var_selected = tk.IntVar(value=0)

        self.options_frame = tk.Frame(q_frame)
        self.options_frame.pack(pady=4, padx=8, anchor="w")

        self.opt_rbs = []
        for i in range(4):
            rb = tk.Radiobutton(self.options_frame, text="", variable=self.var_selected, value=i+1,
                                font=self.opt_font, anchor="w", justify="left", wraplength=700,
                                command=self.on_select_option)
            rb.pack(fill="x", pady=6, padx=12)
            self.opt_rbs.append(rb)

        # Footer with navigation controls
        footer = tk.Frame(self.root, height=70)
        footer.pack(side="bottom", fill="x", padx=8, pady=8)
        footer.pack_propagate(False)

        self.prev_btn = tk.Button(footer, text="◀ Previous", width=12, command=self.previous_question)
        self.prev_btn.pack(side="left", padx=8)

        self.save_next_btn = tk.Button(footer, text="💾 Save & Next", width=14, command=self.save_and_next)
        self.save_next_btn.pack(side="left", padx=8)

        self.mark_btn = tk.Button(footer, text="⚑ Mark for Review", width=16, command=self.toggle_mark_review)
        self.mark_btn.pack(side="left", padx=10)

        self.submit_btn = tk.Button(footer, text="✅ Submit Test", width=14, command=self.submit_exam)
        self.submit_btn.pack(side="right", padx=8)

        # status hint
        tip = tk.Label(footer, text="Tip: Click nav numbers to jump. Mark for Review to revisit.", font=("Arial", 10))
        tip.pack(side="left", padx=6)

        # initial theme apply
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "light":
            bg = "#f5f5f5"
            fg = "#000000"
            frame_bg = "#ffffff"
        else:
            bg = "#1e1e1e"
            fg = "#eaeaea"
            frame_bg = "#2b2b2b"

        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg)
            except:
                pass

        self.question_label.configure(bg=frame_bg, fg=fg)
        self.options_frame.configure(bg=frame_bg)
        for rb in self.opt_rbs:
            rb.configure(bg=frame_bg, fg=fg, selectcolor=frame_bg, activebackground=frame_bg)
        # nav buttons color backgrounds handled separately
        self.user_label.configure(bg=bg, fg=fg)
        self.timer_label.configure(bg=bg, fg="red" if self.theme == "light" else "lightgreen")
        self.toggle_btn.configure(bg=frame_bg, fg=fg)
        self.prev_btn.configure(bg=frame_bg, fg=fg)
        self.save_next_btn.configure(bg=frame_bg, fg=fg)
        self.mark_btn.configure(bg=frame_bg, fg=fg)
        self.submit_btn.configure(bg=frame_bg, fg=fg)

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    # ----------------------------
    # Timer
    # ----------------------------
    def update_timer(self):
        elapsed = int(time.time() - self.time_started)
        remaining = max(0, self.total_seconds - elapsed)
        mins, secs = divmod(remaining, 60)
        self.timer_label.config(text=f"⏱ Time Left: {mins:02d}:{secs:02d}")
        if remaining <= 0:
            # Auto submit
            messagebox.showinfo("Time's up", "Time finished. The test will be submitted automatically.")
            self.submit_exam(auto=True)
            return
        # schedule next update after 1s
        self.root.after(1000, self.update_timer)

    # ----------------------------
    # Display question
    # ----------------------------
    def display_question(self, index):
        self.current_q = index
        q = exam_data[index]
        self.question_label.config(text=f"Q{index+1}. {q['question']}")
        self.var_selected.set(self.selected_answers[index])  # restore selected option if any
        for i, opt_text in enumerate(q["options"]):
            self.opt_rbs[i].config(text=f"{chr(65+i)}. {opt_text}")

        # mark visited
        if not self.visited[index]:
            self.visited[index] = True
        self.update_nav_buttons()
        # update mark button text
        if self.marked_review[index]:
            self.mark_btn.config(text="⛳ Unmark Review")
        else:
            self.mark_btn.config(text="⚑ Mark for Review")

    def on_select_option(self):
        # when user selects radiobutton, reflect in selected_answers immediately but do not auto-advance
        sel = self.var_selected.get()
        if sel:
            self.selected_answers[self.current_q] = sel
        self.update_nav_buttons()

    # ----------------------------
    # Navigation functions
    # ----------------------------
    def jump_to_question(self, index):
        # save current selection before jumping
        self.selected_answers[self.current_q] = self.var_selected.get()
        self.display_question(index)

    def previous_question(self):
        if self.current_q > 0:
            self.selected_answers[self.current_q] = self.var_selected.get()
            self.display_question(self.current_q - 1)

    def save_and_next(self):
        # save and go next (or stay if last)
        self.selected_answers[self.current_q] = self.var_selected.get()
        if self.current_q < self.num_q - 1:
            self.display_question(self.current_q + 1)
        else:
            messagebox.showinfo("End of Test", "You are at the last question.")
        self.update_nav_buttons()

    def toggle_mark_review(self):
        self.marked_review[self.current_q] = not self.marked_review[self.current_q]
        # if marking review also consider it visited
        self.visited[self.current_q] = True
        self.update_nav_buttons()
        self.display_question(self.current_q)

    def update_nav_buttons(self):
        # set colors based on state
        for i, btn in enumerate(self.nav_buttons):
            if self.marked_review[i]:
                btn.config(bg="#ff9f1c")  # orange for review
            elif self.selected_answers[i] != 0:
                btn.config(bg="#8bc34a")  # green for answered
            elif self.visited[i]:
                btn.config(bg="#ffd54f")  # yellow for visited not answered
            else:
                btn.config(bg="#d3d3d3")  # default grey

    # ----------------------------
    # Submit and Scoring
    # ----------------------------
    def submit_exam(self, auto=False):
        # Save current selection first
        self.selected_answers[self.current_q] = self.var_selected.get()
        if not auto:
            confirm = messagebox.askyesno("Submit Confirmation", "Are you sure you want to submit the test?")
            if not confirm:
                return

        # scoring
        correct = 0
        attempted = 0
        for i, q in enumerate(exam_data):
            if self.selected_answers[i] != 0:
                attempted += 1
                if self.selected_answers[i] == q["answer"]:
                    correct += 1

        total = self.num_q
        wrong = attempted - correct
        percent = (correct / total) * 100
        elapsed = int(time.time() - self.time_started)
        elapsed_display = time.strftime("%H:%M:%S", time.gmtime(elapsed))

        # result message
        msg = (
            f"👤 {self.username}\n\n"
            f"✅ Correct: {correct}\n"
            f"❌ Wrong: {wrong}\n"
            f"📝 Attempted: {attempted} / {total}\n"
            f"🎯 Percentage: {percent:.2f}%\n"
            f"⏱ Time Taken: {elapsed_display}\n\n"
            "Do you want to restart the test?"
        )

        retry = messagebox.askyesno("Test Result", msg)
        if retry:
            self.restart_test()
        else:
            self.root.destroy()

    def restart_test(self):
        # reset state and reshuffle
        random.shuffle(exam_data)
        self.selected_answers = [0] * self.num_q
        self.visited = [False] * self.num_q
        self.marked_review = [False] * self.num_q
        self.time_started = time.time()
        self.display_question(0)
        self.update_nav_buttons()
        self.update_timer()

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ExamPortal(root)
    root.mainloop()
