#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author  : SupplyGraph AI
@Site    :
@File    : manifest_builder.py

OpenAI A2A Manifest Builder for SupplyGraph AI Agents.

This module converts the SupplyGraph agent manifest into an
OpenAI-compatible A2A manifest while preserving *all* SG metadata
under a non-breaking `extended` section.

OpenAI A2A requires the following canonical structure:

{
  "object": "agent",
  "id": "...",
  "name": "...",
  "version": "...",
  "description": "...",
  "type": "agent",

  "capabilities": {
      "manifest": true,
      "run": bool,
      "status": bool,
      "results": bool,
      "streaming": bool
  },

  "input_schema": {...},
  "output_schema": {...},

  "pricing": {...},

  "metadata": {...},

  "api_key_required": true | false,

  "extended": {  <-- all SupplyGraph extra metadata lives here
      ...
  }
}

This file is the SINGLE source of truth for the manifest
normalization logic used by the SDK.
"""

from typing import Any, Dict


def build_openai_manifest(sg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a SupplyGraph manifest into a fully canonical
    OpenAI-compatible A2A manifest.

    All SG fields not explicitly mapped into OpenAI standard
    schema are stored under the `extended` field.
    """

    # ----------------------------------------------------------------------
    # Extract basic SG fields
    # ----------------------------------------------------------------------
    capabilities = sg.get("capabilities", [])
    protocol = sg.get("protocol", {})
    auth_cfg = sg.get("auth", {})

    # ----------------------------------------------------------------------
    # 1. Build OpenAI canonical manifest
    # ----------------------------------------------------------------------
    manifest = {
        "object": "agent",
        "id": sg.get("agent_id"),
        "name": sg.get("name"),
        "version": sg.get("version", "1.0.0"),
        "description": sg.get("description", ""),
        "type": "agent",

        # --------------------------------------------------------------
        # Capabilities (OpenAI-required)
        # --------------------------------------------------------------
        "capabilities": {
            "manifest": True,
            "run": "run" in capabilities,
            "status": "status" in capabilities,
            "results": "results" in capabilities,
            "streaming": protocol.get("streaming", False),
        },

        # --------------------------------------------------------------
        # Schemas
        # --------------------------------------------------------------
        "input_schema": sg.get("input_schema", {}),
        "output_schema": sg.get("output_schema", {}),

        # --------------------------------------------------------------
        # Pricing (OpenAI-friendly)
        # --------------------------------------------------------------
        "pricing": {
            "unit": sg.get("pricing", {}).get("unit", "credits"),
            "per_run": sg.get("pricing", {}).get("per_run"),
        },

        # --------------------------------------------------------------
        # Metadata block (OpenAI side)
        # --------------------------------------------------------------
        "metadata": {
            "organization": sg.get("organization"),
            "category": sg.get("category"),
            "tags": sg.get("tags", []),
            "model_type": sg.get("model_type"),
            "protocol_version": sg.get("protocol_version"),
            "documentation_url": sg.get("documentation_url"),
            "created_at": sg.get("created_at"),
            "updated_at": sg.get("updated_at"),
            "streaming": protocol.get("streaming"),
            "endpoints": protocol.get("endpoints", {}),
        },

        # --------------------------------------------------------------
        # Auth indicator (OpenAI expects a simple boolean)
        # --------------------------------------------------------------
        "api_key_required": bool(auth_cfg.get("required", True)),
    }

    # ----------------------------------------------------------------------
    # 2. Build extended (SG-only) fields
    # ----------------------------------------------------------------------
    extended: Dict[str, Any] = {
        "execution_context": sg.get("execution_context"),
        "priority": sg.get("priority"),
        "compatibility": sg.get("compatibility", {}),
        "schema_version": sg.get("schema_version"),
        "protocol": {
            "base_url": protocol.get("base_url"),
            "endpoints": protocol.get("endpoints", {}),
            "methods": protocol.get("methods", []),
            "streaming": protocol.get("streaming"),
        },
        "lifecycle": sg.get("lifecycle", {}),
        "interaction": sg.get("interaction", {}),
        "intents": sg.get("intents", []),
        "notes": sg.get("notes"),
        "auth": sg.get("auth", {}),
        "license": sg.get("license"),
        "output_rights": sg.get("output_rights"),
        "output_license": sg.get("output_license"),
        "compliance": sg.get("compliance", {}),
        "usage_policy": sg.get("usage_policy"),
        "localization": sg.get("localization", {}),
    }

    # ----------------------------------------------------------------------
    # 3. Include ALL unknown or unmapped SG fields → extended.extra_fields
    # ----------------------------------------------------------------------
    known_keys = {
        "agent_id", "name", "description", "version",
        "organization", "category", "tags",
        "created_at", "updated_at",
        "capabilities", "protocol", "input_schema", "output_schema",
        "stream_event_schema", "pricing", "model_type",
        "execution_context", "priority", "compatibility",
        "lifecycle", "interaction", "intents", "notes", "auth",
        "license", "output_rights", "output_license",
        "compliance", "usage_policy", "localization",
        "schema_version", "documentation_url",
    }

    extra_fields = {k: v for k, v in sg.items() if k not in known_keys}
    if extra_fields:
        extended["extra_fields"] = extra_fields

    manifest["extended"] = extended

    return manifest
