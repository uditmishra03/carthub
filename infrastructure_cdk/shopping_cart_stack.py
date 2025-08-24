from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    BundlingOptions
)
from constructs import Construct


class ShoppingCartStack(Stack):
    """CDK Stack for Shopping Cart API infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table for storing shopping carts
        cart_table = dynamodb.Table(
            self, "ShoppingCartTable",
            table_name="shopping-carts",
            partition_key=dynamodb.Attribute(
                name="customer_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # For development only
            point_in_time_recovery=True
        )

        # Lambda function for adding items to cart
        add_item_lambda = _lambda.Function(
            self, "AddItemToCartFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="presentation.handlers.add_item_handler.lambda_handler",
            code=_lambda.Code.from_asset(
                "../",
                exclude=[
                    "infrastructure_cdk/*",
                    "tests/*",
                    "**/__pycache__/*",
                    "**/*.pyc",
                    "*.md",
                    ".git/*",
                    "cdk.out/*",
                    ".pytest_cache/*"
                ]
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "CART_TABLE_NAME": cart_table.table_name
                # AWS_REGION is automatically available in Lambda runtime
            }
        )

        # Lambda function for checkout
        checkout_lambda = _lambda.Function(
            self, "CheckoutFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="presentation.handlers.checkout_handler.lambda_handler",
            code=_lambda.Code.from_asset(
                "../",
                exclude=[
                    "infrastructure_cdk/*",
                    "tests/*",
                    "**/__pycache__/*",
                    "**/*.pyc",
                    "*.md",
                    ".git/*",
                    "cdk.out/*",
                    ".pytest_cache/*"
                ]
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "CART_TABLE_NAME": cart_table.table_name
            }
        )

        # Grant Lambda permissions to read/write to DynamoDB table
        cart_table.grant_read_write_data(add_item_lambda)
        cart_table.grant_read_write_data(checkout_lambda)

        # API Gateway REST API
        api = apigateway.RestApi(
            self, "ShoppingCartApi",
            rest_api_name="Shopping Cart API",
            description="API for managing shopping cart operations",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )

        # API Gateway resources and methods
        cart_resource = api.root.add_resource("cart")
        items_resource = cart_resource.add_resource("items")
        checkout_resource = cart_resource.add_resource("checkout")

        # POST /cart/items - Add item to cart
        add_item_integration = apigateway.LambdaIntegration(
            add_item_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )

        items_resource.add_method(
            "POST",
            add_item_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigateway.Model.EMPTY_MODEL
                    }
                ),
                apigateway.MethodResponse(
                    status_code="400",
                    response_models={
                        "application/json": apigateway.Model.ERROR_MODEL
                    }
                ),
                apigateway.MethodResponse(
                    status_code="500",
                    response_models={
                        "application/json": apigateway.Model.ERROR_MODEL
                    }
                )
            ]
        )

        # POST /cart/checkout - Process checkout
        checkout_integration = apigateway.LambdaIntegration(
            checkout_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )

        checkout_resource.add_method(
            "POST",
            checkout_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigateway.Model.EMPTY_MODEL
                    }
                ),
                apigateway.MethodResponse(
                    status_code="400",
                    response_models={
                        "application/json": apigateway.Model.ERROR_MODEL
                    }
                ),
                apigateway.MethodResponse(
                    status_code="500",
                    response_models={
                        "application/json": apigateway.Model.ERROR_MODEL
                    }
                )
            ]
        )

        # Output the API Gateway URL
        self.api_url = api.url
