import tkinter as tk
from tkinter import scrolledtext, messagebox
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from textblob import TextBlob
import datetime
import threading
import pyttsx3
import json
import os

engine = pyttsx3.init()

conversation_history = []
if os.path.exists('conversation_history.json'):
    with open('conversation_history.json', 'r') as f:
        conversation_history = json.load(f)

questions = [
    "How do I reset my password?",
    "What is your refund policy?",
    "How can I change my delivery address?",
    "What payment options are available?",
    "Where can I view my past orders?",
    "How do I contact customer support?",
    "Can I track my package?",
    "How do I update my account details?",
    "What are your working hours?",
    "How do I return a product?",
    "What are the shipping charges?",
    "Hi",
    "Hello",
    "Goodbye",
    "Who are you?",
    "What is your name?",
    "Tell me something interesting.",
    "Can I change my order?",
    "What is the estimated delivery time?",
    "How do I apply a discount code?",
    "Check shipments"
]

responses = [
    "You can reset your password in the 'Account Settings' section.",
    "Our refund policy allows returns and refunds within 30 days of purchase.",
    "You can change your delivery address by going to the 'Shipping Details' in your profile.",
    "We accept credit cards, debit cards, and PayPal as payment methods.",
    "You can view your past orders in the 'Order History' section of your account.",
    "You can contact customer support through our Help Center or by calling our hotline.",
    "Yes, you can track your package under the 'My Orders' section.",
    "You can update your account details in the 'Account Settings' section.",
    "Our working hours are from 9 AM to 6 PM, Monday to Friday.",
    "To return a product, go to the 'Returns' section and follow the steps.",
    "Shipping charges depend on the destination and order size. You can view them at checkout.",
    "Hello! How can I assist you today?",
    "Hi there! How can I help you?",
    "Goodbye! Have a great day!",
    "I'm your virtual assistant here to help with your queries!",
    "I am your friendly chatbot, here to assist you.",
    "Did you know honey never spoils? It can last indefinitely!",
    "Yes, you can change your order before it is shipped. Please contact support for assistance.",
    "The estimated delivery time is displayed at checkout and in the 'Order Details' section.",
    "You can apply a discount code during checkout in the 'Payment' section.",
    "Shipments will be traced automatically.Will be get shortly."
]

user_context = {
    "name": None,
    "last_query": ""
}

model = make_pipeline(TfidfVectorizer(), LogisticRegression())
model.fit(questions, responses)

def chatbot_response(user_input):
    return model.predict([user_input])[0]

def analyze_sentiment(user_input):
    blob = TextBlob(user_input)
    return blob.sentiment.polarity

def save_conversation(user_input, response):
    conversation_history.append({"user": user_input, "bot": response})
    with open('conversation_history.json', 'w') as f:
        json.dump(conversation_history, f)

def retrain_model():
    global questions, responses
    for entry in conversation_history:
        questions.append(entry["user"])
        responses.append(entry["bot"])
    model.fit(questions, responses)

def get_response(user_input):
    user_context["last_query"] = user_input

    if user_context["name"] and "name" in user_input.lower():
        full_response = f"Nice to meet you, {user_context['name']}! "
    else:
        full_response = ""

    sentiment = analyze_sentiment(user_input)
    if sentiment < 0:
        full_response += "I sense you're upset. "
    else:
        full_response += "Sure! "

    response = chatbot_response(user_input)
    full_response += response

    save_conversation(user_input, full_response)

    if len(conversation_history) % 10 == 0:
        retrain_model()

    chat_display.insert(tk.END, f"You: {user_input}\n", "user")
    chat_display.insert(tk.END, f"Bot: {full_response}\n\n", "bot")

    engine.say(full_response)
    engine.runAndWait()

    if "return" in user_input.lower():
        chat_display.insert(tk.END, "Note: You can view the return policy in the Help section.\n\n", "info")
    
    if "order" in user_input.lower():
        chat_display.insert(tk.END, "Tip: Make sure to check your order confirmation email for details.\n\n", "info")
    
    if "my name is" in user_input.lower():
        user_context["name"] = user_input.split("my name is")[-1].strip()
        chat_display.insert(tk.END, f"Got it! I'll remember your name as {user_context['name']}.\n\n", "info")

    chat_display.see(tk.END)

def send_message(event=None):
    user_input = user_input_entry.get().strip()
    if user_input:
        threading.Thread(target=get_response, args=(user_input,)).start()
        user_input_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter a message.")

def show_faq():
    faq_text = (
        "Frequently Asked Questions:\n\n"
        "1. How do I reset my password?\n   You can reset your password in the 'Account Settings' section.\n\n"
        "2. What is your refund policy?\n   Our refund policy allows returns within 30 days of purchase.\n\n"
        "3. How can I change my delivery address?\n   You can change your delivery address in 'Shipping Details'.\n\n"
        "4. What payment options are available?\n   We accept credit cards, debit cards, and PayPal.\n\n"
        "5. Where can I view my past orders?\n   You can view your past orders in 'Order History'.\n\n"
        "6. How do I contact customer support?\n   You can contact customer support via the Help Center.\n\n"
        "7. Can I track my package?\n   Yes, you can track your package in 'My Orders'.\n\n"
        "8. How do I update my account details?\n   You can update your account details in 'Account Settings'.\n\n"
        "9. What are your working hours?\n   We are open from 9 AM to 6 PM, Monday to Friday.\n\n"
        "10. How do I return a product?\n   Go to the 'Returns' section and follow the steps.\n\n"
    )
    messagebox.showinfo("FAQ", faq_text)

def quit_application():
    window.quit()

window = tk.Tk()
window.title("Instagram-like Chatbot")
window.configure(bg='white')

chat_display = scrolledtext.ScrolledText(window, width=50, height=20, state='normal', wrap='word', bg='white', fg='black')
chat_display.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

chat_display.tag_configure("user", foreground="black")
chat_display.tag_configure("bot", foreground="blue")
chat_display.tag_configure("info", foreground="green")

input_frame = tk.Frame(window, bg='white')
input_frame.grid(row=1, column=0, columnspan=2, pady=10)

user_input_entry = tk.Entry(input_frame, width=50)
user_input_entry.pack(side=tk.LEFT, padx=10)

send_button = tk.Button(input_frame, text="Send", command=send_message)
send_button.pack(side=tk.LEFT)

faq_button = tk.Button(window, text="FAQ", command=show_faq)
faq_button.grid(row=2, column=0, sticky="w", padx=10, pady=5)

quit_button = tk.Button(window, text="Quit", command=quit_application)
quit_button.grid(row=2, column=1, sticky="e", padx=10, pady=5)

window.bind('<Return>', send_message)

window.mainloop()
