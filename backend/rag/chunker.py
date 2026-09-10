import os
import re
from pathlib import Path
from typing import List, Dict, Any

class DocumentChunker:
    def __init__(self, knowledge_base_dir: str):
        self.kb_dir = Path(knowledge_base_dir)

    def load_and_chunk(self) -> List[Dict[str, Any]]:
        chunks = []
        if not self.kb_dir.exists():
            return chunks

        md_files = list(self.kb_dir.glob("*.md"))
        for file_path in md_files:
            file_chunks = self._chunk_file(file_path)
            chunks.extend(file_chunks)

        return chunks

    def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse header metadata
        course_name = "General"
        domain = "General"
        sub_domain = "General"
        module = "Curriculum"
        source = str(file_path.name)

        lines = content.split("\n")
        body_lines = []
        for line in lines:
            if line.startswith("# Course:"):
                course_name = line.replace("# Course:", "").strip()
            elif line.startswith("Domain:"):
                domain = line.replace("Domain:", "").strip()
            elif line.startswith("Sub-Domain:"):
                sub_domain = line.replace("Sub-Domain:", "").strip()
            elif line.startswith("## Module:"):
                module = line.replace("## Module:", "").strip()
            elif line.startswith("Source:"):
                source = line.replace("Source:", "").strip()
            else:
                body_lines.append(line)

        body_text = "\n".join(body_lines)

        # Split by section headers (### )
        sections = re.split(r"(###\s+[^\n]+)", body_text)
        chunks = []
        current_section = "Overview"

        for i in range(len(sections)):
            part = sections[i].strip()
            if not part:
                continue
            if part.startswith("###"):
                current_section = part.replace("###", "").strip()
            else:
                text = part
                # If text is substantial, create a chunk
                if len(text) > 40:
                    chunk_id = f"{file_path.stem}_{len(chunks) + 1}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "course": course_name,
                        "domain": domain,
                        "sub_domain": sub_domain,
                        "module": module,
                        "topic": current_section,
                        "source": f"{course_name} → {current_section} (Source: {source})",
                        "text": f"Course: {course_name}\nTopic: {current_section}\nContent:\n{text}",
                        "raw_content": text
                    })

        return chunks
