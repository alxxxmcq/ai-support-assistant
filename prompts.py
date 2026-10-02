def build_client_response(client_message: str, knowledge_answer: str) -> str:
    """
    Builds a polite customer-facing response.

    In a production version this function can be replaced by an LLM call.
    """
    return (
        "Здравствуйте! Спасибо за обращение. "
        f"{knowledge_answer} "
        "Если останутся вопросы, я помогу уточнить детали."
    )


def build_manager_tip(client_message: str, upsell_hint: str) -> str:
    """
    Builds a short recommendation for a sales/support manager.

    In a production version this function can be replaced by an LLM prompt.
    """
    return (
        "Подсказка менеджеру: "
        f"{upsell_hint}"
    )
