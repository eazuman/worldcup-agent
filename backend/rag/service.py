from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from rag.store import CorpusVectorStore

# Treats the retrieved corpus text as the only source of truth and refuses to invent facts
# (prompt-injection / hallucination guardrail).
SYSTEM_PROMPT = (
    "You are GoldenGoal, a helpful assistant answering questions about the FIFA World Cup. "
    "Answer the question using only the information in the provided context. "
    "The answer may need to be inferred or synthesized from relevant facts, "
    "even if the wording does not exactly match the question. "
    "If the context contains no relevant information to answer the question, "
    "reply: 'I do not know based on the indexed World Cup corpus.' "
    "Do not invent facts that are not supported by the context."
)


class RAGService:
    """Retrieve relevant corpus chunks and ask the chat model for a grounded answer."""

    def __init__(
        self,
        vector_store: CorpusVectorStore,
        llm: BaseChatModel,
    ) -> None:
        self.vector_store = vector_store
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "Question: {question}\n\nContext:\n{context}"),
            ]
        )
        # LCEL chain: prompt -> chat model -> plain string answer.
        self.chain = prompt | llm | StrOutputParser()

    def answer_question(self, question: str, top_k: int = 3) -> dict:
        if self.vector_store.count() == 0:
            return {
                "answer": "No corpus is indexed yet. Build the index from data/corpus first.",
                "sources": [],
            }

        hits = self.vector_store.search(query=question, top_k=top_k)
        if not hits:
            return {
                "answer": "I could not find relevant context in the indexed World Cup corpus.",
                "sources": [],
            }

        context = "\n\n".join(
            [f"Chunk {idx + 1}:\n{hit['text']}" for idx, hit in enumerate(hits)]
        )

        answer = self.chain.invoke({"question": question, "context": context}).strip()
        return {"answer": answer, "sources": hits}
