from aws_cdk import Stack
from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)
from aws_cdk.aws_elasticloadbalancingv2_targets import InstanceTarget

class StackConstructLevel2(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # ******** L2 Example - ALB/EC2 ************** #
        vpc = ec2.Vpc(self, "DojoVPC")

        # SG
        security_group = ec2.SecurityGroup(self, "DojoSG",
            vpc=vpc,
            description="Allow HTTP",
            allow_all_outbound=True
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP from anywhere"
        )

        # EC2 instance
        ec2_instance = ec2.Instance(self, "DojoEc2",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
            security_group=security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # EC2 User data
        ec2_instance.user_data.add_commands("yum update -y","yum install -y httpd","systemctl start httpd","systemctl enable httpd","echo \"<h1>Hello World from $(hostname -f)</h1>\" > /var/www/html/index.html")

        # ALB
        alb = elbv2.ApplicationLoadBalancer(self, "DojoALB",
            vpc=vpc,
            internet_facing=True,
            security_group=security_group
        )

        # Listener
        listener = alb.add_listener("DojoListener",
            port=80,
            open=True
        )

        # Target Group
        listener.add_targets("DojoTargetGroup",
            port=80,
            targets=[InstanceTarget(ec2_instance)]
        )
