TICKET_HEADER = "X-Udj-Ticket-Hash"
MISSING_RESOURCE_HEADER = "X-Udj-Missing-Resource"
CONFLICT_RESOURCE_HEADER = "X-Udj-Conflict-Resource"
MISSING_REASON_HEADER = "X-Udj-Missing-Reason"
FORBIDDEN_REASON_HEADER = "X-Udj-Forbidden-Reason"
NOT_ACCEPTABLE_REASON_HEADER = "X-Udj-Not-Acceptable-Reason"

DJANGO_TICKET_HEADER = "HTTP_X_UDJ_TICKET_HASH"

EXPOSED_HEADERS = [TICKET_HEADER, MISSING_RESOURCE_HEADER, CONFLICT_RESOURCE_HEADER,
                   MISSING_REASON_HEADER, FORBIDDEN_REASON_HEADER, NOT_ACCEPTABLE_REASON_HEADER]

ALLOWED_HEADERS = [TICKET_HEADER, 'Content-Type']
