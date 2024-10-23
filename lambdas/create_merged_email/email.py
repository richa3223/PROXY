from dataclasses import dataclass
from json import dumps

from jinja2 import Environment, select_autoescape

env = Environment(autoescape=select_autoescape())


@dataclass
class Email:
    email_subject: str
    email_body: str

    def to_json(self) -> str:
        return dumps(
            {
                "email_subject": self.email_subject,
                "email_body": self.email_body,
            }
        )

    def replace_with_variables(self, values_to_replace: dict) -> None:
        def replace_with_jinja(attribute: str) -> str:
            template = env.from_string(attribute)
            return template.render(**values_to_replace)

        self.email_subject = replace_with_jinja(self.email_subject)
        self.email_body = replace_with_jinja(self.email_body)
