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


def _get_client(client_type=None):
    """Get the next AI client in the round-robin pool."""
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
    client_info = _get_client(client_type="gemini")

    if client_info is None:
        # Mock response when no Gemini API key
        return _mock_eco_response()
        
    client = client_info["client"]

    try:
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

        import json
        # Extract JSON from response
        text = response.text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)

    except Exception as e:
        logger.error(f"Gemini eco-vision error: {e}")
        return _mock_eco_response()


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
    client_info = _get_client()

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
- "REQUEST_IMAGE" — When the user has generic waste/trash but hasn't specified what it is. Ask them to upload a photo or describe the item.
- "SHOW_ECO_RESULT" — When the user explicitly names the waste item (e.g., "plastic cup", "banana peel", "food") OR when an image is processed. In your message, tell them exactly which bin to use (Green for Compost, Blue for Recycle, Black for Landfill, Red for Hazardous).
- "DISPATCH_INCIDENT" — When the user REPORTS A PROBLEM: spill, broken seat, fight, medical emergency, suspicious activity. Extract the description.
  Set payload.description to a clear summary of the issue.
- "SHOW_CROWD" — When the user asks about crowd levels, density, or how busy sections are.
- "HIDE_MAP" — When the map is no longer needed (user says thanks, done, close, etc.)

Context about the current fan:
- Name: {holder_name}
- Seat: Section {section}, Row {row}, Seat {seat_number}
- Match: {match_id}
- Transit preference: {transit_method}

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
    client_info = _get_client()
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
            parts = [types.Part.from_text(text="\n\n".join(contents))]
    
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
            text = response.text.strip()
        result = json.loads(text)

        # Validate required fields
        if "message" not in result:
            result["message"] = "I'm here to help! What do you need?"
        if "ui_action" not in result:
            result["ui_action"] = "NONE"
        if "payload" not in result:
            result["payload"] = {}

        return result

    except Exception as e:
        logger.error(f"Gemini agentic chat error: {e}")
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

