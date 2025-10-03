"""
AI Assistant for Pen-Deck
Provides AI-powered assistance for cybersecurity tasks
"""

import openai
import requests
import logging
import json
from datetime import datetime

class AIAssistant:
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.conversation_history = []
        
    def get_response(self, query):
        """Get AI response to user query"""
        try:
            ai_config = self.config.get_ai_config()
            
            if not ai_config.get('api_key'):
                return "AI Assistant not configured. Please set API key in settings."
                
            provider = ai_config.get('provider', 'openai')
            
            if provider == 'openai':
                return self._get_openai_response(query, ai_config)
            else:
                return "Unsupported AI provider"
                
        except Exception as e:
            self.logger.error(f"AI response error: {e}")
            return f"AI Assistant error: {str(e)}"
            
    def _get_openai_response(self, query, config):
        """Get response from OpenAI API"""
        try:
            openai.api_key = config['api_key']
            
            # Add context for cybersecurity
            system_prompt = """You are a cybersecurity assistant built into a penetration testing device called Pen-Deck. 
You help users with:
- Penetration testing guidance
- Tool usage and parameters
- Network security concepts
- Command explanations
- Security best practices
- Vulnerability analysis

Keep responses concise and practical for a small screen display. Focus on actionable advice."""
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Add conversation history (last 3 exchanges)
            for entry in self.conversation_history[-6:]:  # 6 = 3 exchanges (user + assistant)
                messages.insert(-1, entry)
                
            response = openai.chat.completions.create(
                model=config.get('model', 'gpt-3.5-turbo'),
                messages=messages,
                max_tokens=config.get('max_tokens', 500),
                temperature=config.get('temperature', 0.7)
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": query},
                {"role": "assistant", "content": ai_response}
            ])
            
            # Keep only recent history
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
                
            return ai_response
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return f"OpenAI API error: {str(e)}"
            
    def get_tool_help(self, tool_name):
        """Get AI help for a specific tool"""
        query = f"Explain how to use {tool_name} for penetration testing. Include common use cases and important parameters."
        return self.get_response(query)
        
    def analyze_results(self, tool_name, results):
        """Get AI analysis of tool results"""
        query = f"Analyze these {tool_name} results and explain what they mean:\n\n{results[:1000]}"
        return self.get_response(query)
        
    def suggest_next_steps(self, current_findings):
        """Get AI suggestions for next penetration testing steps"""
        query = f"Based on these findings, what should be the next steps in this penetration test?\n\n{current_findings}"
        return self.get_response(query)
        
    def explain_vulnerability(self, vulnerability):
        """Get explanation of a specific vulnerability"""
        query = f"Explain this vulnerability and how to test for it: {vulnerability}"
        return self.get_response(query)
        
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        
    def get_conversation_history(self):
        """Get current conversation history"""
        return self.conversation_history.copy()
        
    def save_conversation(self, filename=None):
        """Save conversation history to file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ai_conversation_{timestamp}.json"
                
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "conversation": self.conversation_history
            }
            
            with open(f"results/{filename}", 'w') as f:
                json.dump(conversation_data, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            return False
            
    def load_conversation(self, filename):
        """Load conversation history from file"""
        try:
            with open(f"results/{filename}", 'r') as f:
                conversation_data = json.load(f)
                
            self.conversation_history = conversation_data.get('conversation', [])
            return True
        except Exception as e:
            self.logger.error(f"Error loading conversation: {e}")
            return False