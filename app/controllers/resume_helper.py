import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain


from app.database.models import Resume
from app.utils.return_message import Success

load_dotenv()

UPLOAD_PATH = os.environ["UPLOAD_PATH"]
groq_api_key = os.environ['GROQ_API_KEY']
HUGGINGFACEHUB_API = os.environ['HUGGINGFACEHUB_API_TOKEN']
VECTORDB_PATH = os.environ["VECTORDB_PATH"]

embeddings = HuggingFaceBgeEmbeddings(model_name = "sentence-transformers/all-MiniLM-l6-v2", model_kwargs = {'device': 'cpu'}, encode_kwargs = {'normalize_embeddings' : True})

llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="llama-3.1-70b-versatile")

async def resume_upload(file, db, current_user):
    if file:
        filename = file.filename
        
        upload_dir = UPLOAD_PATH
        os.makedirs(upload_dir, exist_ok=True)
        
        file_location = os.path.join(upload_dir, filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        return await pdf_uploader(db, file_location, filename, current_user)
    
    
    
async def pdf_uploader(db, file_location, filename, current_user):
    loader = PyPDFLoader(file_path=file_location)
    pdf_doc = loader.load()
    
    vector_store_path = VECTORDB_PATH
    vector_db = None
    
    if os.path.exists(vector_store_path):
        vector_db = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        
    pdf_content = ''.join([page.page_content.replace('\n', ' ') for page in pdf_doc])
    print(current_user)
    documents = [
    Document(page_content=pdf_content, metadata={"user_id": current_user['id'], 'source': file_location})
    ]    
    
    vectordb = FAISS.from_documents(documents=documents, embedding=embeddings)

    ids = list(vectordb.index_to_docstore_id.values())
    ids_json = json.dumps(ids)
    
    uploaded_file = Resume(
        filename=filename,
        user_id = current_user['id'],
        location=file_location,
        faiss_index = ids_json
        )
    
    db.add(uploaded_file)
    db.commit()
    
    if not vector_db:
        vectordb.save_local(vector_store_path)
    else:
        vector_db.merge_from(vectordb)
        vector_db.save_local(vector_store_path)
        
    return Success(message="Resume Uploaded Successfully", data=filename)


def load_db():
    vector_DB = VECTORDB_PATH
    if os.path.exists(vector_DB):
        vector_DB = FAISS.load_local(VECTORDB_PATH, embeddings, allow_dangerous_deserialization=True)
        return vector_DB
    return None
        
        
def load_chain(vector_db, user_id):
    """Logic for loading the chain you want to use should go here."""
    prompt = """
    {question}
    You are an experienced hiring manager and you are going to score this resume content out of 100 and provide valuable insights such as
    Strong parts of the resume, Weak parts of the resume, Scope of improvements, Useful links to improve resume or users knowledge on the domain
    Give response like you are taling to that perticular user like "your skills", "your proifle"
    give response in the following format
    Resume score:
    Strong parts of the resume:
    Weak parts of the resume:
    Scope of improvements:
    Resume is best suited for the following roles:
    Useful links:
    
    <Resume Content>
    {summaries}
    <Resume Content>
    ALWAYS GIVE ANSWER IN TABLE FORMAT
    """



    QA_PROMPT = PromptTemplate(
        template=prompt, input_variables=["summaries", "question"]
    )
    
    qa_chain = load_qa_with_sources_chain(
        llm,
        chain_type="stuff",
        prompt=QA_PROMPT,
    )
    

    chain = RetrievalQAWithSourcesChain(
        combine_documents_chain=qa_chain,
        retriever=vector_db.as_retriever(
            search_kwargs={'filter': {'user_id': user_id}},
        ),
        return_source_documents=True,
    )

    return chain


def final_chain(user_id):
    vector_db= load_db()
    
    if vector_db:
        chain = load_chain(vector_db, user_id)
        output = chain({"question": ''}, return_only_outputs=True)
        
        return output
    
    return None, False

async def resume_review(db, user_id):
    response = final_chain(user_id)
    print(response['answer'])
    return response