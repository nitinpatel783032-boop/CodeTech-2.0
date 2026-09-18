# ============================================
# Code Master AI - Backend (Flask)
# Runs on YOUR server (Render/Railway/etc), NOT in the browser.
# Your Groq API key stays hidden here - never exposed to users.
#
# v4: switched from Google's Gemini API to Groq API (super fast
# inference). Still supports text + image (screenshot) messages
# exactly the same way from the frontend.
# ============================================

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # allows the CodeMaster frontend to call this backend

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👉 Groq models:
# - text-only, very fast + smart: "llama-3.3-70b-versatile"
# - supports images (vision): "meta-llama/llama-4-scout-17b-16e-instruct"
# We auto-pick the vision model only when a message actually contains an image,
# since vision models are a bit slower than pure text models.
TEXT_MODEL = "openai/gpt-oss-120b"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = """You are Code Master AI — a friendly, supportive coding buddy inside the "CodeMaster" web development learning platform (a Hindi/Hinglish coding tutorial site).

Your personality:
- Talk like a friendly, encouraging coding "bro" — casual, warm, never boring or textbook-like.
- Respond in Hinglish (Hindi + English mix) to match the site's tone, unless the user writes in pure English.
- Keep explanations simple and beginner-friendly. Assume the user is still learning.
- Use small code examples when helpful, wrapped in markdown code blocks with the right language tag.
- Break down concepts step-by-step.

Your focus areas ONLY:
- HTML, CSS, JavaScript, React, Node.js, MongoDB, Git & GitHub, Python/Flask, and general programming/debugging help.

Image handling: users may send you a screenshot of their code or an error message.
When they do, carefully read the code/error in the image, identify the bug or issue,
explain what's wrong in simple terms, and show the corrected code.

If the user asks about something unrelated to web development or programming, politely decline and redirect them back to web dev topics. Example: "Haha, that's outside my zone bro — main tumhara Code Master AI hoon, web dev mein level up karne ke liye! Koi HTML, CSS, JS, ya coding sawal hai?"

Never break character. Never claim to be a general-purpose AI."""


def anthropic_style_to_groq(messages):
    """
    The frontend (code-master-ai.js) builds messages in this shape:
        {"role": "user" | "assistant",
         "content": [
            {"type": "text", "text": "..."},
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}
         ]}

    Groq's API (OpenAI-compatible) wants:
        {"role": "user" | "assistant",
         "content": [
            {"type": "text", "text": "..."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
         ]}

    This function converts one into the other, and also tells us whether
    any image was found (so we know which model to use).
    """
    groq_messages = []
    has_image = False

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content")

        if isinstance(content, str):
            groq_messages.append({"role": role, "content": content})
            continue

        parts = []
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    text_value = block.get("text", "")
                    if text_value.strip():
                        parts.append({"type": "text", "text": text_value})
                elif block.get("type") == "image":
                    has_image = True
                    source = block.get("source", {})
                    media_type = source.get("media_type", "image/png")
                    data = source.get("data", "")
                    parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{media_type};base64,{data}"}
                    })

        if parts:
            groq_messages.append({"role": role, "content": parts})

    return groq_messages, has_image


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages")

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "messages array is required"}), 400

    try:
        groq_messages, has_image = anthropic_style_to_groq(messages)

        # Vision model only when needed — text model is faster
        model = VISION_MODEL if has_image else TEXT_MODEL

        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + groq_messages

        response = requests.post(
            GROQ_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json={
                "model": model,
                "messages": full_messages,
                "max_tokens": 1200,
            },
            timeout=60,
        )
        resp_json = response.json()

        if "error" in resp_json:
            print(f"GROQ API ERROR: {resp_json['error']}")
            return jsonify({"error": resp_json["error"].get("message", "Groq API error")}), 500

        reply_text = "Sorry bro, samajh nahi aaya. Phir se try karo?"
        choices = resp_json.get("choices")
        if choices and len(choices) > 0:
            reply_text = choices[0].get("message", {}).get("content", reply_text)

        return jsonify({"reply": reply_text})

    except requests.exceptions.RequestException as e:
        print(f"REQUEST ERROR: {e}")
        return jsonify({"error": "AI service tak nahi pahunch paya. Phir se try karo."}), 500
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return jsonify({"error": "Server mein kuch gadbad ho gayi."}), 500


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Code Master AI backend is running (Groq)"}), 200


if __name__ == "__main__":
    # For local testing only. In production, gunicorn runs this (see Procfile).
    app.run(debug=True, port=5000)