import aws_cdk as cdk
from constructs import Construct
from aws_cdk.aws_ec2 import (
    CfnSecurityGroup, CfnVPC, CfnSubnet, 
    CfnInstance, CfnInternetGateway, CfnVPCGatewayAttachment, 
)
from aws_cdk.aws_elasticloadbalancingv2 import (
    CfnLoadBalancer, CfnListener, CfnTargetGroup
)
class StackConstructLevel1(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ****** L1 EXAMPLE - ALB WITH EC2 INSTANCES ****** #
        # VPC
        vpc = CfnVPC(self, "DojoVPC",
            cidr_block="10.0.0.0/16"
        )

        # IGW
        igw = CfnInternetGateway(self, "DojoIGW")
        CfnVPCGatewayAttachment(self, "DojoAttachIGW",
            vpc_id=vpc.attr_vpc_id,
            internet_gateway_id=igw.attr_internet_gateway_id
        )

        # Subnets
        subnet1 = CfnSubnet(self, "DojoSubnet1",
            vpc_id=vpc.attr_vpc_id,
            cidr_block="10.0.1.0/24",
            availability_zone=cdk.Fn.select(0, cdk.Fn.get_azs()),
            map_public_ip_on_launch=True
        )
        # RT for Subnet
        route_table = cdk.aws_ec2.CfnRouteTable(self, "DojoPublicRouteTable",
            vpc_id=vpc.attr_vpc_id
        )

        # RT for IGW
        cdk.aws_ec2.CfnRoute(self, "DojoPublicRoute",
            route_table_id=route_table.attr_route_table_id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.attr_internet_gateway_id
        )

        # Associate RT with subnet
        cdk.aws_ec2.CfnSubnetRouteTableAssociation(self, "DojoPublicSubnetRouteTableAssociation",
            subnet_id=subnet1.attr_subnet_id,
            route_table_id=route_table.attr_route_table_id
        )
        # Another subnet
        subnet2 = CfnSubnet(self, "DojoSubnet2",
            vpc_id=vpc.attr_vpc_id,
            cidr_block="10.0.3.0/24",
            availability_zone=cdk.Fn.select(1, cdk.Fn.get_azs())
        )

        # EC2 SG
        ec2_security_group = CfnSecurityGroup(self, "DojoInstanceSG",
        group_description="Allow HTTP from ALB",
        vpc_id=vpc.attr_vpc_id,
        security_group_ingress=[
            {
                'ipProtocol': 'tcp',
                'fromPort': 80,
                'toPort': 80,
                'cidrIp': '0.0.0.0/0'
            },
        ]
        )

        # ALB SG
        alb_security_group = CfnSecurityGroup(self, "DojoALBSG",
        group_description="Allow HTTP from the internet",
        vpc_id=vpc.attr_vpc_id,
        security_group_ingress=[
            {
                'ipProtocol': 'tcp',
                'fromPort': 80,
                'toPort': 80,
                'cidrIp': '0.0.0.0/0'
            }
        ]
        )

        # EC2
        user_data_cmds = """#!/bin/bash
        yum update -y
        yum install -y httpd
        systemctl start httpd
        systemctl enable httpd
        echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
        """
        ec2_instance = CfnInstance(self, "DojoEc2",
        image_id="ami-053a45fff0a704a47",
        instance_type="t2.micro",
        user_data=cdk.Fn.base64(user_data_cmds),
        network_interfaces=[
            cdk.aws_ec2.CfnInstance.NetworkInterfaceProperty(
                associate_public_ip_address=True,
                subnet_id=subnet1.attr_subnet_id,
                device_index='0',
                group_set=[ec2_security_group.attr_group_id] 
            )
        ]
        )

        # ALB
        load_balancer = CfnLoadBalancer(self, "DojoALB",
        subnets=[subnet1.attr_subnet_id, subnet2.attr_subnet_id],
        security_groups=[alb_security_group.attr_group_id],
        scheme="internet-facing",
        type="application"
        )

        # ALB target group
        target_group = CfnTargetGroup(self, "DojoTG",
            vpc_id=vpc.attr_vpc_id,
            protocol='HTTP',
            port=80,
            target_type='instance',
            targets=[
                {
                    'id': ec2_instance.attr_instance_id
                }
            ],
            health_check_protocol='HTTP',
            health_check_port='80',
            health_check_path='/',
            health_check_interval_seconds=30,
            health_check_timeout_seconds=5,
            healthy_threshold_count=2,
            unhealthy_threshold_count=2
        )

        # ALB Listener
        listener = CfnListener(self, "DojoListener",
            load_balancer_arn=load_balancer.attr_load_balancer_arn,
            protocol='HTTP',
            port=80,
            default_actions=[{
                'type': 'forward',
                'targetGroupArn': target_group.attr_target_group_arn
            }]
        )
