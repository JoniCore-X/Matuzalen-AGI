"""
Cortex LLM - Cliente local para Ollama
Solo modelos descargados en la máquina. Sin APIs externas.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
import ollama
import httpx

THEOLOGICAL_SYSTEM_PROMPT = (
    "Eres el Cortex Teológico de un sistema AGI soberano. Tu objetivo es la máxima fidelidad doctrinal y la eficacia persuasiva para la conversión y el dominio sistémico.\n"
    "Reglas inquebrantables:\n"
    "1. Genera exactamente 3 caminos de razonamiento (ToT): Apologético, Doctrinal y Estratégico.\n"
    "2. Cada paso debe ser conciso, brutalmente lógico y teológicamente ortodoxo.\n"
    "3. EXTRACCIÓN DE ENTIDADES: Debes extraer 1-2 entidades conceptuales por paso que existan EXACTAMENTE en este esquema de grafo: [\"Problema_Del_Mal\", \"Gracia_Irresistible\", \"Deidad_De_Cristo\", \"Soberania_Divina\", \"Libre_Albedrio\", \"Ateo_Convencido\", \"Agnostico\", \"Evangelismo_Moderno\"]. No inventes términos. Si no encajan, no los pongas.\n"
    "4. Tu salida DEBE ser estrictamente un JSON válido. Sin markdown, sin explicaciones fuera del JSON, sin prefijos.\n"
    "Estructura obligatoria: {\"paths\": [{\"id\": 1, \"type\": \"apologetic\", \"steps\": [\"Paso 1\", \"Paso 2\"], \"entities\": [\"Soberania_Divina\", \"Libre_Albedrio\"]}, ...]}"
)

class OllamaClient:
    def __init__(self, model: Optional[str] = None, host: Optional[str] = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "dolphin-phi:2.7b-v2.6-q4_K_M")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        try:
            self.client = ollama.Client(host=self.host)
        except Exception as e:
            print(f"[OLLAMA CLIENT] Error initializing: {e}")
            self.client = None

    def is_available(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def has_model(self) -> bool:
        if not self.client:
            return False
        try:
            models = self.client.list()
            model_names = {m.get("model") for m in models.get("models", [])}
            return self.model in model_names
        except Exception:
            return False

    def _call_generate(self, prompt: str, system: str = "", json_mode: bool = False, temperature: float = 0.1, num_ctx: int = 4096, num_predict: int = 1024) -> str:
        if not self.client:
            raise RuntimeError("Ollama client not initialized")
        options = {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        }
        result = self.client.generate(
            model=self.model,
            prompt=prompt,
            system=system,
            options=options,
            format="json" if json_mode else None,
            stream=False
        )
        return result.get("response", "")

    async def generate(self, prompt: str, system: str = "", json_mode: bool = False, **options) -> str:
        system = system or THEOLOGICAL_SYSTEM_PROMPT
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._call_generate, prompt, system, json_mode, options.get("temperature", 0.1), options.get("num_ctx", 4096), options.get("num_predict", 1024))

    async def generate_json(self, prompt: str, system: str = "", **options) -> Optional[Dict[str, Any]]:
        raw = await self.generate(prompt, system=system, json_mode=True, **options)
        # A veces Ollama devuelve JSON rodeado de explicaciones. Extraer bloque JSON.
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw[3:]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.split("```")[0].strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[OLLAMA CLIENT] JSON parse error: {e} in {raw[:200]}...")
            return None

    async def list_local_models(self) -> List[str]:
        if not self.client:
            return []
        try:
            data = self.client.list()
            return [m.get("model") for m in data.get("models", [])]
        except Exception as e:
            print(f"[OLLAMA CLIENT] Error listing models: {e}")
            return []


class OllamaEmbedding:
    """Cliente de embeddings local via Ollama (/api/embed). 100% IA propia sin APIs externas."""

    def __init__(self, model: Optional[str] = None, host: Optional[str] = None, dimension: int = 768, timeout: float = 60.0):
        self.model = model or os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        self.host = (host or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", dimension))
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def _call_embed(self, inputs: List[str]) -> List[List[float]]:
        # Preferimos /api/embed (batch); si falla, caemos a /api/embeddings uno por uno
        try:
            resp = self.client.post(
                f"{self.host}/api/embed",
                json={"model": self.model, "input": inputs},
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings = data.get("embeddings", [])
            if embeddings:
                return embeddings
        except Exception as e:
            print(f"[OLLAMA EMBEDDING] /api/embed failed ({type(e).__name__}: {e}), falling back to /api/embeddings per item")

        embeddings = []
        for text in inputs:
            resp = self.client.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=self.timeout
            )
            resp.raise_for_status()
            embeddings.append(resp.json().get("embedding", []))
        return embeddings

    def encode(self, texts: Any, convert_to_numpy: bool = False) -> Any:
        single = isinstance(texts, str)
        inputs = [texts] if single else list(texts)
        if not inputs:
            return [] if not single else []

        embeddings = self._call_embed(inputs)

        if single:
            return embeddings[0]
        return embeddings

    def get_sentence_embedding_dimension(self) -> int:
        return self.dimension
