from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import os
from dotenv import load_dotenv

load_dotenv()


class NERProcessor:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0,
            max_tokens=1024,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        self.ner_prompt = PromptTemplate.from_template(
            """Extract named entities from this text following these rules:

            1. Categories:
            - PER (People)
            - ORG (Organizations)
            - LOC (Locations)
            - DATE (Dates/Times)
            - MISC (Other Important Terms)

            2. Format:
            {{
                "PER": [],
                "ORG": [],
                "LOC": [],
                "DATE": [],
                "MISC": []
            }}

            Text: {text}

            Return only valid JSON:"""
        )

        self.ner_chain = LLMChain(llm=self.llm, prompt=self.ner_prompt)

    def process_text(self, text):
        try:
            if not text.strip():
                raise ValueError("Empty input text")

            result = self.ner_chain.invoke({"text": text})
            return self._format_output(result["text"])
        except Exception as e:
            raise RuntimeError(f"Processing failed: {str(e)}") from e

    def _format_output(self, raw_output):
        try:
            # Clean common formatting issues
            cleaned = raw_output.strip()
            if '```json' in cleaned:
                cleaned = cleaned.split('```json')[1].split('```')[0]
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"error": "Failed to parse model output"}
        except Exception as e:
            return {"error": f"Formatting error: {str(e)}"}