import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("Chybí OPENAI_API_KEY. Zkontroluj soubor .env.")

print("API klíč načten.")


def spocitej_davku(delka, sirka, hloubka, davkovani):
    objem = delka * sirka * hloubka
    mnozstvi_pripravku = objem * davkovani

    return {
        "objem_m3": objem,
        "mnozstvi_ml": mnozstvi_pripravku

    }


tools = [
    {
        "type": "function",
        "function": {
            "name": "spocitej_davku",
            "description": (
                "Vypočítá objem vody v obdélníkovém bazénu "
                "a množství přípravku podle dávkování zadaného uživatelem."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "delka": {
                        "type": "number",
                        "description": "Délka bazénu v metrech."
                    },
                    "sirka": {
                        "type": "number",
                        "description": "Šířka bazénu v metrech."
                    },
                    "hloubka": {
                        "type": "number",
                        "description": "Skutečná hloubka vody v metrech."
                    },
                    "davkovani": {
                        "type": "number",
                        "description": (
                            "Dávkování v ml na m³ podle etikety přípravku, "
                            "které zadal uživatel."
                        )
                    }
                },
                "required": ["delka", "sirka", "hloubka", "davkovani"]
            }
        }
    }
]

client = OpenAI(api_key=api_key)

messages = [
    {
        "role": "user",
        "content": (
            "Mám obdélníkový bazén dlouhý 6 metrů a široký 3 metry. "
            "Hloubka vody je 1,4 metru. Na etiketě je 20 ml na m³. "
            "Použij dostupný nástroj a zjisti, kolik přípravku potřebuji."
        ),
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

zprava = response.choices[0].message
if zprava.tool_calls:
    messages.append(zprava)

    for volani in zprava.tool_calls:
        vstupy = json.loads(volani.function.arguments)
        vysledek = spocitej_davku(**vstupy)
        print("Výsledek Python funkce:", vysledek)

        messages.append({
            "role": "tool",
            "tool_call_id": volani.id,
            "content": json.dumps(vysledek),
        })

    druha_odpoved = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    print("Odpověď modelu:", druha_odpoved.choices[0].message.content)
else:
    print("Model odpověděl:", zprava.content)
