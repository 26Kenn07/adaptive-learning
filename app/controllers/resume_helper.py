import os
from groq import Groq
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from app.database.models import Resume
from app.utils.return_message import Success

load_dotenv()

UPLOAD_PATH = os.environ["UPLOAD_PATH"]
groq_api_key = os.environ['GROQ_API_KEY']
HUGGINGFACEHUB_API = os.environ['HUGGINGFACEHUB_API_TOKEN']

embeddings = HuggingFaceBgeEmbeddings(model_name = "sentence-transformers/all-MiniLM-l6-v2", model_kwargs = {'device': 'cpu'}, encode_kwargs = {'normalize_embeddings' : True})

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

async def resume_upload(file, db, current_user):
    if file:
        filename = file.filename
        
        upload_dir = UPLOAD_PATH
        os.makedirs(upload_dir, exist_ok=True)
        
        file_location = os.path.join(upload_dir, filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        resume_content = pdf_parser(file_location)
        
        resume_review = await resume_evaluation(resume_content)

        uploaded_file = Resume(
        filename=filename,
        user_id = current_user['id'],
        location=file_location,
        resume_results=str(resume_review)
        )
    
        db.add(uploaded_file)
        db.commit()
        
    return Success(message="Resume Evaluated Successfully", data=resume_review)
            
def pdf_parser(file_location):
    loader = PyPDFLoader(file_path=file_location)
    pdf_doc = loader.load()
            
    pdf_content = ''.join([page.page_content.replace('\n', ' ') for page in pdf_doc])
    
    print(pdf_content)
            
    return pdf_content

                
async def resume_evaluation(resume_content):
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are an experienced hiring manager tasked with reviewing and scoring a resume."
        },
        {
            "role": "user",
            "content": f"""
    Resume Score (out of 100): Provide a score based on the overall quality of the resume.
    Strong Parts of the Resume: Highlight the strengths in the resume content, such as skills, achievements, and presentation.
    Weak Parts of the Resume: Point out areas that need improvement or are lacking.
    Scope of Improvements: Offer actionable suggestions to enhance the resume, such as refining formatting, adding missing details, or improving clarity.
    Resume is Best Suited for the Following Roles: Suggest job roles or positions for which the resume is most suitable.
    Useful Links: Provide domain-specific links or resources to help the user expand their knowledge and skills. (Do not include links to resume-building or reviewing websites.)
    Response Format:
    Always present your response in list of json format, structured as follows:
    <your_answer>
    [{{
        "Resume Score": "(Score out of 100)/100",
        "Strong Parts of the Resume	": "(Strengths in bullet points)",
        "Weak Parts of the Resume": "(Weaknesses in bullet points)",
        "Scope of Improvements": "(Specific improvement areas in bullet points)",
        "Resume is Best Suited for Roles": "(Roles the resume is best suited for)",
        "Useful Links": "(Provide domain-specific resources to enhance knowledge or skills)",
        "Additional Instructions": ,
    }}]
    </your_answer>
    
    Use phrases like “your skills” and “your profile” to personalize the response.
    Strictly follow the response format and do not include any additional notes outside of the list of json.
    Do not provide links to resume-building or reviewing websites in the "Useful Links" section.
    Input:

    <Resume Content> {resume_content} <Resume Content>: The actual content of the resume to be reviewed.
    
    <DO NOT FORGET TO GIVE RESPONSE IN LIST OF JSON FORMAT>
    """
    }],
    model="llama-3.1-70b-versatile",
    )
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content
