TEST_QUESTIONS = [

    # =====================================================
    # 1. BERT - Definition
    # =====================================================

    {
        "question": "What is BERT?",
        "answerable": True,
        "expected_files": ["bert_paper.pdf"],
        "reference_answer": (
            "BERT is a bidirectional Transformer encoder."
        )
    },


    # =====================================================
    # 2. BERT - Technical concept
    # =====================================================

    {
        "question": "What is masked language modeling?",
        "answerable": True,
        "expected_files": ["bert_paper.pdf"],
        "reference_answer": (
            "Masked language modeling is a pre-training task "
            "in which selected tokens are masked and the model "
            "predicts the original tokens using surrounding context."
        )
    },


    # =====================================================
    # 3. AI - Definition
    # =====================================================

    {
        "question": "What is Artificial Intelligence?",
        "answerable": True,
        "expected_files": ["ai_introduction.pdf"],
        "reference_answer": (
            "Artificial Intelligence is the field of building "
            "computational systems capable of performing tasks "
            "that traditionally require human cognition."
        )
    },


    # =====================================================
    # 4. AeroTHON - Eligibility
    # =====================================================

    {
        "question": (
            "What are the eligibility requirements for AeroTHON 2026 team members and teams?"
        ),
        "answerable": True,
        "expected_files": ["aerothon_2026.pdf"],
        "reference_answer": (
            "AeroTHON 2026 teams must consist of undergraduate "
            "or postgraduate students who are SAE India members. "
            "A team must have a minimum of 5 and a maximum of "
            "10 students from multiple disciplines, along with "
            "one faculty advisor."
        )
    },


    # =====================================================
    # 5. AeroTHON - Specific information
    # =====================================================

    {
        "question": "What are the phases of AeroTHON 2026?",
        "answerable": True,
        "expected_files": ["aerothon_2026.pdf"],
        "reference_answer": (
            "AeroTHON 2026 consists of a design and development "
            "phase followed by a flying competition phase."
        )
    },


    # =====================================================
    # 6. Internship - Specific information
    # =====================================================

    {
        "question": "What is the duration of the internship?",
        "answerable": True,
        "expected_files": ["internship_program.pdf"],
        "reference_answer": (
        "The internship duration is June 2026 to August 2026, "
        "and the program is an 8-week internship."
        )
    },


    # =====================================================
    # 7. Internship - Detailed information
    # =====================================================

    {
        "question": "What is the internship structure?",
        "answerable": True,
        "expected_files": ["internship_program.pdf"],
        "reference_answer": (
            "The internship follows a week-wise structured "
            "learning plan covering applications and use cases, "
            "data engineering, machine learning, data preparation, "
            "machine learning mastery, applications and use cases "
            "mastery, and platform administration."
        )
    },


    # =====================================================
    # 8. Internship - Assessment
    # =====================================================

    {
        "question": "How is the final internship grade determined?",
        "answerable": True,
        "expected_files": ["internship_program.pdf"],
        "reference_answer": (
            "The final grade is based on overall performance, "
            "including weekly assessments, project submissions, "
            "and the final assessment test."
        )
    },


    # =====================================================
    # 9. Unanswerable question
    # =====================================================

    {
        "question": "Who invented Python?",
        "answerable": False,
        "expected_files": [],
        "reference_answer": ""
    },


    # =====================================================
    # 10. Unanswerable question
    # =====================================================

    {
        "question": "What is the current stock price of NVIDIA?",
        "answerable": False,
        "expected_files": [],
        "reference_answer": ""
    }

]