
# from scraper.utils import jobOffer


def format_job_alert(job: jobOffer) -> str:
    """Build an HTML-formatted Telegram message for a single job offer."""
    lines = [f"🆕 <b>{job.title}</b>", f"🏢 {job.company}"]
    if job.location:
        lines.append(f"📍 {job.location}")
    if job.job_type:
        lines.append(f"🕒 {job.job_type}")
    lines.append(f'<a href="{job.url}">Apply here</a>')
    return "\n".join(lines)