
import re


# Match numbered requirements such as:
# 1. Describe your approach
# 2) Explain security controls
# Q3. What support do you provide?
QUESTION_PATTERN = re.compile(
    r"^\s*(?:Q\s*)?(\d+)[.)]\s+(.+)$",
    re.IGNORECASE,
)


def extract_questions(text: str) -> list[dict]:
    """
    Extract numbered questions or requirements
    from customer RFP text.

    Supports multiline question content.
    """

    questions = []
    current_number = None
    current_lines = []

    def save_current_question():
        if current_number is None:
            return

        question_text = " ".join(current_lines).strip()

        if question_text:
            questions.append({
                "question_id": f"Q{current_number}",
                "question": question_text,
            })

    for line in text.splitlines():
        match = QUESTION_PATTERN.match(line)

        if match:
            # Save the previous question.
            save_current_question()

            current_number = match.group(1)
            current_lines = [match.group(2).strip()]

        elif current_number is not None:
            # Continue a question across multiple lines.
            if line.strip():
                current_lines.append(line.strip())

    # Save the final question.
    save_current_question()

    return questions
