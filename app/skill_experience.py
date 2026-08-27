from app.schemas import CandidateProfile, RawCandidateProfile, Skill


def resolve_skill_experience(raw: RawCandidateProfile) -> CandidateProfile:
    years_by_skill: dict[str, float] = {}

    for job in raw.work_experience:
        for skill_name in job.skills:
            key = skill_name.strip().casefold()
            years_by_skill[key] = years_by_skill.get(key, 0.0) + job.duration

    resolved_skills: list[Skill] = []

    for raw_skill in raw.skills:
        key = raw_skill.name.strip().casefold()

        if raw_skill.stated_years is not None:
            experience = raw_skill.stated_years
        else:
            experience = round(years_by_skill.get(key, 0.0), 1)

        resolved_skills.append(
            Skill(name=raw_skill.name, experience=experience)
        )

    return CandidateProfile(
        personal_info=raw.personal_info,
        work_experience=raw.work_experience,
        educations=raw.educations,
        skills=resolved_skills,
        certificates=raw.certificates,
        language=raw.language,
    )
