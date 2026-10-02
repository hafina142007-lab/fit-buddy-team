import os
from typing import Optional

# Uses the current Google Gen AI SDK. If no API key is configured, the app
# supplies a clearly labelled local demo plan so the rest of the project works.
MODEL_WORKOUT = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")
MODEL_TIP = os.getenv("GEMINI_TIP_MODEL", "gemini-2.5-flash")


def _gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() in {"replace_with_your_api_key", ""}:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        # If the user has a key but the SDK is missing, make the setup problem explicit.
        raise RuntimeError(
            "Google Gen AI SDK is not installed. Run: pip install -r requirements.txt"
        )


def _generate(prompt: str, model: str, fallback: str) -> str:
    client = _gemini_client()
    if client is None:
        return "DEMO MODE — add GOOGLE_API_KEY to your .env file to enable Gemini AI.\n\n" + fallback
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        result = (getattr(response, "text", None) or "").strip()
        if not result:
            raise RuntimeError("The AI model returned an empty response.")
        return result
    except Exception as exc:
        # Fail clearly rather than silently pretending a real AI response was generated.
        raise RuntimeError(f"Gemini request failed: {exc}") from exc


def _fallback_workout(name: str, goal: str, intensity: str, experience: str) -> str:
    if goal == "Weight loss":
        focus = "Cardio and full-body movement"
        main = "Brisk walking or cycling: 20–30 min; bodyweight squats: 2–3 × 10; wall/incline push-ups: 2–3 × 8; dead bug: 2 × 8 each side"
    elif goal == "Muscle gain":
        focus = "Full-body strength"
        main = "Bodyweight squats: 3 × 10; incline push-ups: 3 × 8; glute bridges: 3 × 12; backpack rows: 3 × 10; plank: 3 × 20 sec"
    elif goal == "Flexibility":
        focus = "Mobility and flexibility"
        main = "Cat-cow: 2 × 8; hip-flexor stretch: 2 × 30 sec each side; hamstring stretch: 2 × 30 sec; thoracic rotations: 2 × 8 each side; easy walk: 10 min"
    else:
        focus = "Balanced wellness"
        main = "Brisk walk: 20 min; bodyweight squats: 2 × 10; wall push-ups: 2 × 8; bird-dog: 2 × 8 each side; gentle stretching: 5 min"

    days = [
        ("Day 1 — Foundation", focus, main),
        ("Day 2 — Light cardio", "Easy movement", "Comfortable walk or cycle: 20–30 min; gentle mobility: 5–10 min"),
        ("Day 3 — Strength and core", "Controlled strength", main),
        ("Day 4 — Recovery", "Active recovery", "Easy walk: 10–20 min or gentle yoga; stop if uncomfortable"),
        ("Day 5 — Full body", focus, main),
        ("Day 6 — Enjoyable activity", "Cardio or mobility", "Choose a comfortable walk, cycling, swimming, or mobility session: 20–30 min"),
        ("Day 7 — Rest and reflect", "Recovery", "Rest; optional gentle stretching. Note energy, comfort, and what you enjoyed"),
    ]
    lines = [
        f"Personalized starter plan for {name}",
        f"Goal: {goal} | Preferred intensity: {intensity} | Experience: {experience}",
        "",
        "Before each session: warm up gently for 5–10 minutes. Use a pace that lets you maintain good form.",
        "Rest 45–90 seconds between strength sets as needed. Cool down with 5 minutes of easy movement and comfortable stretches.",
        "",
    ]
    for title, focus_text, activity in days:
        lines.extend([title, f"Focus: {focus_text}", f"Main session: {activity}", ""])
    lines.append("Safety: This is general wellness information, not medical advice. Adapt exercises to your abilities; stop for pain, dizziness, chest pain, or unusual shortness of breath and seek appropriate medical help.")
    return "\n".join(lines)


def generate_workout_gemini(user) -> str:
    fallback = _fallback_workout(user.username, user.goal, user.intensity, user.experience)
    prompt = f"""
You are a careful fitness-planning assistant. Create a practical 7-day starter workout plan.
Profile: name={user.username}, age={user.age}, weight_kg={user.weight}, goal={user.goal},
preferred intensity={user.intensity}, experience={user.experience}.
Return readable plain text with each day clearly labelled. For each day include focus,
warm-up (5–10 minutes), exercises with sets/reps or duration, rest/recovery, and cooldown.
Include at least one recovery/rest day. Scale volume conservatively to the experience level.
Do not promise results or prescribe extreme dieting. Do not diagnose or give medical treatment.
If a detail is missing, make conservative assumptions. Include a short safety note.
"""
    return _generate(prompt, MODEL_WORKOUT, fallback)


def generate_nutrition_tip_with_flash(goal: str) -> str:
    examples = {
        "Weight loss": "Build balanced meals around vegetables, a protein source, high-fibre carbohydrates, and water; avoid crash diets.",
        "Muscle gain": "Include a protein-rich food such as beans, lentils, eggs, fish, tofu, or yogurt in regular meals, alongside enough overall food and sleep.",
        "Flexibility": "Drink water regularly and eat balanced meals; recovery and adequate energy support mobility practice.",
        "General wellness": "Aim for varied meals with vegetables, fruit, protein, whole grains, and regular hydration.",
    }
    prompt = f"""Give one concise, practical, non-medical nutrition or recovery tip for a person whose fitness goal is {goal}.
Avoid calorie prescriptions, supplements, extreme restrictions, and guaranteed outcomes."""
    return _generate(prompt, MODEL_TIP, examples.get(goal, examples["General wellness"]))


def update_workout_plan(user, original_plan: str, feedback: str) -> str:
    fallback = (
        "UPDATED PLAN — DEMO MODE\n"
        f"Your requested change: {feedback}\n\n"
        "Keep the original plan's warm-up and cooldown. Apply the request gradually: replace or "
        "adjust one session at a time, keep at least one rest/recovery day, and reduce volume if "
        "form or recovery suffers.\n\n" + original_plan
    )
    prompt = f"""
Revise the following 7-day fitness plan using the user's feedback. Keep it practical and conservative.
Profile: age={user.age}, goal={user.goal}, intensity={user.intensity}, experience={user.experience}.
User feedback: {feedback}
Original plan:
{original_plan}
Return the complete revised 7-day plan, clearly label all days, preserve warm-ups/cooldowns,
include recovery/rest, and add a brief safety note. Do not provide medical diagnosis or extreme advice.
"""
    return _generate(prompt, MODEL_WORKOUT, fallback)
