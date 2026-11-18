
"""Explainable rule-based profile-to-project matching."""

import re

WEIGHTS = {
    "skills": 0.30,
    "role": 0.15,
    "interests": 0.10,
    "experience": 0.10,
    "availability": 0.10,
    "goals": 0.10,
    "work_preference": 0.05,
    "contribution": 0.10,
}


def tokens(value):
    return {
        item.strip().lower()
        for item in re.split(r"[,;/\n]+", value or "")
        if item.strip()
    }


def overlap_score(user_value, project_value):
    user_tokens = tokens(user_value)
    project_tokens = tokens(project_value)

    if not project_tokens:
        return 0.5

    if not user_tokens:
        return 0.0

    return len(user_tokens & project_tokens) / len(project_tokens)


def text_similarity(a, b):
    first = tokens(a)
    second = tokens(b)

    if not first or not second:
        return 0.5

    return len(first & second) / len(first | second)


def match_candidate(user, project):
    scores = {}

    # 1. Skills matching
    common_skills = tokens(user.skills) & tokens(project.required_skills)
    scores["skills"] = overlap_score(
        user.skills, project.required_skills
    )

    # 2. Role matching
    user_role = (user.preferred_role or "").strip().lower()
    project_roles = tokens(project.roles_needed)

    scores["role"] = (
        1.0 if user_role and user_role in project_roles
        else 0.5 if not project_roles
        else 0.0
    )

    # 3. Interests matching
    scores["interests"] = text_similarity(
        user.interests, project.interests
    )

    # 4. Experience matching
    levels = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    user_level = levels.get((user.experience or "").lower(), 1)
    project_level = levels.get((project.experience or "").lower(), 1)

    scores["experience"] = max(
        0.0, 1 - abs(user_level - project_level) / 2
    )

    # 5. Availability matching
    user_availability = (user.availability or "").lower()
    project_availability = (project.availability or "").lower()

    scores["availability"] = (
        1.0 if user_availability == project_availability
        or "flexible" in (user_availability, project_availability)
        else 0.4
    )

    # 6. Goals matching
    scores["goals"] = text_similarity(
        user.goals, project.goals
    )

    # 7. Work preference matching
    scores["work_preference"] = (
        1.0 if (user.work_preference or "").lower()
        == (project.work_preference or "").lower()
        else 0.4
    )

    # 8. Contribution matching
    scores["contribution"] = 1.0 if common_skills else 0.0

    total = sum(
        scores[key] * WEIGHTS[key]
        for key in WEIGHTS
    ) * 100

    reasons = []

    if common_skills:
        reasons.append(
            "Matching skills: " + ", ".join(sorted(common_skills))
        )

    if scores["role"] == 1.0:
        reasons.append("Your preferred role matches a required role")

    if scores["interests"] >= 0.5:
        reasons.append("Your interests overlap with this project")

    if scores["experience"] == 1.0:
        reasons.append("Your experience level matches")

    if scores["availability"] == 1.0:
        reasons.append("Your availability is compatible")

    if not reasons:
        reasons.append(
            "Complete your profile to improve matching suggestions"
        )

    return round(total), scores, reasons
