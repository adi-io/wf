from google import genai
from google.genai import types
import concurrent.futures

def process_chunk(chunk):
    client = genai.Client(
        vertexai=True, project="so-concrete", location="global",
    )
    chat = client.chats.create(model="gemini-2.0-flash-lite-001")

    response = chat.send_message("You are given a part of a file which needs some processing. Your task is to convert the English text within the HTML code to Dutch. Please translate ONLY the English text content that appears between HTML tags, while preserving all HTML code exactly as it is. Return only the complete HTML with translated text content. If there is no English text to translate, just send back the original text unchanged. NOTHING ELSE. No additional explanations, questions, or commentary. Only respond with the HTML containing the translated text. Do not change any HTML tags or attributes - only translate the content text." + str(chunk))

    result = response.text
    if result is not None:
        result.replace("```html\n", "").replace("```\n", "").replace("```", "")
    return (result)

def process_properties_file(file_path, max_chunk_size=5000, max_workers=5):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    chunks = []
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line)

        if (line.strip() == "") and current_chunk:
            chunks.append("".join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(line)
        current_size += line_size

    if current_chunk:
        chunks.append("".join(current_chunk))

    # Process chunks in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and collect future objects
        future_to_chunk = {executor.submit(process_chunk, chunk): i for i, chunk in enumerate(chunks)}

        # Collect results in order
        responses = [None] * len(chunks)
        for future in concurrent.futures.as_completed(future_to_chunk):
            index = future_to_chunk[future]
            try:
                responses[index] = future.result()
            except Exception as exc:
                print(f'Chunk {index} generated an exception: {exc}')
                responses[index] = chunks[index]  # Fall back to original content

    # Combine responses
    combined_response = "\n".join(responses)
    return combined_response

file_path = "d.properties"
result = process_properties_file(file_path, max_workers=5)
print(result)
