from typing import Any, List

from InstructorEmbedding import INSTRUCTOR
from llama_index.embeddings.base import BaseEmbedding

model = INSTRUCTOR("hkunlp/instructor-large")
sentence = "3D ActionSLAM: wearable person tracking in multi-floor environments"
instruction = "Represent the Science title:"
embeddings = model.encode([[instruction, sentence]])
print(embeddings)


class InstructorEmbeddings(
    BaseEmbedding,
):
    def __init__(
        self,
        instructor_model_name: str = "hkunlp/instructor-large",
        instruction: str = "Represent the Computer Science text for retrieval:",
        **kwargs: Any,
    ) -> None:
        self._model = INSTRUCTOR(instructor_model_name)
        self._instruction = instruction
        super().__init__(**kwargs)

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = model.encode([[self._instruction, query]])
        return embeddings[0].tolist()

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = model.encode([[self._instruction, text]])
        return embeddings[0].tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = model.encode([[self._instruction, text] for text in texts])
        return embeddings.tolist()
