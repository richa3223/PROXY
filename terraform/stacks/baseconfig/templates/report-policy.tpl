{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "athena:ListDataCatalogs",
                "athena:ListWorkGroups",
                "kms:ListAliases",
                "s3:GetAccountPublicAccessBlock",
                "s3:ListAccessPoints",
                "s3:ListAllMyBuckets",
                "tag:GetResources",
                "glue:ListCrawlers"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "athena:BatchGetQueryExecution",
                "athena:GetQueryExecution",
                "athena:GetQueryResults",
                "athena:GetQueryRuntimeStatistics",
                "athena:GetWorkGroup",
                "athena:ListQueryExecutions",
                "athena:StartQueryExecution"
            ],
            "Resource": "arn:aws:athena:${aws_region}:${aws_account}:workgroup/${workgroup}"
        },
        {
            "Effect": "Allow",
            "Action": "kms:Decrypt",
            "Resource": "arn:aws:kms:${aws_region}::alias/aws/s3"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketAcl",
                "s3:GetBucketLocation",
                "s3:GetBucketOwnershipControls",
                "s3:GetBucketPolicyStatus",
                "s3:GetBucketPublicAccessBlock",
                "s3:GetBucketVersioning",
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::${query_bucket}",
                "arn:aws:s3:::${query_bucket}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketAcl",
                "s3:GetBucketLocation",
                "s3:GetBucketOwnershipControls",
                "s3:GetBucketPolicyStatus",
                "s3:GetBucketPublicAccessBlock",
                "s3:GetBucketVersioning",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::${result_bucket}",
                "arn:aws:s3:::${result_bucket}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:BatchGetCrawlers",
                "glue:StartCrawler",
                "glue:ListCrawls",
                "glue:GetCrawlers",
                "glue:GetCrawler"
            ],
            "Resource": "arn:aws:glue:${aws_region}:${aws_account}:crawler/${crawler}"
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:GetDatabases",
                "glue:GetDatabase",
                "glue:GetTables",
                "glue:GetTable",
                "glue:SearchTables",
                "glue:GetPartitions"
            ],
            "Resource": "arn:aws:glue:${aws_region}:${aws_account}:catalog"
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:GetDatabases",
                "glue:GetDatabase",
                "glue:GetTables",
                "glue:GetTable",
                "glue:SearchTables",
                "glue:GetPartitions"
            ],
            "Resource": "arn:aws:glue:${aws_region}:${aws_account}:database/${catalog_database}"
        },
        {
            "Effect": "Allow",
            "Action": [
                "glue:GetTables",
                "glue:GetTable",
                "glue:SearchTables",
                "glue:GetPartitions",
                "glue:GetPartition"
            ],
            "Resource": "arn:aws:glue:${aws_region}:${aws_account}:table/${catalog_database}/*"
        }
    ]
}
