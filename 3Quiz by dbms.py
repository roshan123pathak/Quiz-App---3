import sqlite3
import time

def connect():
    conn = sqlite3.connect('quiz_app_db.db')  
    return conn

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        enrollment TEXT UNIQUE,
                        password TEXT,
                        name TEXT,
                        email TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT,
                        option1 TEXT,
                        option2 TEXT,
                        option3 TEXT,
                        option4 TEXT,
                        correct_option TEXT,
                        category TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        enrollment TEXT,
                        score TEXT,
                        time_taken REAL,
                        subject TEXT
                    )''')

    conn.commit()
    conn.close()

def create_account():
    print("\n--- Create Account ---")
    name = input("Enter your name: ")
    enrollment = input("Enter your enrollment number: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE enrollment = ?''', (enrollment,))
    user = cursor.fetchone()

    if user:
        print("Enrollment number already exists! Please try again with a different enrollment number.")
    else:

        cursor.execute('''INSERT INTO users (enrollment, password, name, email)
                          VALUES (?, ?, ?, ?)''', (enrollment, password, name, email))
        conn.commit()
        print("Account created successfully!")
    
    conn.close()

def login():
    print("\n--- Login ---")
    enrollment = input("Enter your enrollment number: ")
    password = input("Enter your password: ")

    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM users WHERE enrollment = ? AND password = ?''', (enrollment, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("Login successful!")
        return enrollment
    else:
        print("Invalid enrollment number or password!")
        return None
    
def load_questions(category):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''SELECT question, option1, option2, option3, option4, correct_option
                      FROM questions WHERE category = ?''', (category,))
    rows = cursor.fetchall()
    conn.close()

    questions = []
    for row in rows:
        questions.append({
            "question": row[0],
            "options": [row[1], row[2], row[3], row[4]],
            "correct": row[5]
        })
    return questions

def take_quiz(enrollment):
    print("\n--- Take a Quiz ---")
    categories = ["Cybersecurity", "Computer Networks", "DBMS"]
    
    print("Available subjects:")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")
    
    while True:
        category_choice = input("Enter the number corresponding to the subject you want to attempt (1-3): ")
        if category_choice.isdigit() and 1 <= int(category_choice) <= len(categories):
            selected_category = categories[int(category_choice) - 1]
            break
        print("Invalid input! Please enter a valid number (1-3).")

    print(f"\nYou selected: {selected_category}")

    questions = load_questions(selected_category)

    if not questions:
        print(f"No questions available for {selected_category}.")
        return

    correct_answers = 0
    total_questions = len(questions)

    start_time = time.time()
    for i, q in enumerate(questions, start=1):
        print(f"\nQ{i}: {q['question']}")
        for j, option in enumerate(q['options'], start=1):
            print(f"{j}. {option}")

        while True:
            answer = input("Your answer (1-4): ")
            if answer.isdigit() and 1 <= int(answer) <= 4:
                break
            print("Invalid input! Please enter a number between 1 and 4.")

        if q['options'][int(answer) - 1] == q['correct']:
            correct_answers += 1

    end_time = time.time()
    time_taken = round(end_time - start_time, 2)
    score = f"{correct_answers}/{total_questions}"

    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO results (enrollment, score, time_taken, subject)
                      VALUES (?, ?, ?, ?)''', (enrollment, score, time_taken, selected_category))
    conn.commit()
    conn.close()

    print(f"\nQuiz finished! Your score: {score}")
    print(f"Time taken: {time_taken} seconds")

def view_result(enrollment):
    print("\n--- Results ---")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('''SELECT score, time_taken, subject FROM results WHERE enrollment = ?''', (enrollment,))
    results = cursor.fetchall()
    conn.close()

    if results:
        for result in results:
            score, time_taken, subject = result
            print(f"Subject: {subject}, Score: {score}, Time: {time_taken} seconds")
    else:
        print("No results found!")

def main():
    create_tables()  

    while True:
        print("\n--- Quiz Application ---")
        print("1. Create Account")
        print("2. Login")
        print("3. Take a Quiz")
        print("4. View Results")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            create_account()
        elif choice == '2':
            enrollment = login()
            if enrollment:
                while True:
                    print("\n1. Take a Quiz")
                    print("2. View Results")
                    print("3. Logout")
                    sub_choice = input("Enter your choice: ")
                    if sub_choice == '1':
                        take_quiz(enrollment)
                    elif sub_choice == '2':
                        view_result(enrollment)
                    elif sub_choice == '3':
                        break
                    else:
                        print("Invalid choice!")
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

main()
