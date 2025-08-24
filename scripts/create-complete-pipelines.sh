#!/bin/bash

# Create Complete CI/CD Pipelines for All Carthub Microservices
# This script creates proper IAM roles, CodeBuild projects, and CodePipelines

set -e

REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
CLUSTER_NAME="carthub-cluster"

echo "🚀 Creating Complete CI/CD Pipelines for Carthub Microservices"
echo "=============================================================="
echo "Region: $REGION"
echo "Account: $ACCOUNT_ID"
echo ""

# Create S3 bucket for pipeline artifacts if it doesn't exist
BUCKET_NAME="carthub-pipeline-artifacts-$ACCOUNT_ID-$REGION"
echo "📦 Creating S3 bucket for pipeline artifacts..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# Create comprehensive IAM policy for CodeBuild
echo "📋 Creating comprehensive IAM policy for CodeBuild..."
cat > codebuild-comprehensive-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams",
                "logs:DescribeLogGroups"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:GetAuthorizationToken",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "codecommit:GitPull",
                "codecommit:GitPush",
                "codecommit:GetBranch",
                "codecommit:GetCommit",
                "codecommit:GetRepository",
                "codecommit:ListBranches",
                "codecommit:ListRepositories"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "eks:DescribeCluster",
                "eks:ListClusters"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name CarthubCodeBuildComprehensivePolicy \
    --policy-document file://codebuild-comprehensive-policy.json 2>/dev/null || echo "Policy already exists"

# Attach comprehensive policy to CodeBuild role
aws iam attach-role-policy \
    --role-name CarthubCodeBuildRole \
    --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/CarthubCodeBuildComprehensivePolicy 2>/dev/null || echo "Policy already attached"

# Create comprehensive IAM policy for CodePipeline
echo "📋 Creating comprehensive IAM policy for CodePipeline..."
cat > codepipeline-comprehensive-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketVersioning",
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "codecommit:CancelUploadArchive",
                "codecommit:GetBranch",
                "codecommit:GetCommit",
                "codecommit:GetRepository",
                "codecommit:ListBranches",
                "codecommit:ListRepositories",
                "codecommit:UploadArchive"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "codebuild:BatchGetBuilds",
                "codebuild:StartBuild"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name CarthubCodePipelineComprehensivePolicy \
    --policy-document file://codepipeline-comprehensive-policy.json 2>/dev/null || echo "Policy already exists"

# Attach comprehensive policy to CodePipeline role
aws iam attach-role-policy \
    --role-name CarthubCodePipelineRole \
    --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/CarthubCodePipelineComprehensivePolicy 2>/dev/null || echo "Policy already attached"

# Wait for IAM propagation
echo "⏳ Waiting for IAM role propagation..."
sleep 30

# Function to create CodeBuild project
create_codebuild_project() {
    local SERVICE_NAME=$1
    local REPO_NAME="carthub-$SERVICE_NAME"
    
    echo "🔨 Creating CodeBuild project for $SERVICE_NAME..."
    
    cat > ${SERVICE_NAME}-codebuild-project.json << EOF
{
    "name": "carthub-${SERVICE_NAME}-build",
    "description": "Build project for Carthub ${SERVICE_NAME} microservice",
    "source": {
        "type": "CODECOMMIT",
        "location": "https://git-codecommit.${REGION}.amazonaws.com/v1/repos/${REPO_NAME}",
        "buildspec": "buildspec.yml"
    },
    "artifacts": {
        "type": "NO_ARTIFACTS"
    },
    "environment": {
        "type": "LINUX_CONTAINER",
        "image": "aws/codebuild/amazonlinux2-x86_64-standard:5.0",
        "computeType": "BUILD_GENERAL1_MEDIUM",
        "privilegedMode": true,
        "environmentVariables": [
            {
                "name": "AWS_DEFAULT_REGION",
                "value": "${REGION}"
            },
            {
                "name": "AWS_ACCOUNT_ID",
                "value": "${ACCOUNT_ID}"
            },
            {
                "name": "IMAGE_REPO_NAME",
                "value": "${REPO_NAME}"
            },
            {
                "name": "EKS_CLUSTER_NAME",
                "value": "${CLUSTER_NAME}"
            }
        ]
    },
    "serviceRole": "arn:aws:iam::${ACCOUNT_ID}:role/CarthubCodeBuildRole"
}
EOF

    aws codebuild create-project \
        --cli-input-json file://${SERVICE_NAME}-codebuild-project.json \
        --region $REGION 2>/dev/null || echo "CodeBuild project for $SERVICE_NAME already exists"
}

# Function to create CodePipeline
create_codepipeline() {
    local SERVICE_NAME=$1
    local REPO_NAME="carthub-$SERVICE_NAME"
    
    echo "🔄 Creating CodePipeline for $SERVICE_NAME..."
    
    cat > ${SERVICE_NAME}-pipeline.json << EOF
{
    "pipeline": {
        "name": "carthub-${SERVICE_NAME}-pipeline",
        "roleArn": "arn:aws:iam::${ACCOUNT_ID}:role/CarthubCodePipelineRole",
        "artifactStore": {
            "type": "S3",
            "location": "${BUCKET_NAME}"
        },
        "stages": [
            {
                "name": "Source",
                "actions": [
                    {
                        "name": "SourceAction",
                        "actionTypeId": {
                            "category": "Source",
                            "owner": "AWS",
                            "provider": "CodeCommit",
                            "version": "1"
                        },
                        "configuration": {
                            "RepositoryName": "${REPO_NAME}",
                            "BranchName": "main",
                            "PollForSourceChanges": "true"
                        },
                        "outputArtifacts": [
                            {
                                "name": "SourceOutput"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Build",
                "actions": [
                    {
                        "name": "BuildAction",
                        "actionTypeId": {
                            "category": "Build",
                            "owner": "AWS",
                            "provider": "CodeBuild",
                            "version": "1"
                        },
                        "configuration": {
                            "ProjectName": "carthub-${SERVICE_NAME}-build"
                        },
                        "inputArtifacts": [
                            {
                                "name": "SourceOutput"
                            }
                        ],
                        "outputArtifacts": [
                            {
                                "name": "BuildOutput"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}
EOF

    aws codepipeline create-pipeline \
        --cli-input-json file://${SERVICE_NAME}-pipeline.json \
        --region $REGION 2>/dev/null || echo "Pipeline for $SERVICE_NAME already exists"
}

# Create projects and pipelines for all microservices
SERVICES=("frontend" "backend" "database")

for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "🎯 Setting up complete CI/CD for $SERVICE microservice..."
    create_codebuild_project $SERVICE
    sleep 5  # Brief pause between operations
    create_codepipeline $SERVICE
    sleep 5
done

echo ""
echo "✅ Complete CI/CD Pipeline Setup Finished!"
echo "=========================================="
echo ""

# Verify what was created
echo "📊 Verifying Created Resources:"
echo ""
echo "CodeBuild Projects:"
aws codebuild list-projects --region $REGION --query 'projects[?contains(@, `carthub`)]' --output table

echo ""
echo "CodePipelines:"
aws codepipeline list-pipelines --region $REGION --query 'pipelines[?contains(name, `carthub`)]' --output table

echo ""
echo "🎯 Pipeline Features:"
echo "- ✅ Automatic triggers on code commits to main branch"
echo "- ✅ Build Docker images and push to ECR"
echo "- ✅ Comprehensive logging and monitoring"
echo "- ✅ Proper IAM permissions and security"
echo ""

echo "🔄 Pipeline Workflow:"
echo "1. Developer pushes code to CodeCommit repository"
echo "2. CodePipeline automatically detects changes"
echo "3. CodeBuild builds Docker image using buildspec.yml"
echo "4. Built image is pushed to ECR with latest tag"
echo "5. Kubernetes can pull new image for deployment"
echo ""

echo "🚀 Next Steps:"
echo "1. Make a code change and push to any CodeCommit repository"
echo "2. Watch the pipeline automatically trigger and build"
echo "3. New Docker images will appear in ECR"
echo "4. Update Kubernetes deployments to use new images"
echo ""

echo "🌐 Monitor Your Pipelines:"
echo "- CodePipeline Console: https://console.aws.amazon.com/codesuite/codepipeline/pipelines?region=$REGION"
echo "- CodeBuild Console: https://console.aws.amazon.com/codesuite/codebuild/projects?region=$REGION"
echo "- ECR Console: https://console.aws.amazon.com/ecr/repositories?region=$REGION"

# Cleanup temporary files
rm -f *-codebuild-project.json *-pipeline.json *-policy.json

echo ""
echo "🎉 All microservice CI/CD pipelines are now ready!"
