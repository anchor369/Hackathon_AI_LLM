import imaplib
import email
from email.header import decode_header
from groq import Groq
import os
from typing import List, Dict, Optional

class IntelligentEmailChatbot:
    def __init__(self, 
                 email_address: Optional[str] = None, 
                 password: Optional[str] = None, 
                 groq_api_key: Optional[str] = None):
        """
        Initialize the intelligent email chatbot with advanced context understanding
        """
        self.email_address = email_address or input("Enter your Gmail address: ")
        self.password = password or input("Enter your App Password: ")
        self.groq_api_key = groq_api_key or input("Enter Groq API Key: ")
        self.groq_client = Groq(api_key=self.groq_api_key)

        # IMAP settings
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

    def connect_to_email(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Establish secure email connection
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            return mail
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def get_emails(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Retrieve emails from the inbox
        """
        emails = []
        try:
            mail = self.connect_to_email()
            if not mail:
                return []

            mail.select('inbox')
            _, search_data = mail.search(None, 'ALL')
            email_ids = search_data[0].split()

            for email_id in reversed(email_ids[-limit:]):
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        email_body = response_part[1]
                        email_message = email.message_from_bytes(email_body)

                        subject = self._decode_header(email_message['Subject'])
                        sender = self._decode_header(email_message['From'])
                        body = self._extract_email_body(email_message)

                        emails.append({
                            'subject': subject,
                            'sender': sender,
                            'body': body
                        })

            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Error retrieving emails: {e}")

        return emails

    def _decode_header(self, header: Optional[str]) -> str:
        """
        Decode email headers to handle non-ASCII characters
        """
        if not header:
            return "No Header"
        
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_part = part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_part = part
            decoded_parts.append(decoded_part)
        
        return ' '.join(decoded_parts)

    def _extract_email_body(self, email_message) -> str:
        """
        Extract the body of an email message
        """
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return body[:500]

    def analyze_intent(self, user_input: str) -> str:
        """
        Advanced intent analysis with Groq AI
        """
        system_prompt = """
        You are an intelligent email assistant. Accurately interpret the user's intent from their query. 
        Possible intents include:
        - Finding emails from a specific sender
        - Searching for emails about a particular topic
        - Locating emails within a date range
        - Finding emails with specific keywords
        - Don't give non-matching emails and don't even mention about this
        
        Provide a clear, concise intent description that guides precise email filtering.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Interpret the intent behind: '{user_input}'"}
                ],
                model="llama3-8b-8192",
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Intent analysis error: {e}")
            return "general email search"

    def filter_emails(self, emails: List[Dict[str, str]], intent: str) -> str:
        """
        Enhanced email filtering with Groq AI
        """
        system_prompt = """
        You are an expert email classifier. For each email:
        1. Carefully assess its relevance to the given intent
        2. Provide a brief description of 100 words, clear explanation of why it matches
        3. If matching, extract key details
        4. Organize results for easy user comprehension
        5. Don't give non-matching emails and don't mention about this
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Intent: '{intent}'\n\nEmails:\n" + 
                        "\n".join([
                            f"Email {i+1}:\n"
                            f"Subject: {email['subject']}\n"
                            f"Sender: {email['sender']}\n"
                            f"Body Preview: {email['body'][:200]}"
                            for i, email in enumerate(emails)
                        ])
                    }
                ],
                model="llama3-8b-8192",
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Email filtering error: {e}")
            return "No matching emails found."

    def process_request(self, user_input: str) -> str:
        """
        Process user's email search request with AI-powered filtering
        """
        if not user_input or not isinstance(user_input, str):
            return "Invalid input provided."

        try:
            emails = self.get_emails()
            if not emails:
                return "No emails found."
        except Exception as e:
            return f"Email retrieval failed: {str(e)}"

        try:
            intent = self.analyze_intent(user_input)
            filtered_results = self.filter_emails(emails, intent)
            return filtered_results
        except Exception as e:
            return f"Email filtering failed: {str(e)}"

def main():
    print("🤖 Intelligent Email Context Assistant 🤖")
    chatbot = IntelligentEmailChatbot()

    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                print("Goodbye!")
                break

            response = chatbot.process_request(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\nOperation cancelled. Type 'quit' to exit.")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()