from fastapi import status


class AppException(Exception):
    """Base class for custom application exceptions.

    Subclasses set error_code/error_status/message as class defaults; `detail`
    carries the specific, request-level context for a given raise site.
    """

    error_code: str = "internal_error"
    error_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.message
        super().__init__(self.detail)


class NotFoundException(AppException):
    error_code = "not_found"
    error_status = status.HTTP_404_NOT_FOUND
    message = "Resource not found"


class PdfRenderingException(AppException):
    error_code = "pdf_rendering_error"
    error_status = status.HTTP_503_SERVICE_UNAVAILABLE
    message = "PDF rendering is temporarily unavailable. Please try again shortly."


class DriveUploadException(AppException):
    error_code = "drive_upload_error"
    error_status = status.HTTP_502_BAD_GATEWAY
    message = "Upload to Google Drive failed."
