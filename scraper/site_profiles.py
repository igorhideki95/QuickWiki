from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote, urlparse

from .paths import resolve_profiles_dir

PROFILE_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
WIKI_FAMILY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
DEFAULT_SITE_PROFILE_SCHEMA_VERSION = 1
SUPPORTED_SITE_PROFILE_SCHEMA_VERSIONS = frozenset({DEFAULT_SITE_PROFILE_SCHEMA_VERSION})


def _missing_profiles_message(directory: Path) -> str:
    return (
        f"Nenhum perfil de wiki encontrado em {directory}. "
        "QuickWiki e source-first: execute a partir da raiz do repositorio, "
        "defina QUICKWIKI_ROOT para apontar para um checkout valido ou informe "
        "--profiles-dir/--site-profile-file explicitamente."
    )


@dataclass(frozen=True, slots=True)
class WikiSiteProfile:
    key: str
    label: str
    description: str
    default_seed_url: str
    allowed_domains: tuple[str, ...]
    schema_version: int = DEFAULT_SITE_PROFILE_SCHEMA_VERSION
    wiki_family: str = "mediawiki"
    allowed_path_prefix: str = "/wiki/"
    api_path: str = "/api.php"
    title_selectors: tuple[str, ...] = ("h1#firstHeading", "h1.firstHeading", "h1")
    content_root_selectors: tuple[str, ...] = ("#mw-content-text .mw-parser-output", "#mw-content-text", "main")
    category_selectors: tuple[str, ...] = ("#mw-normal-catlinks a", ".catlinks a")
    extra_noise_selectors: tuple[str, ...] = field(default_factory=tuple)
    theme: dict[str, str] = field(default_factory=dict)
    definition_path: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, object], *, definition_path: str = "") -> "WikiSiteProfile":
        return cls(
            schema_version=int(payload.get("schema_version", DEFAULT_SITE_PROFILE_SCHEMA_VERSION)),
            wiki_family=str(payload.get("wiki_family", "mediawiki")),
            key=str(payload["key"]),
            label=str(payload.get("label", payload["key"])),
            description=str(payload.get("description", "")),
            default_seed_url=str(payload["default_seed_url"]),
            allowed_domains=tuple(str(domain) for domain in payload.get("allowed_domains", [])),
            allowed_path_prefix=str(payload.get("allowed_path_prefix", "/wiki/")),
            api_path=str(payload.get("api_path", "/api.php")),
            title_selectors=tuple(str(value) for value in payload.get("title_selectors", ("h1",))),
            content_root_selectors=tuple(
                str(value) for value in payload.get("content_root_selectors", ("main",))
            ),
            category_selectors=tuple(str(value) for value in payload.get("category_selectors", tuple())),
            extra_noise_selectors=tuple(str(value) for value in payload.get("extra_noise_selectors", tuple())),
            theme={str(key): str(value) for key, value in dict(payload.get("theme", {})).items()},
            definition_path=definition_path,
        )

    def matches_url(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc.lower()
        except ValueError:
            return False
        if domain.endswith(":443"):
            domain = domain[:-4]
        return domain in self.allowed_domains

    def api_url(self) -> str:
        return f"https://{self.allowed_domains[0]}{self.api_path}"

    def build_source_urls(self, title: str) -> tuple[str, str]:
        normalized_title = quote(title.replace(" ", "_"), safe=":_/")
        base = f"https://{self.allowed_domains[0]}/index.php?title={normalized_title}"
        return f"{base}&action=edit", f"{base}&action=raw"


def load_site_profiles(
    profiles_dir: Path | None = None,
    *,
    extra_profile_files: tuple[Path, ...] = (),
) -> dict[str, WikiSiteProfile]:
    directory = (profiles_dir or resolve_profiles_dir()).expanduser().resolve()
    profiles: dict[str, WikiSiteProfile] = {}

    candidate_files: list[Path] = []
    if directory.exists():
        candidate_files.extend(sorted(directory.glob("*.json")))
    candidate_files.extend(path.expanduser().resolve() for path in extra_profile_files)

    for path in candidate_files:
        try:
            raw_payload = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"Perfil invalido em {path}: nao foi possivel ler o arquivo ({exc}).") from exc

        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Perfil invalido em {path}: JSON malformado na linha {exc.lineno}, coluna {exc.colno}."
            ) from exc
        if not isinstance(payload, dict):
            raise ValueError(f"Perfil inválido em {path}: esperado objeto JSON.")
        validate_site_profile_payload(payload, definition_path=str(path))
        profile = WikiSiteProfile.from_dict(payload, definition_path=str(path))
        if profile.key in profiles:
            raise ValueError(f"Perfil invalido em {path}: chave duplicada '{profile.key}'.")
        profiles[profile.key] = profile

    if not profiles:
        raise FileNotFoundError(_missing_profiles_message(directory))
    return profiles


def resolve_site_profile(
    profile_key: str,
    seed_url: str | None,
    *,
    profiles_dir: Path | None = None,
    extra_profile_files: tuple[Path, ...] = (),
) -> WikiSiteProfile:
    profiles = load_site_profiles(profiles_dir, extra_profile_files=extra_profile_files)
    normalized = (profile_key or "auto").strip().lower()
    if normalized and normalized != "auto":
        profile = profiles.get(normalized)
        if profile is None:
            raise KeyError(f"Perfil de wiki desconhecido: {profile_key}")
        return profile

    if seed_url:
        for profile in profiles.values():
            if profile.matches_url(seed_url):
                return profile

    fallback = profiles.get("tibiawiki_br")
    if fallback is not None:
        return fallback
    return next(iter(profiles.values()))


def available_site_profile_keys(
    profiles_dir: Path | None = None,
    *,
    extra_profile_files: tuple[Path, ...] = (),
) -> tuple[str, ...]:
    profiles = load_site_profiles(profiles_dir, extra_profile_files=extra_profile_files)
    return ("auto",) + tuple(sorted(profiles.keys()))


def validate_site_profile_payload(payload: dict[str, object], *, definition_path: str = "") -> None:
    errors: list[str] = []
    source = definition_path or "<memory>"

    schema_version = payload.get("schema_version", DEFAULT_SITE_PROFILE_SCHEMA_VERSION)
    if not isinstance(schema_version, int):
        errors.append("campo 'schema_version' deve ser um inteiro.")
    elif schema_version not in SUPPORTED_SITE_PROFILE_SCHEMA_VERSIONS:
        errors.append(
            "campo 'schema_version' usa uma versao nao suportada pelo carregador atual."
        )

    wiki_family = payload.get("wiki_family", "mediawiki")
    if not isinstance(wiki_family, str) or not wiki_family.strip():
        errors.append("campo 'wiki_family' deve ser uma string nao vazia.")
    elif not WIKI_FAMILY_PATTERN.fullmatch(wiki_family.strip()):
        errors.append("campo 'wiki_family' deve usar letras minusculas, numeros, '_' ou '-'.")

    key = payload.get("key")
    if not isinstance(key, str) or not key.strip():
        errors.append("campo 'key' deve ser uma string não vazia.")
    elif not PROFILE_KEY_PATTERN.fullmatch(key.strip()):
        errors.append("campo 'key' deve usar apenas letras minúsculas, números, '_' ou '-'.")

    default_seed_url = payload.get("default_seed_url")
    seed_domain = ""
    if not isinstance(default_seed_url, str) or not default_seed_url.strip():
        errors.append("campo 'default_seed_url' deve ser uma URL não vazia.")
    else:
        parsed_seed = urlparse(default_seed_url)
        if parsed_seed.scheme not in {"http", "https"} or not parsed_seed.netloc:
            errors.append("campo 'default_seed_url' deve usar http(s) e conter domínio.")
        else:
            seed_domain = parsed_seed.netloc.lower().removesuffix(":443")

    allowed_domains = payload.get("allowed_domains")
    if not isinstance(allowed_domains, list) or not allowed_domains:
        errors.append("campo 'allowed_domains' deve ser uma lista não vazia.")
        normalized_domains: list[str] = []
    else:
        normalized_domains = []
        for domain in allowed_domains:
            if not isinstance(domain, str) or not domain.strip():
                errors.append("todos os itens de 'allowed_domains' devem ser strings não vazias.")
                continue
            normalized_domains.append(domain.strip().lower().removesuffix(":443"))
        if seed_domain and normalized_domains and seed_domain not in normalized_domains:
            errors.append("o domínio de 'default_seed_url' deve existir em 'allowed_domains'.")

    for field_name, default_value in (
        ("allowed_path_prefix", "/wiki/"),
        ("api_path", "/api.php"),
    ):
        raw_value = payload.get(field_name, default_value)
        if not isinstance(raw_value, str) or not raw_value.strip():
            errors.append(f"campo '{field_name}' deve ser uma string não vazia.")
        elif not raw_value.startswith("/"):
            errors.append(f"campo '{field_name}' deve iniciar com '/'.")

    for field_name, fallback in (
        ("title_selectors", ("h1",)),
        ("content_root_selectors", ("main",)),
        ("category_selectors", tuple()),
        ("extra_noise_selectors", tuple()),
    ):
        raw_value = payload.get(field_name, fallback)
        if not isinstance(raw_value, (list, tuple)):
            errors.append(f"campo '{field_name}' deve ser uma lista de strings.")
            continue
        for item in raw_value:
            if not isinstance(item, str) or not item.strip():
                errors.append(f"campo '{field_name}' deve conter apenas strings não vazias.")
                break

    theme = payload.get("theme", {})
    if not isinstance(theme, dict):
        errors.append("campo 'theme' deve ser um objeto JSON.")
    else:
        for raw_key, raw_value in theme.items():
            if not isinstance(raw_key, str) or not raw_key.strip():
                errors.append("todas as chaves de 'theme' devem ser strings não vazias.")
                break
            if not isinstance(raw_value, str) or not raw_value.strip():
                errors.append("todos os valores de 'theme' devem ser strings não vazias.")
                break

    if errors:
        formatted = "\n- ".join(errors)
        raise ValueError(f"Perfil inválido em {source}:\n- {formatted}")
