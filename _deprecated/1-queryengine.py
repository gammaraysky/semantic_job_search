import logging
import os

import chromadb
import requests
import yaml
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index import Document, ServiceContext, StorageContext, VectorStoreIndex
from llama_index.embeddings import LangchainEmbedding  # BertEmbedding
from llama_index.llms import OpenAI
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.response_synthesizers import get_response_synthesizer
from llama_index.vector_stores import ChromaVectorStore

from src.mycareersfuture import MyCareersFutureListings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def read_yaml_config(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


# Example usage
file_path = "conf/base/config.yml"
config = read_yaml_config(file_path)
print(config)

# Load environment variables from .env
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["LLAMA_INDEX_CACHE_DIR"] = "cache"


mcf_listings = MyCareersFutureListings(sleep_delay=config["scraper_delay"])

listings = mcf_listings.load_json(json_load_file=config["scraper_results_file"])


### REDUCE DATASET TO RELEVANT FIELDS ###
reduced = []
for listing in listings:
    reduced.append(
        {
            "url": listing["metadata"]["jobDetailsUrl"],
            "job_title": listing["title"],
            "job_desc": listing["job_desc"],
            "company": listing["postedCompany"]["name"],
            "salary_min": listing["salary"]["minimum"],
            "salary_max": listing["salary"]["maximum"],
            "skills": ", ".join([skill["skill"] for skill in listing["skills"]]),
        }
    )

### CREATE DOCUMENTS FROM ALL THE RETURNED LISTINGS ###
documents = [
    Document(
        text=listing["job_desc"],
        metadata={
            "url": listing["url"],
            "job_title": listing["job_title"],
            "company": listing["company"],
            "salary_min": listing["salary_min"],
            "salary_max": listing["salary_max"],
            "skills": listing["skills"],
        },
        excluded_llm_metadata_keys=["url", "salary_min", "salary_max"],
        excluded_embed_metadata_keys=["url", "salary_min", "salary_max"],
        metadata_separator="::",
        metadata_template="{key}->{value}",
        text_template="Job Listing Metadata: {metadata_str}\n-----\nJob Listing: {content}\n-----\n",
    )
    for listing in reduced
]

### CREATE VECTOR STORE ###
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
embed_model = LangchainEmbedding(
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
)
service_context_embedding = ServiceContext.from_defaults(embed_model=embed_model)
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    service_context=service_context_embedding,
)

### SET UP SERVICE CONTEXT ###
service_context_llm = ServiceContext.from_defaults(
    llm=OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
    ),
)

### CREATE RETRIEVER ###
retriever = index.as_retriever(similarity_top_k=config["similarity_top_k"])

response_synthesizer = get_response_synthesizer(
    response_mode="compact",
    service_context=service_context_llm,
    use_async=False,
    streaming=False,
)

### CREATE QUERY ENGINE ###
query_engine = RetrieverQueryEngine.from_args(
    retriever=retriever, response_synthesizer=response_synthesizer
)

### LOAD USER'S RESUME ###
with open(config["user_resume_txt_file"], "r", encoding="utf8") as file:
    user_resume = file.read()

### PROMPT TEMPLATE ###
user_input = (
    f"INSTRUCTION:\n{config['instruction_prompt']}\n\n RESUME:\n{user_resume}\n"
)

### RUN QUERY ###
result = query_engine.query(user_input)
print(f"Answer: {str(result)}")
