import streamlit as st
from email.header import decode_header
from getpass import getpass
from groq import Groq
import imaplib
import email
import os
import re

class IntelligentEmailChatbot:
    def __init__(self, email_address, password, groq_api_key):
        """
        Initialize the intelligent email chatbot with advanced context understanding
        """
        self.email_address = email_address
        self.password = password
        self.groq_api_key = groq_api_key
        self.groq_client = Groq(api_key=self.groq_api_key)

        # IMAP settings
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

    def connect_to_email(self):
        """
        Establish secure email connection
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            return mail
        except Exception as e:
            st.error(f"Connection error: {e}")
            return None

    def get_emails(self, num_emails=50):
        """
        Retrieve emails with comprehensive retrieval
        """
        mail = self.connect_to_email()
        if not mail:
            return []

        try:
            mail.select('INBOX')
            _, search_data = mail.search(None, 'ALL')
            email_ids = search_data[0].split()[-num_emails:]
            emails = []

            for email_id in email_ids:
                _, email_data = mail.fetch(email_id, '(RFC822)')
                raw_email = email_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Advanced subject decoding
                subject, encoding = decode_header(email_message['Subject'])[0]
                subject = subject.decode(encoding or 'utf-8') if isinstance(subject, bytes) else subject

                # Extract email body
                body = self._extract_email_body(email_message)

                emails.append({
                    'subject': subject or "No Subject",
                    'sender': email_message['From'] or "Unknown Sender",
                    'body': body,
                    'date': email_message['Date'] or "No Date",
                    'id': email_id.decode('utf-8')
                })

            mail.close()
            mail.logout()
            return emails

        except Exception as e:
            st.error(f"Email retrieval error: {e}")
            return []

    def _extract_email_body(self, email_message):
        """
        Extract comprehensive email body content
        """
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()

        return body[:1000]  # Limit to first 1000 characters

    def analyze_intent(self, user_input):
        """
        Use AI to understand user's email retrieval intent
        """
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": '''You are an intelligent email assistant that helps users find relevant emails by understanding context and intent.
                                      Understand the intent of this request and identify any time or date-related filters to apply for email retrieval.
                                      If the request is ambiguous, suggest follow-up questions that can help clarify the user's intent
                                      Identify if the user is prioritizing certain senders, subjects, or types of emails. Include reasoning in your analysis
                                      Analyze the user's intent and detect if there's an emotional tone (e.g., urgency, frustration) that might affect how emails should be retrieved.
                                      Focus on understanding technical or project-related keywords in the user's query. Suggest filters that might help in these cases
                                      Analyze the intent keeping in mind the user typically searches for [meeting notes/important updates/personal emails
                                      Based on this intent and past preferences, predict what type of email the user is most likely seeking and filter appropriately.'''
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the intent behind this request and suggest how to filter emails: '{user_input}'"
                    }
                ],
                model="llama3-8b-8192"
            )
            return response.choices[0].message.content

        except Exception as e:
            st.error(f"Intent analysis error: {e}")
            return "Unable to analyze intent"

    def filter_emails(self, emails, intent):
        """
        Filter emails based on AI-interpreted intent
        """
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": '''You are an email filtering expert. Provide a strategy to filter emails based on a given intent.
                                      Based on this intent, suggest a filtering strategy for retrieving emails, considering relevance and priority.
                                      Analyze the provided intent and prioritize emails that seem urgent or time-sensitive. Explain why
                                      dentify key terms in the intent that can be matched with email content. Suggest appropriate filters based on these terms.
                                      Check if the intent indicates importance for certain senders, domains, or groups. Filter emails accordingly.
                                      Filter emails based on the intent, paying particular attention to any dates, times, or recent activity mentioned.
                                      If there are multiple possible intents, outline strategies to filter emails for each case and indicate your primary suggestion
                                      Suggest strategies to exclude irrelevant emails based on this intent. Highlight the reasoning behind your choices
                                      Provide a filtering strategy for these emails and explain your reasoning as if you were describing it to the user.
                                      Focus on identifying project-related content in the user's intent and suggest relevant filters.
                                      Detect if the user might be searching for emails with specific attachments or media. Suggest filters for these cases'''
                    },
                    {
                        "role": "user",
                        "content": f"Given this intent: '{intent}', filter these emails and explain your reasoning:\n" +
                                   "\n".join([f"Subject: {email['subject']}, Sender: {email['sender']}, Body Preview: {email['body'][:100]}" for email in emails])
                    }
                ],
                model="llama3-8b-8192"
            )
            return response.choices[0].message.content

        except Exception as e:
            st.error(f"Email filtering error: {e}")
            return "Unable to filter emails"

# Streamlit UI
def main():
    st.title("📧 Intelligent Email Context Assistant")

    with st.form("credentials_form"):
        email_address = st.text_input("Gmail Address", value="", placeholder="Enter your Gmail address")
        password = st.text_input("App Password", type="password", placeholder="Enter your App Password")
        groq_api_key = st.text_input("Groq API Key", type="password", placeholder="Enter your Groq API Key")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not email_address or not password or not groq_api_key:
            st.error("All fields are required!")
            return

        chatbot = IntelligentEmailChatbot(email_address, password, groq_api_key)
        st.success("Connected successfully!")

        user_input = st.text_input("Enter your email query")
        if user_input:
            with st.spinner("Processing your request..."):
                emails = chatbot.get_emails()
                if not emails:
                    st.warning("No emails found or retrieval failed.")
                    return

                intent = chatbot.analyze_intent(user_input)
                filtered_results = chatbot.filter_emails(emails, intent)

                st.write(filtered_results)

if __name__ == "__main__":
    main()
