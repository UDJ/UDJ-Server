from django.http import HttpResponse, HttpResponseNotFound

class HttpJSONResponse(HttpResponse):

  def __init__(self, content, status=200):
    super(HttpJSONResponse, self).__init__(content,
                                           status=status,
                                           content_type="text/json; charset=utf-8")

class HttpMissingResponse(HttpResponseNotFound):

  def __init__(self, missing_resource):
    super(HttpMissingResponse, self).__init__()
    self[MISSING_RESOURCE_HEADER] = missing_resource
