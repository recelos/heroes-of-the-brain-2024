import tkinter as tk
import random
import time

class MathGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Game")
        
        self.score = 0
        self.remaining_time = 60
        self.current_question = {}
        
        self.question_label = tk.Label(root, text="", font=("Arial", 24))
        self.question_label.pack(pady=20)
        
        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 18))
        self.score_label.pack()
        
        self.timer_label = tk.Label(root, text="Time left: 60s", font=("Arial", 18))
        self.timer_label.pack()
        
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(pady=20)
        self.answer_buttons = []
        for i in range(4):
            button = tk.Button(self.buttons_frame, text="", font=("Arial", 18), command=lambda i=i: self.check_answer(i))
            button.grid(row=0, column=i, padx=10)
            self.answer_buttons.append(button)
        
        self.generate_question()
        self.update_timer()
    
    def generate_question(self):
        """Generates a new math question and updates the UI."""
        num1 = random.randint(1, 50)
        num2 = random.randint(1, 50)
        operation = random.choice(["+", "-"])
        
        if operation == "+":
            correct_answer = num1 + num2
        else:
            correct_answer = num1 - num2
        
        self.current_question = {
            "question": f"{num1} {operation} {num2}",
            "correct_answer": correct_answer
        }
        
        answers = [correct_answer]
        while len(answers) < 4:
            wrong_answer = correct_answer + random.randint(-10, 10)
            if wrong_answer != correct_answer and wrong_answer not in answers:
                answers.append(wrong_answer)
        
        random.shuffle(answers)
        
        self.question_label.config(text=self.current_question["question"])
        for i, button in enumerate(self.answer_buttons):
            button.config(text=str(answers[i]))
    
    def check_answer(self, button_index):
        selected_answer = int(self.answer_buttons[button_index].cget("text"))
        if selected_answer == self.current_question["correct_answer"]:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
        self.generate_question()
    
    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.config(text=f"Time left: {self.remaining_time}s")
            self.root.after(1000, self.update_timer)
        else:
            self.end_game()
    
    def end_game(self):
        for button in self.answer_buttons:
            button.config(state="disabled")
        self.question_label.config(text="Game Over!")
        self.timer_label.config(text="Time's up!")
        self.score_label.config(text=f"Final Score: {self.score}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MathGame(root)
    root.mainloop()
