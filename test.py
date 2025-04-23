from google import genai
from google.genai import types


def process_properties_file(file_path, max_chunk_size=5000):
    # Read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Create chunks based on empty lines
    chunks = []
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line)

        # If we hit an empty line or exceed max size, start a new chunk
        if (line.strip() == "") and current_chunk:
            chunks.append("".join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(line)
        current_size += line_size

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append("".join(current_chunk))

    # Process each chunk and collect responses
    responses = []
    for i, chunk in enumerate(chunks):

        client = genai.Client(
            vertexai=True, project="so-concrete", location="global",
        )
        chat = client.chats.create(model="")

        response = chat.send_message("You are given a part of a file which needs some processing. Your task is to convert the English text within the HTML code to Dutch. Please translate ONLY the English text content that appears between HTML tags, while preserving all HTML code exactly as it is. Return only the complete HTML with translated text content. If there is no English text to translate, just send back the original text unchanged. NOTHING ELSE. No additional explanations, questions, or commentary. Only respond with the HTML containing the translated text. Do not change any HTML tags or attributes - only translate the content text." + str(chunk))
        result = response.text
        responses.append(result)

    # Combine responses
    combined_response = "\n".join(responses)
    combined_response = combined_response.replace("```html\n", "").replace("```\n", "")
    return combined_response

# Example usage
file_path = "d.properties"
result = process_properties_file(file_path)
print(result)
