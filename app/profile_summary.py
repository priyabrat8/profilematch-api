from app.schemas import CandidateProfile


def build_profile_summary(profile: CandidateProfile) -> str:
    parts: list[str] = []
    total_experience = round(sum(job.duration for job in profile.work_experience), 1)

    parts.append(f"Total professional experience: {total_experience} years")

    if profile.skills:
        skill_str = ", ".join(f"{s.name} ({s.experience} yrs)" for s in profile.skills)
        parts.append(f"Skills: {skill_str}")

    for job in profile.work_experience:
        parts.append(
            f"Worked at {job.company_name} for {job.duration} years. "
            f"Skills used: {', '.join(job.skills) if job.skills else 'not specified'}. "
            f"Summary: {job.summary}"
        )

    for edu in profile.educations:
        parts.append(f"Education: {edu.degree} at {edu.school} ({edu.duration or 'n/a'})")

    if profile.certificates:
        parts.append("Certificates: " + ", ".join(profile.certificates))

    if profile.language:
        parts.append("Languages: " + ", ".join(profile.language))

    return "\n".join(parts)
