from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from sendgrid import SendGridAPIClient
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
import app.Utils.database_handler as crud
import os
from urllib.parse import quote

sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
sendgrid_from_email = os.getenv("SENDGRID_FROM_EMAIL")

async def get_api_key_and_from_mail(db: Session):
    # Retrieve variables from the database using CRUD operations
    variables = await crud.get_variables(db)
    api_key = ''
    from_mail = ''
    if variables:
        api_key = variables.sendgridApiKey or sendgrid_api_key
        from_mail = variables.sendgridEmail or sendgrid_from_email
    else:
        api_key = sendgrid_api_key
        from_mail = sendgrid_from_email
    return api_key, from_mail


async def send_mail(text: str, subject: str, to_email: str, db: Session):
    try:
        api_key, from_mail = await get_api_key_and_from_mail(db)

        sendgrid_client = SendGridAPIClient(api_key=api_key)
        print("sendgrid - to_email", to_email)
        print(api_key, from_mail)
        # to_email = "serhiivernyhora@outlook.com"
        from_email_obj = Email(from_mail)  # Change to your verified sender
        to_email_obj = To(to_email)  # Change to your recipient
        content = Content("text/plain", text)
        mail = Mail(from_email_obj, to_email_obj, subject, content)
        mail_json = mail.get()
        
        # Send an HTTP POST request to /mail/send
        response = sendgrid_client.client.mail.send.post(request_body=mail_json)
        print("status code: ", response.status_code)
        print(response)
        if response.status_code == 202:
            return True
        else:
            return False
    except Exception as e:
        print(f"Send mail Error: {e}")
        return False

async def send_opt_in_email(customer_id: int, to_email: str, db: Session):
    print("sendgrid - customer_id: ", customer_id)
    print("sendgrid - to_email: ", to_email)
    try:
        confirm_url = f"https://backend.getdelmar.com/api/v1/confirm-opt-in-status?customer_id={customer_id}&response=accept"
        refuse_url = f"https://backend.getdelmar.com/api/v1/confirm-opt-in-status?customer_id={customer_id}&response=refuse"

        # Create the HTML content for the email with two buttons
        html_content = f"""
            <html>
            <head>
                <style>
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    text-align: center;
                    text-decoration: none;
                    outline: none;
                    color: #fff;
                    background-color: #4CAF50;
                    border: none;
                    border-radius: 15px;
                    box-shadow: 0 9px #999;
                }}
                .button:hover {{background-color: #3e8e41}}
                .button:active {{
                    background-color: #3e8e41;
                    box-shadow: 0 5px #666;
                    transform: translateY(4px);
                }}
                .button-red {{
                    background-color: #f44336;
                }}
                .button-red:hover {{background-color: #da190b}}
                .button-red:active {{
                    background-color: #da190b;
                    box-shadow: 0 5px #666;
                    transform: translateY(4px);
                }}
                </style>
            </head>
            <body>
                <p>Please click one of the buttons below to confirm your choice:</p>
                <a href="{confirm_url}" class="button">Accept</a>
                <a href="{refuse_url}" class="button button-red">Refuse</a>
            </body>
            </html>
        """
        api_key, from_mail = await get_api_key_and_from_mail(db)
        # from_mail="jack.bear000@gmail.com"
        sendgrid_client = SendGridAPIClient(api_key=api_key)

        # to_email = "ceo@m2echicago.com"
        # to_email = "serhiivernyhora@outlook.com"

        from_email_obj = Email(from_mail)  # Change to your verified sender
        to_email_obj = To(to_email)  # Change to your recipient
        html_content = HtmlContent(html_content)
        print("sendgrid - html_content: ", html_content)
        mail = Mail(from_email_obj, to_email_obj, 'Please Confirm Your Opt-In Status', html_content)
        mail_json = mail.get()
        
        # Send an HTTP POST request to /mail/send
        response = sendgrid_client.client.mail.send.post(request_body=mail_json)
        
        print("sendgrid - response: ", response)
        
        if response.status_code == 202:
            return True
        else:
            print("-----------------------------------", response.status_code)
            return False
    except Exception as e:
        print(f"Send mail Error: {e}")
        return False
    
async def send_approve_email(customer_email: str, db: Session):
    
    encoded_email = quote(customer_email)
    try:
        # confirm_url = f"https://backend.getdelmar.com/api/v1/approved?email={encoded_email}&response=accept"
        # refuse_url = f"https://backend.getdelmar.com/api/v1/approved?email={encoded_email}&response=refuse"

        confirm_url = f"https://backend.thequarrythornton.com/api/v1/approved?email={encoded_email}&response=accept"
        refuse_url =  f"https://backend.thequarrythornton.com/api/v1/approved?email={encoded_email}&response=refuse"

        print("sendgrid - confirm_url", confirm_url)
        # Create the HTML content for the email with two buttons
        html_content = f"""
            <html>
            <head>
                <style>
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    text-align: center;
                    text-decoration: none;
                    outline: none;
                    color: #fff;
                    background-color: #4CAF50;
                    border: none;
                    border-radius: 15px;
                    box-shadow: 0 9px #999;
                }}
                .button:hover {{background-color: #3e8e41}}
                .button:active {{
                    background-color: #3e8e41;
                    box-shadow: 0 5px #666;
                    transform: translateY(4px);
                }}
                .button-red {{
                    background-color: #f44336;
                }}
                .button-red:hover {{background-color: #da190b}}
                .button-red:active {{
                    background-color: #da190b;
                    box-shadow: 0 5px #666;
                    transform: translateY(4px);
                }}
                </style>
            </head>
            <body>
                <p>Please click one of the buttons below to confirm your choice:</p>
                <a href="{confirm_url}" class="button">Approve</a>
                <a href="{refuse_url}" class="button button-red">Decline</a>
            </body>
            </html>
        """
        api_key, from_mail = await get_api_key_and_from_mail(db)
        
        # from_mail="jack.bear000@gmail.com"
        sendgrid_client = SendGridAPIClient(api_key=api_key)

        to_email = "ceo@m2echicago.com"
        # to_email = "serhiivernyhora@outlook.com"
        # to_email = "y.h.forever.212@gmail.com"

        from_email_obj = Email(from_mail)  # Change to your verified sender
        to_email_obj = To(to_email)  # Change to your recipient
        html_content = HtmlContent(html_content)
        print("sendgrid - from_email_obj: ", from_mail)
        mail = Mail(from_email_obj, to_email_obj, 'New customer registerd!', html_content)
        mail_json = mail.get()
        print("sendgrid - to_email: ", to_email)
        # Send an HTTP POST request to /mail/send
        response = sendgrid_client.client.mail.send.post(request_body=mail_json)
        
        print("sendgrid - response: ", response)
        
        if response.status_code == 202:
            return True
        else:
            print("-----------------------------------", response.status_code)
            return False
    except Exception as e:
        print(f"Send mail Error: {e}")
        return False