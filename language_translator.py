from unicodedata import name
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from google import genai
import concurrent.futures
import zipfile
import os
import tempfile


def extract_full_language_file(zip_path, file_to_extract="whatfix.com/full/default.properties"):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        try:
            for item in file_list:
                if item.endswith(file_to_extract):
                    extracted_path = zip_ref.extract(item)
                    return os.path.abspath(extracted_path)
        except:
            print(f"File '{file_to_extract}' not found in the archive")
            return (None)

def background_task_after_response(temp_file_path, zip_file_path, language_file_path):
    def task():
        try:
            os.unlink(temp_file_path)
            os.unlink(zip_file_path)
            os.unlink(language_file_path)
        except Exception as e:
            print(f"Error deleting files: {e}")

def process_chunk(chunk, language):
    if chunk.strip() == "":
        return (chunk)

    print(f"processing initiated for {chunk}")

    client = genai.Client(
        vertexai=True, project="so-concrete", location="global",
    )
    chat = client.chats.create(model="gemini-2.5-pro-preview-03-25")

    response = chat.send_message(f"You are given a part of a file which needs some processing. Your task is to convert the English text within the HTML code to {language}. Please translate ONLY the English text content that appears between HTML tags, while preserving all HTML code exactly as it is. Return only the complete HTML with translated text content. If there is no English text to translate, just send back the original text unchanged. NOTHING ELSE. No additional explanations, questions, or commentary. Only respond with the HTML containing the translated text. Do not change any HTML tags or attributes - only translate the content text. {chunk}")

    result = response.text
    print(result)
    if result is not None:
        result = result.replace("```html\n", "").replace("```\n", "").replace("```", "")
    return (result)

def language_code_to_name(language_code):
    language_map = {
        'CZ': 'Czech',
        'DE': 'German',
        'ES': 'Spanish',
        'FR': 'French',
        'IT': 'Italian',
        'JA': 'Japanese',
        'KO': 'Korean',
        'NL': 'Dutch',
        'PL': 'Polish',
        'PT': 'Portuguese',
        'RU': 'Russian',
        'SV': 'Swedish',
        'TR': 'Turkish',
        'ZH': 'Chinese',
        'AR': 'Arabic',
        'HI': 'Hindi',
        'VI': 'Vietnamese',
        'TH': 'Thai',
        'DA': 'Danish',
        'FI': 'Finnish',
        'NO': 'Norwegian',
        'HU': 'Hungarian',
        'RO': 'Romanian',
        'EL': 'Greek',
        'BG': 'Bulgarian',
        'HR': 'Croatian',
        'SK': 'Slovak',
        'SL': 'Slovenian',
        'UK': 'Ukrainian',
        'ID': 'Indonesian',
        'MS': 'Malay',
        'HE': 'Hebrew',
        'FA': 'Persian'
    }

    return language_map.get(language_code, "English")

def process_properties_file(file_path, language_code, fastmode, max_workers=5000):
    language = language_code_to_name(language_code)
    with open(file_path, 'r') as file:
        lines = file.readlines()

    chunks = []
    current_chunk = []

    if fastmode is True:
        for line in lines:
            chunks.append(line)
    else:
        for line in lines:
            if (line.strip() == "") and current_chunk:
                chunks.append("".join(current_chunk))
                current_chunk = []

            current_chunk.append(line)

        if current_chunk:
            chunks.append("".join(current_chunk))

    # Process chunks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {executor.submit(process_chunk, chunk, language): i for i, chunk in enumerate(chunks)}

        responses = [None] * len(chunks)
        for future in concurrent.futures.as_completed(future_to_chunk):
            index = future_to_chunk[future]
            try:
                responses[index] = future.result()
            except Exception as exc:
                print(f'Chunk {index} generated an exception: {exc}')
                responses[index] = chunks[index]  # Fall back to original content

    combined_response = "\n".join(responses)
    return combined_response

def handle_and_process_file(zip_file_path, language_code, fastmode):
    try:
        language_file_path = extract_full_language_file(zip_file_path)
        result = process_properties_file(language_file_path, language_code,fastmode, max_workers=5000)
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f'{language_code}.properties')
        with open(temp_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(result)

        return FileResponse(
            path= temp_file_path,
            filename=f'{language_code}.properties',
            media_type="text/plain",
            background=background_task_after_response(temp_file_path, zip_file_path, language_file_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=(str(e)))
