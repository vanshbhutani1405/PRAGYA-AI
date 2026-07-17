import base64
import json

from groq import Groq

from config import settings

_client = Groq(api_key=settings.GROQ_API_KEY)

_EXTRACTION_SCHEMA = {
    "equipment_tags": [],
    "permit_ids": [],
    "dates": [],
    "procedure_refs": [],
    "regulation_clauses": [],
    "personnel": [],
    "state_transitions": [],
    "document_type": "",
    "summary": "",
}

_SYSTEM_PROMPT = (
    "You are an industrial document analysis engine. Extract structured knowledge "
    "from the provided text and return ONLY valid JSON matching this schema: "
    "equipment_tags (list of strings), permit_ids (list of strings), "
    "dates (list of strings), procedure_refs (list of strings), "
    "regulation_clauses (list of strings), personnel (list of strings), "
    "state_transitions (list of objects with keys: tag, from_state, to_state, timestamp), "
    "document_type (string), summary (string). "
    "Use empty lists or empty strings when nothing is found."
)


def _parse_json(content: str) -> dict:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return dict(_EXTRACTION_SCHEMA)
    result = dict(_EXTRACTION_SCHEMA)
    result.update({k: data[k] for k in _EXTRACTION_SCHEMA if k in data})
    return result


def extract_entities(text: str) -> dict:
    """Extract structured entities from document text as JSON."""
    completion = _client.chat.completions.create(
        model=settings.GROQ_TEXT_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return _parse_json(completion.choices[0].message.content)


def vision_extract(image_bytes: bytes) -> dict:
    """Extract structured entities from a scanned/image document via the vision model."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    completion = _client.chat.completions.create(
        model=settings.GROQ_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _SYSTEM_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded}"},
                    },
                ],
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return _parse_json(completion.choices[0].message.content)
