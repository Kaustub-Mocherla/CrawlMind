import re

def chunked_markdown(markdown:str)->list[str]:
    pattern = r"#+\s+.*"
    chunks = re.split(pattern, markdown)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks


