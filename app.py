#!/usr/bin/env python3
import os

import aws_cdk as cdk

from techstack.stack_cdk_l1 import StackConstructLevel1
from techstack.stack_cdk_l2 import StackConstructLevel2
from techstack.stack_cdk_l3 import StackConstructLevel3
from techstack.stack_use_custom_reusable import UseCustomReusableStack

app = cdk.App()
StackConstructLevel1(app, "StackConstructLevel1",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)
StackConstructLevel2(app, "StackConstructLevel2",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)
StackConstructLevel3(app, "StackConstructLevel3",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)
UseCustomReusableStack(app, "UseCustomReusableStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
