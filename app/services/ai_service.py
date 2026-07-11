class AIService:
    def generate_interview_questions(self, interview: dict) -> list[dict]:
        """
        Mock question generation.

        Keep or merge your existing implementation if you already have one.
        This method is included here so the file can run end-to-end in a simple project.
        """
        interview_id = interview["interview_id"]
        interview_types = interview.get("interview_types", ["coding"])
        target_role = interview.get("target_role", "software engineer")
        difficulty = interview.get("difficulty", "medium")

        questions = []
        order = 1

        if "coding" in interview_types:
            questions.append(
                {
                    "question_id": f"{interview_id}#{order}",
                    "interview_id": interview_id,
                    "type": "coding",
                    "question_order": order,
                    "question": (
                        f"Solve a {difficulty} coding problem for a "
                        f"{target_role} interview: Given an array of numbers, "
                        f"return the two numbers that add up to a target."
                    ),
                    "expected_signals": [
                        "Uses hash map",
                        "Explains time complexity",
                        "Handles edge cases",
                    ],
                    "follow_up_questions": [
                        "How would you handle duplicate numbers?",
                        "What is the time and space complexity?",
                    ],
                }
            )
            order += 1

        if "behavioral" in interview_types:
            questions.append(
                {
                    "question_id": f"{interview_id}#{order}",
                    "interview_id": interview_id,
                    "type": "behavioral",
                    "question_order": order,
                    "question": (
                        f"Tell me about a technical project that is relevant "
                        f"to a {target_role} role."
                    ),
                    "expected_signals": [
                        "Uses STAR structure",
                        "Explains personal contribution",
                        "Mentions impact",
                    ],
                    "follow_up_questions": [
                        "What was the hardest technical challenge?",
                        "What would you improve if you did it again?",
                    ],
                }
            )
            order += 1

        if "system_design" in interview_types:
            questions.append(
                {
                    "question_id": f"{interview_id}#{order}",
                    "interview_id": interview_id,
                    "type": "system_design",
                    "question_order": order,
                    "question": (
                        f"Design a scalable mock interview platform for a "
                        f"{target_role} candidate."
                    ),
                    "expected_signals": [
                        "Defines APIs",
                        "Discusses storage",
                        "Uses async workers",
                        "Mentions scalability",
                    ],
                    "follow_up_questions": [
                        "How would you handle long-running AI calls?",
                        "How would you scale the worker system?",
                    ],
                }
            )

        return questions

    def evaluate_answer(
        self,
        question: dict,
        answer: dict,
        interview: dict,
    ) -> dict:
        question_text = question.get("question", "")
        answer_text = answer.get("answer_text", "")
        target_role = interview.get("target_role", "software engineer")
        difficulty = interview.get("difficulty", "medium")
        expected_signals = question.get("expected_signals", [])

        return {
            "score": 8,
            "feedback": (
                f"This is a mock evaluation for a {difficulty} "
                f"{target_role} interview question. The answer addresses the "
                f"question but could be improved with more details, trade-offs, "
                f"and edge cases."
            ),
            "strengths": [
                "The answer shows a reasonable understanding of the problem.",
                "The candidate provides a clear high-level approach.",
            ],
            "improvements": [
                "Explain trade-offs more clearly.",
                "Discuss edge cases and failure scenarios.",
                "Provide more details about scalability and implementation.",
            ],
            "follow_up_questions": [
                "How would you improve your solution if traffic increased 10x?",
                "What edge cases would you test?",
            ],
            "model_name": "mock-llm",
            "metadata": {
                "question_preview": question_text[:100],
                "answer_preview": answer_text[:100],
                "expected_signal_count": len(expected_signals),
            },
        }
