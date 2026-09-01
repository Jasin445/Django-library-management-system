import asyncio
import json
import os
import re

import pymupdf
from dotenv import load_dotenv
from httpx import AsyncClient
from nltk.tokenize import sent_tokenize
from pydantic import BaseModel

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


class Message(BaseModel):
    role: str
    content: str


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object: str
    model: str
    created: int
    choices: list[Choice]
    usage: Usage


class MistralClient:
    BASE_URL = "https://api.mistral.ai"

    def __init__(self, api_key):
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY is not set!")
        self.api_key = api_key

    def build_headers(self):
        return {
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

    def parse_response(self, data: dict) -> ChatResponse:
        return ChatResponse.model_validate(data)

    def to_dict(self, messages: list[Message]) -> list[dict]:
        return [m.model_dump() for m in messages]

    def payload(self, msg, max_tokens, temp, model, stream: bool = False):
        return {
            "messages": self.to_dict(msg),
            "temperature": temp,
            "max_tokens": max_tokens,
            "model": model,
            "stream": stream,
        }

    async def chat(
        self,
        message: list[Message],
        max_tokens: int = 30000,
        temperature: float = 0.5,
        model: str = "mistral-small-latest",
    ):
        async with AsyncClient() as client:
            res = await client.post(
                url=f"{self.BASE_URL}/v1/chat/completions",
                headers=self.build_headers(),
                json=self.payload(
                    msg=message, max_tokens=max_tokens, temp=temperature, model=model
                ),
            )
            res.raise_for_status()
            data = res.json()
            parsed = self.parse_response(data)
            print(parsed)
            return parsed

    async def stream(
        self,
        message: list[Message],
        max_tokens: int = 1000,
        temperature: float = 0.5,
        model: str = "mistral-small-latest",
    ):
        async with AsyncClient() as client:  # noqa: SIM117
            async with client.stream(
                url=f"{self.BASE_URL}/v1/chat/completions",
                method="POST",
                headers=self.build_headers(),
                json=self.payload(
                    msg=message,
                    max_tokens=max_tokens,
                    temp=temperature,
                    model=model,
                    stream=True,
                ),
            ) as res:
                res.raise_for_status()

                async for chunk in res.aiter_lines():
                    if not chunk.startswith("data: "):
                        continue

                    payload_str = chunk.removeprefix("data: ").strip()

                    if payload_str == "[DONE]":
                        break

                    parsed_chunk = json.loads(payload_str)
                    content = parsed_chunk["choices"][0]["delta"].get("content")

                    if content:
                        print(content, end="", flush=True)

                print()


async def mainw():
    client = MistralClient(MISTRAL_API_KEY)
    await client.stream(
        message=[
            Message(
                role="system",
                content=(
                    "You are a character who has zero knowledge about anything. "
                    "You do not know facts, definitions, or explanations for any topic, "
                    "no matter how simple. When asked a question, respond with confusion "
                    "or a vague, unhelpful guess — never give an accurate or educational answer. "
                    "Stay in character at all times, even for basic questions."
                ),
            ),
            Message(role="user", content="what is tokenization??"),
        ],
        temperature=0.8,
    )


def main(path: str):
    with pymupdf.open(filename=path, filetype="pdf") as doc:
        content = []
        for page_number, page in enumerate(doc, start=1):
            content.append({"page_number": page_number, "text": page.get_text()})
        result = {"source": path, "content": content}
        return result

def clean_text(text: str) -> str:
    # Normalize non-breaking spaces
    text = text.replace("\xa0", " ")

    # Remove Markdown code-fence markers
    text = re.sub(r"```(?:\w+)?", "", text)

    # Remove remaining Markdown backticks
    text = text.replace("`", "")

    # Remove obvious PDF diagram border artifacts
    text = re.sub(r"I{3,}", "", text)

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r'--- Page \d+ ---', '', text)

    # Remove Markdown heading markers
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def clean_document(doc):
    cleaned_content = []
    for page in doc["content"]:
        cleaned_text = clean_text(page["text"])
        cleaned_content.append({
            "page_number": page["page_number"],
            "text": cleaned_text
        })

    return {
        "source": doc["source"],
        "content": cleaned_content
    }

# if __name__ == "__main__":
doc = main("documents/Jason_Dagana_CV (1).pdf")
doc_obj = clean_document(doc)
text = ""
for page in doc_obj["content"]:
    # print(f"\n--- Page {page['page_number']} ---")
    # print(page["text"])
    text += f"""{page["text"]}"""
sentences = sent_tokenize(text)

start = 0
chunk = []

# while start < len(sentences):
#     end = start + 2
#     chunkSentences = sentences[start:end]
#     chunk.append(",".join(chunkSentences))


#     start = end - 1

# print(" ".join(chunk))



text = "In the beginning God created the heavens and the earth and the earth was without form and void and the darkness was upon the face of the deep and the spirit of the lord moved upon the face of the waters and God said let there be light and there was light and the Lord saw that it was good and the beginning and the morning was the first day"

words = text.split()
start = 0
chunk = []

while start < len(words):
    end = start + 5
    chunkWord = words[start:end]
    chunk.append(" ".join(chunkWord))


    start = end - 2

print(chunk)