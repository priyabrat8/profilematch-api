def _normalize(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def _skill_score(required_skills: list[str], candidate_skills: list[dict]) -> float:
    if not required_skills:
        return 1.0

    candidate_names = {_normalize(skill.get("name", "")) for skill in candidate_skills}
    matched = sum(1 for skill in required_skills if _normalize(skill) in candidate_names)
    return matched / len(required_skills)


def _experience_score(minimum: float | None, maximum: float | None, value: float) -> float:
    if minimum is None and maximum is None:
        return 1.0
    if minimum is not None and value < minimum:
        return 0.0
    if maximum is not None and value > maximum:
        return 0.5
    return 1.0


def rank_candidates(candidates: list[dict], requirements) -> list[dict]:
    ranked = []

    for candidate in candidates:
        similarity = max(0.0, 1.0 - float(candidate["distance"]))
        skill_score = _skill_score(requirements.skills, candidate["skills"])
        experience_score = _experience_score(
            requirements.minimum_total_experience,
            requirements.maximum_total_experience,
            float(candidate["total_experience_years"] or 0),
        )

        score = (
            similarity * 0.40
            + skill_score * 0.35
            + experience_score * 0.25
        ) * 100

        candidate = dict(candidate)
        candidate["match_score"] = round(score, 1)
        candidate["skill_match_score"] = round(skill_score * 100, 1)
        candidate["semantic_score"] = round(similarity * 100, 1)
        candidate["experience_match_score"] = round(experience_score * 100, 1)
        ranked.append(candidate)

    return sorted(ranked, key=lambda item: item["match_score"], reverse=True)
