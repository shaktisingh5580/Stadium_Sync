import sys

file_path = "app/services/gemini_client.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace _get_client
old_get_client = """def _get_client():
    \"\"\"Get the next Gemini client in the round-robin pool.\"\"\"
    global _genai_clients, _current_client_idx
    
    if not _genai_clients:
        # Load keys from GEMINI_API_KEYS (comma separated) or fallback to GEMINI_API_KEY
        keys = []
        if settings.GEMINI_API_KEYS:
            keys = [k.strip() for k in settings.GEMINI_API_KEYS.split(",") if k.strip()]
        elif settings.GEMINI_API_KEY:
            keys = [settings.GEMINI_API_KEY.strip()]
            
        if not keys:
            logger.warning("GEMINI_API_KEY not set — AI features will use mock responses")
            return None
            
        try:
            from google import genai
            for key in keys:
                _genai_clients.append(genai.Client(api_key=key))
            logger.info(f"✅ Initialized {len(_genai_clients)} Gemini clients for round-robin rotation")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini clients: {e}")
            return None
            
    if not _genai_clients:
        return None
        
    # Round-robin selection
    client = _genai_clients[_current_client_idx]
    _current_client_idx = (_current_client_idx + 1) % len(_genai_clients)
    
    return client"""

new_get_client = """def _get_client(client_type=None):
    \"\"\"Get the next AI client in the round-robin pool.\"\"\"
    global _genai_clients, _current_client_idx
    
    if not _genai_clients:
        keys = []
        if settings.GEMINI_API_KEYS:
            keys = [k.strip() for k in settings.GEMINI_API_KEYS.split(",") if k.strip()]
        elif settings.GEMINI_API_KEY:
            keys = [settings.GEMINI_API_KEY.strip()]
            
        if not keys:
            logger.warning("API keys not set — AI features will use mock responses")
            return None
            
        try:
            for key in keys:
                if key.startswith("nvapi-"):
                    from openai import OpenAI
                    _genai_clients.append({
                        "type": "nvidia",
                        "client": OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key),
                        "model": "meta/llama-3.1-70b-instruct"
                    })
                else:
                    from google import genai
                    _genai_clients.append({
                        "type": "gemini",
                        "client": genai.Client(api_key=key),
                        "model": settings.GEMINI_MODEL
                    })
            logger.info(f"✅ Initialized {len(_genai_clients)} AI clients for round-robin rotation")
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            return None
            
    available = _genai_clients
    if client_type:
        available = [c for c in _genai_clients if c.get("type") == client_type]
        
    if not available:
        return None
        
    client_info = available[_current_client_idx % len(available)]
    _current_client_idx = (_current_client_idx + 1) % len(_genai_clients)
    
    return client_info"""

# Fix classify_waste_image (must use gemini since it requires multimodal)
old_classify_client = """    client = _get_client()

    if client is None:
        # Mock response when no API key
        return _mock_eco_response()"""
new_classify_client = """    client_info = _get_client(client_type="gemini")

    if client_info is None:
        # Mock response when no Gemini API key
        return _mock_eco_response()
        
    client = client_info["client"]"""

# Fix triage_incident
old_triage_client = """    client = _get_client()

    if client is None:
        return _mock_triage_response(description)

    try:
        prompt = TRIAGE_PROMPT.format(
            description=description,
            section=section,
            row=row,
        )

        from google.genai import types
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=300,
            ),
        )

        import json
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)"""
new_triage_client = """    client_info = _get_client()

    if client_info is None:
        return _mock_triage_response(description)

    try:
        prompt = TRIAGE_PROMPT.format(
            description=description,
            section=section,
            row=row,
        )

        import json
        if client_info["type"] == "nvidia":
            client = client_info["client"]
            response = client.chat.completions.create(
                model=client_info["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            text = response.choices[0].message.content.strip()
        else:
            client = client_info["client"]
            from google.genai import types
            response = client.models.generate_content(
                model=client_info["model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=300,
                ),
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\\n", 1)[1].rsplit("```", 1)[0].strip()
                
        return json.loads(text)"""

# Fix agentic_chat
old_agentic_client = """    client = _get_client()
    fan_context = fan_context or {}

    if client is None:
        return _mock_agentic_response(message, image_base64)

    try:
        # Build system prompt with fan context
        system_prompt = AGENTIC_SYSTEM_PROMPT.format(
            holder_name=fan_context.get("holder_name", "Fan"),
            section=fan_context.get("section", "Unknown"),
            row=fan_context.get("row", "Unknown"),
            seat_number=fan_context.get("seat_number", "Unknown"),
            match_id=fan_context.get("match_id", "Unknown"),
            transit_method=fan_context.get("transit_method", "not set"),
        )

        # Build conversation messages
        contents = [system_prompt]

        # Add history
        if history:
            for msg in history[-10:]:  # Keep last 10 messages for context
                role_prefix = "User: " if msg.get("role") == "user" else "Assistant: "
                contents.append(role_prefix + msg.get("content", ""))

        # Add current message
        contents.append(f"User: {message}")

        from google.genai import types
        parts = [types.Part.from_text(text="\\n\\n".join(contents))]

        # Add image if provided
        if image_base64:
            import base64 as b64
            image_bytes = b64.b64decode(image_base64)
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[types.Content(parts=parts)],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500,
                response_mime_type="application/json",
            ),
        )

        import json
        text = response.text.strip()"""
new_agentic_client = """    client_info = _get_client()
    fan_context = fan_context or {}

    if client_info is None:
        return _mock_agentic_response(message, image_base64)

    try:
        # Build system prompt with fan context
        system_prompt = AGENTIC_SYSTEM_PROMPT.format(
            holder_name=fan_context.get("holder_name", "Fan"),
            section=fan_context.get("section", "Unknown"),
            row=fan_context.get("row", "Unknown"),
            seat_number=fan_context.get("seat_number", "Unknown"),
            match_id=fan_context.get("match_id", "Unknown"),
            transit_method=fan_context.get("transit_method", "not set"),
        )

        import json
        if client_info["type"] == "nvidia":
            client = client_info["client"]
            messages = [{"role": "system", "content": system_prompt}]
            if history:
                for msg in history[-10:]:
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model=client_info["model"],
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            text = response.choices[0].message.content.strip()
        else:
            client = client_info["client"]
            # Build conversation messages
            contents = [system_prompt]
    
            # Add history
            if history:
                for msg in history[-10:]:  # Keep last 10 messages for context
                    role_prefix = "User: " if msg.get("role") == "user" else "Assistant: "
                    contents.append(role_prefix + msg.get("content", ""))
    
            # Add current message
            contents.append(f"User: {message}")
    
            from google.genai import types
            parts = [types.Part.from_text(text="\\n\\n".join(contents))]
    
            # Add image if provided
            if image_base64:
                import base64 as b64
                image_bytes = b64.b64decode(image_base64)
                parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
    
            response = client.models.generate_content(
                model=client_info["model"],
                contents=[types.Content(parts=parts)],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                    response_mime_type="application/json",
                ),
            )
            text = response.text.strip()"""

content = content.replace(old_get_client, new_get_client)
content = content.replace(old_classify_client, new_classify_client)
content = content.replace(old_triage_client, new_triage_client)
content = content.replace(old_agentic_client, new_agentic_client)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("gemini_client.py updated successfully!")
