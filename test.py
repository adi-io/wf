from google import genai
from bs4 import BeautifulSoup

from google.genai import types

def process_text_with_ai(text):

    client = genai.Client(
        vertexai=True, project="so-concrete", location="global",
    )
    chat = client.chats.create(model="gemini-2.0-flash")
    response = chat.send_message("Please translate the English text to Dutch and only respond back with the translated string. If there is no English text to translate, just send back the original text. NOTHING ELSE. No additional explanations, questions, or commentary. Only respond with the translated text." + str(text))
    return (response.text)

def parse_and_process_data_file(filepath):
    parsed_data = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line: continue

                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = parts[0]
                    value = parts[1]

                    value = process_text_with_ai(value)


                    parsed_data[key] = {
                        'text': value
                    }
                    print(parsed_data)

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return None


    return parsed_data


input_file = 'default.properties'

processed_data = parse_and_process_data_file(input_file)
