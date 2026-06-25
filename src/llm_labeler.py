import os
import re
import sys
from abc import ABC, abstractmethod

PROMPT_TEMPLATE = """You are labeling sentences for a remote-sensing training dataset.

A sentence is RELEVANT if it describes something a satellite could see on the ground:
land cover (e.g forest, water, wetland, grassland, bare soil, ice...), land use (e.g farmland,
meadow, orchard, vineyard, industrial zone, residential area...), or human-made
infrastructure visible from above (e.g buildings, roads, railways, bridges, parking lots,
dams, ports, solar farms...).

A sentence is NOT RELEVANT if it talks about history, policy, economics, biology,
chemistry, or any topic that does not describe the physical surface of the Earth.

Sentence: "{sentence}"

Answer with exactly one word: RELEVANT or NOT_RELEVANT.
"""

_LABEL_RE = re.compile(r"\b(RELEVANT|NOT_RELEVANT)\b", re.IGNORECASE)


def parse_label(response: str) -> bool | None:
    """Given an LLM response, outputs whether the LLM assessed a sentence as RELEVANT or NOT_RELEVANT.
    If nothing is matched, it returns None.
    """

    match = _LABEL_RE.search(response)
    if not match:
        return None

    return match.group(1).upper() == "RELEVANT"


class BaseLabeler(ABC):
    @abstractmethod
    def label(self, sentence: str) -> tuple[bool | None, str]:
        """Return (label, raw_response). Returns None is the response could not be parsed"""


class LlamaCppLabeler(BaseLabeler):
    """
    Runs a model locally using llama-cpp-python. Needs LLAMACPP_REPO_ID and LLAMACPP_FILENAME to be configured.
    """

    def __init__(
        self,
        repo_id: str,
        filename: str,
        **llama_kwargs,
    ):
        from llama_cpp import Llama

        self.repo_id = repo_id
        self.filename = filename
        self.model_path = f"hf://{repo_id}/{filename}"
        self.llama = Llama.from_pretrained(
            repo_id=repo_id, filename=filename, **llama_kwargs
        )

    def label(self, sentence: str) -> tuple[bool | None, str]:
        prompt = PROMPT_TEMPLATE.format(sentence=sentence)
        response = self.llama.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8,
            temperature=0.0,
            stream=False,
        )
        raw = response["choices"][0]["message"]["content"]
        return parse_label(raw), raw


def make_labeler() -> BaseLabeler:

    repo_id = os.environ.get("LLAMACPP_REPO_ID")
    filename = os.environ.get("LLAMACPP_FILENAME")
    if repo_id and filename:
        return LlamaCppLabeler(repo_id=repo_id, filename=filename)

    raise RuntimeError(
        "No model repo id and filename configured for llamacpp. Set LLAMACPP_REPO_ID and LLAMACPP_FILENAME to continue."
    )


if __name__ == "__main__":
    labeler = make_labeler()
    test_sentences = [
        "A dense forest covers the northern slopes of the region.",
        "The history of agriculture in Mesopotamia is well documented.",
        "Solar panels cover the rooftop of the warehouse.",
        "Bird species richness was higher near the wetland edges.",
    ]

    count = 0
    with open("samples/smoke_test_labels.txt", "w", encoding="utf8") as f:
        for sentence in test_sentences:
            count += 1
            label, raw = labeler.label(sentence)
            line = f"Sentence {count}: {sentence[:50]}. Label : {label} "
            f.write(line + "\n")
            print(line)
