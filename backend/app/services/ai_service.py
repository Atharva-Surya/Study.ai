import os
import json
import urllib.error
import urllib.request
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models.item_model import Item
from app.models.flashcard_model import Flashcard
from app.models.quiz_model import QuizQuestion

load_dotenv()

# Fetch Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

class AIService:
    _last_gemini_error = ""

    @staticmethod
    def _message_value(message: Any, key: str) -> str:
        if isinstance(message, dict):
            return message.get(key, "")
        return getattr(message, key, "")

    @staticmethod
    def _has_gemini_key() -> bool:
        """
        Check whether Gemini is configured.
        """
        return bool(GEMINI_API_KEY and GEMINI_API_KEY.strip())

    @classmethod
    def _set_gemini_error(cls, message: str) -> None:
        cls._last_gemini_error = message

    @staticmethod
    def _extract_gemini_text(data: Dict[str, Any]) -> str:
        candidates = data.get("candidates", [])
        if not candidates:
            return ""

        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts).strip()

    @staticmethod
    def _parse_json_response(raw: str) -> Dict[str, Any]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        return json.loads(cleaned)

    @classmethod
    def _generate_content(
        cls,
        prompt: str = "",
        messages: List[Dict[str, str]] | None = None,
        expect_json: bool = False,
    ) -> str:
        """
        Call Gemini through the REST API and return the generated text.
        """
        if not cls._has_gemini_key():
            return ""

        contents = []
        if messages:
            seen_user_message = False
            for message in messages:
                raw_role = cls._message_value(message, "role")
                role = "model" if raw_role == "assistant" else "user"
                content = (cls._message_value(message, "content") or "").strip()
                if role == "user":
                    seen_user_message = True
                if content and seen_user_message:
                    contents.append({"role": role, "parts": [{"text": content}]})
        else:
            contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
            },
        }

        if expect_json:
            payload["generationConfig"]["response_mime_type"] = "application/json"

        request = urllib.request.Request(
            GEMINI_API_URL.format(model=GEMINI_MODEL),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
                cls._set_gemini_error("")
                return cls._extract_gemini_text(data)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            cls._set_gemini_error(f"Gemini API returned HTTP {e.code}.")
            print(f"Gemini HTTP error: {e.code} {detail}")
        except Exception as e:
            cls._set_gemini_error("Gemini request failed.")
            print(f"Gemini request error: {e}")

        return ""

    @classmethod
    async def get_flashcards(cls, db: Session, item_id: int, user_id: int) -> List[Flashcard]:
        """
        Retrieve existing flashcards for a study item.
        """
        # Ensure the item belongs to the user
        item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
        if not item:
            return []
        return db.query(Flashcard).filter(Flashcard.item_id == item_id).all()

    @classmethod
    async def get_quiz(cls, db: Session, item_id: int, user_id: int) -> List[QuizQuestion]:
        """
        Retrieve existing quiz questions for a study item.
        """
        # Ensure the item belongs to the user
        item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
        if not item:
            return []
        return db.query(QuizQuestion).filter(QuizQuestion.item_id == item_id).all()

    @classmethod
    async def generate_flashcards(cls, db: Session, item_id: int, user_id: int) -> List[Flashcard]:
        """
        Generate flashcards using Gemini or fallback mockup, save to DB, and return them.
        """
        item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
        if not item:
            raise ValueError(f"Study item with ID {item_id} not found.")

        # Delete existing flashcards first to avoid accumulation on re-generation
        db.query(Flashcard).filter(Flashcard.item_id == item_id).delete()
        db.commit()

        generated_cards = []

        if cls._has_gemini_key():
            try:
                prompt = (
                    f"You are an AI study tutor. Generate exactly 4 study flashcards (Question and Answer) "
                    f"for the study topic: '{item.title}'. Description: '{item.description or ''}'.\n"
                    f"Output your response strictly as a JSON object matching this schema:\n"
                    f"{{\n"
                    f"  \"flashcards\": [\n"
                    f"    {{\"question\": \"Question text here\", \"answer\": \"Answer text here\"}}\n"
                    f"  ]\n"
                    f"}}\n"
                    f"Do not include any extra explanation or markdown block symbols outside the JSON."
                )
                
                raw = cls._generate_content(prompt, expect_json=True)
                data = cls._parse_json_response(raw)
                cards_data = data.get("flashcards", [])
                
                for card in cards_data:
                    generated_cards.append({
                        "question": card.get("question", ""),
                        "answer": card.get("answer", "")
                    })
            except Exception as e:
                # Log error and fall back to local generation
                print(f"Gemini error during flashcard generation: {e}")
                generated_cards = cls._fallback_flashcards(item.title, item.description)
        else:
            # No API key, use local fallback
            generated_cards = cls._fallback_flashcards(item.title, item.description)

        # Save to DB
        db_cards = []
        for card in generated_cards:
            db_card = Flashcard(
                question=card["question"],
                answer=card["answer"],
                item_id=item_id
            )
            db.add(db_card)
            db_cards.append(db_card)
        
        db.commit()
        for db_card in db_cards:
            db.refresh(db_card)
            
        return db_cards

    @classmethod
    async def generate_quiz(cls, db: Session, item_id: int, user_id: int) -> List[QuizQuestion]:
        """
        Generate quiz questions using Gemini or fallback mockup, save to DB, and return them.
        """
        item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
        if not item:
            raise ValueError(f"Study item with ID {item_id} not found.")

        # Delete existing quiz questions first
        db.query(QuizQuestion).filter(QuizQuestion.item_id == item_id).delete()
        db.commit()

        generated_questions = []

        if cls._has_gemini_key():
            try:
                prompt = (
                    f"You are an AI study tutor. Generate exactly 3 multiple-choice quiz questions "
                    f"for the study topic: '{item.title}'. Description: '{item.description or ''}'.\n"
                    f"Each question must have exactly 4 choices, and one correct_answer which MUST be one of the choices.\n"
                    f"Output your response strictly as a JSON object matching this schema:\n"
                    f"{{\n"
                    f"  \"quiz_questions\": [\n"
                    f"    {{\n"
                    f"      \"question\": \"Question prompt here\",\n"
                    f"      \"options\": [\"Choice A\", \"Choice B\", \"Choice C\", \"Choice D\"],\n"
                    f"      \"correct_answer\": \"Choice B\"\n"
                    f"    }}\n"
                    f"  ]\n"
                    f"}}\n"
                    f"Do not include any extra explanation or markdown block symbols outside the JSON."
                )
                
                raw = cls._generate_content(prompt, expect_json=True)
                data = cls._parse_json_response(raw)
                questions_data = data.get("quiz_questions", [])
                
                for q in questions_data:
                    generated_questions.append({
                        "question": q.get("question", ""),
                        "options": q.get("options", []),
                        "correct_answer": q.get("correct_answer", "")
                    })
            except Exception as e:
                # Log error and fall back to local generation
                print(f"Gemini error during quiz generation: {e}")
                generated_questions = cls._fallback_quiz(item.title, item.description)
        else:
            # No API key, use local fallback
            generated_questions = cls._fallback_quiz(item.title, item.description)

        # Save to DB
        db_questions = []
        for q in generated_questions:
            db_question = QuizQuestion(
                question=q["question"],
                options=json.dumps(q["options"]), # serialize options list to JSON string
                correct_answer=q["correct_answer"],
                item_id=item_id
            )
            db.add(db_question)
            db_questions.append(db_question)
        
        db.commit()
        for db_q in db_questions:
            db.refresh(db_q)
            
        return db_questions

    @classmethod
    async def generate_flashcards_for_topic(cls, topic: str, details: str = '') -> List[Dict[str, str]]:
        """
        Generate concise study flashcards from a topic or content string.
        """
        prompt = (
            f"You are an AI tutor that creates study flashcards. "
            f"Generate exactly 5 concise flashcards for the topic: '{topic}'. "
            f"If additional context is provided, include it: '{details}'.\n"
            f"Return the result as valid JSON with a top-level key 'flashcards'. "
            f"Each flashcard must include 'question' and 'answer'."
        )

        if cls._has_gemini_key():
            try:
                raw = cls._generate_content(prompt, expect_json=True)
                data = cls._parse_json_response(raw)
                cards = data.get("flashcards", [])
                if isinstance(cards, list) and cards:
                    return [
                        {
                            "question": card.get("question", "").strip(),
                            "answer": card.get("answer", "").strip(),
                        }
                        for card in cards
                        if isinstance(card, dict)
                    ]
            except Exception as e:
                print(f"Gemini flashcard error: {e}")

        return cls._fallback_flashcards(topic, details)

    @classmethod
    async def generate_quiz_for_topic(cls, topic: str, details: str = '') -> List[Dict[str, Any]]:
        """
        Generate multiple-choice quiz questions from a topic or content string.
        """
        prompt = (
            f"You are an AI tutor that writes quiz questions. "
            f"Generate exactly 3 multiple-choice questions for the topic: '{topic}'. "
            f"If additional context is provided, include it: '{details}'.\n"
            f"Return valid JSON with a top-level key 'quiz_questions'. "
            f"Each item must include 'question', 'options' (list of 4), and 'correct_answer'."
        )

        if cls._has_gemini_key():
            try:
                raw = cls._generate_content(prompt, expect_json=True)
                data = cls._parse_json_response(raw)
                questions = data.get("quiz_questions", [])
                if isinstance(questions, list) and questions:
                    return [
                        {
                            "question": q.get("question", "").strip(),
                            "options": q.get("options", []) if isinstance(q.get("options", []), list) else [],
                            "correct_answer": q.get("correct_answer", "").strip(),
                        }
                        for q in questions
                        if isinstance(q, dict)
                    ]
            except Exception as e:
                print(f"Gemini quiz error: {e}")

        return cls._fallback_quiz(topic, details)

    @staticmethod
    def _fallback_flashcards(title: str, desc: str) -> List[Dict[str, str]]:
        """
        Procedural generator that matches keywords or generates general academic study cards.
        """
        title_lower = title.lower()
        desc_lower = (desc or "").lower()

        # Keyword mapping
        if "react" in title_lower or "react" in desc_lower:
            return [
                {
                    "question": "What is the purpose of useEffect in React?",
                    "answer": "It allows you to perform side effects in functional components, such as fetching data, subscribing to services, or manually changing the DOM."
                },
                {
                    "question": "What are the rules of Hooks in React?",
                    "answer": "1. Only call Hooks at the top level (not inside loops or conditionals). 2. Only call Hooks from React function components or custom Hooks."
                },
                {
                    "question": "What is state in React?",
                    "answer": "An object that holds information about the component that may change over the lifetime of the component. Changing state triggers a re-render."
                },
                {
                    "question": "Explain the virtual DOM concept.",
                    "answer": "A lightweight in-memory representation of the real DOM. React updates the virtual DOM first, diffs it with the previous state, and makes minimal updates to the real DOM."
                }
            ]
        elif "sql" in title_lower or "database" in title_lower or "sql" in desc_lower:
            return [
                {
                    "question": "What is the difference between INNER JOIN and LEFT JOIN?",
                    "answer": "INNER JOIN returns records that have matching values in both tables. LEFT JOIN returns all records from the left table, and the matched records from the right table (if any, otherwise NULL)."
                },
                {
                    "question": "What is a primary key in database design?",
                    "answer": "A unique identifier for each record in a database table. It must contain unique values and cannot contain NULL values."
                },
                {
                    "question": "Explain the concept of normalization.",
                    "answer": "The process of organizing data in a database to reduce redundancy and improve data integrity, typically by splitting tables and creating relationships."
                },
                {
                    "question": "What does ACID stand for in databases?",
                    "answer": "Atomicity (all or nothing), Consistency (valid state), Isolation (independent transactions), and Durability (permanently saved)."
                }
            ]
        elif "python" in title_lower or "python" in desc_lower:
            return [
                {
                    "question": "What is a decorator in Python?",
                    "answer": "A function that takes another function as an argument, extends its behavior without modifying the original function, and returns a new function."
                },
                {
                    "question": "Explain the difference between lists and tuples.",
                    "answer": "Lists are mutable (can be edited after creation) and defined with square brackets []. Tuples are immutable (cannot be changed) and defined with parentheses ()."
                },
                {
                    "question": "What is list comprehension in Python?",
                    "answer": "A concise and readable syntax for creating new lists from existing iterables. Example: [x*2 for x in numbers if x > 0]."
                },
                {
                    "question": "How does memory management work in Python?",
                    "answer": "Python uses a private heap to manage memory, alongside a built-in Garbage Collector that performs reference counting and detects reference cycles."
                }
            ]
        elif "git" in title_lower or "git" in desc_lower:
            return [
                {
                    "question": "What is the difference between git fetch and git pull?",
                    "answer": "git fetch downloads new commits from remote but doesn't merge them. git pull downloads and immediately merges them into your current active branch."
                },
                {
                    "question": "What is the staging area in Git?",
                    "answer": "A file index where changes are prepared before they are committed to the repository's history."
                },
                {
                    "question": "What is a merge conflict and how do you resolve it?",
                    "answer": "Occurs when changes are made to the same line of a file in different branches. You resolve it by manually editing the conflicted file, choosing which changes to keep, staging, and committing."
                },
                {
                    "question": "Explain git rebase.",
                    "answer": "A process of moving or combining a sequence of commits to a new base commit, creating a clean, linear project history."
                }
            ]
        
        # General fallbacks using title and description
        d_val = desc if desc else "this subject matter"
        return [
            {
                "question": f"What is the primary definition or concept of '{title}'?",
                "answer": f"It focuses on: '{d_val}'. Studying this is essential to master the fundamentals and applications of this topic."
            },
            {
                "question": f"What are 3 core pillars/concepts you should learn regarding '{title}'?",
                "answer": "1. The fundamental definitions and setup. 2. Common use-cases and practical challenges. 3. Best practices, optimization, and integration."
            },
            {
                "question": f"What is a common pitfall when learning '{title}'?",
                "answer": "Focusing purely on high-level theory without writing active code/examples or testing your understanding with quizzes."
            },
            {
                "question": f"How can you apply knowledge of '{title}' in real-world scenarios?",
                "answer": f"By building small projects, analyzing existing implementations, and explaining the mechanics of {title} to peers."
            }
        ]

    @classmethod
    async def chat(cls, messages: List[Dict[str, str]]) -> str:
        """
        Send a conversation to Gemini or fallback to a local assistant message.
        """
        if cls._has_gemini_key():
            try:
                answer = cls._generate_content(messages=messages)
                if answer:
                    return answer
            except Exception as e:
                cls._set_gemini_error("Gemini chat failed.")
                print(f"Gemini chat error: {e}")

        return cls._fallback_chat(messages)

    @staticmethod
    def _fallback_chat(messages: List[Dict[str, str]]) -> str:
        last_user = next(
            (
                AIService._message_value(m, "content")
                for m in reversed(messages)
                if AIService._message_value(m, "role") == "user"
            ),
            None,
        )
        if not last_user:
            return "Hello! I'm your study assistant. Ask me anything about your subjects."
        if any(term in last_user.lower() for term in ["jwt", "json web token", "token"]):
            return (
                "JWT tokens are compact signed strings used to prove claims between a client and server. "
                "A JWT has three parts: a header, a payload, and a signature. The payload stores claims like user id or expiry time, "
                "and the signature lets the server verify the token was not changed. In a login flow, the backend creates a JWT after "
                "valid credentials, the frontend sends it in the Authorization header, and protected routes verify it before returning data."
            )
        if "python" in last_user.lower():
            return "Python is a powerful language for building web apps, automation, and data tools. What would you like to learn next?"
        if "react" in last_user.lower():
            return "React lets you build interactive user interfaces using components and state. Do you want to ask about hooks or props?"
        return "I can help you craft study plans, answer questions, and review topics. Ask me anything."

    @staticmethod
    def _fallback_quiz(title: str, desc: str) -> List[Dict[str, Any]]:
        """
        Procedural generator that matches keywords or generates general academic study quizzes.
        """
        title_lower = title.lower()
        desc_lower = (desc or "").lower()

        if "react" in title_lower or "react" in desc_lower:
            return [
                {
                    "question": "Which React hook is used to perform side effects in functional components?",
                    "options": ["useState", "useEffect", "useContext", "useReducer"],
                    "correct_answer": "useEffect"
                },
                {
                    "question": "Which of the following is true about React state?",
                    "options": [
                        "It is read-only and cannot be changed",
                        "Changing state triggers a re-render of the component",
                        "It must be declared outside of the component",
                        "It is shared automatically across all components in the app"
                    ],
                    "correct_answer": "Changing state triggers a re-render of the component"
                },
                {
                    "question": "What is the primary function of the virtual DOM in React?",
                    "options": [
                        "To store browser history state securely",
                        "To replace HTML entirely with web assembly",
                        "To compare changes and update the real DOM efficiently",
                        "To run React apps without a browser"
                    ],
                    "correct_answer": "To compare changes and update the real DOM efficiently"
                }
            ]
        elif "sql" in title_lower or "database" in title_lower or "sql" in desc_lower:
            return [
                {
                    "question": "Which SQL clause is used to filter group results after applying aggregate functions?",
                    "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"],
                    "correct_answer": "HAVING"
                },
                {
                    "question": "What does a LEFT JOIN return?",
                    "options": [
                        "Only the matching records from both tables",
                        "All records from the left table and matched records from the right table",
                        "All records from the right table and matched records from the left table",
                        "Only the non-matching records from both tables"
                    ],
                    "correct_answer": "All records from the left table and matched records from the right table"
                },
                {
                    "question": "Which constraint ensures that all values in a column are unique and not NULL?",
                    "options": ["FOREIGN KEY", "UNIQUE", "PRIMARY KEY", "CHECK"],
                    "correct_answer": "PRIMARY KEY"
                }
            ]
        elif "python" in title_lower or "python" in desc_lower:
            return [
                {
                    "question": "Which keyword is used to make a function behave as a generator in Python?",
                    "options": ["return", "yield", "generator", "await"],
                    "correct_answer": "yield"
                },
                {
                    "question": "What is the key difference between list and tuple in Python?",
                    "options": [
                        "Lists are mutable while tuples are immutable",
                        "Tuples can only store integers",
                        "Lists are faster to search than tuples",
                        "Tuples use square brackets [] and lists use parentheses ()"
                    ],
                    "correct_answer": "Lists are mutable while tuples are immutable"
                },
                {
                    "question": "Which of the following is NOT a built-in data type in Python?",
                    "options": ["dict", "list", "double", "float"],
                    "correct_answer": "double"
                }
            ]
        elif "git" in title_lower or "git" in desc_lower:
            return [
                {
                    "question": "Which Git command combines remote changes into your local branch and merges them immediately?",
                    "options": ["git fetch", "git pull", "git merge --fetch", "git push"],
                    "correct_answer": "git pull"
                },
                {
                    "question": "What is the purpose of the staging area in Git?",
                    "options": [
                        "To host your code online publicly",
                        "To backup changes directly on the cloud server",
                        "To prepare and review changes before committing them",
                        "To store deleted files indefinitely"
                    ],
                    "correct_answer": "To prepare and review changes before committing them"
                },
                {
                    "question": "Which git command is used to change your active branch?",
                    "options": ["git checkout", "git commit", "git reset", "git status"],
                    "correct_answer": "git checkout"
                }
            ]

        # General fallbacks
        d_val = desc if desc else "the topic"
        return [
            {
                "question": f"When beginning to study '{title}', what should be your primary focal point?",
                "answer": "Memorizing syntactic formulas",
                "options": [
                    f"Understanding the core principles and context of {title}",
                    "Memorizing syntactic formulas",
                    "Skipping basic principles to write production code",
                    "Hiring someone else to write it"
                ],
                "correct_answer": f"Understanding the core principles and context of {title}"
            },
            {
                "question": f"How is a student's retention of '{title}' best consolidated?",
                "options": [
                    "By reading slides repeatedly without practice",
                    f"By applying concepts to small projects and explaining {title} to others",
                    "By deleting the study materials after reading them once",
                    "By memorizing definitions word-for-word"
                ],
                "correct_answer": f"By applying concepts to small projects and explaining {title} to others"
            },
            {
                "question": f"Which of the following describes the description: '{d_val}'?",
                "options": [
                    f"It outlines the context/scope of studying '{title}'",
                    "It is entirely unrelated to the study topic",
                    "It is auto-generated and should be completely ignored",
                    "It is the exact code implementation of the topic"
                ],
                "correct_answer": f"It outlines the context/scope of studying '{title}'"
            }
        ]
