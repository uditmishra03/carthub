from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_rds as rds,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct
import json


class MicroservicesStack(Stack):
    """CDK Stack for 3-tier microservices architecture with VPC."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC with 3-tier architecture
        self.vpc = self._create_vpc()
        
        # Create security groups
        self.security_groups = self._create_security_groups()
        
        # Create RDS database in private subnet
        self.database = self._create_database()
        
        # Create ECS cluster
        self.cluster = self._create_ecs_cluster()
        
        # Create backend service
        self.backend_service = self._create_backend_service()
        
        # Create frontend service
        self.frontend_service = self._create_frontend_service()
        
        # Create outputs
        self._create_outputs()

    def _create_vpc(self) -> ec2.Vpc:
        """Create VPC with 3-tier subnet configuration."""
        vpc = ec2.Vpc(
            self, "ShoppingCartVPC",
            vpc_name="shopping-cart-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            subnet_configuration=[
                # Public subnet for web tier (ALB, NAT Gateway)
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                # Private subnet for application tier (Backend services)
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                # Isolated subnet for database tier
                ec2.SubnetConfiguration(
                    name="DatabaseSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )

        # Enable VPC Flow Logs for monitoring
        vpc_flow_log_role = iam.Role(
            self, "VPCFlowLogRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com")
        )

        vpc_flow_log_group = logs.LogGroup(
            self, "VPCFlowLogGroup",
            log_group_name="/aws/vpc/flowlogs",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY
        )

        vpc_flow_log_group.grant_write(vpc_flow_log_role)

        ec2.FlowLog(
            self, "VPCFlowLog",
            resource_type=ec2.FlowLogResourceType.from_vpc(vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(
                vpc_flow_log_group, vpc_flow_log_role
            )
        )

        return vpc

    def _create_security_groups(self) -> dict:
        """Create security groups for each tier."""
        security_groups = {}

        # ALB Security Group (Public tier)
        security_groups['alb'] = ec2.SecurityGroup(
            self, "ALBSecurityGroup",
            vpc=self.vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=False
        )
        
        security_groups['alb'].add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP from internet"
        )
        
        security_groups['alb'].add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443),
            "Allow HTTPS from internet"
        )

        # Frontend Security Group (Public tier)
        security_groups['frontend'] = ec2.SecurityGroup(
            self, "FrontendSecurityGroup",
            vpc=self.vpc,
            description="Security group for Frontend service",
            allow_all_outbound=True
        )
        
        security_groups['frontend'].add_ingress_rule(
            security_groups['alb'],
            ec2.Port.tcp(80),
            "Allow HTTP from ALB"
        )

        # Backend Security Group (Private tier)
        security_groups['backend'] = ec2.SecurityGroup(
            self, "BackendSecurityGroup",
            vpc=self.vpc,
            description="Security group for Backend service",
            allow_all_outbound=True
        )
        
        security_groups['backend'].add_ingress_rule(
            security_groups['frontend'],
            ec2.Port.tcp(8000),
            "Allow API calls from Frontend"
        )

        # Database Security Group (Database tier)
        security_groups['database'] = ec2.SecurityGroup(
            self, "DatabaseSecurityGroup",
            vpc=self.vpc,
            description="Security group for Database",
            allow_all_outbound=False
        )
        
        security_groups['database'].add_ingress_rule(
            security_groups['backend'],
            ec2.Port.tcp(5432),
            "Allow PostgreSQL from Backend"
        )

        return security_groups

    def _create_database(self) -> rds.DatabaseInstance:
        """Create RDS PostgreSQL database in isolated subnet."""
        # Create database credentials in Secrets Manager
        db_credentials = secretsmanager.Secret(
            self, "DatabaseCredentials",
            description="Credentials for Shopping Cart Database",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "cartadmin"}),
                generate_string_key="password",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"\\",
                password_length=32
            )
        )

        # Create DB subnet group
        db_subnet_group = rds.SubnetGroup(
            self, "DatabaseSubnetGroup",
            description="Subnet group for Shopping Cart Database",
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )
        )

        # Create RDS instance
        database = rds.DatabaseInstance(
            self, "ShoppingCartDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            credentials=rds.Credentials.from_secret(db_credentials),
            database_name="shoppingcart",
            vpc=self.vpc,
            subnet_group=db_subnet_group,
            security_groups=[self.security_groups['database']],
            backup_retention=Duration.days(7),
            deletion_protection=False,  # Set to True for production
            removal_policy=RemovalPolicy.DESTROY,  # For development only
            multi_az=False,  # Set to True for production
            storage_encrypted=True,
            monitoring_interval=Duration.seconds(60),
            enable_performance_insights=True,
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT
        )

        # Store database endpoint in Parameter Store
        ssm.StringParameter(
            self, "DatabaseEndpoint",
            parameter_name="/shoppingcart/database/endpoint",
            string_value=database.instance_endpoint.hostname
        )

        return database

    def _create_ecs_cluster(self) -> ecs.Cluster:
        """Create ECS cluster for microservices."""
        cluster = ecs.Cluster(
            self, "ShoppingCartCluster",
            cluster_name="shopping-cart-cluster",
            vpc=self.vpc,
            container_insights=True
        )

        return cluster

    def _create_backend_service(self) -> ecs_patterns.ApplicationLoadBalancedFargateService:
        """Create backend service in private subnet."""
        # Create task definition
        task_definition = ecs.FargateTaskDefinition(
            self, "BackendTaskDefinition",
            memory_limit_mib=512,
            cpu=256
        )

        # Add container to task definition
        backend_container = task_definition.add_container(
            "BackendContainer",
            image=ecs.ContainerImage.from_asset(
                "../backend",
                file="Dockerfile"
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="backend",
                log_group=logs.LogGroup(
                    self, "BackendLogGroup",
                    log_group_name="/ecs/shopping-cart-backend",
                    retention=logs.RetentionDays.ONE_WEEK,
                    removal_policy=RemovalPolicy.DESTROY
                )
            ),
            environment={
                "DATABASE_ENDPOINT": self.database.instance_endpoint.hostname,
                "DATABASE_NAME": "shoppingcart",
                "DATABASE_PORT": "5432"
            },
            secrets={
                "DATABASE_CREDENTIALS": ecs.Secret.from_secrets_manager(
                    secretsmanager.Secret.from_secret_complete_arn(
                        self, "BackendDBSecret",
                        secret_complete_arn=self.database.secret.secret_arn
                    )
                )
            }
        )

        backend_container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)
        )

        # Create Fargate service with internal load balancer
        backend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "BackendService",
            cluster=self.cluster,
            task_definition=task_definition,
            public_load_balancer=False,  # Internal ALB
            listener_port=8000,
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.security_groups['backend']],
            desired_count=2,
            enable_logging=True
        )

        # Grant database access to backend task
        self.database.secret.grant_read(backend_service.task_definition.task_role)

        return backend_service

    def _create_frontend_service(self) -> ecs_patterns.ApplicationLoadBalancedFargateService:
        """Create frontend service in public subnet."""
        # Create task definition
        task_definition = ecs.FargateTaskDefinition(
            self, "FrontendTaskDefinition",
            memory_limit_mib=512,
            cpu=256
        )

        # Add container to task definition
        frontend_container = task_definition.add_container(
            "FrontendContainer",
            image=ecs.ContainerImage.from_asset(
                "../frontend",
                file="Dockerfile"
            ),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="frontend",
                log_group=logs.LogGroup(
                    self, "FrontendLogGroup",
                    log_group_name="/ecs/shopping-cart-frontend",
                    retention=logs.RetentionDays.ONE_WEEK,
                    removal_policy=RemovalPolicy.DESTROY
                )
            ),
            environment={
                "BACKEND_URL": f"http://{self.backend_service.load_balancer.load_balancer_dns_name}:8000"
            }
        )

        frontend_container.add_port_mappings(
            ecs.PortMapping(container_port=80, protocol=ecs.Protocol.TCP)
        )

        # Create Fargate service with public load balancer
        frontend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FrontendService",
            cluster=self.cluster,
            task_definition=task_definition,
            public_load_balancer=True,  # Public ALB
            listener_port=80,
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            security_groups=[self.security_groups['frontend']],
            desired_count=2,
            enable_logging=True
        )

        return frontend_service

    def _create_outputs(self) -> None:
        """Create CloudFormation outputs."""
        CfnOutput(
            self, "VPCId",
            value=self.vpc.vpc_id,
            description="VPC ID"
        )

        CfnOutput(
            self, "DatabaseEndpoint",
            value=self.database.instance_endpoint.hostname,
            description="Database endpoint"
        )

        CfnOutput(
            self, "FrontendURL",
            value=f"http://{self.frontend_service.load_balancer.load_balancer_dns_name}",
            description="Frontend application URL"
        )

        CfnOutput(
            self, "BackendURL",
            value=f"http://{self.backend_service.load_balancer.load_balancer_dns_name}:8000",
            description="Backend API URL (internal)"
        )
