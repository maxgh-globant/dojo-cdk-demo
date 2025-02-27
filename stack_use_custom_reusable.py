from aws_cdk import Stack
from constructs import Construct
from techstack.stack_custom_reusable import CustomReusableStack

class UseCustomReusableStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Tags
        tags = [
            {"key": "Environment", "value": "Development"},
            {"key": "Project", "value": "TechStack"}
            ]

        # Reusable Stack
        elb_ec2 = CustomReusableStack(self, "MyWebServer",
            ec2_instance_type="t2.micro",
            tags=tags
        )
