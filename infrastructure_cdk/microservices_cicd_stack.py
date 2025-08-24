"""
AWS CDK Stack for Carthub Microservices CI/CD Pipeline
Creates CodeCommit repositories, CodePipeline, ECR repositories, and EKS cluster
"""

from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_ecr as ecr,
    aws_eks as eks,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    aws_s3 as s3,
    RemovalPolicy,
    Duration,
    CfnOutput
)
from constructs import Construct
import json


class MicroservicesCicdStack(Stack):
    """
    CDK Stack for Carthub Microservices CI/CD Pipeline
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC for EKS cluster
        self.vpc = ec2.Vpc(
            self, "CarthubVPC",
            max_azs=3,
            nat_gateways=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        # Create S3 bucket for pipeline artifacts
        self.artifacts_bucket = s3.Bucket(
            self, "CarthubArtifactsBucket",
            bucket_name=f"carthub-pipeline-artifacts-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        # Create ECR repositories
        self.create_ecr_repositories()

        # Create CodeCommit repositories
        self.create_codecommit_repositories()

        # Create RDS database
        self.create_database()

        # Create EKS cluster
        self.create_eks_cluster()

        # Create IAM roles
        self.create_iam_roles()

        # Create CodeBuild projects
        self.create_codebuild_projects()

        # Create CodePipelines
        self.create_codepipelines()

        # Output important values
        self.create_outputs()

    def create_ecr_repositories(self):
        """Create ECR repositories for each microservice"""
        self.ecr_repositories = {}
        
        microservices = ["frontend", "backend", "database"]
        
        for service in microservices:
            self.ecr_repositories[service] = ecr.Repository(
                self, f"CarthubECR{service.title()}",
                repository_name=f"carthub-{service}",
                removal_policy=RemovalPolicy.DESTROY,
                lifecycle_rules=[
                    ecr.LifecycleRule(
                        max_image_count=10,
                        rule_priority=1,
                        description=f"Keep only 10 images for {service}"
                    )
                ]
            )

    def create_codecommit_repositories(self):
        """Create CodeCommit repositories for each microservice"""
        self.codecommit_repositories = {}
        
        microservices = ["frontend", "backend", "database"]
        
        for service in microservices:
            self.codecommit_repositories[service] = codecommit.Repository(
                self, f"CarthubRepo{service.title()}",
                repository_name=f"carthub-{service}",
                description=f"Carthub {service} microservice repository"
            )

    def create_database(self):
        """Create RDS PostgreSQL database"""
        # Create database subnet group
        db_subnet_group = rds.SubnetGroup(
            self, "CarthubDBSubnetGroup",
            description="Subnet group for Carthub database",
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )
        )

        # Create database security group
        db_security_group = ec2.SecurityGroup(
            self, "CarthubDBSecurityGroup",
            vpc=self.vpc,
            description="Security group for Carthub database",
            allow_all_outbound=False
        )

        # Create database credentials secret
        self.db_secret = secretsmanager.Secret(
            self, "CarthubDBSecret",
            description="Carthub database credentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "carthub_admin"}),
                generate_string_key="password",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"\\",
                password_length=32
            )
        )

        # Create RDS instance
        self.database = rds.DatabaseInstance(
            self, "CarthubDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            credentials=rds.Credentials.from_secret(self.db_secret),
            database_name="carthub",
            vpc=self.vpc,
            subnet_group=db_subnet_group,
            security_groups=[db_security_group],
            backup_retention=Duration.days(7),
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY
        )

    def create_eks_cluster(self):
        """Create EKS cluster"""
        # Create EKS cluster role
        cluster_role = iam.Role(
            self, "CarthubEKSClusterRole",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy")
            ]
        )

        # Create node group role
        nodegroup_role = iam.Role(
            self, "CarthubEKSNodeGroupRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
            ]
        )

        # Create EKS cluster
        self.eks_cluster = eks.Cluster(
            self, "CarthubEKSCluster",
            cluster_name="carthub-cluster",
            version=eks.KubernetesVersion.V1_28,
            vpc=self.vpc,
            vpc_subnets=[
                ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
            ],
            role=cluster_role,
            default_capacity=0,  # We'll add managed node groups separately
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE
        )

        # Add managed node group
        self.eks_cluster.add_nodegroup_capacity(
            "CarthubNodeGroup",
            nodegroup_name="carthub-nodes",
            node_role=nodegroup_role,
            instance_types=[
                ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM)
            ],
            min_size=2,
            max_size=10,
            desired_size=3,
            subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            ami_type=eks.NodegroupAmiType.AL2_X86_64
        )

    def create_iam_roles(self):
        """Create IAM roles for CodeBuild and CodePipeline"""
        # CodeBuild service role
        self.codebuild_role = iam.Role(
            self, "CarthubCodeBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
            ]
        )

        # Add permissions for ECR
        self.codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:GetAuthorizationToken",
                    "ecr:PutImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload"
                ],
                resources=["*"]
            )
        )

        # Add permissions for EKS
        self.codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "eks:DescribeCluster",
                    "eks:DescribeNodegroup"
                ],
                resources=[self.eks_cluster.cluster_arn]
            )
        )

        # Add permissions for S3 artifacts bucket
        self.codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:GetObjectVersion"
                ],
                resources=[f"{self.artifacts_bucket.bucket_arn}/*"]
            )
        )

        # Add permissions for Secrets Manager
        self.codebuild_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "secretsmanager:GetSecretValue"
                ],
                resources=[self.db_secret.secret_arn]
            )
        )

        # CodePipeline service role
        self.codepipeline_role = iam.Role(
            self, "CarthubCodePipelineRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com")
        )

        # Add permissions for CodeCommit
        self.codepipeline_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "codecommit:GetBranch",
                    "codecommit:GetCommit",
                    "codecommit:GetRepository",
                    "codecommit:ListBranches",
                    "codecommit:ListRepositories"
                ],
                resources=[repo.repository_arn for repo in self.codecommit_repositories.values()]
            )
        )

        # Add permissions for CodeBuild
        self.codepipeline_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "codebuild:BatchGetBuilds",
                    "codebuild:StartBuild"
                ],
                resources=["*"]
            )
        )

        # Add permissions for S3 artifacts bucket
        self.codepipeline_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:GetObjectVersion",
                    "s3:ListBucket"
                ],
                resources=[
                    self.artifacts_bucket.bucket_arn,
                    f"{self.artifacts_bucket.bucket_arn}/*"
                ]
            )
        )

    def create_codebuild_projects(self):
        """Create CodeBuild projects for each microservice"""
        self.codebuild_projects = {}

        # Frontend CodeBuild project
        self.codebuild_projects["frontend"] = codebuild.Project(
            self, "CarthubFrontendBuild",
            project_name="carthub-frontend-build",
            source=codebuild.Source.code_commit(
                repository=self.codecommit_repositories["frontend"]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL
            ),
            environment_variables={
                "AWS_DEFAULT_REGION": codebuild.BuildEnvironmentVariable(value=self.region),
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(value=self.account),
                "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.ecr_repositories["frontend"].repository_name
                ),
                "IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
                "EKS_CLUSTER_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.eks_cluster.cluster_name
                )
            },
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            role=self.codebuild_role
        )

        # Backend CodeBuild project
        self.codebuild_projects["backend"] = codebuild.Project(
            self, "CarthubBackendBuild",
            project_name="carthub-backend-build",
            source=codebuild.Source.code_commit(
                repository=self.codecommit_repositories["backend"]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL
            ),
            environment_variables={
                "AWS_DEFAULT_REGION": codebuild.BuildEnvironmentVariable(value=self.region),
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(value=self.account),
                "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.ecr_repositories["backend"].repository_name
                ),
                "IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
                "EKS_CLUSTER_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.eks_cluster.cluster_name
                ),
                "DB_SECRET_ARN": codebuild.BuildEnvironmentVariable(
                    value=self.db_secret.secret_arn
                )
            },
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            role=self.codebuild_role
        )

        # Database CodeBuild project
        self.codebuild_projects["database"] = codebuild.Project(
            self, "CarthubDatabaseBuild",
            project_name="carthub-database-build",
            source=codebuild.Source.code_commit(
                repository=self.codecommit_repositories["database"]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=True,
                compute_type=codebuild.ComputeType.SMALL
            ),
            environment_variables={
                "AWS_DEFAULT_REGION": codebuild.BuildEnvironmentVariable(value=self.region),
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(value=self.account),
                "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.ecr_repositories["database"].repository_name
                ),
                "IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
                "EKS_CLUSTER_NAME": codebuild.BuildEnvironmentVariable(
                    value=self.eks_cluster.cluster_name
                ),
                "DB_SECRET_ARN": codebuild.BuildEnvironmentVariable(
                    value=self.db_secret.secret_arn
                )
            },
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            role=self.codebuild_role
        )

    def create_codepipelines(self):
        """Create CodePipelines for each microservice"""
        self.pipelines = {}

        for service in ["frontend", "backend", "database"]:
            # Create source output
            source_output = codepipeline.Artifact(f"{service}_source")
            
            # Create build output
            build_output = codepipeline.Artifact(f"{service}_build")

            # Create pipeline
            self.pipelines[service] = codepipeline.Pipeline(
                self, f"Carthub{service.title()}Pipeline",
                pipeline_name=f"carthub-{service}-pipeline",
                artifact_bucket=self.artifacts_bucket,
                role=self.codepipeline_role,
                stages=[
                    # Source stage
                    codepipeline.StageProps(
                        stage_name="Source",
                        actions=[
                            codepipeline_actions.CodeCommitSourceAction(
                                action_name="Source",
                                repository=self.codecommit_repositories[service],
                                branch="main",
                                output=source_output
                            )
                        ]
                    ),
                    # Build stage
                    codepipeline.StageProps(
                        stage_name="Build",
                        actions=[
                            codepipeline_actions.CodeBuildAction(
                                action_name="Build",
                                project=self.codebuild_projects[service],
                                input=source_output,
                                outputs=[build_output]
                            )
                        ]
                    )
                ]
            )

    def create_outputs(self):
        """Create CloudFormation outputs"""
        # EKS Cluster outputs
        CfnOutput(
            self, "EKSClusterName",
            value=self.eks_cluster.cluster_name,
            description="EKS Cluster Name"
        )

        CfnOutput(
            self, "EKSClusterEndpoint",
            value=self.eks_cluster.cluster_endpoint,
            description="EKS Cluster Endpoint"
        )

        # CodeCommit repository outputs
        for service, repo in self.codecommit_repositories.items():
            CfnOutput(
                self, f"CodeCommit{service.title()}RepoUrl",
                value=repo.repository_clone_url_http,
                description=f"CodeCommit {service} repository clone URL"
            )

        # ECR repository outputs
        for service, repo in self.ecr_repositories.items():
            CfnOutput(
                self, f"ECR{service.title()}RepoUri",
                value=repo.repository_uri,
                description=f"ECR {service} repository URI"
            )

        # Database outputs
        CfnOutput(
            self, "DatabaseEndpoint",
            value=self.database.instance_endpoint.hostname,
            description="RDS Database Endpoint"
        )

        CfnOutput(
            self, "DatabaseSecretArn",
            value=self.db_secret.secret_arn,
            description="Database credentials secret ARN"
        )

        # Pipeline outputs
        for service, pipeline in self.pipelines.items():
            CfnOutput(
                self, f"Pipeline{service.title()}Name",
                value=pipeline.pipeline_name,
                description=f"CodePipeline {service} pipeline name"
            )
