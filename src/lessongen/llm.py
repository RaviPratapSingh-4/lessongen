"""Thin LLM wrapper: one OpenAI-compatible client per provider, disk cache, backoff on rate limits, mock mode."""
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass

from .config import path_of

log = logging.getLogger("lessongen.llm")


@dataclass
class LLMResponse:
    text: str
    tokens: int = 0
    cached: bool = False


def loads_lenient(text: str) -> dict:
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        s, e = t.find("{"), t.rfind("}")
        if s != -1 and e > s:
            return json.loads(t[s : e + 1])
        raise


class LLM:
    def __init__(self, cfg: dict, mock: bool = False, use_cache: bool = True):
        self.cfg, self.mock = cfg, mock
        self.use_cache = use_cache and not mock
        self.cache_dir = path_of(cfg, "cache_dir")
        self.tokens = self.calls = self.cache_hits = 0
        self._clients = {}

    # -- public -------------------------------------------------------------
    def chat(self, role: str, system: str, user: str, json_mode: bool = False, meta: dict | None = None) -> LLMResponse:
        self.calls += 1
        if self.mock:
            from .mock_backend import respond

            return LLMResponse(respond(role, system, user, meta or {}))
        spec = self.cfg["models"][role]
        provider, model, temp = spec["provider"], spec["name"], self.cfg["temperature"][role]
        key = hashlib.sha256(json.dumps([provider, model, temp, system, user, json_mode]).encode()).hexdigest()
        cache_file = self.cache_dir / f"{key}.json"
        if self.use_cache and cache_file.exists():
            self.cache_hits += 1
            return LLMResponse(json.loads(cache_file.read_text(encoding="utf-8"))["text"], 0, True)
        resp = self._call(role, provider, model, temp, system, user, json_mode)
        self.tokens += resp.tokens
        if self.use_cache:
            ok = True
            if json_mode:  # never cache an unparseable JSON reply
                try:
                    loads_lenient(resp.text)
                except json.JSONDecodeError:
                    ok = False
            if ok:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps({"text": resp.text}), encoding="utf-8")
        return resp

    # -- internals ----------------------------------------------------------
    def _get_client(self, provider: str):
        if provider not in self._clients:
            from openai import OpenAI

            p = self.cfg["providers"][provider]
            key = os.environ.get(p["api_key_env"])
            if not key:
                raise RuntimeError(f"{p['api_key_env']} is not set. Add it to .env (or use --mock).")
            self._clients[provider] = OpenAI(base_url=p["base_url"], api_key=key, max_retries=0)
        return self._clients[provider]

    def _call(self, role, provider, model, temp, system, user, json_mode) -> LLMResponse:
        import openai

        client = self._get_client(provider)
        kwargs = dict(
            model=model,
            temperature=temp,
            max_tokens=self.cfg["max_tokens"][role],
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        if self.cfg.get("reasoning_effort") and model.startswith("openai/gpt-oss"):
            kwargs["extra_body"] = {"reasoning_effort": self.cfg["reasoning_effort"]}
        last = None
        for i in range(4):
            try:
                r = client.chat.completions.create(**kwargs)
                text = re.sub(r"<think>.*?</think>", "", r.choices[0].message.content or "", flags=re.S).strip()
                if not text:
                    raise RuntimeError(f"{provider}/{model} returned an empty reply (reasoning probably used up max_tokens). Raise max_tokens for '{role}' in config.yaml.")
                return LLMResponse(text, getattr(r.usage, "total_tokens", 0) or 0)
            except openai.BadRequestError as e:
                opt = next((k for k in ("response_format", "extra_body") if k in kwargs), None)
                if opt:  # the model may not support this option: retry without it
                    log.warning("%s rejected (%s); retrying without it", opt, e)
                    kwargs.pop(opt)
                    last = e
                    continue
                raise
            except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError, openai.InternalServerError) as e:
                if "too large" in str(e).lower():  # oversize request: waiting cannot fix it
                    raise RuntimeError(f"{provider}/{model}: request exceeds your tier's per-minute token limit. Choose another model or lower max_tokens in config.yaml. Details: {e}") from e
                last = e
                wait = 3 * 2**i
                hdr = getattr(getattr(e, "response", None), "headers", None)
                if hdr and hdr.get("retry-after"):
                    try:
                        wait = min(float(hdr["retry-after"]) + 1, 90)
                    except ValueError:
                        pass
                log.warning("%s on %s/%s; waiting %.0fs (try %d/4)", type(e).__name__, provider, model, wait, i + 1)
                time.sleep(wait)
        raise RuntimeError(f"LLM call failed after retries ({type(last).__name__}). If this is a daily quota limit, wait or switch model in config.yaml.") from last
