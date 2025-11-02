# --- 1. IMPORT YOUR TOOLS ---
import os
import requests
from flask import Flask, request
from openai import OpenAI  # <-- NEW IMPORT

# --- 2. SET UP YOUR "PASSWORD" VARIABLES ---

# --- Meta Variables ---
# Find this in your Meta App Dashboard > Messenger > Instagram Settings
PAGE_ACCESS_TOKEN = 'EAAKvNj7XklIBP7pqARtHQyhiNcj8lLFO3tJHu5DarDeGZCR6Hs5nlcTkQC3oYv9dKcAdZA91ZAwW1H0OqNnek31hudUFa9ZBgaiZAtR5rtDuKF2vDHJZCZCGbGv3UhZCN89ZBhSuk98YYskd8vwTiWgKHXUu3w4NJxWaft4vFKWCVpQU3AxATQg82blnSmjsB0cZCxawcdxzQSKLUPuONMvf9rlBKV' 
# This is the password YOU made up
VERIFY_TOKEN = 'my-secret-token-123'

# --- OpenRouter Variables ---
OPENROUTER_API_KEY = "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"
YOUR_SITE_URL = "https://www.my-bot-project.com" # Optional: Change this to your site
YOUR_SITE_NAME = "My Instagram AI Bot"          # Optional: Change this to your bot's name

# --- 3. INITIALIZE THE OPENROUTER CLIENT (NEW!) ---
# We do this once when the app starts for efficiency
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

# --- 4. CREATE THE WEB SERVER ---
app = Flask(__name__)

# --- 5. CREATE THE WEBHOOK "LISTENER" ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    
    # --- 5a. THE 'GET' REQUEST (ONE-TIME VERIFICATION) ---
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verification token mismatch', 403

    # --- 5b. THE 'POST' REQUEST (A NEW MESSAGE ARRIVES) ---
    elif request.method == 'POST':
        data = request.get_json()
        
        if data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                for message in entry.get('messaging', []):
                    
                    sender_id = message['sender']['id']
                    
                    if message.get('message') and message['message'].get('text'):
                        text = message['message']['text']
                        
                        print(f"Received message from {sender_id}: {text}")

                        # --- 6. YOUR "BRAIN" (OPENROUTER AI) LOGIC ---
                        # This block is new and uses the OpenRouter SDK
                        try:
                            completion = client.chat.completions.create(
                              extra_headers={
                                "HTTP-Referer": YOUR_SITE_URL,
                                "X-Title": YOUR_SITE_NAME,
                              },
                              model="z-ai/glm-4.5-air:free", # The free model you requested
                              messages=[
                                {
                                  "role": "user",
                                  "content": text # Pass the user's message as content
                                }
                              ]
                            )
                            
                            # Get the AI's response text
                            ai_response = completion.choices[0].message.content

                        except Exception as e:
                            print(f"OPENROUTER AI ERROR: {e}")
                            ai_response = "Sorry, my AI brain is having a problem right now."
                        # --- END OF AI LOGIC ---

                        # 7. Send the reply back to the user
                        send_reply(sender_id, ai_response)
                        
        return 'OK', 200

# --- 8. THE "REPLY" FUNCTION (Unchanged) ---
def send_reply(recipient_id, text):
    """Sends a text message reply to the user."""
    
    url = f"https://graph.facebook.com/v24.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': text},
        'messaging_type': 'RESPONSE'
    }
    
    response = requests.post(url, json=payload)
    print(f"Meta Reply Response: {response.json()}")


# --- 9. START THE SERVER (Unchanged) ---
if __name__ == '__main__':
    # Make sure to install the openai library: pip install openai
    app.run(port=5000, debug=True)

