from icoscp_core.metacore import SpatioTemporalMeta


class UriValueError(ValueError):
    # Todo: fix this according to the FormatValueError class.
    def __init__(self,
                 message: str = 'Invalid data object uri value') -> None:
        super().__init__(message)
        return


class FormatValueError(ValueError):
    def __init__(self, unsupported_format: str) -> None:
        message = (
            f"Unsupported citation format: {unsupported_format}\n"
            f"Please use one of the following instead: 'plain', "
            f"'bibtex', or 'ris'."
        )
        super().__init__(message)
        return


class MetaValueError(ValueError):
    def __init__(self) -> None:
        message = "Column metadata is not available for this object."
        super().__init__(message)
        return


class MetaTypeError(TypeError):
    def __init__(self, unsupported_type: SpatioTemporalMeta,
                 caller: str) -> None:
        message = (
            f"{type(unsupported_type)} does not support the "
            f"'{caller}' call."
        )
        super().__init__(message)
        return
