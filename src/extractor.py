import trafilatura


def extract_text(html: str) -> str | None:
    return trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_recall=True,
    )
