from sqlalchemy.orm import Session
from database import AsyncSessionLocal
import app.Utils.database_handler as crud
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from datetime import datetime
load_dotenv()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

openai_api_key = os.getenv('OPENAI_API_KEY')
standard_prompts = """
    Focus on:
    Introduction acknowledging our role as their contractor.
    Overview of project objectives and recent progress.
    Summary of milestones, deliverables, and key metrics.
    Notable challenges and solutions.
    Next steps and expected outcomes.
    Conclusion emphasizing our commitment and appreciation.
    When there are no new work orders or changes, focus on notable challenges, solutions, next steps, and appreciation.

    The report should be professional, engaging, and reflect our brand. Exclude individual employee references.
"""

# Function to retrieve API key and prompts from the database
async def get_api_key_and_prompts(db: Session):
    variables = await crud.get_variables(db)
    api_key = ''
    main_prompts = ''
    if variables:
        api_key = variables.openAIKey or openai_api_key
        main_prompts = variables.prompts or standard_prompts
    else:
        api_key = openai_api_key
        main_prompts = standard_prompts
    return api_key, main_prompts

# Function to get the last message using OpenAI
async def get_last_message(db: Session, manager_name, manager_phone, manager_email, report_list, customer_name: str):
    api_key, main_prompts = await get_api_key_and_prompts(db)
    print("chatgpt - main_prompts: ", api_key, main_prompts)
    client = AsyncOpenAI(api_key=api_key)
    
    if not report_list:
        return ""

    report_history = '\n'.join(report.message for report in report_list)  # 2 means message column

    print("chatgpt - main_prompts: ", main_prompts)

    if not manager_name:
        manager_name = "Angela Bermudez"
        manager_phone = "+1 312 443 2120"
        manager_email = "angelab@getdelmar.com"
    
    instruction = f"""
        Now is {datetime.now()}
        I need a work report for our customer, {customer_name}, summarizing the latest update in the project timeline.
        And below is the project manager contact information for this project.
            Project manager name: {manager_name}
            Project manager phone: {manager_phone}
            Project manager email: {manager_email}
        
        This is the historical report on the progress of this project. Before you analyze this report history, please sort them by time so that you can understand the progress of project correctly.
        In easy word, please sort below history in reverse cronological order before you refer to below history.
        {report_history}
        -----------------------------
        {main_prompts}
    """
    
    response = await client.chat.completions.create(
        model='gpt-4-0125-preview',
        max_tokens=2000,
        messages=[
            {'role': 'system', 'content': instruction},
            {'role': 'user', 'content': f"Please provide a personalized notification."}
        ],
        temperature=0.7
    )
    response_message = response.choices[0].message.content
    
    print("chatgpt - response_message: ", response_message)
    
    return response_message