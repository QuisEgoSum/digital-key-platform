from http import HTTPStatus

STATUS_TO_DESCRIPTION = {status.value: status.phrase for status in HTTPStatus}
