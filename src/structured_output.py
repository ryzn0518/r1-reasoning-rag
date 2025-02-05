json_schema = {
    "title": "retrieval_response",
    "description": "Response from the retrieval validator.",
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "The status of the retrieval",
        },
        "useful_information": {
            "type": "string",
            "description": "The useful information from the retrieval",
        },
        "missing_information": {
            "type": "string",
            "description": "The missing information from the retrieval",
            "default": None,
        },
    },
    "required": ["status", "useful_information", "missing_information"],
}

# Custom parser
# def extract_json(message: AIMessage) -> List[dict]:
#     """Extracts JSON content from a string where JSON is embedded between \`\`\`json and \`\`\` tags.

#     Parameters:
#         text (str): The text containing the JSON content.

#     Returns:
#         list: A list of extracted JSON strings.
#     """
#     text = message.content
#     # Define the regular expression pattern to match JSON blocks
#     pattern = r"\`\`\`json(.*?)\`\`\`"

#     # Find all non-overlapping matches of the pattern in the string
#     matches = re.findall(pattern, text, re.DOTALL)

#     # Return the list of matched JSON strings, stripping any leading or trailing whitespace
#     try:
#         return [json.loads(match.strip()) for match in matches]
#     except Exception:
#         raise ValueError(f"Failed to parse: {message}")