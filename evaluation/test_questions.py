TEST_QUESTIONS = [

    # =========================================================
    # 1. BASIC FACTUAL QUESTIONS
    # =========================================================

    {
        "question": "What is BERT?",
        "answerable": True,
        "reference_answer":
            "BERT is a bidirectional Transformer encoder."
    },

    {
        "question": "What is masked language modeling?",
        "answerable": True,
        "reference_answer":
            "Masked language modeling is a pre-training task where selected tokens are masked and the model predicts the original tokens using surrounding context."
    },

    {
        "question": "What is Artificial Intelligence?",
        "answerable": True,
        "reference_answer":
            "Artificial Intelligence is the field of building computational systems capable of performing tasks that traditionally require human cognition."
    },


    # =========================================================
    # 2. BERT - SPECIFIC QUESTIONS
    # =========================================================

    {
        "question": "What is the purpose of the [CLS] token in BERT?",
        "answerable": True,
        "reference_answer":
            "The [CLS] token is used as the aggregate sequence representation for classification tasks."
    },

    {
        "question": "What is the purpose of the [SEP] token in BERT?",
        "answerable": True,
        "reference_answer":
            "The [SEP] token is used to separate or bound sentences in BERT input sequences."
    },

    {
        "question": "What is the maximum context window of BERT described in the document?",
        "answerable": True,
        "reference_answer":
            "The maximum context window described for BERT is 512 tokens."
    },


    # =========================================================
    # 3. AEROTHON - ELIGIBILITY
    # =========================================================

    {
        "question":
            "What are the eligibility requirements for AeroTHON 2026 team members and teams?",
        "answerable": True,
        "reference_answer":
            "Team members must be undergraduate or postgraduate students and every student must be a SAE India member. A team can have a minimum of 5 and maximum of 10 students from multiple disciplines with one faculty advisor. Faculty membership is advised but not mandatory."
    },

    {
        "question":
            "How many students can be part of an AeroTHON 2026 team?",
        "answerable": True,
        "reference_answer":
            "An AeroTHON 2026 team can have a minimum of 5 and a maximum of 10 students."
    },

    {
        "question":
            "What membership is required for AeroTHON 2026 student participants?",
        "answerable": True,
        "reference_answer":
            "Every student participant must be a member of SAE India."
    },

    {
        "question":
            "Can a university nominate multiple AeroTHON 2026 teams?",
        "answerable": True,
        "reference_answer":
            "Yes. A university or institute can nominate multiple teams, provided the teams meet the requirements and work independently."
    },


    # =========================================================
    # 4. AEROTHON - REGISTRATION
    # =========================================================

    {
        "question":
            "What is the registration fee for AeroTHON 2026?",
        "answerable": True,
        "reference_answer":
            "The registration fee is Rs. 20,000 per team, excluding 18% GST."
    },

    {
        "question":
            "What are the phases of AeroTHON 2026?",
        "answerable": True,
        "reference_answer":
            "AeroTHON 2026 has Phase 1, Design Report and Presentation, followed by Phase 2, the Flying Competition."
    },

    {
        "question":
            "What happens in Phase 1 of AeroTHON 2026?",
        "answerable": True,
        "reference_answer":
            "Phase 1 involves design reports and presentations. Innovative designs are evaluated by industry and academic experts, and top-performing teams are shortlisted for Phase 2."
    },

    {
        "question":
            "What is required from qualified teams during the flying competition?",
        "answerable": True,
        "reference_answer":
            "Qualified teams are required to build an Uncrewed Aircraft System and successfully complete the missions described in the rulebook during the flying competition."
    },


    # =========================================================
    # 5. AEROTHON - DESIGN REQUIREMENTS
    # =========================================================

    {
        "question":
            "What type of UAS is allowed in AeroTHON 2026 Track 1?",
        "answerable": True,
        "reference_answer":
            "Track 1 allows multirotor UASs."
    },

    {
        "question":
            "What is the maximum take-off weight specified for the AeroTHON 2026 UAS?",
        "answerable": True,
        "reference_answer":
            "The specified maximum take-off weight is 2 kg."
    },

    {
        "question":
            "What is the payload capacity requirement for the AeroTHON 2026 UAS?",
        "answerable": True,
        "reference_answer":
            "The payload capacity requirement is 100 grams."
    },


    # =========================================================
    # INTERNSHIP QUESTIONS
    # =========================================================

    {
        "question": "What is the duration of the internship?",
        "answerable": True,
        "reference_answer":
            "The internship is an 8-week program running from June 2026 to August 2026."
    },

    {
        "question": "What is the structure of the internship?",
        "answerable": True,
        "reference_answer":
            "The internship follows a week-wise structured learning plan over 8 weeks. It includes weekly assessments, project documentation and assignments for certain modules, and a Final Assessment Test in the final week."
    },

    {
        "question": "How is the final internship grade determined?",
        "answerable": True,
        "reference_answer":
            "The final grade is based on overall performance, including weekly assessments, project submissions, and the final assessment test."
    },



    # =========================================================
    # 7. PARAPHRASED QUESTIONS
    # =========================================================

    {
        "question":
            "How many participants are allowed in one AeroTHON team?",
        "answerable": True,
        "reference_answer":
            "An AeroTHON team can contain between 5 and 10 students."
    },

    {
        "question":
            "What qualifications must students have to participate in AeroTHON 2026?",
        "answerable": True,
        "reference_answer":
            "Students must be undergraduate or postgraduate students and must be members of SAE India."
    },

    {
        "question":
            "What does the first stage of the AeroTHON competition involve?",
        "answerable": True,
        "reference_answer":
            "The first stage involves a design report and presentation, with designs evaluated by industry and academic experts."
    },
    {
    "question": "How long does the EduSkills internship program last?",
    "answerable": True,
    "reference_answer":
        "The EduSkills internship program lasts 8 weeks, from June 2026 to August 2026."
    },

    {
        "question": "What factors are used to calculate the internship grade?",
        "answerable": True,
        "reference_answer":
            "The final grade is based on weekly assessments, project submissions, and the final assessment test."
    },


    # =========================================================
    # 8. UNANSWERABLE / ABSTENTION QUESTIONS
    # =========================================================

    {
        "question": "Who invented Python?",
        "answerable": False,
        "reference_answer": ""
    },

    {
        "question": "What is the population of Japan?",
        "answerable": False,
        "reference_answer": ""
    },

    {
        "question": "What is the weather today in Coimbatore?",
        "answerable": False,
        "reference_answer": ""
    },

    {
        "question": "Who is the current CEO of Microsoft?",
        "answerable": False,
        "reference_answer": ""
    }

    ]