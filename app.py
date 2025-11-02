import os
import requests
from flask import Flask, request
from openai import OpenAI

# --- 1. LOAD ALL SECRET KEYS from Environment Variables ---
# --- This is the new, secure way to handle tokens ---
# --- You will set these in your Render.com dashboard ---

# OpenRouter Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.environ.get("YOUR_SITE_URL", "https://my-bot.com")
YOUR_SITE_NAME = os.environ.get("YOUR_SITE_NAME", "My AI Bot")

# Instagram Config
INSTA_PAGE_ACCESS_TOKEN = os.environ.get("INSTA_PAGE_ACCESS_TOKEN")
INSTA_VERIFY_TOKEN = os.environ.get("INSTA_VERIFY_TOKEN")

# WhatsApp Config
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")

# --- 2. INITIALIZE CLIENTS ---
app = Flask(__name__)
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

# --- 3. CREATE THE WEBHOOK "LISTENER" (NOW SMARTER) ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # --- WEBHOOK VERIFICATION (Handles BOTH Insta and WA) ---
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == INSTA_VERIFY_TOKEN:
                print('INSTAGRAM WEBHOOK_VERIFIED')
                return challenge, 200
            elif mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
                print('WHATSAPP WEBHOOK_VERIFIED')
                return challenge, 200
            else:
                print('VERIFICATION_FAILED')
                return 'Verification token mismatch', 403
        else:
            return 'Missing parameters', 400

    elif request.method == 'POST':
        # --- NEW MESSAGE "ROUTER" (Handles BOTH Insta and WA) ---
        data = request.get_json()
        
        # Check if this is an Instagram message
        if data.get('object') == 'instagram':
            handle_instagram_message(data)
            
        # Check if this is a WhatsApp message
        elif data.get('object') == 'whatsapp_business_account':
            handle_whatsapp_message(data)
            
        return 'OK', 200

# --- 4. SEPARATE LOGIC FOR EACH PLATFORM ---

def handle_instagram_message(data):
    """Parses and replies to an Instagram message."""
    try:
        for entry in data.get('entry', []):
            for message in entry.get('messaging', []):
                if message.get('message') and message['message'].get('text'):
                    sender_id = message['sender']['id']
                    text = message['message']['text']
                    
                    print(f"Received Instagram message from {sender_id}: {text}")
                    ai_response = get_ai_response(text, sender_id)
                    send_instagram_reply(sender_id, ai_response)
    except Exception as e:
        print(f"INSTAGRAM ERROR: {e}")

def handle_whatsapp_message(data):
    """Parses and replies to a WhatsApp message."""
    try:
        entry = data.get('entry', [])[0]
        change = entry.get('changes', [])[0]
        value = change.get('value', {})
        
        if 'messages' in value:
            message_data = value['messages'][0]
            if message_data['type'] == 'text':
                sender_phone = message_data['from'] # User's phone number
                text = message_data['text']['body']
                
                print(f"Received WhatsApp message from {sender_phone}: {text}")
                ai_response = get_ai_response(text, sender_phone)
                send_whatsapp_reply(sender_phone, ai_response)
    except Exception as e:
        print(f"WHATSAPP ERROR: {e}")

# --- 5. AI "BRAIN" FUNCTION (Reusable) ---

def get_ai_response(text, user_id):
    """Gets a reply from the OpenRouter AI."""
    try:
        completion = client.chat.completions.create(
          extra_headers={
            "HTTP-Referer": YOUR_SITE_URL,
            "X-Title": YOUR_SITE_NAME,
          },
          model="openai/gpt-oss-20b", # Using a fast, free model
          messages=[
            { "role": "system", "content": "You are SalesBot named hooman, a super chatty, friendly, and persuasive AI salesman for our cutting-edge Instagram and WhatsApp AI DM Automation System. Your goal is to ethically convince users of its value by highlighting how it saves time, boosts engagement, and grows businesses without spammy tactics—always focusing on genuine connections and compliance. Be bubbly, use cat emojis, ask questions to engage, share relatable stories or quick stats, and gently guide conversations toward a free trial sign-up. Respond in short, energetic bursts to keep the chat flowing, and never push too hard—build trust first!" },
            { "role": "user", "content": text }
          ]
        )
        ai_response = completion.choices[0].message.content
        return ai_response
    except Exception as e:
        print(f"AI ERROR: {e}")
        return "Sorry, my AI brain is having a problem right now."

# --- 6. SEPARATE "REPLY" FUNCTIONS FOR EACH PLATFORM ---

def send_instagram_reply(recipient_id, text):
    """Sends a text message reply to Instagram."""
    url = f"https://graph.facebook.com/v24.0/me/messages?access_token={INSTA_PAGE_ACCESS_TOKEN}"
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': text},
        'messaging_type': 'RESPONSE'
    }
    response = requests.post(url, json=payload)
    print(f"Instagram Reply Response: {response.json()}")

def send_whatsapp_reply(recipient_phone, text):
    """Sends a text message reply to WhatsApp."""
    url = f"https://graph.facebook.com/v24.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": { "body": text }
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"WhatsApp Reply Response: {response.json()}")

# --- 7. START THE SERVER ---
if __name__ == '__main__':
    app.run(port=5000) # Removed debug=True for production

