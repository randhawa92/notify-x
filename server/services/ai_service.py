import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_message(data, custom_instruction=None):

    try:

        # --------------------------------
        # Prepare Excel Data
        # --------------------------------

        details = []

        for key, value in data.items():

            # Phone number AI ko mat bhejo
            if key.strip().upper() in [
                "NUMBER",
                "PHONE",
                "PHONE_NUMBER",
                "MOBILE",
                "CONTACT"
            ]:
                continue

            # Empty values ignore karo
            if str(value).strip() == "":
                continue

            details.append(
                f"{key.strip()}: {str(value).strip()}"
            )

        excel_data = "\n".join(details)

        # --------------------------------
        # User Instruction
        # --------------------------------

        if not custom_instruction:

            custom_instruction = """
Generate a personalized WhatsApp message
based on the provided Excel data.
"""

        # --------------------------------
        # AI Prompt
        # --------------------------------

        prompt = f"""
You are the AI messaging engine of NotifyX.

You are given ONE row of data from an Excel dataset.

Your task is to understand the meaning, context,
and important information contained in the data
and generate an appropriate WhatsApp message.

EXCEL DATA:

{excel_data}

USER INSTRUCTION:

{custom_instruction}

IMPORTANT RULES:

1. Understand the data before writing the message.
2. Use only information present in the Excel data.
3. Never invent names, amounts, dates, products,
   events, or other facts.
4. Do not mention the phone number.
5. Do not mention Excel, dataset, columns, or AI.
6. If a person's name is available, use it naturally.
7. Keep the message professional and friendly.
8. Keep the message concise and WhatsApp-friendly.
9. Maximum 80 words.
10. Do not mention missing or empty fields.
11. Return ONLY the final WhatsApp message.
12. Do not add explanations before or after the message.

Generate the message now.
"""

        # --------------------------------
        # Generate Response
        # --------------------------------

        response = model.generate_content(prompt)

        message = response.text.strip()

        if not message:
            raise Exception("Empty response from Gemini")

        return message

    except Exception as e:

        print("Gemini Error:", e)

        # --------------------------------
        # Safe Fallback
        # --------------------------------

        name = (
            data.get("NAME")
            or data.get("Name")
            or data.get("name")
            or "there"
        )

        return f"""
Hello {name},

We wanted to share an update with you.

Please feel free to contact us if you have
any questions.

Regards,
NotifyX
""".strip()