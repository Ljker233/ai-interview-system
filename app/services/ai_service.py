class AIService:
    """
    Mock AI service for local development and classroom testing.

    This class has the same public method as the real AIService:
        generate_interview_questions(interview)

    So QuestionService does not need to change.
    Later, we can replace this mock implementation with a real LLM API call.
    """

    def generate_interview_questions(self, interview: dict) -> list[dict]:
        interview_types = interview.get("interview_types", [])
        target_role = interview.get("target_role", "software engineer")
        difficulty = interview.get("difficulty", "medium")

        questions = []

        for interview_type in interview_types:
            if interview_type == "coding":
                questions.append(
                    self._build_coding_question(
                        target_role=target_role,
                        difficulty=difficulty,
                    )
                )
            elif interview_type == "behavioral":
                questions.append(
                    self._build_behavioral_question(
                        target_role=target_role,
                        difficulty=difficulty,
                    )
                )
            elif interview_type == "system_design":
                questions.append(
                    self._build_system_design_question(
                        target_role=target_role,
                        difficulty=difficulty,
                    )
                )
            else:
                questions.append(
                    self._build_generic_question(
                        interview_type=interview_type,
                        target_role=target_role,
                        difficulty=difficulty,
                    )
                )

        return questions

    def _build_coding_question(
        self,
        target_role: str,
        difficulty: str,
    ) -> dict:
        return {
            "type": "coding",
            "question": (
                f"You are interviewing for a {target_role} role. "
                f"Difficulty: {difficulty}.\n\n"
                "Problem: Given a list of user login events, each event contains "
                "a user_id and a timestamp. Return the top K users with the highest "
                "number of login events.\n\n"
                "Input:\n"
                "- events: List of objects, each with user_id and timestamp\n"
                "- k: integer\n\n"
                "Output:\n"
                "- A list of user_ids ordered by login count descending\n\n"
                "Example:\n"
                "events = [\n"
                "  {user_id: 'u1', timestamp: 100},\n"
                "  {user_id: 'u2', timestamp: 105},\n"
                "  {user_id: 'u1', timestamp: 110}\n"
                "]\n"
                "k = 1\n"
                "Output: ['u1']\n\n"
                "Constraints:\n"
                "- 1 <= len(events) <= 100000\n"
                "- 1 <= k <= number of unique users\n\n"
                "Do not write the solution yet. Explain your approach first."
            ),
            "expected_signals": [
                "Uses a hash map to count events by user_id",
                "Can explain time and space complexity",
                "Handles ties or clarifies tie-breaking behavior",
                "Considers large input size",
            ],
            "follow_up_questions": [
                "How would you handle ties between users with the same login count?",
                "How would you solve this if the event stream is too large to fit in memory?",
            ],
        }

    def _build_behavioral_question(
        self,
        target_role: str,
        difficulty: str,
    ) -> dict:
        return {
            "type": "behavioral",
            "question": (
                f"You are interviewing for a {target_role} role. "
                f"Difficulty: {difficulty}.\n\n"
                "Tell me about a time when you had to make a technical decision "
                "with incomplete information. What options did you consider, "
                "what tradeoffs did you evaluate, and what was the final outcome?"
            ),
            "expected_signals": [
                "Uses a clear STAR structure",
                "Explains tradeoffs instead of only describing the final decision",
                "Shows ownership and communication with stakeholders",
                "Reflects on what they learned",
            ],
            "follow_up_questions": [
                "What would you do differently if you faced the same situation again?",
                "How did you convince others that your decision was the right one?",
            ],
        }

    def _build_system_design_question(
        self,
        target_role: str,
        difficulty: str,
    ) -> dict:
        return {
            "type": "system_design",
            "question": (
                f"You are interviewing for a {target_role} role. "
                f"Difficulty: {difficulty}.\n\n"
                "Design a backend system for an AI mock interview platform. "
                "Users can create interviews, the system generates questions asynchronously, "
                "users submit answers, and the system evaluates the answers later.\n\n"
                "Functional requirements:\n"
                "- Create an interview session\n"
                "- Generate interview questions asynchronously\n"
                "- Store questions and answers\n"
                "- Track interview status\n\n"
                "Non-functional requirements:\n"
                "- The API should respond quickly\n"
                "- Question generation should be reliable\n"
                "- The system should handle many interviews at the same time\n"
                "- Failures should be retried or tracked\n\n"
                "Please describe the main services, data model, async workflow, "
                "and how you would scale the system."
            ),
            "expected_signals": [
                "Separates API server from async worker",
                "Uses a queue such as SQS for background processing",
                "Designs reasonable DynamoDB or database tables",
                "Mentions retries, idempotency, and failure handling",
                "Can discuss scaling API and worker independently",
            ],
            "follow_up_questions": [
                "How would you avoid generating duplicate questions for the same interview?",
                "How would you monitor failures in the async workflow?",
            ],
        }

    def _build_generic_question(
        self,
        interview_type: str,
        target_role: str,
        difficulty: str,
    ) -> dict:
        return {
            "type": interview_type,
            "question": (
                f"You are interviewing for a {target_role} role. "
                f"Difficulty: {difficulty}. "
                f"Please answer a realistic {interview_type} interview question."
            ),
            "expected_signals": [
                "Provides a structured answer",
                "Explains reasoning clearly",
            ],
            "follow_up_questions": [
                "Can you explain your reasoning in more detail?",
            ],
        }
