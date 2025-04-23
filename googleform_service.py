# google_forms_mcp.py
from mcp.server.fastmcp import FastMCP, Context
import os
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Create an MCP server for Google Forms
mcp = FastMCP("Google Forms")

# Google Forms API scope
SCOPES = ['https://www.googleapis.com/auth/forms.body', 'https://www.googleapis.com/auth/forms.responses.readonly']

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Replace these with your actual values
CLIENT_ID = 'YOUR_WEB_CLIENT_ID'
CLIENT_SECRET = 'YOUR_WEB_CLIENT_SECRET'
REFRESH_TOKEN = 'YOUR_REFRESH_TOKEN'

SCOPES = ['https://www.googleapis.com/auth/forms.body']


def get_forms_service():
    """Get authenticated Google Forms service using refresh token."""
    try:
        creds = Credentials(
            token=None,  # No access token initially
            refresh_token=REFRESH_TOKEN,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=SCOPES,
        )

        # Refresh the access token
        creds.refresh(Request())

        # Build and return the service
        service = build('forms', 'v1', credentials=creds)
        return service

    except Exception as e:
        print(f"Error creating Google Forms service: {e}")
        return None

# ----- RESOURCES -----

@mcp.resource("forms://list")
def list_forms() -> str:
    """List all Google Forms the user has access to."""
    try:
        service = get_forms_service()
        # Currently, Forms API doesn't have a direct listing method,
        # so we can use Drive API to list forms
        drive_service = build('drive', 'v3', credentials=service._credentials)
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.form'",
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        if not items:
            return "No forms found."
        
        forms_list = "Available Google Forms:\n\n"
        for item in items:
            forms_list += f"- {item['name']} (ID: {item['id']})\n"
        return forms_list
    except Exception as e:
        return f"Error listing forms: {str(e)}"

@mcp.resource("forms://{form_id}")
def get_form_details(form_id: str) -> str:
    """Get details about a specific Google Form."""
    try:
        service = get_forms_service()
        form = service.forms().get(formId=form_id).execute()
        
        details = f"Form: {form.get('info', {}).get('title', 'Untitled Form')}\n"
        details += f"Description: {form.get('info', {}).get('description', 'No description')}\n\n"
        
        # Add questions
        if 'items' in form:
            details += "Questions:\n"
            for i, item in enumerate(form['items'], 1):
                question = item.get('questionItem', {}).get('question', {})
                details += f"{i}. {question.get('questionId')}: {question.get('title', 'Untitled Question')}\n"
                
                # Add options for multiple choice questions
                if 'choiceQuestion' in question:
                    options = question['choiceQuestion'].get('options', [])
                    for option in options:
                        details += f"   - {option.get('value', 'No value')}\n"
        else:
            details += "No questions in this form."
            
        return details
    except Exception as e:
        return f"Error getting form details: {str(e)}"

@mcp.resource("forms://{form_id}/responses")
def get_form_responses(form_id: str) -> str:
    """Get responses for a specific Google Form."""
    try:
        service = get_forms_service()
        responses = service.forms().responses().list(formId=form_id).execute()
        
        if not responses.get('responses'):
            return f"No responses for form {form_id}"
        
        result = f"Responses for form {form_id}:\n\n"
        for response in responses.get('responses', []):
            result += f"Response ID: {response.get('responseId')}\n"
            result += f"Timestamp: {response.get('createTime')}\n"
            
            answers = response.get('answers', {})
            for question_id, answer in answers.items():
                result += f"Question {question_id}:\n"
                
                # Handle different answer types
                if 'textAnswers' in answer:
                    text_answers = answer['textAnswers'].get('answers', [])
                    for text_answer in text_answers:
                        result += f"  Answer: {text_answer.get('value')}\n"
                
                # Add other answer types as needed
            
            result += "\n---\n\n"
        
        return result
    except Exception as e:
        return f"Error getting responses: {str(e)}"

# ----- TOOLS -----
@mcp.tool()
def addTwo(a : int, b: int):
    return a + b

@mcp.tool()
def create_form(title: str, description: Optional[str] = None) -> str:
    """Create a new Google Form with the specified title and description."""
    try:
        service = get_forms_service()
        print("got called")
        form_body = {
            'info': {
                'title': title
            }
        }
        
        if description:
            form_body['info']['description'] = description

        print("callig service")
        
        result = service.forms().create(body=form_body).execute()
        
        return f"Form created successfully!\nTitle: {title}\nID: {result['formId']}\nEdit URL: {result.get('responderUri', 'Not available')}"
    except Exception as e:
        return f"Error creating form: {str(e)}"

@mcp.tool()
def add_question(form_id: str, question_text: str, question_type: str = "TEXT", choices: Optional[List[str]] = None) -> str:
    """
    Add a question to an existing Google Form.
    
    question_type can be: TEXT, PARAGRAPH, MULTIPLE_CHOICE, CHECKBOX, DROPDOWN
    choices: Required for MULTIPLE_CHOICE, CHECKBOX, and DROPDOWN question types
    """
    try:
        service = get_forms_service()
        
        # Get the current form
        form = service.forms().get(formId=form_id).execute()
        
        # Prepare the question item based on type
        item = {
            'title': question_text,
        }
          
        if question_type in ["MULTIPLE_CHOICE", "CHECKBOX", "DROPDOWN"]:
            if not choices or len(choices) == 0:
                return "Error: Choices are required for this question type"
            
            choice_items = [{'value': choice} for choice in choices]
            
            if question_type == "MULTIPLE_CHOICE":
                item['questionItem'] = {
                    'question': {
                        'choiceQuestion': {
                            'type': 'RADIO',
                            'options': choice_items
                        }
                    }
                }
            elif question_type == "CHECKBOX":
                item['questionItem'] = {
                    'question': {
                        'choiceQuestion': {
                            'type': 'CHECKBOX',
                            'options': choice_items
                        }
                    }
                }
            elif question_type == "DROPDOWN":
                item['questionItem'] = {
                    'question': {
                        'choiceQuestion': {
                            'type': 'DROP_DOWN',
                            'options': choice_items
                        }
                    }
                }
        else:  # TEXT or PARAGRAPH
            text_type = 'PARAGRAPH_TEXT' if question_type == 'PARAGRAPH' else 'SHORT_TEXT'
            item['questionItem'] = {
                'question': {
                    'textQuestion': {
                        'paragraph': text_type == 'PARAGRAPH_TEXT'
                    }
                }
            }
        
        # Create request to add the question
        update = {
            'requests': [{
                'createItem': {
                    'item': item,
                    'location': {
                        'index': len(form.get('items', []))
                    }
                }
            }]
        }
        
        # Execute the update
        result = service.forms().batchUpdate(formId=form_id, body=update).execute()
        
        return f"Question added successfully to form {form_id}"
    except Exception as e:
        return f"Error adding question: {str(e)}"

@mcp.tool()
def submit_form_response(form_id: str, answers: Dict[str, Any]) -> str:
    """
    Submit a response to a Google Form.
    
    answers: Dictionary where keys are question IDs and values are the answers
    """
    try:
        service = get_forms_service()
        
        # Format the answers according to the Forms API
        formatted_answers = {}
        for question_id, answer in answers.items():
            if isinstance(answer, str):
                # Text answer
                formatted_answers[question_id] = {
                    'textAnswers': {
                        'answers': [{'value': answer}]
                    }
                }
            elif isinstance(answer, list):
                # Multiple choice/checkbox answer
                formatted_answers[question_id] = {
                    'textAnswers': {
                        'answers': [{'value': val} for val in answer]
                    }
                }
        
        # Create the response body
        response_body = {
            'answers': formatted_answers
        }
        
        # Submit the response
        result = service.forms().responses().create(
            formId=form_id,
            body=response_body
        ).execute()
        
        return f"Form response submitted successfully! Response ID: {result.get('responseId')}"
    except Exception as e:
        return f"Error submitting form response: {str(e)}"

# ----- PROMPTS -----

@mcp.prompt()
def create_form_prompt() -> str:
    """Prompt to help create a new Google Form."""
    return """
I'll help you create a new Google Form. Please provide the following information:

1. What should be the title of your form?
2. Do you want to add a description? If yes, what should it be?
3. What questions would you like to add to the form? For each question, specify:
   - The question text
   - The question type (TEXT, PARAGRAPH, MULTIPLE_CHOICE, CHECKBOX, or DROPDOWN)
   - For multiple choice questions, list the options
   
I'll guide you through the process of creating the form and adding questions.
"""

@mcp.prompt()
def analyze_responses_prompt() -> str:
    """Prompt to help analyze form responses."""
    return """
I'll help you analyze responses from your Google Form. Please provide the form ID, and I'll:

1. Retrieve all responses
2. Summarize the key findings
3. Identify patterns in the responses
4. Generate visualizations of the data (if needed)

Let me know if you have specific questions about the data that you'd like me to address.
"""

# Run the server when the script is executed directly
if __name__ == "__main__":
    mcp.run()