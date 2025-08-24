#!/usr/bin/env python3
"""
CartHub Domain Infrastructure Stack
Creates Route 53 hosted zone, CloudFront distribution, and S3 hosting
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    RemovalPolicy,
    Duration,
    CfnOutput
)
from constructs import Construct

class CartHubDomainStack(Stack):
    """
    Stack for CartHub domain infrastructure with custom domain
    """

    def __init__(self, scope: Construct, construct_id: str, domain_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.domain_name = domain_name
        self.subdomain = f"app.{domain_name}"
        
        # Create Route 53 Hosted Zone
        self.hosted_zone = self._create_hosted_zone()
        
        # Create SSL Certificate
        self.certificate = self._create_ssl_certificate()
        
        # Create S3 bucket for hosting
        self.website_bucket = self._create_website_bucket()
        
        # Create CloudFront distribution
        self.distribution = self._create_cloudfront_distribution()
        
        # Create Route 53 records
        self._create_dns_records()
        
        # Deploy website content
        self._deploy_website_content()
        
        # Output important information
        self._create_outputs()

    def _create_hosted_zone(self) -> route53.HostedZone:
        """Create Route 53 hosted zone for the domain"""
        hosted_zone = route53.HostedZone(
            self, "CartHubHostedZone",
            zone_name=self.domain_name,
            comment=f"Hosted zone for CartHub application - {self.domain_name}"
        )
        
        return hosted_zone

    def _create_ssl_certificate(self) -> acm.Certificate:
        """Create SSL certificate for the domain and subdomain"""
        certificate = acm.Certificate(
            self, "CartHubSSLCertificate",
            domain_name=self.domain_name,
            subject_alternative_names=[
                f"*.{self.domain_name}",  # Wildcard for subdomains
                f"www.{self.domain_name}"
            ],
            validation=acm.CertificateValidation.from_dns(self.hosted_zone)
        )
        
        return certificate

    def _create_website_bucket(self) -> s3.Bucket:
        """Create S3 bucket for website hosting"""
        bucket = s3.Bucket(
            self, "CartHubWebsiteBucket",
            bucket_name=f"carthub-{self.domain_name.replace('.', '-')}",
            website_index_document="index.html",
            website_error_document="index.html",  # SPA routing
            public_read_access=False,  # CloudFront will handle access
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        return bucket

    def _create_cloudfront_distribution(self) -> cloudfront.Distribution:
        """Create CloudFront distribution with custom domain"""
        
        # Origin Access Identity for S3
        oai = cloudfront.OriginAccessIdentity(
            self, "CartHubOAI",
            comment=f"OAI for CartHub {self.domain_name}"
        )
        
        # Grant CloudFront access to S3 bucket
        self.website_bucket.grant_read(oai)
        
        # CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "CartHubDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.website_bucket,
                    origin_access_identity=oai
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True
            ),
            domain_names=[self.subdomain, f"www.{self.domain_name}"],
            certificate=self.certificate,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(30)
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(30)
                )
            ],
            default_root_object="index.html",
            comment=f"CartHub CloudFront Distribution for {self.domain_name}"
        )
        
        return distribution

    def _create_dns_records(self):
        """Create Route 53 DNS records"""
        
        # A record for subdomain (app.domain.com)
        route53.ARecord(
            self, "CartHubSubdomainRecord",
            zone=self.hosted_zone,
            record_name="app",
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            )
        )
        
        # A record for www subdomain
        route53.ARecord(
            self, "CartHubWWWRecord",
            zone=self.hosted_zone,
            record_name="www",
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.distribution)
            )
        )
        
        # CNAME record for root domain redirect (optional)
        route53.CnameRecord(
            self, "CartHubRootRedirect",
            zone=self.hosted_zone,
            record_name="carthub",
            domain_name=self.subdomain
        )

    def _deploy_website_content(self):
        """Deploy website content to S3"""
        s3deploy.BucketDeployment(
            self, "CartHubWebsiteDeployment",
            sources=[s3deploy.Source.asset("../frontend/public")],
            destination_bucket=self.website_bucket,
            distribution=self.distribution,
            distribution_paths=["/*"]
        )

    def _create_outputs(self):
        """Create CloudFormation outputs"""
        
        CfnOutput(
            self, "DomainName",
            value=self.domain_name,
            description="Root domain name"
        )
        
        CfnOutput(
            self, "WebsiteURL",
            value=f"https://{self.subdomain}",
            description="CartHub application URL"
        )
        
        CfnOutput(
            self, "CloudFrontDistributionId",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID"
        )
        
        CfnOutput(
            self, "HostedZoneId",
            value=self.hosted_zone.hosted_zone_id,
            description="Route 53 hosted zone ID"
        )
        
        CfnOutput(
            self, "NameServers",
            value=",".join(self.hosted_zone.hosted_zone_name_servers or []),
            description="Name servers for domain configuration"
        )
        
        CfnOutput(
            self, "S3BucketName",
            value=self.website_bucket.bucket_name,
            description="S3 bucket name for website content"
        )
