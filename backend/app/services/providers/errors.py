class ProviderRequestError(RuntimeError):
    def __init__(
        self,
        *,
        provider: str,
        status_code: int | None,
        code: str,
        message: str,
    ) -> None:
        self.provider = provider
        self.status_code = status_code
        self.code = code
        self.message = message
        status_part = f" HTTP {status_code}" if status_code is not None else ""
        super().__init__(f"{provider}{status_part}: {code} - {message}")
