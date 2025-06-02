"""
Module xử lý LLM và reranking.
"""

from typing import List, Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.config import GOOGLE_API_KEY


class LLMManager:
    def __init__(
        self,
        api_key: str = GOOGLE_API_KEY,
        model_name: str = "gemini-2.0-flash-001",
        temperature: float = 0.7,
        max_output_tokens: int = 2048
    ):
        """
        Khởi tạo LLMManager.

        Args:
            api_key: Google API key
            model_name: Tên model LLM
            temperature: Nhiệt độ cho model
            max_output_tokens: Số token tối đa cho output
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
        self.default_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""Dựa trên thông tin sau, hãy trả lời câu hỏi:
            
            Thông tin:
            {context}
            
            Câu hỏi: {question}
            
            Câu trả lời:"""
        )

    def setup_reranker(
        self,
        base_retriever,
        compression_prompt: Optional[str] = None
    ) -> ContextualCompressionRetriever:
        """
        Thiết lập reranker.

        Args:
            base_retriever: Retriever cơ sở
            compression_prompt: Prompt tùy chỉnh cho compression

        Returns:
            ContextualCompressionRetriever: Retriever đã được rerank
        """
        if compression_prompt:
            compressor = LLMChainExtractor.from_llm(
                self.llm,
                prompt=compression_prompt
            )
        else:
            compressor = LLMChainExtractor.from_llm(self.llm)

        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )

    def generate_response(
        self,
        question: str,
        context: str,
        custom_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Tạo câu trả lời dựa trên context và câu hỏi.

        Args:
            question: Câu hỏi cần trả lời
            context: Context để trả lời câu hỏi
            custom_prompt: Prompt tùy chỉnh
            **kwargs: Các tham số bổ sung cho LLM

        Returns:
            str: Câu trả lời được tạo ra
        """
        if custom_prompt:
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template=custom_prompt
            )
        else:
            prompt = self.default_prompt

        chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )

        response = chain.run(
            context=context,
            question=question,
            **kwargs
        )
        return response

    def generate_summary(
        self,
        text: str,
        max_length: int = 200,
        **kwargs
    ) -> str:
        """
        Tạo tóm tắt cho văn bản.

        Args:
            text: Văn bản cần tóm tắt
            max_length: Độ dài tối đa của tóm tắt
            **kwargs: Các tham số bổ sung cho LLM

        Returns:
            str: Tóm tắt được tạo ra
        """
        prompt = PromptTemplate(
            input_variables=["text", "max_length"],
            template=f"""Hãy tóm tắt đoạn văn bản sau trong khoảng {{max_length}} từ:
            
            {{text}}
            
            Tóm tắt:"""
        )

        chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )

        response = chain.run(
            text=text,
            max_length=max_length,
            **kwargs
        )
        return response
