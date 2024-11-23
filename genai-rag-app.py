import os
import gradio as gr
import pymongo
import mysql.connector
from typing import List, Dict, Any
from pathlib import Path
from llama_index.core import Settings, VectorStoreIndex, get_response_synthesizer
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.readers.file import PDFReader, CSVReader
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.llms import ChatMessage, MessageRole

class DataSourceManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mongodb_client = None
        self.mysql_connection = None
        self.embeddings = HuggingFaceEmbedding(model_name=config['embed_model'])
        Settings.embed_model = self.embeddings

    def connect_mongodb(self):
        if not self.mongodb_client:
            self.mongodb_client = pymongo.MongoClient(self.config['mongodb_url'])
        return self.mongodb_client

    def connect_mysql(self):
        if not self.mysql_connection:
            self.mysql_connection = mysql.connector.connect(
                host=self.config['mysql_host'],
                user=self.config['mysql_user'],
                password=self.config['mysql_password'],
                database=self.config['mysql_database']
            )
        return self.mysql_connection

class ModelManager:
    def __init__(self):
        self.models = {
            'local': {
                'phi': lambda: Ollama(base_url='http://localhost:11434', model='phi'),
                'llama2': lambda: Ollama(base_url='http://localhost:11434', model='llama2'),
                'codellama': lambda: Ollama(base_url='http://localhost:11434', model='codellama')
            },
            'api': {
                'gpt-3.5-turbo': lambda: OpenAI(model='gpt-3.5-turbo'),
                'gpt-4': lambda: OpenAI(model='gpt-4')
            }
        }

    def get_model(self, model_type: str, model_name: str):
        return self.models[model_type][model_name]()

class DocumentProcessor:
    @staticmethod
    def process_files(files: List[str], file_types: List[str]) -> List[Any]:
        documents = []
        for file, file_type in zip(files, file_types):
            if file_type == 'pdf':
                reader = PDFReader()
                documents.extend(reader.load_data(file))
            elif file_type == 'csv':
                reader = CSVReader()
                documents.extend(reader.load_data(file))
            elif file_type == 'log':
                with open(file, 'r') as f:
                    documents.extend([f.read()])
        return documents

def create_chat_interface():
    config = {
        'mongodb_url': os.getenv('MONGODB_URL'),
        'mongodb_dbname': os.getenv('MONGODB_DBNAME'),
        'mysql_host': os.getenv('MYSQL_HOST'),
        'mysql_user': os.getenv('MYSQL_USER'),
        'mysql_password': os.getenv('MYSQL_PASSWORD'),
        'mysql_database': os.getenv('MYSQL_DATABASE'),
        'embed_model': 'BAAI/bge-small-en-v1.5'
    }

    data_manager = DataSourceManager(config)
    model_manager = ModelManager()

    def process_query(
        message: str,
        history: List[str],
        model_type: str,
        model_name: str,
        data_source: str,
        files: List[str]
    ) -> str:
        llm = model_manager.get_model(model_type, model_name)
        Settings.llm = llm

        chat_message = [ChatMessage(role=MessageRole.USER, content=message)]
        
        if files:
            file_types = [Path(f).suffix[1:] for f in files]
            documents = DocumentProcessor.process_files(files, file_types)
            index = VectorStoreIndex.from_documents(documents)
        else:
            if data_source == 'mongodb':
                vector_store = MongoDBAtlasVectorSearch(
                    mongodb_client=data_manager.connect_mongodb(),
                    db_name=config['mongodb_dbname'],
                    collection_name='documents',
                    index_name='document_index'
                )
                index = VectorStoreIndex.from_vector_store(vector_store)
            else:
                # Handle MySQL data source
                pass

        retriever = VectorIndexRetriever(index=index, similarity_top_k=4)
        response_synthesizer = get_response_synthesizer(llm=llm)
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)]
        )
        
        chat_engine = CondenseQuestionChatEngine.from_defaults(
            query_engine=query_engine,
            llm=llm
        )

        response = chat_engine.stream_chat(chat_message)
        return "".join(response.response_gen)

    with gr.Blocks(title='Advanced GenAI with RAG') as app:
        with gr.Row():
            with gr.Column():
                model_type = gr.Radio(
                    choices=['local', 'api'],
                    value='local',
                    label='Model Type'
                )
                model_name = gr.Dropdown(
                    choices=['phi', 'llama2', 'codellama'],
                    value='phi',
                    label='Model'
                )
                data_source = gr.Radio(
                    choices=['mongodb', 'mysql', 'files'],
                    value='mongodb',
                    label='Data Source'
                )
                file_upload = gr.File(
                    file_types=['.pdf', '.csv', '.log'],
                    file_count='multiple',
                    visible=False,
                    label='Upload Files'
                )

        def update_model_choices(model_type):
            return gr.Dropdown(
                choices=list(ModelManager().models[model_type].keys())
            )

        def update_file_upload(data_source):
            return gr.File(visible=data_source == 'files')

        model_type.change(
            fn=update_model_choices,
            inputs=model_type,
            outputs=model_name
        )
        
        data_source.change(
            fn=update_file_upload,
            inputs=data_source,
            outputs=file_upload
        )

        gr.ChatInterface(
            fn=process_query,
            title='Advanced GenAI RAG System',
            description='Interact with multiple models and data sources',
            additional_inputs=[
                model_type,
                model_name,
                data_source,
                file_upload
            ]
        )

    return app

if __name__ == "__main__":
    app = create_chat_interface()
    app.launch(server_name='0.0.0.0', server_port=7860)
