"""
AI Assistant for Pen-Deck
Provides AI-powered assistance for cybersecurity tasks
"""

from openai import OpenAI
import logging
import json
from datetime import datetime

class AIAssistant:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.conversation_history = []
        self.client = None
        
    def get_response(self, query):
        """Get AI response to user query"""
        try:
            ai_config = self.config.get_ai_config()
            
            if not ai_config.get('api_key'):
                return "AI Assistant not configured. Please set API key in config.json"
            
            # Initialize OpenAI client (v1.0+ API)
            if not self.client:
                self.client = OpenAI(api_key=ai_config['api_key'])
            
            system_prompt = """You are a cybersecurity assistant built into a penetration testing device called Pen-Deck. 
You help users with:
- Penetration testing guidance
- Tool usage and parameters
- Network security concepts
- Command explanations
- Security best practices
- Vulnerability analysis

Keep responses concise and practical for a small screen display. Focus on actionable advice."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Add conversation history
            for entry in self.conversation_history[-6:]:
                messages.insert(-1, entry)
            
            # Use new API
            response = self.client.chat.completions.create(
                model=ai_config.get('model', 'gpt-3.5-turbo'),
                messages=messages,
                max_tokens=ai_config.get('max_tokens', 500),
                temperature=ai_config.get('temperature', 0.7)
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": query},
                {"role": "assistant", "content": ai_response}
            ])
            
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
                
            return ai_response
            
        except Exception as e:
            self.logger.error(f"AI response error: {e}")
            return f"AI Error: {str(e)}"
