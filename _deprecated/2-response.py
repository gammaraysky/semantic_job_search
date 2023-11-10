import logging
import os

import chromadb
import requests
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index import Document, ServiceContext, StorageContext, VectorStoreIndex
from llama_index.embeddings import LangchainEmbedding  # BertEmbedding
from llama_index.llms import OpenAI
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.response_synthesizers import get_response_synthesizer
from llama_index.vector_stores import ChromaVectorStore

from src.mycareersfuture import MyCareersFutureListings


def setup_environment():
    # Load environment variables from .env
    load_dotenv()
    # os.environ['OPENAI_API_KEY'] = 'sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    os.environ["LLAMA_INDEX_CACHE_DIR"] = "cache"
    HF_TOKEN = os.getenv("HF_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def load_documents():
    # return SimpleDirectoryReader(
    #     path,
    #     recursive=True,
    #     required_exts=[".pdf"],
    #     filename_as_id=True,
    # ).load_data()

    JSON_LOAD_FILE = "./jobslist.json"
    SLEEP_DELAY = 0.5

    mcf_listings = MyCareersFutureListings(sleep_delay=SLEEP_DELAY)
    listings = mcf_listings.load_json(json_load_file=JSON_LOAD_FILE)

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
            text_template="Metadata: {metadata_str}\n-----\nJob Listing: {content}",
        )
        for listing in reduced
    ]

    return documents


def setup_index(documents):
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("quickstart")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = LangchainEmbedding(
        HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    )
    service_context_embedding = ServiceContext.from_defaults(embed_model=embed_model)
    return VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        service_context=service_context_embedding,
    )


def setup_query_engine(index):
    # node_parser = SimpleNodeParser.from_defaults(
    #     text_splitter=TokenTextSplitter(chunk_size=1024, chunk_overlap=20)
    # )
    # prompt_helper = PromptHelper(
    #     context_window=4096,
    #     num_output=256,
    #     chunk_overlap_ratio=0.1,
    #     chunk_size_limit=None,
    # )

    # service_context = ServiceContext.from_defaults(
    #     llm=llm,
    #     embed_model=embed_model,
    #     node_parser=node_parser,
    #     prompt_helper=prompt_helper,
    # )
    service_context_llm = ServiceContext.from_defaults(
        llm=OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
        ),
        # system_prompt="You are an AI assistant assisting job seekers find the best matches based on their profile."
    )
    # retriever = VectorIndexRetriever(
    #     index=index,
    #     similarity_top_k=10,
    # )
    retriever = index.as_retriever(similarity_top_k=10)

    response_synthesizer = get_response_synthesizer(
        response_mode="compact",
        service_context=service_context_llm,
        use_async=False,
        streaming=False,
    )

    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever, response_synthesizer=response_synthesizer
    )
    return query_engine


def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    return logger


def main():
    logger = get_logger()
    setup_environment()

    documents = load_documents()
    index = setup_index(documents)
    query_engine = setup_query_engine(index)

    user_input = "Which of the job listings require SQL as a skill?"
    result = query_engine.query(user_input)
    print(f"Answer: {str(result)}")


if __name__ == "__main__":
    main()
