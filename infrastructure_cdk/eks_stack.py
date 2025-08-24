from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_rds as rds,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,
    aws_logs as logs,
    aws_ecr as ecr,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct
import json


class EKSMicroservicesStack(Stack):
    """CDK Stack for EKS-based microservices architecture."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC for EKS
        self.vpc = self._create_vpc()
        
        # Create ECR repositories
        self.ecr_repos = self._create_ecr_repositories()
        
        # Create RDS database
        self.database = self._create_database()
        
        # Create EKS cluster
        self.cluster = self._create_eks_cluster()
        
        # Create Kubernetes resources
        self._create_kubernetes_resources()
        
        # Create outputs
        self._create_outputs()

    def _create_vpc(self) -> ec2.Vpc:
        """Create VPC optimized for EKS."""
        vpc = ec2.Vpc(
            self, "EKSShoppingCartVPC",
            vpc_name="eks-shopping-cart-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=3,  # EKS works better with 3 AZs
            subnet_configuration=[
                # Public subnets for load balancers and NAT gateways
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                # Private subnets for EKS worker nodes
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                # Isolated subnets for database
                ec2.SubnetConfiguration(
                    name="DatabaseSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )

        # Tag subnets for EKS
        for subnet in vpc.public_subnets:
            subnet.node.add_metadata("kubernetes.io/role/elb", "1")
        
        for subnet in vpc.private_subnets:
            subnet.node.add_metadata("kubernetes.io/role/internal-elb", "1")

        # Enable VPC Flow Logs
        vpc_flow_log_role = iam.Role(
            self, "VPCFlowLogRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com")
        )

        vpc_flow_log_group = logs.LogGroup(
            self, "VPCFlowLogGroup",
            log_group_name="/aws/vpc/eks-flowlogs",
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

    def _create_ecr_repositories(self) -> dict:
        """Create ECR repositories for container images."""
        repos = {}
        
        # Frontend repository
        repos['frontend'] = ecr.Repository(
            self, "FrontendRepository",
            repository_name="shopping-cart-frontend",
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=10,
                    rule_priority=1,
                    description="Keep only 10 images"
                )
            ],
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Backend repository
        repos['backend'] = ecr.Repository(
            self, "BackendRepository",
            repository_name="shopping-cart-backend",
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=10,
                    rule_priority=1,
                    description="Keep only 10 images"
                )
            ],
            removal_policy=RemovalPolicy.DESTROY
        )
        
        return repos

    def _create_database(self) -> rds.DatabaseInstance:
        """Create RDS PostgreSQL database."""
        # Create database security group
        db_security_group = ec2.SecurityGroup(
            self, "DatabaseSecurityGroup",
            vpc=self.vpc,
            description="Security group for PostgreSQL database",
            allow_all_outbound=False
        )

        # Create database credentials
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
            security_groups=[db_security_group],
            backup_retention=Duration.days(7),
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY,
            multi_az=False,  # Set to True for production
            storage_encrypted=True,
            monitoring_interval=Duration.seconds(60),
            enable_performance_insights=True,
            performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT
        )

        # Store database connection info in Parameter Store
        ssm.StringParameter(
            self, "DatabaseEndpoint",
            parameter_name="/shoppingcart/database/endpoint",
            string_value=database.instance_endpoint.hostname
        )

        ssm.StringParameter(
            self, "DatabasePort",
            parameter_name="/shoppingcart/database/port",
            string_value="5432"
        )

        ssm.StringParameter(
            self, "DatabaseName",
            parameter_name="/shoppingcart/database/name",
            string_value="shoppingcart"
        )

        return database

    def _create_eks_cluster(self) -> eks.Cluster:
        """Create EKS cluster with managed node groups."""
        # Create EKS cluster role
        cluster_role = iam.Role(
            self, "EKSClusterRole",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy")
            ]
        )

        # Create node group role
        node_role = iam.Role(
            self, "EKSNodeRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        # Add additional permissions for accessing secrets and parameters
        node_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue",
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath"
                ],
                resources=["*"]
            )
        )

        # Create EKS cluster
        cluster = eks.Cluster(
            self, "ShoppingCartEKSCluster",
            cluster_name="shopping-cart-cluster",
            version=eks.KubernetesVersion.V1_28,
            vpc=self.vpc,
            vpc_subnets=[ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            )],
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            role=cluster_role,
            default_capacity=0,  # We'll add managed node groups
            output_cluster_name=True,
            output_config_command=True
        )

        # Add managed node group
        cluster.add_nodegroup_capacity(
            "DefaultNodeGroup",
            instance_types=[
                ec2.InstanceType("t3.medium"),
                ec2.InstanceType("t3.large")
            ],
            min_size=2,
            max_size=10,
            desired_size=3,
            node_role=node_role,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            ami_type=eks.NodegroupAmiType.AL2_X86_64,
            capacity_type=eks.CapacityType.ON_DEMAND,
            disk_size=20,
            tags={
                "Environment": "development",
                "Application": "shopping-cart"
            }
        )

        # Install AWS Load Balancer Controller
        self._install_aws_load_balancer_controller(cluster)
        
        # Install Cluster Autoscaler
        self._install_cluster_autoscaler(cluster)
        
        # Install Metrics Server
        self._install_metrics_server(cluster)

        return cluster

    def _install_aws_load_balancer_controller(self, cluster: eks.Cluster):
        """Install AWS Load Balancer Controller for ALB/NLB support."""
        # Create service account for AWS Load Balancer Controller
        alb_service_account = cluster.add_service_account(
            "AWSLoadBalancerControllerServiceAccount",
            name="aws-load-balancer-controller",
            namespace="kube-system"
        )

        # Add IAM policy for AWS Load Balancer Controller
        alb_policy_document = iam.PolicyDocument.from_json({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:CreateServiceLinkedRole",
                        "ec2:DescribeAccountAttributes",
                        "ec2:DescribeAddresses",
                        "ec2:DescribeAvailabilityZones",
                        "ec2:DescribeInternetGateways",
                        "ec2:DescribeVpcs",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeSecurityGroups",
                        "ec2:DescribeInstances",
                        "ec2:DescribeNetworkInterfaces",
                        "ec2:DescribeTags",
                        "ec2:GetCoipPoolUsage",
                        "ec2:DescribeCoipPools",
                        "elasticloadbalancing:DescribeLoadBalancers",
                        "elasticloadbalancing:DescribeLoadBalancerAttributes",
                        "elasticloadbalancing:DescribeListeners",
                        "elasticloadbalancing:DescribeListenerCertificates",
                        "elasticloadbalancing:DescribeSSLPolicies",
                        "elasticloadbalancing:DescribeRules",
                        "elasticloadbalancing:DescribeTargetGroups",
                        "elasticloadbalancing:DescribeTargetGroupAttributes",
                        "elasticloadbalancing:DescribeTargetHealth",
                        "elasticloadbalancing:DescribeTags"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "cognito-idp:DescribeUserPoolClient",
                        "acm:ListCertificates",
                        "acm:DescribeCertificate",
                        "iam:ListServerCertificates",
                        "iam:GetServerCertificate",
                        "waf-regional:GetWebACL",
                        "waf-regional:GetWebACLForResource",
                        "waf-regional:AssociateWebACL",
                        "waf-regional:DisassociateWebACL",
                        "wafv2:GetWebACL",
                        "wafv2:GetWebACLForResource",
                        "wafv2:AssociateWebACL",
                        "wafv2:DisassociateWebACL",
                        "shield:DescribeProtection",
                        "shield:GetSubscriptionState",
                        "shield:DescribeSubscription",
                        "shield:CreateProtection",
                        "shield:DeleteProtection"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:AuthorizeSecurityGroupIngress",
                        "ec2:RevokeSecurityGroupIngress"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:CreateSecurityGroup"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:CreateTags"
                    ],
                    "Resource": "arn:aws:ec2:*:*:security-group/*",
                    "Condition": {
                        "StringEquals": {
                            "ec2:CreateAction": "CreateSecurityGroup"
                        },
                        "Null": {
                            "aws:RequestTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:CreateLoadBalancer",
                        "elasticloadbalancing:CreateTargetGroup"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Null": {
                            "aws:RequestTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:CreateListener",
                        "elasticloadbalancing:DeleteListener",
                        "elasticloadbalancing:CreateRule",
                        "elasticloadbalancing:DeleteRule"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:AddTags",
                        "elasticloadbalancing:RemoveTags"
                    ],
                    "Resource": [
                        "arn:aws:elasticloadbalancing:*:*:targetgroup/*/*",
                        "arn:aws:elasticloadbalancing:*:*:loadbalancer/net/*/*",
                        "arn:aws:elasticloadbalancing:*:*:loadbalancer/app/*/*"
                    ],
                    "Condition": {
                        "Null": {
                            "aws:RequestTag/elbv2.k8s.aws/cluster": "true",
                            "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:ModifyLoadBalancerAttributes",
                        "elasticloadbalancing:SetIpAddressType",
                        "elasticloadbalancing:SetSecurityGroups",
                        "elasticloadbalancing:SetSubnets",
                        "elasticloadbalancing:DeleteLoadBalancer",
                        "elasticloadbalancing:ModifyTargetGroup",
                        "elasticloadbalancing:ModifyTargetGroupAttributes",
                        "elasticloadbalancing:DeleteTargetGroup"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Null": {
                            "aws:ResourceTag/elbv2.k8s.aws/cluster": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:RegisterTargets",
                        "elasticloadbalancing:DeregisterTargets"
                    ],
                    "Resource": "arn:aws:elasticloadbalancing:*:*:targetgroup/*/*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "elasticloadbalancing:SetWebAcl",
                        "elasticloadbalancing:ModifyListener",
                        "elasticloadbalancing:AddListenerCertificates",
                        "elasticloadbalancing:RemoveListenerCertificates",
                        "elasticloadbalancing:ModifyRule"
                    ],
                    "Resource": "*"
                }
            ]
        })

        alb_service_account.role.attach_inline_policy(
            iam.Policy(self, "AWSLoadBalancerControllerPolicy", document=alb_policy_document)
        )

        # Install AWS Load Balancer Controller using Helm
        cluster.add_helm_chart(
            "AWSLoadBalancerController",
            chart="aws-load-balancer-controller",
            repository="https://aws.github.io/eks-charts",
            namespace="kube-system",
            values={
                "clusterName": cluster.cluster_name,
                "serviceAccount": {
                    "create": False,
                    "name": "aws-load-balancer-controller"
                },
                "region": self.region,
                "vpcId": self.vpc.vpc_id
            }
        )

    def _install_cluster_autoscaler(self, cluster: eks.Cluster):
        """Install Cluster Autoscaler for automatic node scaling."""
        # Create service account for Cluster Autoscaler
        ca_service_account = cluster.add_service_account(
            "ClusterAutoscalerServiceAccount",
            name="cluster-autoscaler",
            namespace="kube-system"
        )

        # Add IAM policy for Cluster Autoscaler
        ca_policy_document = iam.PolicyDocument.from_json({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "autoscaling:DescribeAutoScalingGroups",
                        "autoscaling:DescribeAutoScalingInstances",
                        "autoscaling:DescribeLaunchConfigurations",
                        "autoscaling:DescribeTags",
                        "autoscaling:SetDesiredCapacity",
                        "autoscaling:TerminateInstanceInAutoScalingGroup",
                        "ec2:DescribeLaunchTemplateVersions"
                    ],
                    "Resource": "*"
                }
            ]
        })

        ca_service_account.role.attach_inline_policy(
            iam.Policy(self, "ClusterAutoscalerPolicy", document=ca_policy_document)
        )

    def _install_metrics_server(self, cluster: eks.Cluster):
        """Install Metrics Server for HPA support."""
        cluster.add_helm_chart(
            "MetricsServer",
            chart="metrics-server",
            repository="https://kubernetes-sigs.github.io/metrics-server/",
            namespace="kube-system",
            values={
                "args": [
                    "--cert-dir=/tmp",
                    "--secure-port=4443",
                    "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                    "--kubelet-use-node-status-port"
                ]
            }
        )

    def _create_kubernetes_resources(self):
        """Create Kubernetes resources for the application."""
        # Allow EKS nodes to access the database
        self.database.connections.allow_from(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            ec2.Port.tcp(5432),
            "Allow EKS nodes to access database"
        )

        # Create namespace
        namespace_manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "shopping-cart",
                "labels": {
                    "name": "shopping-cart"
                }
            }
        }

        self.cluster.add_manifest("ShoppingCartNamespace", namespace_manifest)

        # Create ConfigMap for application configuration
        config_map_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "app-config",
                "namespace": "shopping-cart"
            },
            "data": {
                "DATABASE_HOST": self.database.instance_endpoint.hostname,
                "DATABASE_PORT": "5432",
                "DATABASE_NAME": "shoppingcart",
                "AWS_REGION": self.region
            }
        }

        self.cluster.add_manifest("AppConfigMap", config_map_manifest)

        # Create Secret for database credentials
        secret_manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "db-credentials",
                "namespace": "shopping-cart"
            },
            "type": "Opaque",
            "data": {
                "secret-arn": self.database.secret.secret_arn
            }
        }

        self.cluster.add_manifest("DatabaseSecret", secret_manifest)

    def _create_outputs(self):
        """Create CloudFormation outputs."""
        CfnOutput(
            self, "EKSClusterName",
            value=self.cluster.cluster_name,
            description="EKS Cluster Name"
        )

        CfnOutput(
            self, "EKSClusterEndpoint",
            value=self.cluster.cluster_endpoint,
            description="EKS Cluster Endpoint"
        )

        CfnOutput(
            self, "KubectlCommand",
            value=f"aws eks update-kubeconfig --region {self.region} --name {self.cluster.cluster_name}",
            description="Command to configure kubectl"
        )

        CfnOutput(
            self, "FrontendECRRepository",
            value=self.ecr_repos['frontend'].repository_uri,
            description="Frontend ECR Repository URI"
        )

        CfnOutput(
            self, "BackendECRRepository",
            value=self.ecr_repos['backend'].repository_uri,
            description="Backend ECR Repository URI"
        )

        CfnOutput(
            self, "DatabaseEndpoint",
            value=self.database.instance_endpoint.hostname,
            description="Database Endpoint"
        )

        CfnOutput(
            self, "VPCId",
            value=self.vpc.vpc_id,
            description="VPC ID"
        )
