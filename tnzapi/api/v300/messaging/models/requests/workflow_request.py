from dataclasses import dataclass, field


@dataclass
class WorkflowRequest:
    WorkflowTemplateID: str = None
    Destinations: list = field(default_factory=list)
    Destination: str = None
    ToNumber: str = None
    MainPhone: str = None
    ContactID: str = None
    GroupID: str = None
    MessageID: str = None
    Reference: str = None
    NotificationType: str = None
    WebhookCallbackURL: str = None
    WebhookCallbackFormat: str = None
    SubAccount: str = None
    Department: str = None
    SendTime: str = None
    Timezone: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"WorkflowRequestDTO": WorkflowRequest})

__all__ = ["WorkflowRequest", "WorkflowRequestDTO"]
