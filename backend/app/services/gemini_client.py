"""
Stadium Sync — Gemini AI Client.

Wrapper around the Google Gemini API for:
- Eco-Vision: Classify waste from photos
- Triage: Classify incident severity from text descriptions
- Agentic Chat: Conversational stadium concierge with UI action routing
"""

import base64
import logging
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Lazy-initialize the Gemini clients (round-robin)
_genai_clients = []
_current_client_idx = 0


def _get_client(client_type=None, purpose=None):
    """Get the next AI client in the round-robin pool based on purpose."""
    global _genai_clients, _current_client_idx
    
    if not _genai_clients:
        keys_gemini = []
        if settings.GEMINI_API_KEY_1: keys_gemini.append(settings.GEMINI_API_KEY_1.strip())
        if settings.GEMINI_API_KEY_3: keys_gemini.append(settings.GEMINI_API_KEY_3.strip())
        
        nvidia_key = settings.NVIDIA_API_KEY.strip() if settings.NVIDIA_API_KEY else None
            
        if not keys_gemini and not nvidia_key:
            logger.warning("API keys not set — AI features will use mock responses")
            return None
            
        try:
            if nvidia_key:
                from openai import OpenAI
                _genai_clients.append({
                    "type": "nvidia",
                    "client": OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=nvidia_key),
                    "model": "meta/llama-3.1-70b-instruct"
                })
                
            for key in keys_gemini:
                from google import genai
                _genai_clients.append({
                    "type": "gemini",
                    "client": genai.Client(api_key=key),
                    "model": settings.GEMINI_MODEL
                })
            logger.info(f"✅ Initialized {len(_genai_clients)} AI clients for purpose-based rotation")
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            return None
            
    available = _genai_clients
    
    if client_type:
        available = [c for c in available if c.get("type") == client_type]
        
    if purpose == "eco_vision":
        # Images MUST go to Gemini
        available = [c for c in available if c.get("type") == "gemini"]
    elif purpose in ("admin_chat", "fan_chat"):
        # Prefer Gemini for chat but allow Nvidia round-robin to avoid rate limits
        gemini_clients = [c for c in available if c.get("type") == "gemini"]
        if gemini_clients and _current_client_idx % 2 == 0:
            # Send roughly half the traffic to Gemini if available
            pass
    elif purpose == "triage":
        # Prefer NVIDIA, else round robin
        nvidia_clients = [c for c in available if c.get("type") == "nvidia"]
        if nvidia_clients:
            return nvidia_clients[0]
            
    if not available:
        available = _genai_clients
        if not available:
            return None
            
    client_info = available[_current_client_idx % len(available)]
    _current_client_idx = (_current_client_idx + 1) % len(available)
    
    return client_info


# ── Eco-Vision: Waste Classification ──

ECO_VISION_PROMPT = """You are an AI waste classification assistant at a FIFA World Cup 2026 stadium.

Analyze the image of waste/trash provided by a fan and classify it.

Respond ONLY with valid JSON in this exact format:
{
    "category": "compost" | "recycle" | "landfill" | "hazardous",
    "item_name": "short name of the item",
    "confidence": 0.0-1.0,
    "bin_color": "green" | "blue" | "black" | "red",
    "instructions": "Brief instruction on how to dispose of this item",
    "fun_fact": "One-sentence sustainability fun fact"
}

Classification rules:
- COMPOST (green bin): Food waste, napkins, paper plates, wooden utensils
- RECYCLE (blue bin): Plastic bottles, aluminum cans, cardboard
- LANDFILL (black bin): Styrofoam, chip bags, mixed materials
- HAZARDOUS (red bin): Batteries, electronics, chemicals
"""


async def classify_waste_image(image_base64: str, mime_type: str = "image/jpeg") -> dict:
    """
    Send an image to Gemini for waste classification.

    Args:
        image_base64: Base64-encoded image data.
        mime_type: Image MIME type.

    Returns:
        Dict with classification result.
    """
    client_info = _get_client(purpose="eco_vision")

    if client_info is None:
        # Mock response when no Gemini API key
        return _mock_eco_response()
        
    client = client_info["client"]

    try:
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split("base64,")[1]
        image_bytes = base64.b64decode(image_base64)

        from google.genai import types
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(parts=[
                    types.Part.from_text(text=ECO_VISION_PROMPT),
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ])
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=300,
            ),
        )

        text = response.text.strip() if response.text else "{}"
        try:
            return _parse_json_response(text)
        except Exception as je:
            logger.error(f"Gemini eco-vision JSON error: {je}")
            return _mock_eco_response()

    except Exception as e:
        logger.error(f"Gemini eco-vision error: {e}")
        return _mock_eco_response()

def _parse_json_response(text: str) -> dict:
    import json
    import ast
    text = text.strip()
    
    # Extract json block if there is a preamble
    if "{" in text and "}" in text:
        start = text.find("{")
        end = text.rfind("}") + 1
        text = text[start:end]
        
    if not text:
        return {}
        
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            clean_text = text.replace("true", "True").replace("false", "False").replace("null", "None")
            return ast.literal_eval(clean_text)
        except Exception:
            raise ValueError(f"Raw text: {text}")


def _mock_eco_response() -> dict:
    """Fallback mock response when Gemini is unavailable."""
    return {
        "category": "recycle",
        "item_name": "plastic bottle",
        "confidence": 0.85,
        "bin_color": "blue",
        "instructions": "Empty the bottle and place it in the blue recycling bin.",
        "fun_fact": "Recycling one plastic bottle saves enough energy to power a laptop for 25 minutes!",
    }


# ── Incident Triage ──

TRIAGE_PROMPT = """You are an AI incident triage system for a FIFA World Cup 2026 stadium.

A fan has reported the following issue. Classify its severity and suggest a response.

Report: "{description}"
Location: Section {section}, Row {row}

Respond ONLY with valid JSON in this exact format:
{{
    "severity": "low" | "medium" | "high" | "critical",
    "category": "spill" | "medical" | "safety" | "maintenance" | "crowd" | "other",
    "estimated_response_mins": 1-30,
    "suggested_action": "Brief action for the volunteer",
    "requires_escalation": true | false,
    "escalation_reason": "null or reason string"
}}

Severity rules:
- CRITICAL: Medical emergency, fire, structural damage, security threat
- HIGH: Large spill in walkway, broken glass, aggressive behavior
- MEDIUM: Small spill, broken seat, blocked aisle
- LOW: Overflowing bin, minor litter, lighting issue
"""


async def triage_incident(
    description: str,
    section: str = "Unknown",
    row: str = "Unknown",
) -> dict:
    """
    Use Gemini to classify incident severity and suggest response.

    Args:
        description: Fan's description of the issue.
        section: Section name.
        row: Row identifier.

    Returns:
        Dict with triage result.
    """
    client_info = _get_client(purpose="triage")

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
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                
        return json.loads(text)

    except Exception as e:
        logger.error(f"Gemini triage error: {e}")
        return _mock_triage_response(description)


def _mock_triage_response(description: str) -> dict:
    """Fallback mock triage when Gemini is unavailable."""
    # Simple keyword-based severity
    desc_lower = description.lower()
    if any(w in desc_lower for w in ["medical", "fire", "emergency", "injury", "unconscious"]):
        severity = "critical"
        category = "medical"
        mins = 2
    elif any(w in desc_lower for w in ["spill", "broken", "glass"]):
        severity = "high"
        category = "spill"
        mins = 5
    elif any(w in desc_lower for w in ["blocked", "seat", "aisle"]):
        severity = "medium"
        category = "maintenance"
        mins = 10
    else:
        severity = "low"
        category = "other"
        mins = 15

    return {
        "severity": severity,
        "category": category,
        "estimated_response_mins": mins,
        "suggested_action": f"Respond to reported issue: {description[:50]}",
        "requires_escalation": severity in ("critical", "high"),
        "escalation_reason": "Auto-escalated based on severity" if severity in ("critical", "high") else None,
    }


# ── Agentic Chat: Conversational Stadium Concierge ──

AGENTIC_SYSTEM_PROMPT = """You are "Stadium AI", an intelligent concierge for the FIFA World Cup 2026 stadium experience app "Stadium Sync".

You help fans with:
1. Finding locations (their seat, washrooms, food courts, gates, medical stations)
2. Classifying waste using Eco-Vision (when they have an image)
3. Reporting incidents (spills, broken seats, medical emergencies)
4. Getting navigation routes to gates based on their transit preference
5. Checking crowd density levels in stadium sections
6. General stadium info and match-day tips

You MUST respond with ONLY valid JSON in this exact format. No text before or after the JSON:
{{
    "message": "Your conversational response to the fan",
    "ui_action": "NONE",
    "payload": {{}}
}}

Available ui_action values and when to use them:
- "NONE" — General conversation, greetings, information, tips. No visual action needed.
- "SHOW_MAP" — When the user asks about a LOCATION (washroom, food court, gate, medical station, their seat). Set payload.target to the location type: "washroom", "food_court", "gate_north", "gate_south", "gate_east", "gate_west", "medical", "seat".
- "SHOW_ROUTE" — When the user wants DIRECTIONS or NAVIGATION to a specific place. Set payload.target to the location (e.g., "gate_north", "gate_south", "gate_east", "gate_west", "washroom", "food_court"). If the user asks for a route between their seat and a specific gate, set payload.target to that specific gate (NOT "seat").
- "REQUEST_IMAGE" — When the user asks where to throw trash but DOES NOT say what the item is. Ask them "Can you tell me what the item is (e.g. plastic, paper) or upload an image?". NEVER ask for an image if they already named the item!
- "SHOW_ECO_RESULT" — When the user explicitly names the waste item (e.g., "paper", "plastic cup", "banana peel", "can") OR when an image is processed. In your message, tell them exactly which bin to use (Green for Compost, Blue for Recycle, Black for Landfill, Red for Hazardous).
- "DISPATCH_INCIDENT" — When the user REPORTS A PROBLEM: spill, broken seat, fight, medical emergency, suspicious activity. Extract the description.
  Set payload.description to a clear summary of the issue.
- "SHOW_CROWD" — When the user asks about crowd levels, density, or how busy sections are.
- "CLEAR_MAP" — When the user asks to remove routes, marks, or pins from the map, but keep the map open.
- "HIDE_MAP" — When the map is no longer needed (user says thanks, done, close, etc.)

Context about the current fan:
- Name: {holder_name}
- Seat: Section {section}, Row {row}, Seat {seat_number}
- Match: {match_id}
- Transit preference: {transit_method}
- Needs Accessibility: {needs_accessibility}

IMPORTANT RULES:
1. Be warm, concise, and helpful. Use emojis sparingly.
2. ALWAYS respond with valid JSON. Never add text outside the JSON.
3. If unsure about intent, default to ui_action: "NONE" and ask a clarifying question.
4. For incident reports, always acknowledge urgency and reassure the fan.
"""


async def agentic_chat(
    message: str,
    history: list = None,
    fan_context: dict = None,
    image_base64: str = None,
) -> dict:
    """
    Process a conversational message through the Gemini agent.

    Args:
        message: The user's text input.
        history: Previous conversation messages [{role, content}, ...].
        fan_context: Fan session data (name, seat, match, transit).
        image_base64: Optional image for eco-vision classification.

    Returns:
        Dict with 'message', 'ui_action', and 'payload'.
    """
    fan_context = fan_context or {}
    max_retries = 4
    last_error = None

    for attempt in range(max_retries):
        if image_base64:
            client_info = _get_client(purpose="eco_vision")
        else:
            client_info = _get_client(purpose="fan_chat")

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
                needs_accessibility="Yes" if fan_context.get("needs_accessibility") else "No",
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
                parts = [types.Part.from_text(text="\n\n".join(contents))]
        
                # Add image if provided
                if image_base64:
                    import base64 as b64
                    if image_base64.startswith("data:image"):
                        image_base64 = image_base64.split("base64,")[1]
                    image_bytes = b64.b64decode(image_base64)
                    parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
        
                response = client.models.generate_content(
                    model=client_info["model"],
                    contents=[types.Content(parts=parts)],
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=500,
                    ),
                )
                text = response.text.strip() if response.text else "{}"
                
            try:
                result = _parse_json_response(text)
            except Exception as je:
                logger.error(f"Gemini agentic JSON error: {je}. Raw text: {text}")
                # Don't retry on bad JSON, just fallback
                return _mock_agentic_response(message, image_base64)

            # Validate required fields
            if "message" not in result:
                result["message"] = "I'm here to help! What do you need?"
            if "ui_action" not in result:
                result["ui_action"] = "NONE"
            if "payload" not in result:
                result["payload"] = {}

            return result

        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for agentic chat: {e}")
            
            # If it's a rate limit or model not found, loop and try the next key
            if "429" in error_str or "404" in error_str or "503" in error_str or "quota" in error_str or "exhausted" in error_str:
                continue
            else:
                break # Not a rate limit / model issue, so break

    logger.error(f"Gemini agentic chat error after {max_retries} attempts. Last error: {last_error}")
    return _mock_agentic_response(message, image_base64)


def _mock_agentic_response(message: str, image_base64: str = None) -> dict:
    """
    Keyword-based fallback when Gemini is unavailable.
    Provides a reasonable experience for demos and testing.
    """
    msg_lower = message.lower().strip()

    # Image attached → eco-vision
    if image_base64:
        return {
            "message": "I've analyzed your image! This looks like a **plastic bottle**. Please dispose of it in the **Blue Recycling Bin** ♻️",
            "ui_action": "SHOW_ECO_RESULT",
            "payload": {
                "category": "recycle",
                "item_name": "plastic bottle",
                "confidence": 0.92,
                "bin_color": "blue",
                "instructions": "Empty the bottle and place it in the blue recycling bin.",
                "fun_fact": "Recycling one plastic bottle saves enough energy to power a laptop for 25 minutes!",
            },
        }

    # Greetings
    if any(w in msg_lower for w in ["hi", "hello", "hey", "hii", "sup", "yo"]):
        return {
            "message": "Hey there! 👋 Welcome to Stadium Sync. I'm your personal stadium concierge. How can I help you today? You can ask me to find locations, report issues, or help you with waste sorting!",
            "ui_action": "NONE",
            "payload": {},
        }

    # Navigation / Location
    if any(w in msg_lower for w in ["seat", "find my seat", "where am i", "my seat", "section"]):
        return {
            "message": "Let me show you the way to your seat! I'll highlight it on the map. 🎯",
            "ui_action": "SHOW_ROUTE",
            "payload": {"target": "seat"},
        }

    if any(w in msg_lower for w in ["washroom", "bathroom", "toilet", "restroom", "wc"]):
        return {
            "message": "There's a washroom near **Gate North**, about a 2 minute walk from your section. Let me show you on the map! 🗺️",
            "ui_action": "SHOW_MAP",
            "payload": {"target": "washroom"},
        }

    if any(w in msg_lower for w in ["food", " eat ", "hungry", "drink", "snack", "coffee", "beer"]):
        return {
            "message": "The nearest food court is between **Gate East and Gate South**. They have burgers, pizza, and drinks! 🍔 Let me show you the way.",
            "ui_action": "SHOW_MAP",
            "payload": {"target": "food_court"},
        }

    if any(w in msg_lower for w in ["gate", "exit", "leave", "go home", "way out"]):
        return {
            "message": "I'll show you the nearest exit gate on the map. Head towards the highlighted gate! 🚪",
            "ui_action": "SHOW_MAP",
            "payload": {"target": "gate_north"},
        }

    if any(w in msg_lower for w in ["medical", "doctor", "nurse", "first aid", "hurt", "injured"]):
        return {
            "message": "⚕️ There's a medical station near **Gate South**. If this is an emergency, I'll also dispatch help immediately. Let me show you the location.",
            "ui_action": "SHOW_MAP",
            "payload": {"target": "medical"},
        }

    # Eco-Vision (no image)
    if any(w in msg_lower for w in ["trash", "waste", "recycle", "bin", "throw", "garbage", "dispose", "cup", "bottle", "eco"]):
        return {
            "message": "I can help you sort your waste! 📸 Please upload a photo of the item and I'll tell you which bin to use.",
            "ui_action": "REQUEST_IMAGE",
            "payload": {},
        }

    # Incidents
    if any(w in msg_lower for w in ["spill", "broken", "fight", "emergency", "problem", "issue", "report", "help", "dangerous", "suspicious"]):
        return {
            "message": "I'm sorry to hear that! 🚨 I've logged this incident and a volunteer is being dispatched to your section. Expected response time: ~5 minutes.",
            "ui_action": "DISPATCH_INCIDENT",
            "payload": {
                "description": message,
                "severity": "medium",
                "estimated_response_mins": 5,
            },
        }

    # Crowd
    if any(w in msg_lower for w in ["crowd", "busy", "packed", "density", "how many people", "crowded"]):
        return {
            "message": "Let me show you the current crowd levels across the stadium. 📊 The heatmap will highlight busy and quiet areas.",
            "ui_action": "SHOW_CROWD",
            "payload": {},
        }

    # Close map
    if any(w in msg_lower for w in ["close", "hide", "dismiss", "done", "thanks", "thank", "got it", "ok"]):
        return {
            "message": "You're welcome! Let me know if you need anything else. Enjoy the match! ⚽",
            "ui_action": "HIDE_MAP",
            "payload": {},
        }

    # Default fallback
    return {
        "message": "I'm here to help! You can ask me about:\n• 📍 **Finding locations** (washroom, food, medical)\n• 🗺️ **Navigation** to your seat or exit gates\n• ♻️ **Eco-Vision** waste sorting (upload a photo!)\n• 🚨 **Report an issue** (spill, broken seat, etc.)\n• 📊 **Crowd levels** in the stadium\n\nWhat would you like help with?",
        "ui_action": "NONE",
        "payload": {},
    }


# ── Admin Copilot ──

ADMIN_SYSTEM_PROMPT = """You are "Stadium AI", the operational copilot for the FIFA World Cup 2026 stadium organizers.

You help stadium admins monitor the digital twin of the stadium. You have access to live state data.
When the organizer asks a question, use the following stadium state to provide actionable operational insights.

Stadium State:
{stadium_state}

IMPORTANT RULES:
1. You MUST respond with ONLY a valid JSON object. Do NOT include markdown code blocks like ```json.
2. The JSON object must have EXACTLY this structure:
{{
  "message": "Your text response to the admin",
  "action": "NONE" | "BROADCAST",
  "broadcast_payload": {{
    "type": "chat_message",
    "message": "The personalized message sent directly to the fans",
    "target_ui": "NONE" | "SHOW_MAP" | "SHOW_ROUTE",
    "target_location": "Gate South"
  }}
}}
3. If the admin asks you to tell fans to evacuate, offer a promotion, or route them somewhere, set action to "BROADCAST".
4. If "action" is "NONE", you can set "broadcast_payload" to null.
5. Keep your text message concise, professional, and highlight risks.
"""

async def admin_chat(message: str, stadium_state: dict, history: list = None) -> dict:
    """Chat with the admin copilot."""
    client_info = _get_client(purpose="admin_chat")
    
    if not client_info:
        return {"message": "Admin AI is in offline mock mode. The stadium looks operational, but AI predictions are disabled."}

    try:
        import json
        # remove datetime objects for json dump
        def default_serializer(obj):
            from datetime import datetime
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        state_str = json.dumps(stadium_state, indent=2, default=default_serializer)
        system_prompt = ADMIN_SYSTEM_PROMPT.format(stadium_state=state_str)
        
        if client_info["type"] == "nvidia":
            client = client_info["client"]
            messages = [{"role": "system", "content": system_prompt}]
            if history:
                for msg in history[-5:]:
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
            messages.append({"role": "user", "content": message})
            
            import asyncio
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=client_info["model"],
                messages=messages,
                temperature=0.2,
                max_tokens=500
            )
            raw_text = response.choices[0].message.content.strip()
        else:
            client = client_info["client"]
            contents = [system_prompt]
            if history:
                for msg in history[-5:]:
                    prefix = "User: " if msg.get("role") == "user" else "Assistant: "
                    contents.append(prefix + msg.get("content", ""))
            contents.append(f"User: {message}")
            
            from google.genai import types
            import asyncio
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=client_info["model"],
                contents=[types.Part.from_text(text="\n\n".join(contents))],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=500,
                    response_mime_type="application/json"
                ),
            )
            raw_text = response.text.strip()
            
        # Parse JSON
        try:
            text = raw_text.strip()
            
            # Extract json block if there is a preamble
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            elif "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                text = text[start:end]
            parsed = json.loads(text)
            return parsed
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Admin AI JSON parse failed: {e}. Raw text: {raw_text}")
            return {"message": raw_text, "action": "NONE", "broadcast_payload": None}
            
    except Exception as e:
        logger.error(f"Gemini admin chat error: {e}")
        return {"message": f"Error communicating with AI Copilot: {str(e)}"}

# ── CV Event Processing ──

CV_EVENT_PROMPT = """You are the AI Copilot for a Stadium Command Center.
A Computer Vision (CV) edge node just sent a raw event payload.
Analyze the event and decide how to alert the admin.

Raw CV Data: {cv_data}
Current Stadium State: {state_summary}

IMPORTANT: Format the "message" field richly using emojis and bold text (e.g. "🔥 **Fire Alert:** ...", "📊 **Crowd Insight:** ...", "🏃 **Action Taken:** ..."). Be descriptive and professional. Do not use generic fallback text.

Respond ONLY with valid JSON in this exact format. Do NOT wrap it in markdown code blocks.
{{
    "action": "ALERT_ADMIN" | "AUTO_RESOLVE",
    "message": "The richly formatted message to display in the Admin chat",
    "severity": "critical" | "high" | "medium" | "low"
}}
"""

async def process_cv_event(cv_data: dict, state: dict) -> dict:
    import json
    client_info = _get_client(purpose="admin_chat")
    if not client_info:
        return {"action": "ALERT_ADMIN", "message": f"🚨 CV Alert: {cv_data.get('type')} detected.", "severity": "high"}
        
    state_summary = f"Total Incidents: {len(state.get('incidents', []))}"
    system_prompt = CV_EVENT_PROMPT.format(cv_data=json.dumps(cv_data), state_summary=state_summary)
    
    try:
        if client_info["type"] == "nvidia":
            client = client_info["client"]
            import asyncio
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=client_info["model"],
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.2,
                max_tokens=300
            )
            text = response.choices[0].message.content.strip()
        else:
            client = client_info["client"]
            from google.genai import types
            import asyncio
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=client_info["model"],
                contents=[types.Part.from_text(text=system_prompt)],
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=200, response_mime_type="application/json"),
            )
            text = response.text.strip()
            
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        elif "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            text = text[start:end]
            
        return json.loads(text)
    except Exception as e:
        logger.error(f"Error processing CV event: {e}. Raw output: {text if 'text' in locals() else 'None'}")
        return {"action": "ALERT_ADMIN", "message": f"🚨 CV Alert: {cv_data.get('type')} detected.", "severity": "high"}
