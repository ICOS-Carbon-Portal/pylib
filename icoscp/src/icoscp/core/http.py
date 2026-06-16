import json
from urllib import request
from urllib.request import Request, HTTPError, urlopen
from urllib.parse import urlencode
from http.client import HTTPResponse, HTTPMessage
from typing import Any, Literal, IO

Method = Literal["GET", "POST"]

def http_request(
	url: str,
	error_hint: str,
	method: Method = "GET",
	headers: dict[str, str] = {},
	data: str | dict[str, Any] | None = None
) -> HTTPResponse:

	h = {k.lower(): v for k, v in headers.items()}
	cont_type_h = "content-type"

	class NoRedirect(request.HTTPRedirectHandler):
		def redirect_request(self, req: Request, fp: IO[bytes], code: int, msg: str, headers: HTTPMessage, newurl: str) -> Request | None:
			return None

	opener = request.build_opener(NoRedirect)
	request.install_opener(opener)

	if isinstance(data, str):
		if not cont_type_h in h:
			h[cont_type_h] = "text/plain"
		d = bytes(data, encoding="utf-8")
	elif isinstance(data, dict):
		if h.get(cont_type_h) == "application/x-www-form-urlencoded":
			d = bytes(urlencode(data), encoding="utf-8")
		else:
			h[cont_type_h] = "application/json"
			d = json.dumps(data).encode("utf-8")
	else:
		d = None

	req = Request(url=url, data=d, headers=h, method=method)

	try:
		return urlopen(req)
	except HTTPError as err:
		resp_text = err.read().decode()
		if err.status is not None and err.status >= 300 and err.status < 400 and "licence" in resp_text.lower():
			resp_text = "Accepting data licence in your user profile is required for data downloads"
		msg = f"{error_hint} at {url} problem, HTTP response code: {err.status}, response: {resp_text}"
		raise Exception(msg) from None

