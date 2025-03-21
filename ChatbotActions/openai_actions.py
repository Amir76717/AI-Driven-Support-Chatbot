from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ActionAskGPT(Action):
    def name(self) -> Text:
        return "action_ask_gpt"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the latest user message
        user_message = tracker.latest_message.get('text', 'No message provided')
        
        # Build conversation history (last 5 turns)
        conversation_history = []
        for event in reversed(tracker.events):
            if len(conversation_history) >= 10:  # 5 user + 5 bot
                break
            if event.get('event') == 'user' and event.get('text'):
                conversation_history.append({"role": "user", "content": event.get('text')})
            elif event.get('event') == 'bot' and event.get('text'):
                conversation_history.append({"role": "assistant", "content": event.get('text')})
        
        conversation_history.reverse()
        
        # Construct messages for OpenAI
        messages = [
            {"role": "system", "content": "You are a helpful customer support assistant. Be concise, friendly, and helpful."},
            *conversation_history,  # Unpack history into the list
            {"role": "user", "content": user_message}
        ]
        
        try:
            # Call OpenAI API (using latest SDK syntax)
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Switch to "gpt-4" if you have access
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            # Extract the response
            gpt_response = response.choices[0].message.content.strip()
            
            # Send to user
            dispatcher.utter_message(text=gpt_response)
        except Exception as e:
            dispatcher.utter_message(text="I'm having trouble connecting to my knowledge base. Please try again later.")
            print(f"OpenAI API Error: {e}")
            
        return []