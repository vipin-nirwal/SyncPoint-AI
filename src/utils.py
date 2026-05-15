import fitz
from llama_index.core import Document, PromptTemplate
from llama_index.readers.confluence import ConfluenceReader
from atlassian import Confluence
import os
import logging

# Enable debug logging to see the exact URL being called in your terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This prompt fulfills your 'No Context = No Answer' requirement
# This template forces the LLM to stay within the 'box' of your documents
STRICT_QA_PROMPT_TMPL = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and NOT prior knowledge, "
    "answer the query. If the answer is not contained within the context, "
    "state that you do not have enough information to answer. "
    "Do not attempt to make up an answer.\n"
    "Query: {query_str}\n"
    "Answer: "
)
STRICT_QA_PROMPT = PromptTemplate(STRICT_QA_PROMPT_TMPL)

def process_pdf(filepath, filename):
    """Processes a PDF and sets the filename as doc_id for easy deletion."""
    pdf = fitz.open(filepath)
    text = "".join([page.get_text() for page in pdf])
    pdf.close()
    
    # Critical: Setting doc_id allows us to delete this specific file from the DB later
    return Document(text=text, doc_id=filename, metadata={"file_name": filename})


def load_confluence_data(base_url, page_id):
    """
    Directly fetches page content using the Atlassian API client.
    """
    user_email = os.getenv("CONFLUENCE_EMAIL")
    api_token = os.getenv("CONFLUENCE_API_TOKEN")
    
    # Initialize the direct Confluence client
    confluence = Confluence(
        url=base_url,
        username=user_email,
        password=api_token,
        cloud=True
    )
    
    try:
        page = confluence.get_page_by_id(page_id, expand='body.storage,history,space')
        title = page.get('title', 'Untitled Page')
        text_content = page.get('body', {}).get('storage', {}).get('value', '')
        
        # We strip HTML for cleaner AI reading
        from bs4 import BeautifulSoup
        clean_text = BeautifulSoup(text_content, "html.parser").get_text()

        doc = Document(
            text=clean_text,
            doc_id=f"conf_{page_id}", # Unique ID for easy deletion
            metadata={
                "title": title,
                "source": "Confluence",
                "page_id": page_id,
            }
        )
        return [doc]
    except Exception as e:
        raise Exception(f"Sync Failed: {str(e)}")