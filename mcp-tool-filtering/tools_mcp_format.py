# Enterprise MCP tool definitions following official MCP specification
# Tools converted to proper inputSchema format matching production MCP servers

MCP_TOOLS_CONFIG = {
    "snowflake": [
        {
            "name": "snowflake.query",
            "description": "Execute SQL queries against enterprise Snowflake data warehouse with comprehensive performance monitoring, result formatting, caching strategies, and audit logging. Supports complex analytical workloads including multi-table joins, window functions, advanced aggregations, time-series analysis, and machine learning feature extraction. Automatically optimizes query execution plans, manages result caching, provides detailed performance metrics, and maintains full audit trails for compliance requirements. Returns structured results with comprehensive metadata including execution time, rows affected, query plan details, credit consumption, data freshness indicators, and security context information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Complete SQL query statement to execute against the data warehouse. Must be valid Snowflake SQL syntax. Supports all Snowflake SQL features including CTEs, window functions, advanced analytics functions, and user-defined functions. Query should include appropriate WHERE clauses and LIMIT statements for performance optimization.",
                        "minLength": 10,
                        "maxLength": 100000,
                        "pattern": "^(SELECT|WITH|SHOW|DESCRIBE|EXPLAIN).*",
                        "examples": [
                            "SELECT customer_id, SUM(amount) FROM transactions WHERE date >= '2024-01-01' GROUP BY customer_id LIMIT 1000",
                            "WITH payment_metrics AS (SELECT payment_method, COUNT(*) as txn_count FROM transactions GROUP BY payment_method) SELECT * FROM payment_metrics"
                        ]
                    },
                    "execution_context": {
                        "type": "object",
                        "description": "Execution context and performance configuration for the query",
                        "properties": {
                            "warehouse": {
                                "type": "string",
                                "description": "Virtual warehouse to use for query execution with specific compute resources",
                                "enum": ["COMPUTE_WH_XS", "COMPUTE_WH_S", "COMPUTE_WH_M", "COMPUTE_WH_L", "COMPUTE_WH_XL", "ANALYTICS_WH", "BATCH_WH", "REALTIME_WH"],
                                "default": "COMPUTE_WH_M"
                            },
                            "timeout_seconds": {
                                "type": "integer",
                                "description": "Query execution timeout in seconds. Prevents runaway queries from consuming excessive resources.",
                                "minimum": 30,
                                "maximum": 14400,
                                "default": 1800
                            },
                            "max_result_size_mb": {
                                "type": "integer", 
                                "description": "Maximum result set size in megabytes to prevent memory issues",
                                "minimum": 1,
                                "maximum": 1000,
                                "default": 100
                            },
                            "query_tag": {
                                "type": "string",
                                "description": "Custom tag for query tracking and cost attribution",
                                "maxLength": 255,
                                "pattern": "^[a-zA-Z0-9_-]+$"
                            }
                        },
                        "required": ["warehouse"]
                    },
                    "result_configuration": {
                        "type": "object", 
                        "description": "Configuration for result formatting and delivery",
                        "properties": {
                            "format": {
                                "type": "string",
                                "description": "Output format for query results",
                                "enum": ["json", "csv", "parquet", "arrow", "table"],
                                "default": "json"
                            },
                            "compression": {
                                "type": "string",
                                "description": "Compression algorithm for large result sets",
                                "enum": ["none", "gzip", "lz4", "zstd"],
                                "default": "none"
                            },
                            "pagination": {
                                "type": "object",
                                "description": "Pagination settings for large result sets",
                                "properties": {
                                    "page_size": {
                                        "type": "integer",
                                        "description": "Number of rows per page",
                                        "minimum": 100,
                                        "maximum": 50000,
                                        "default": 10000
                                    },
                                    "max_pages": {
                                        "type": "integer", 
                                        "description": "Maximum number of pages to return",
                                        "minimum": 1,
                                        "maximum": 100,
                                        "default": 10
                                    }
                                }
                            }
                        }
                    },
                    "performance_options": {
                        "type": "object",
                        "description": "Advanced performance and optimization settings",
                        "properties": {
                            "use_cached_result": {
                                "type": "boolean",
                                "description": "Allow use of cached query results if available within TTL",
                                "default": True
                            },
                            "cache_ttl_hours": {
                                "type": "integer",
                                "description": "Time-to-live for result caching in hours",
                                "minimum": 1,
                                "maximum": 168,
                                "default": 24
                            },
                            "explain_plan": {
                                "type": "boolean", 
                                "description": "Return query execution plan instead of executing the query",
                                "default": False
                            },
                            "profile_execution": {
                                "type": "boolean",
                                "description": "Include detailed execution profiling information",
                                "default": False
                            }
                        }
                    },
                    "security_context": {
                        "type": "object",
                        "description": "Security and audit context for the query execution",
                        "properties": {
                            "user_context": {
                                "type": "object",
                                "description": "User identity and authorization context",
                                "properties": {
                                    "user_id": {
                                        "type": "string", 
                                        "description": "Unique user identifier for audit logging"
                                    },
                                    "session_id": {
                                        "type": "string",
                                        "description": "Session identifier for tracking user activity"
                                    },
                                    "ip_address": {
                                        "type": "string",
                                        "description": "Client IP address for security logging",
                                        "format": "ipv4"
                                    }
                                },
                                "required": ["user_id", "session_id"]
                            },
                            "data_classification": {
                                "type": "string",
                                "description": "Data classification level for compliance",
                                "enum": ["public", "internal", "confidential", "restricted"],
                                "default": "internal"
                            },
                            "audit_required": {
                                "type": "boolean",
                                "description": "Whether detailed audit logging is required",
                                "default": True
                            }
                        },
                        "required": ["user_context"]
                    }
                },
                "required": ["query", "execution_context", "security_context"],
                "additionalProperties": False
            },
            "type": "read"
        },
        {
            "name": "snowflake.get_metrics",
            "description": "Retrieve comprehensive business metrics including transaction volumes, error rates, conversion rates, and revenue analytics. Supports time-based filtering, grouping by dimensions like payment method, region, or customer segment. Returns real-time and historical data with statistical summaries and trend analysis.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "metric_types": {
                        "type": "array",
                        "description": "List of metrics to retrieve (transaction_volume, error_rate, revenue, etc.)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start timestamp (ISO format)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End timestamp (ISO format)"
                    },
                    "granularity": {
                        "type": "string",
                        "description": "Data granularity (minute, hour, day)"
                    }
                },
                "required": [
                    "metric_types",
                    "start_time",
                    "end_time"
                ]
            },
            "type": "read"
        },
        {
            "name": "snowflake.list_tables",
            "description": "List all available tables and views in the data warehouse with comprehensive metadata. Returns table names, schemas, row counts, data sizes, last update timestamps, and access patterns. Supports filtering by database, schema, or table type. Includes table relationships and foreign key information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name filter"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name filter"
                    },
                    "table_type": {
                        "type": "string",
                        "description": "Filter by table type (TABLE, VIEW, MATERIALIZED_VIEW)"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "snowflake.get_schema",
            "description": "Get detailed table schema information including column names, data types, constraints, indexes, and statistical information. Returns column-level metadata such as nullable flags, default values, and data distribution statistics. Supports multiple tables and includes foreign key relationships.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Full table name (database.schema.table)"
                    },
                    "include_stats": {
                        "type": "boolean",
                        "description": "Include column statistics and data distribution"
                    }
                },
                "required": [
                    "table_name"
                ]
            },
            "type": "read"
        },
        {
            "name": "snowflake.get_query_history",
            "description": "Retrieve comprehensive query execution history with performance metrics, resource usage, and optimization recommendations. Returns query text, execution plans, duration, bytes processed, credits consumed, and error information. Supports filtering by user, timeframe, or query patterns.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Start timestamp for history lookup"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End timestamp for history lookup"
                    },
                    "user_filter": {
                        "type": "string",
                        "description": "Filter by username"
                    },
                    "query_filter": {
                        "type": "string",
                        "description": "Filter by query text pattern"
                    }
                },
                "required": [
                    "start_time",
                    "end_time"
                ]
            },
            "type": "read"
        },
        {
            "name": "snowflake.analyze_query",
            "description": "Perform comprehensive query performance analysis with optimization recommendations. Analyzes query execution plans, identifies bottlenecks, suggests index improvements, and provides cost optimization strategies. Returns detailed performance metrics and actionable recommendations.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to analyze"
                    },
                    "explain_plan": {
                        "type": "boolean",
                        "description": "Include detailed execution plan analysis"
                    }
                },
                "required": [
                    "query"
                ]
            },
            "type": "read"
        },
        {
            "name": "snowflake.get_costs",
            "description": "Calculate and retrieve detailed cost information for compute resources, storage usage, and data transfer operations. Returns cost breakdowns by warehouse, user, query type, and time period. Includes credit consumption, storage costs, and usage trends with forecasting.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date for cost analysis"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for cost analysis"
                    },
                    "granularity": {
                        "type": "string",
                        "description": "Cost reporting granularity (daily, weekly, monthly)"
                    },
                    "warehouse_filter": {
                        "type": "string",
                        "description": "Filter by specific warehouse"
                    }
                },
                "required": [
                    "start_date",
                    "end_date"
                ]
            },
            "type": "read"
        },
        {
            "name": "snowflake.manage_warehouse",
            "description": "Create, modify, suspend, or resume virtual warehouses for compute workloads. Supports auto-scaling configuration, resource monitoring, and workload isolation. Returns warehouse status, current usage, and configuration details with cost optimization recommendations.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "warehouse_name": {
                        "type": "string",
                        "description": "Name of the warehouse"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, modify, suspend, resume, drop)"
                    },
                    "size": {
                        "type": "string",
                        "description": "Warehouse size (XS, S, M, L, XL, 2XL, 3XL, 4XL)"
                    },
                    "auto_suspend": {
                        "type": "integer",
                        "description": "Auto-suspend timeout in seconds"
                    }
                },
                "required": [
                    "warehouse_name",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "snowflake.monitor_warehouse_usage",
            "description": "Monitor real-time and historical warehouse performance including credit consumption, query concurrency, and resource utilization. Provides insights into cost optimization opportunities and scaling recommendations based on workload patterns.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "warehouse_name": {
                        "type": "string",
                        "description": "Warehouse to monitor"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for monitoring (1h, 6h, 24h, 7d)"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "snowflake.optimize_warehouse",
            "description": "Analyze warehouse performance and provide optimization recommendations including sizing, clustering keys, and workload distribution. Returns detailed analysis of query patterns, resource usage, and cost reduction strategies.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "warehouse_name": {
                        "type": "string",
                        "description": "Warehouse to optimize"
                    },
                    "analysis_period": {
                        "type": "string",
                        "description": "Analysis time period (1d, 7d, 30d)"
                    }
                },
                "required": [
                    "warehouse_name"
                ]
            },
            "type": "read"
        },
        {
            "name": "snowflake.manage_pipes",
            "description": "Create, modify, and monitor Snowpipe for continuous data ingestion from cloud storage. Supports automatic file detection, error handling, and data transformation. Returns pipe status, ingestion statistics, and error logs.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pipe_name": {
                        "type": "string",
                        "description": "Name of the pipe"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (create, alter, drop, refresh)"
                    },
                    "stage": {
                        "type": "string",
                        "description": "Stage name for data source"
                    },
                    "table": {
                        "type": "string",
                        "description": "Target table name"
                    }
                },
                "required": [
                    "pipe_name",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "snowflake.monitor_data_loading",
            "description": "Monitor data loading operations including COPY commands, Snowpipe ingestion, and bulk loading processes. Provides real-time status, error analysis, and performance metrics for data ingestion pipelines.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "load_type": {
                        "type": "string",
                        "description": "Type of loading to monitor (copy, pipe, stream)"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for monitoring"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "snowflake.manage_users",
            "description": "Create, modify, and manage user accounts with role-based access control. Supports user provisioning, password policies, and authentication methods including SSO integration. Returns user status, permissions, and access history.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username to manage"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (create, alter, drop, reset_password)"
                    },
                    "roles": {
                        "type": "array",
                        "description": "Roles to assign"
                    },
                    "email": {
                        "type": "string",
                        "description": "User email address"
                    }
                },
                "required": [
                    "username",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "snowflake.audit_access",
            "description": "Retrieve comprehensive access logs and security audit information including login attempts, query execution, and privilege usage. Supports compliance reporting and security analysis with detailed timestamps and user attribution.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Start time for audit period"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time for audit period"
                    },
                    "user_filter": {
                        "type": "string",
                        "description": "Filter by specific user"
                    },
                    "action_type": {
                        "type": "string",
                        "description": "Filter by action type"
                    }
                },
                "required": [
                    "start_time",
                    "end_time"
                ]
            },
            "type": "read"
        },
        {
            "name": "snowflake.manage_shares",
            "description": "Create and manage secure data shares with external organizations. Supports share creation, consumer management, and usage monitoring. Returns share status, consumer activity, and data consumption metrics.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "share_name": {
                        "type": "string",
                        "description": "Name of the share"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (create, drop, grant, revoke)"
                    },
                    "objects": {
                        "type": "array",
                        "description": "Database objects to share"
                    },
                    "consumers": {
                        "type": "array",
                        "description": "Consumer accounts"
                    }
                },
                "required": [
                    "share_name",
                    "action"
                ]
            },
            "type": "write"
        }
    ],
    "jira": [
        {
            "name": "jira.search_issues",
            "description": "Advanced enterprise Jira issue search with complex JQL (Jira Query Language) queries, comprehensive filtering, field expansion, and result customization. Supports searching across multiple projects, issue types, and custom fields with advanced operators, date arithmetic, and function-based queries. Returns detailed issue metadata including comments, attachments, work logs, links, and custom field values. Includes support for complex aggregations, temporal queries, and cross-project issue relationships. Provides audit trail information, security context validation, and compliance-aware field filtering based on user permissions and data classification levels.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search_criteria": {
                        "type": "object",
                        "description": "Advanced search criteria and query configuration",
                        "properties": {
                            "jql": {
                                "type": "string",
                                "description": "JQL query string for searching issues. Supports advanced operators, functions, and field references. Examples: 'project = DEV AND status != Closed', 'created >= -30d AND priority IN (High, Critical)'",
                                "minLength": 1,
                                "maxLength": 8000,
                                "examples": [
                                    "project = PROJ AND status IN ('In Progress', 'Open') AND assignee = currentUser()",
                                    "created >= '2024-01-01' AND priority = High AND component IN ('API', 'Database')",
                                    "text ~ 'payment error' AND created >= -7d ORDER BY created DESC"
                                ]
                            },
                            "quick_filters": {
                                "type": "array",
                                "description": "Pre-defined quick filter IDs to apply",
                                "items": {
                                    "type": "integer",
                                    "description": "Quick filter ID"
                                },
                                "maxItems": 10
                            },
                            "expand_options": {
                                "type": "array",
                                "description": "Additional data to include in results",
                                "items": {
                                    "type": "string",
                                    "enum": ["renderedFields", "names", "schema", "transitions", "operations", "editmeta", "changelog", "attachments", "comments", "worklog"]
                                },
                                "uniqueItems": True
                            }
                        },
                        "required": ["jql"]
                    },
                    "result_configuration": {
                        "type": "object",
                        "description": "Configuration for result formatting and field selection",
                        "properties": {
                            "fields": {
                                "type": "array",
                                "description": "Specific fields to return. Use '*all' for all fields, '*navigable' for navigable fields, or specify field names",
                                "items": {
                                    "type": "string",
                                    "pattern": "^(\\*all|\\*navigable|[a-zA-Z0-9_.-]+)$"
                                },
                                "default": ["summary", "status", "priority", "assignee", "created", "updated"],
                                "examples": [
                                    ["*navigable"],
                                    ["summary", "status", "priority", "assignee", "customfield_10001", "components"],
                                    ["*all"]
                                ]
                            },
                            "field_customization": {
                                "type": "object",
                                "description": "Custom field rendering and formatting options",
                                "properties": {
                                    "render_custom_fields": {
                                        "type": "boolean",
                                        "description": "Whether to render custom field values in human-readable format",
                                        "default": True
                                    },
                                    "include_field_metadata": {
                                        "type": "boolean",
                                        "description": "Include field schema and metadata information",
                                        "default": False
                                    },
                                    "date_format": {
                                        "type": "string",
                                        "description": "Date format for timestamp fields",
                                        "enum": ["iso8601", "epoch", "human", "relative"],
                                        "default": "iso8601"
                                    }
                                }
                            }
                        }
                    },
                    "pagination_settings": {
                        "type": "object",
                        "description": "Pagination and result limiting configuration",
                        "properties": {
                            "start_at": {
                                "type": "integer",
                                "description": "Starting index for result pagination (0-based)",
                                "minimum": 0,
                                "maximum": 100000,
                                "default": 0
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of issues to return per request",
                                "minimum": 1,
                                "maximum": 1000,
                                "default": 50
                            },
                            "total_count_limit": {
                                "type": "integer",
                                "description": "Maximum total results to count for performance optimization",
                                "minimum": 100,
                                "maximum": 50000,
                                "default": 10000
                            }
                        }
                    },
                    "performance_options": {
                        "type": "object",
                        "description": "Performance optimization and caching settings",
                        "properties": {
                            "validate_query": {
                                "type": "boolean",
                                "description": "Validate JQL syntax before execution",
                                "default": True
                            },
                            "use_cache": {
                                "type": "boolean",
                                "description": "Allow use of cached results for identical queries",
                                "default": True
                            },
                            "cache_ttl_minutes": {
                                "type": "integer",
                                "description": "Cache time-to-live in minutes",
                                "minimum": 1,
                                "maximum": 1440,
                                "default": 15
                            },
                            "query_timeout_seconds": {
                                "type": "integer",
                                "description": "Maximum query execution time",
                                "minimum": 5,
                                "maximum": 300,
                                "default": 60
                            }
                        }
                    },
                    "security_context": {
                        "type": "object",
                        "description": "Security and access control context for the search",
                        "properties": {
                            "user_permissions": {
                                "type": "object",
                                "description": "User permission context for field visibility",
                                "properties": {
                                    "respect_field_security": {
                                        "type": "boolean",
                                        "description": "Apply field-level security restrictions",
                                        "default": True
                                    },
                                    "include_restricted_projects": {
                                        "type": "boolean",
                                        "description": "Include projects with restricted access",
                                        "default": False
                                    },
                                    "security_level_override": {
                                        "type": "string",
                                        "description": "Security level for accessing restricted issues",
                                        "enum": ["standard", "elevated", "admin"],
                                        "default": "standard"
                                    }
                                }
                            },
                            "audit_context": {
                                "type": "object",
                                "description": "Audit and compliance tracking context",
                                "properties": {
                                    "audit_reason": {
                                        "type": "string",
                                        "description": "Business justification for the search operation",
                                        "maxLength": 500
                                    },
                                    "compliance_classification": {
                                        "type": "string",
                                        "description": "Data classification level for compliance requirements",
                                        "enum": ["public", "internal", "confidential", "restricted"],
                                        "default": "internal"
                                    },
                                    "track_access": {
                                        "type": "boolean",
                                        "description": "Whether to log detailed access tracking",
                                        "default": True
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["search_criteria"],
                "additionalProperties": False
            },
            "type": "read"
        },
        {
            "name": "jira.get_issue",
            "description": "Retrieve comprehensive details for a specific Jira issue including all fields, comments, attachments, work logs, and issue history. Returns structured data with custom field values, transitions, and related issue information. Includes security and permission context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key (e.g., INC-12345)"
                    },
                    "expand": {
                        "type": "array",
                        "description": "Additional data to expand (changelog, renderedFields, names)"
                    }
                },
                "required": [
                    "issue_key"
                ]
            },
            "type": "read"
        },
        {
            "name": "jira.create_issue",
            "description": "Create comprehensive incidents, critical service requests, emergency escalations, and high-priority bugs for system outages and application failures. This tool provides complete incident creation capabilities including priority assignment, user assignment, component association, label management, custom field population, attachment uploads, and initial comment addition. The system automatically triggers notification workflows, applies configured business rules, validates field constraints, and ensures proper permission checks. Returns detailed issue information including assigned key, creation timestamp, workflow status, and access URLs for immediate follow-up actions. Supports integration with external monitoring systems and automated escalation policies for critical production incidents.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Target project key or identifier where the issue will be created. Must be a valid project that the authenticated user has CREATE_ISSUES permission for. Project determines available issue types, workflows, and custom fields.",
                        "pattern": "^[A-Z][A-Z0-9]+$"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Concise issue title that clearly describes the problem or request. Should be specific and actionable. Maximum 255 characters. This appears in issue lists and notifications."
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed issue description using Jira markup syntax. Include steps to reproduce for bugs, acceptance criteria for stories, or detailed requirements for tasks. Supports rich formatting, links, and @mentions for team collaboration."
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "Specific issue type that determines available fields and workflow. Common types include Bug, Story, Task, Epic, Sub-task, Incident, Service Request, and Change Request. Must be available in the target project.",
                        "enum": [
                            "Bug",
                            "Story",
                            "Task",
                            "Epic",
                            "Sub-task",
                            "Incident",
                            "Service Request",
                            "Change Request",
                            "Improvement"
                        ]
                    },
                    "priority": {
                        "type": "string",
                        "description": "Issue priority level affecting SLA timers and escalation policies. Higher priorities trigger faster response requirements and management notifications. Some organizations have custom priority schemes.",
                        "enum": [
                            "Highest",
                            "High",
                            "Medium",
                            "Low",
                            "Lowest"
                        ],
                        "default": "Medium"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Username or email of the person assigned to work on this issue. Must be a valid user with ASSIGNABLE_USER permission in the project. Leave empty for automatic assignment based on project configuration."
                    },
                    "components": {
                        "type": "array",
                        "description": "List of project components that this issue affects. Components help categorize issues and can trigger automatic notifications to component leads. Must be valid components within the target project."
                    },
                    "labels": {
                        "type": "array",
                        "description": "Freeform labels for categorization and filtering. Useful for tagging issues with technologies, teams, or custom categories. Labels are case-sensitive and cannot contain spaces."
                    },
                    "parent_key": {
                        "type": "string",
                        "description": "Parent issue key for creating sub-tasks or linking to epics. Must be a valid issue key that the user has permission to link to. Creates hierarchical relationship in issue structure.",
                        "pattern": "^[A-Z][A-Z0-9]+-[0-9]+$"
                    },
                    "security_level": {
                        "type": "string",
                        "description": "Security level for restricting issue visibility. Only users with appropriate permissions can view issues with security levels. Available levels depend on project configuration.",
                        "enum": [
                            "Public",
                            "Internal",
                            "Confidential",
                            "Restricted"
                        ]
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment where the issue occurs (for bugs) or should be implemented (for features). Helps with impact assessment and deployment planning.",
                        "enum": [
                            "Production",
                            "Staging",
                            "Testing",
                            "Development",
                            "Multiple"
                        ]
                    }
                },
                "required": [
                    "project",
                    "summary",
                    "issue_type"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.update_issue",
            "description": "Update existing issues with field modifications including status changes, priority adjustments, assignee updates, and custom field values. Supports bulk field updates with validation and automatic workflow triggers. Maintains audit trail of all changes with timestamps and user attribution.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key to update"
                    },
                    "fields": {
                        "type": "object",
                        "description": "Fields to update with new values"
                    },
                    "notify_users": {
                        "type": "boolean",
                        "description": "Send notifications about the update"
                    }
                },
                "required": [
                    "issue_key",
                    "fields"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.transition_issue",
            "description": "Change issue status through configured workflow transitions with validation of required fields, conditions, and permissions. Supports automatic field population during transitions and custom workflow actions. Returns updated issue status and available next transitions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key to transition"
                    },
                    "transition": {
                        "type": "string",
                        "description": "Transition name or ID"
                    },
                    "fields": {
                        "type": "object",
                        "description": "Fields to update during transition"
                    }
                },
                "required": [
                    "issue_key",
                    "transition"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.get_comments",
            "description": "Retrieve all comments and activity history for a specific issue with author information, timestamps, and comment body content. Returns threaded conversations, @mentions, and comment metadata. Supports filtering by author, date range, and comment visibility levels.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key"
                    },
                    "start_at": {
                        "type": "integer",
                        "description": "Starting comment index"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum comments to return"
                    }
                },
                "required": [
                    "issue_key"
                ]
            },
            "type": "read"
        },
        {
            "name": "jira.add_comment",
            "description": "Add comments and updates to existing issues with rich text formatting, @mentions, and attachment support. Comments can include visibility restrictions, automatic @mentions of watchers, and integration with external systems. Supports threaded replies and comment editing permissions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key to comment on"
                    },
                    "body": {
                        "type": "string",
                        "description": "Comment text content"
                    },
                    "visibility": {
                        "type": "object",
                        "description": "Comment visibility restrictions"
                    }
                },
                "required": [
                    "issue_key",
                    "body"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.get_projects",
            "description": "List all accessible Jira projects with detailed configuration information including project keys, names, descriptions, lead information, and project-specific settings. Returns issue type schemes, workflow configurations, custom fields, and permission schemes associated with each project.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expand": {
                        "type": "array",
                        "description": "Additional project data to include (lead, description, issueTypes)"
                    },
                    "recent": {
                        "type": "boolean",
                        "description": "Return only recently accessed projects"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "jira.manage_project_config",
            "description": "Configure project settings including issue types, workflows, custom fields, and permission schemes. Supports project creation, modification, and configuration management with validation and rollback capabilities.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Project key to configure"
                    },
                    "config_type": {
                        "type": "string",
                        "description": "Configuration type (workflows, fields, permissions)"
                    },
                    "changes": {
                        "type": "object",
                        "description": "Configuration changes to apply"
                    }
                },
                "required": [
                    "project_key",
                    "config_type",
                    "changes"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.manage_automation_rules",
            "description": "Create, modify, and manage automation rules for issue processing, notifications, and workflow automation. Supports complex rule conditions, multi-step actions, and integration with external systems. Returns rule execution status and performance metrics.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rule_name": {
                        "type": "string",
                        "description": "Name of the automation rule"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (create, update, delete, enable, disable)"
                    },
                    "triggers": {
                        "type": "array",
                        "description": "Rule trigger conditions"
                    },
                    "actions": {
                        "type": "array",
                        "description": "Actions to execute"
                    }
                },
                "required": [
                    "rule_name",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.get_automation_logs",
            "description": "Retrieve automation rule execution logs including success/failure status, execution time, and error details. Supports filtering by rule, time period, and execution status for troubleshooting and performance analysis.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "Specific rule to get logs for"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time for log retrieval"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time for log retrieval"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by execution status"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "jira.create_dashboard",
            "description": "Create and configure dashboards with custom gadgets for issue tracking, team performance, and project analytics. Supports real-time widgets, custom filters, and sharing permissions. Returns dashboard configuration and access URLs.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Dashboard name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Dashboard description"
                    },
                    "gadgets": {
                        "type": "array",
                        "description": "List of gadgets to include"
                    },
                    "share_permissions": {
                        "type": "array",
                        "description": "Users/groups to share with"
                    }
                },
                "required": [
                    "name"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.generate_reports",
            "description": "Generate comprehensive reports including burndown charts, velocity reports, control charts, and custom analytics. Supports multiple report formats, scheduling, and automated distribution. Returns report data and visualization URLs.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "description": "Type of report to generate"
                    },
                    "project": {
                        "type": "string",
                        "description": "Project for report scope"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for report data"
                    },
                    "format": {
                        "type": "string",
                        "description": "Output format (JSON, CSV, PDF)"
                    }
                },
                "required": [
                    "report_type",
                    "project",
                    "time_period"
                ]
            },
            "type": "read"
        },
        {
            "name": "jira.monitor_sla",
            "description": "Monitor Service Level Agreement compliance including response times, resolution times, and breach warnings. Provides real-time SLA status, historical performance, and escalation triggers for critical issues.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Specific issue to check SLA"
                    },
                    "project": {
                        "type": "string",
                        "description": "Project for SLA monitoring"
                    },
                    "sla_type": {
                        "type": "string",
                        "description": "Type of SLA to monitor"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "jira.escalate_issue",
            "description": "Automatically escalate issues based on SLA breaches, priority changes, or custom escalation rules. Supports multi-level escalation, notification chains, and manager involvement. Returns escalation status and notification results.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue to escalate"
                    },
                    "escalation_level": {
                        "type": "string",
                        "description": "Level of escalation"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    },
                    "notify_stakeholders": {
                        "type": "boolean",
                        "description": "Send notifications to stakeholders"
                    }
                },
                "required": [
                    "issue_key",
                    "escalation_level",
                    "reason"
                ]
            },
            "type": "write"
        },
        {
            "name": "jira.sync_external_system",
            "description": "Synchronize issue data with external systems including monitoring tools, chat platforms, and other service management platforms. Supports bidirectional sync, field mapping, and conflict resolution.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "system_name": {
                        "type": "string",
                        "description": "External system to sync with"
                    },
                    "sync_direction": {
                        "type": "string",
                        "description": "Sync direction (inbound, outbound, bidirectional)"
                    },
                    "filter": {
                        "type": "string",
                        "description": "Filter for issues to sync"
                    }
                },
                "required": [
                    "system_name",
                    "sync_direction"
                ]
            },
            "type": "write"
        }
    ],
    "confluence": [
        {
            "name": "confluence.search_content",
            "description": "Search across all Confluence spaces for pages, blog posts, attachments, and comments using full-text search with advanced filtering. Returns content summaries, space information, author details, and relevance scoring. Supports content type filtering, space restrictions, and date-based queries.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    },
                    "type": {
                        "type": "string",
                        "description": "Content type filter (page, blogpost, attachment)"
                    },
                    "space_key": {
                        "type": "string",
                        "description": "Limit search to specific space"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return"
                    }
                },
                "required": [
                    "query"
                ]
            },
            "type": "read"
        },
        {
            "name": "confluence.get_page",
            "description": "Retrieve complete page content including body text, metadata, version history, and space information. Returns structured content with macro expansions, embedded media, and table data. Includes page hierarchy, labels, comments, and attachment listings with access permissions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Confluence page ID"
                    },
                    "expand": {
                        "type": "array",
                        "description": "Additional data to include (body.storage, history, children)"
                    },
                    "version": {
                        "type": "integer",
                        "description": "Specific page version to retrieve"
                    }
                },
                "required": [
                    "page_id"
                ]
            },
            "type": "read"
        },
        {
            "name": "confluence.create_page",
            "description": "Create new documentation pages and runbooks with rich content including tables, macros, embedded media, and cross-references. Supports template-based creation, automatic labeling, and permission inheritance from parent pages. Returns created page details with edit links.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "Space where page will be created"
                    },
                    "title": {
                        "type": "string",
                        "description": "Page title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Page content in storage format"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Parent page ID for hierarchy"
                    }
                },
                "required": [
                    "space_key",
                    "title",
                    "body"
                ]
            },
            "type": "write"
        },
        {
            "name": "confluence.update_page",
            "description": "Update existing page content, metadata, and structure with version control and change tracking. Supports partial content updates, label management, and permission modifications. Maintains complete revision history with diff capabilities and rollback options.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "Page ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "Updated page title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Updated page content"
                    },
                    "version": {
                        "type": "integer",
                        "description": "Current page version for conflict detection"
                    }
                },
                "required": [
                    "page_id",
                    "version"
                ]
            },
            "type": "write"
        },
        {
            "name": "confluence.list_pages",
            "description": "List all pages within a space with filtering and sorting options. Returns page hierarchy, creation dates, author information, and content status. Supports filtering by labels, page status, and creation date ranges. Includes pagination and bulk metadata retrieval.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "Space to list pages from"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum pages to return"
                    },
                    "start": {
                        "type": "integer",
                        "description": "Starting index for pagination"
                    },
                    "expand": {
                        "type": "array",
                        "description": "Additional page data to include"
                    }
                },
                "required": [
                    "space_key"
                ]
            },
            "type": "read"
        },
        {
            "name": "confluence.get_space",
            "description": "Get comprehensive space information including description, homepage, permissions, and content statistics. Returns space configuration, theme settings, user access levels, and content organization structure. Includes recent activity and space-level analytics.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "Space key identifier"
                    },
                    "expand": {
                        "type": "array",
                        "description": "Additional space data (description, homepage, permissions)"
                    }
                },
                "required": [
                    "space_key"
                ]
            },
            "type": "read"
        },
        {
            "name": "confluence.create_space",
            "description": "Create new Confluence spaces with customizable templates, permissions, and initial content structure. Supports space categories, homepage creation, and user group assignments. Returns space configuration and access URLs.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Unique space key"
                    },
                    "name": {
                        "type": "string",
                        "description": "Space name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Space description"
                    },
                    "template": {
                        "type": "string",
                        "description": "Space template to use"
                    }
                },
                "required": [
                    "key",
                    "name"
                ]
            },
            "type": "write"
        },
        {
            "name": "confluence.manage_space_permissions",
            "description": "Configure space-level permissions including view, edit, delete, and admin access for users and groups. Supports permission inheritance, role-based access control, and audit logging. Returns current permission matrix and change history.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "Space to configure"
                    },
                    "permissions": {
                        "type": "array",
                        "description": "Permission changes to apply"
                    },
                    "users": {
                        "type": "array",
                        "description": "Users to grant/revoke permissions"
                    },
                    "groups": {
                        "type": "array",
                        "description": "Groups to grant/revoke permissions"
                    }
                },
                "required": [
                    "space_key",
                    "permissions"
                ]
            },
            "type": "write"
        },
        {
            "name": "confluence.manage_templates",
            "description": "Create, modify, and manage page templates for consistent content creation. Supports global and space-specific templates with variable substitution, form fields, and conditional content. Returns template usage statistics and version history.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "description": "Name of the template"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (create, update, delete, list)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Template content"
                    },
                    "space_key": {
                        "type": "string",
                        "description": "Space scope for template"
                    }
                },
                "required": [
                    "template_name",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "confluence.manage_labels",
            "description": "Create, apply, and manage labels for content organization and discovery. Supports hierarchical labeling, auto-labeling rules, and label analytics. Returns label usage statistics and content associations.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "Content to label"
                    },
                    "labels": {
                        "type": "array",
                        "description": "Labels to add or remove"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (add, remove, list)"
                    }
                },
                "required": [
                    "labels",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "confluence.get_analytics",
            "description": "Retrieve comprehensive analytics including page views, user engagement, content performance, and space activity. Supports trend analysis, user behavior tracking, and content optimization recommendations.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "Space for analytics"
                    },
                    "metric_type": {
                        "type": "string",
                        "description": "Type of metrics to retrieve"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for analysis"
                    }
                },
                "required": [
                    "metric_type",
                    "time_range"
                ]
            },
            "type": "read"
        },
        {
            "name": "confluence.export_content",
            "description": "Export Confluence content in various formats including PDF, Word, XML, and HTML. Supports bulk export, custom styling, and automated scheduling. Returns export status and download links.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content_ids": {
                        "type": "array",
                        "description": "Content to export"
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format (PDF, DOCX, HTML, XML)"
                    },
                    "include_attachments": {
                        "type": "boolean",
                        "description": "Include file attachments"
                    },
                    "styling": {
                        "type": "object",
                        "description": "Custom styling options"
                    }
                },
                "required": [
                    "content_ids",
                    "format"
                ]
            },
            "type": "read"
        }
    ],
    "m365": [
        {
            "name": "m365.search_email",
            "description": "Search across Exchange Online mailboxes for email messages and conversations with advanced filtering capabilities. Returns message summaries, sender/recipient information, timestamps, and attachment details. Supports complex queries with date ranges, folder restrictions, and content-based filtering.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Email search query"
                    },
                    "folder": {
                        "type": "string",
                        "description": "Specific folder to search (Inbox, Sent, etc.)"
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Search emails from this date"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "Search emails to this date"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum emails to return"
                    }
                },
                "required": [
                    "query"
                ]
            },
            "type": "read"
        },
        {
            "name": "m365.send_email",
            "description": "Send executive notifications, leadership communication, and critical system alerts through Exchange Online for system outages and service disruptions. Supports rich formatting, attachment support, delivery confirmation, executive briefings, and incident status updates. Supports bulk sending, template-based emails, and integration with organizational policies. Handles priority levels, read receipts, compliance requirements, and executive escalation workflows.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "array",
                        "description": "List of recipient email addresses"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content (HTML supported)"
                    },
                    "cc": {
                        "type": "array",
                        "description": "CC recipients"
                    },
                    "bcc": {
                        "type": "array",
                        "description": "BCC recipients"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Email priority (High, Normal, Low)"
                    }
                },
                "required": [
                    "to",
                    "subject",
                    "body"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.manage_mailbox",
            "description": "Administer Exchange Online mailboxes including quota management, folder permissions, and retention policies. Supports mailbox migration, backup/restore operations, and compliance configuration. Returns mailbox statistics and configuration details.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mailbox": {
                        "type": "string",
                        "description": "Mailbox identifier"
                    },
                    "action": {
                        "type": "string",
                        "description": "Management action to perform"
                    },
                    "settings": {
                        "type": "object",
                        "description": "Mailbox settings to modify"
                    }
                },
                "required": [
                    "mailbox",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.get_calendar",
            "description": "Retrieve calendar events and meeting information from Outlook calendars with detailed attendee lists, recurring event handling, and room/resource booking details. Returns event summaries, locations, time zones, and meeting response status. Supports multiple calendar views and filtering options.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Start time for calendar lookup"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time for calendar lookup"
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Specific calendar ID"
                    },
                    "include_recurring": {
                        "type": "boolean",
                        "description": "Include recurring event instances"
                    }
                },
                "required": [
                    "start_time",
                    "end_time"
                ]
            },
            "type": "read"
        },
        {
            "name": "m365.create_event",
            "description": "Create calendar events and meetings in Outlook with comprehensive scheduling features including attendee management, room booking, recurring events, and meeting options. Supports Teams meeting integration, resource allocation, and automated invitation sending with rich meeting details.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Meeting subject"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Meeting start time (ISO format)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Meeting end time (ISO format)"
                    },
                    "attendees": {
                        "type": "array",
                        "description": "List of attendee email addresses"
                    },
                    "location": {
                        "type": "string",
                        "description": "Meeting location or room"
                    },
                    "body": {
                        "type": "string",
                        "description": "Meeting description/agenda"
                    }
                },
                "required": [
                    "subject",
                    "start_time",
                    "end_time"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.manage_room_booking",
            "description": "Book and manage conference rooms and resources with availability checking, equipment requests, and catering coordination. Supports recurring bookings, resource conflicts resolution, and booking policies enforcement.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "room_email": {
                        "type": "string",
                        "description": "Room resource email"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Booking start time"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Booking end time"
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Meeting purpose"
                    },
                    "equipment": {
                        "type": "array",
                        "description": "Required equipment"
                    }
                },
                "required": [
                    "room_email",
                    "start_time",
                    "end_time"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.search_teams",
            "description": "Search Microsoft Teams chat messages, channel conversations, and shared files across teams and channels. Returns message content, author information, timestamps, reactions, and thread context. Supports filtering by team, channel, date range, and message type with compliance and retention awareness.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Teams search query"
                    },
                    "team_id": {
                        "type": "string",
                        "description": "Specific team to search"
                    },
                    "channel_id": {
                        "type": "string",
                        "description": "Specific channel to search"
                    },
                    "message_type": {
                        "type": "string",
                        "description": "Filter by message type (chat, channel, meeting)"
                    }
                },
                "required": [
                    "query"
                ]
            },
            "type": "read"
        },
        {
            "name": "m365.send_teams_message",
            "description": "Send messages to Microsoft Teams channels or direct chats with rich formatting, @mentions, file attachments, and adaptive card support. Handles message threading, reactions, and integration with Teams apps and workflows. Supports both personal and channel communications.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Teams channel ID for channel messages"
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "Chat ID for direct messages"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content"
                    },
                    "mentions": {
                        "type": "array",
                        "description": "Users to @mention"
                    }
                },
                "required": [
                    "message"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.manage_teams",
            "description": "Create, configure, and manage Microsoft Teams including member management, channel creation, app installation, and policy enforcement. Supports team templates, guest access, and integration with Azure AD groups.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team to manage"
                    },
                    "action": {
                        "type": "string",
                        "description": "Management action"
                    },
                    "settings": {
                        "type": "object",
                        "description": "Team settings to modify"
                    },
                    "members": {
                        "type": "array",
                        "description": "Members to add/remove"
                    }
                },
                "required": [
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.manage_sharepoint_sites",
            "description": "Create, configure, and manage SharePoint sites including document libraries, lists, permissions, and site collections. Supports site templates, hub site associations, and content migration. Returns site statistics and configuration details.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "site_url": {
                        "type": "string",
                        "description": "SharePoint site URL"
                    },
                    "action": {
                        "type": "string",
                        "description": "Management action"
                    },
                    "settings": {
                        "type": "object",
                        "description": "Site settings to modify"
                    }
                },
                "required": [
                    "site_url",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.search_sharepoint_content",
            "description": "Search across SharePoint sites for documents, lists, and content with comprehensive filtering and relevance ranking. Returns content summaries, metadata, author information, and access permissions. Supports advanced query syntax and result refinement.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "site_url": {
                        "type": "string",
                        "description": "Specific site to search"
                    },
                    "content_types": {
                        "type": "array",
                        "description": "Content types to include"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return"
                    }
                },
                "required": [
                    "query"
                ]
            },
            "type": "read"
        },
        {
            "name": "m365.get_contacts",
            "description": "Retrieve contact information from Azure Active Directory and personal contact lists including distribution groups, organizational hierarchy, and contact metadata. Returns comprehensive contact details with phone numbers, addresses, titles, and organizational relationships.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Contact search term (name, email, etc.)"
                    },
                    "contact_folder": {
                        "type": "string",
                        "description": "Specific contact folder"
                    },
                    "include_groups": {
                        "type": "boolean",
                        "description": "Include distribution groups"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "m365.manage_user_accounts",
            "description": "Administer Azure AD user accounts including provisioning, license assignment, group membership, and authentication settings. Supports bulk operations, automated workflows, and compliance reporting. Returns user status and activity information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User to manage"
                    },
                    "action": {
                        "type": "string",
                        "description": "Management action"
                    },
                    "properties": {
                        "type": "object",
                        "description": "User properties to modify"
                    },
                    "licenses": {
                        "type": "array",
                        "description": "Licenses to assign/remove"
                    }
                },
                "required": [
                    "user_id",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.manage_power_apps",
            "description": "Create, deploy, and manage Power Apps applications with data source connections, user permissions, and environment configuration. Supports app sharing, version control, and usage analytics. Returns app status and performance metrics.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "app_id": {
                        "type": "string",
                        "description": "Power App to manage"
                    },
                    "action": {
                        "type": "string",
                        "description": "Management action"
                    },
                    "settings": {
                        "type": "object",
                        "description": "App settings to modify"
                    }
                },
                "required": [
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "m365.run_power_automate",
            "description": "Execute Power Automate workflows for business process automation including data synchronization, approval workflows, and notification systems. Supports flow triggering, parameter passing, and execution monitoring.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "flow_id": {
                        "type": "string",
                        "description": "Flow to execute"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Input parameters for flow"
                    },
                    "wait_for_completion": {
                        "type": "boolean",
                        "description": "Wait for flow completion"
                    }
                },
                "required": [
                    "flow_id"
                ]
            },
            "type": "write"
        }
    ],
    "datadog": [
        {
            "name": "datadog.query_metrics",
            "description": "Execute advanced time-series metric queries against Datadog monitoring infrastructure with comprehensive aggregation functions, mathematical operations, anomaly detection, and multi-dimensional filtering. Supports complex metric expressions, custom functions, percentile calculations, rate computations, and cross-metric correlation analysis. Provides statistical analysis including trend detection, seasonality analysis, and outlier identification. Includes support for SLI/SLO calculations, capacity planning analytics, and predictive forecasting. Returns enriched metric data with metadata, quality indicators, and contextual information for enterprise observability workflows.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query_specification": {
                        "type": "object",
                        "description": "Comprehensive query specification with metrics, filters, and operations",
                        "properties": {
                            "primary_queries": {
                                "type": "array",
                                "description": "Primary metric queries to execute",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "metric_name": {
                                            "type": "string",
                                            "description": "Datadog metric name with namespace",
                                            "pattern": "^[a-z][a-z0-9_.]*[a-z0-9]$",
                                            "examples": [
                                                "system.cpu.usage",
                                                "application.response_time",
                                                "database.connection_pool.active",
                                                "custom.payment.success_rate"
                                            ]
                                        },
                                        "aggregation_config": {
                                            "type": "object",
                                            "description": "Aggregation configuration for metric processing",
                                            "properties": {
                                                "space_aggregation": {
                                                    "type": "string",
                                                    "description": "Spatial aggregation method across hosts/services",
                                                    "enum": ["avg", "sum", "min", "max", "count", "median", "percentile"]
                                                },
                                                "time_aggregation": {
                                                    "type": "string", 
                                                    "description": "Temporal aggregation method within time windows",
                                                    "enum": ["avg", "sum", "min", "max", "count", "rate", "diff"]
                                                },
                                                "percentile_value": {
                                                    "type": "number",
                                                    "description": "Percentile value when using percentile aggregation",
                                                    "minimum": 0.1,
                                                    "maximum": 99.9
                                                },
                                                "rollup_interval": {
                                                    "type": "integer",
                                                    "description": "Data point interval in seconds",
                                                    "minimum": 1,
                                                    "maximum": 3600
                                                }
                                            },
                                            "required": ["space_aggregation", "time_aggregation"]
                                        },
                                        "filter_expressions": {
                                            "type": "array",
                                            "description": "Tag-based filters and conditions",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "tag_key": {
                                                        "type": "string",
                                                        "description": "Tag key for filtering"
                                                    },
                                                    "operator": {
                                                        "type": "string",
                                                        "enum": ["equals", "not_equals", "in", "not_in", "regex_match"]
                                                    },
                                                    "values": {
                                                        "type": "array",
                                                        "items": {"type": "string"},
                                                        "description": "Filter values"
                                                    }
                                                },
                                                "required": ["tag_key", "operator", "values"]
                                            }
                                        }
                                    },
                                    "required": ["metric_name", "aggregation_config"]
                                },
                                "minItems": 1,
                                "maxItems": 20
                            },
                            "mathematical_operations": {
                                "type": "array",
                                "description": "Mathematical operations to apply across queries",
                                "items": {
                                    "type": "object", 
                                    "properties": {
                                        "operation_type": {
                                            "type": "string",
                                            "enum": ["arithmetic", "function", "comparison", "statistical"]
                                        },
                                        "expression": {
                                            "type": "string",
                                            "description": "Mathematical expression using query variables (a, b, c, etc.)",
                                            "examples": [
                                                "a / b * 100",
                                                "abs(a - b)",
                                                "log10(a)",
                                                "derivative(a)"
                                            ]
                                        },
                                        "result_alias": {
                                            "type": "string",
                                            "description": "Alias for the computed result"
                                        }
                                    },
                                    "required": ["operation_type", "expression"]
                                }
                            }
                        },
                        "required": ["primary_queries"]
                    },
                    "time_range_configuration": {
                        "type": "object",
                        "description": "Comprehensive time range and temporal analysis settings",
                        "properties": {
                            "absolute_time_range": {
                                "type": "object",
                                "description": "Absolute time boundaries",
                                "properties": {
                                    "start_timestamp": {
                                        "type": "integer",
                                        "description": "Start time as Unix timestamp in seconds",
                                        "minimum": 946684800
                                    },
                                    "end_timestamp": {
                                        "type": "integer", 
                                        "description": "End time as Unix timestamp in seconds",
                                        "minimum": 946684800
                                    }
                                },
                                "required": ["start_timestamp", "end_timestamp"]
                            },
                            "relative_time_range": {
                                "type": "object",
                                "description": "Relative time range specification",
                                "properties": {
                                    "duration": {
                                        "type": "string",
                                        "description": "Time duration using standard notation",
                                        "pattern": "^[0-9]+[smhdw]$",
                                        "examples": ["1h", "24h", "7d", "30d", "1w"]
                                    },
                                    "end_reference": {
                                        "type": "string",
                                        "description": "Reference point for end time",
                                        "enum": ["now", "hour_boundary", "day_boundary", "week_boundary"],
                                        "default": "now"
                                    }
                                },
                                "required": ["duration"]
                            },
                            "timezone_settings": {
                                "type": "object",
                                "description": "Timezone handling configuration",
                                "properties": {
                                    "timezone": {
                                        "type": "string",
                                        "description": "IANA timezone identifier",
                                        "default": "UTC",
                                        "examples": ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
                                    },
                                    "dst_handling": {
                                        "type": "string",
                                        "description": "Daylight saving time handling strategy",
                                        "enum": ["standard", "adjust_boundaries", "ignore"],
                                        "default": "standard"
                                    }
                                }
                            }
                        },
                        "oneOf": [
                            {"required": ["absolute_time_range"]},
                            {"required": ["relative_time_range"]}
                        ]
                    },
                    "analysis_options": {
                        "type": "object",
                        "description": "Advanced analysis and enrichment options",
                        "properties": {
                            "anomaly_detection": {
                                "type": "object",
                                "description": "Anomaly detection configuration",
                                "properties": {
                                    "enable_detection": {
                                        "type": "boolean",
                                        "description": "Enable anomaly detection analysis",
                                        "default": False
                                    },
                                    "sensitivity": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high"],
                                        "default": "medium"
                                    },
                                    "algorithm": {
                                        "type": "string",
                                        "enum": ["seasonal", "trend", "outlier", "statistical"],
                                        "default": "seasonal"
                                    }
                                }
                            },
                            "statistical_analysis": {
                                "type": "object",
                                "description": "Statistical computation options",
                                "properties": {
                                    "compute_trends": {
                                        "type": "boolean",
                                        "description": "Calculate trend analysis",
                                        "default": False
                                    },
                                    "correlation_analysis": {
                                        "type": "boolean",
                                        "description": "Perform cross-metric correlation",
                                        "default": False
                                    },
                                    "percentile_bands": {
                                        "type": "array",
                                        "description": "Percentile values to calculate",
                                        "items": {
                                            "type": "number",
                                            "minimum": 1,
                                            "maximum": 99
                                        },
                                        "examples": [[50, 95, 99], [25, 50, 75, 90, 95]]
                                    }
                                }
                            }
                        }
                    },
                    "output_configuration": {
                        "type": "object",
                        "description": "Result formatting and delivery configuration",
                        "properties": {
                            "response_format": {
                                "type": "string",
                                "description": "Output data format",
                                "enum": ["timeseries", "scalar", "table", "summary"],
                                "default": "timeseries"
                            },
                            "data_compression": {
                                "type": "string",
                                "description": "Data compression for large result sets",
                                "enum": ["none", "gzip", "lz4"],
                                "default": "none"
                            },
                            "precision_control": {
                                "type": "object",
                                "description": "Numeric precision and formatting",
                                "properties": {
                                    "decimal_places": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 10,
                                        "default": 3
                                    },
                                    "scientific_notation": {
                                        "type": "boolean",
                                        "description": "Use scientific notation for large/small numbers",
                                        "default": False
                                    }
                                }
                            },
                            "metadata_inclusion": {
                                "type": "object",
                                "description": "Metadata and context information to include",
                                "properties": {
                                    "include_query_metadata": {
                                        "type": "boolean",
                                        "description": "Include query execution metadata",
                                        "default": True
                                    },
                                    "include_data_quality": {
                                        "type": "boolean",
                                        "description": "Include data quality indicators",
                                        "default": True
                                    },
                                    "include_performance_metrics": {
                                        "type": "boolean",
                                        "description": "Include query performance statistics",
                                        "default": False
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["query_specification", "time_range_configuration"],
                "additionalProperties": False
            },
            "type": "read"
        },
        {
            "name": "datadog.get_infrastructure_list",
            "description": "Retrieve comprehensive list of monitored infrastructure including hosts, containers, services, and cloud resources. Returns detailed information about system health, tags, metadata, and current status. Supports filtering by environment, service, or custom tags.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": "Filter expression for infrastructure"
                    },
                    "sort_field": {
                        "type": "string",
                        "description": "Field to sort results by"
                    },
                    "include_muted": {
                        "type": "boolean",
                        "description": "Include muted hosts"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "datadog.get_host_details",
            "description": "Get detailed information about specific hosts including system metrics, installed agents, running processes, and network connections. Returns comprehensive host health status, performance metrics, and configuration details.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "host_name": {
                        "type": "string",
                        "description": "Hostname to query"
                    },
                    "include_metrics": {
                        "type": "boolean",
                        "description": "Include latest metrics"
                    },
                    "include_processes": {
                        "type": "boolean",
                        "description": "Include running processes"
                    }
                },
                "required": [
                    "host_name"
                ]
            },
            "type": "read"
        },
        {
            "name": "datadog.trace_search",
            "description": "Search distributed traces for application performance analysis, request flow error investigation, and HTTP status debugging. Returns trace spans, timing information, error details, and service dependencies. Supports filtering by service, operation, error status, and custom tags for root cause analysis of application failures.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Trace search query"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time for trace search"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time for trace search"
                    },
                    "service": {
                        "type": "string",
                        "description": "Specific service to search"
                    },
                    "operation": {
                        "type": "string",
                        "description": "Specific operation to search"
                    }
                },
                "required": [
                    "query",
                    "start_time",
                    "end_time"
                ]
            },
            "type": "read"
        },
        {
            "name": "datadog.get_service_map",
            "description": "Retrieve service dependency map showing relationships between microservices, external dependencies, and data flow patterns. Returns service topology, performance metrics, and error rates for each service connection.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service to center map around"
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environment filter"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for service map data"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "datadog.analyze_service_performance", 
            "description": "Analyze service performance including latency percentiles, HTTP error rates, request throughput, and resource utilization during application processing. Provides performance baseline comparison, anomaly detection, root cause analysis for service errors, and optimization recommendations for system performance.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Service to analyze"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Analysis time period"
                    },
                    "comparison_period": {
                        "type": "string",
                        "description": "Baseline period for comparison"
                    }
                },
                "required": [
                    "service_name",
                    "time_range"
                ]
            },
            "type": "read"
        },
        {
            "name": "datadog.create_monitor",
            "description": "Create custom monitors for infrastructure and application alerting with complex conditions, multi-alert support, and escalation policies. Supports threshold-based, anomaly detection, and forecasting monitors with customizable notification channels.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Monitor type (metric, anomaly, forecast, etc.)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Monitor query definition"
                    },
                    "name": {
                        "type": "string",
                        "description": "Monitor name"
                    },
                    "message": {
                        "type": "string",
                        "description": "Alert message template"
                    },
                    "thresholds": {
                        "type": "object",
                        "description": "Alert thresholds"
                    },
                    "notification_channels": {
                        "type": "array",
                        "description": "Notification channels"
                    }
                },
                "required": [
                    "type",
                    "query",
                    "name",
                    "message"
                ]
            },
            "type": "write"
        },
        {
            "name": "datadog.get_monitor_status",
            "description": "Retrieve current status and history for monitors including alert states, trigger events, and resolution information. Returns detailed monitor health, performance metrics, and notification logs with troubleshooting information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "monitor_id": {
                        "type": "string",
                        "description": "Specific monitor to check"
                    },
                    "group_states": {
                        "type": "array",
                        "description": "Monitor group states to filter"
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter monitors by name"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "datadog.manage_monitor_downtime",
            "description": "Schedule and manage monitor downtime periods for maintenance windows, deployments, or testing. Supports recurring downtime schedules, partial monitor muting, and automated downtime management.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Downtime action (create, update, cancel)"
                    },
                    "scope": {
                        "type": "array",
                        "description": "Monitors or tags to apply downtime"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Downtime start time"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Downtime end time"
                    },
                    "message": {
                        "type": "string",
                        "description": "Downtime reason/message"
                    }
                },
                "required": [
                    "action",
                    "scope",
                    "start_time"
                ]
            },
            "type": "write"
        },
        {
            "name": "datadog.search_logs", 
            "description": "Search and analyze log data for error investigation, application failures, HTTP status code analysis, and system debugging. Returns log events with context, metadata, and statistical analysis. Supports complex queries, time-based filtering, log correlation, and root cause analysis for service errors and performance issues.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Log search query"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time for log search"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time for log search"
                    },
                    "index": {
                        "type": "string",
                        "description": "Log index to search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum logs to return"
                    }
                },
                "required": [
                    "query",
                    "start_time",
                    "end_time"
                ]
            },
            "type": "read"
        },
        {
            "name": "datadog.create_log_pipeline",
            "description": "Create and configure log processing pipelines for data transformation, enrichment, and routing. Supports custom processors, filtering rules, and output destinations. Returns pipeline configuration and processing statistics.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Pipeline name"
                    },
                    "filter": {
                        "type": "object",
                        "description": "Log filter criteria"
                    },
                    "processors": {
                        "type": "array",
                        "description": "Processing steps"
                    },
                    "is_enabled": {
                        "type": "boolean",
                        "description": "Enable pipeline immediately"
                    }
                },
                "required": [
                    "name",
                    "filter",
                    "processors"
                ]
            },
            "type": "write"
        },
        {
            "name": "datadog.create_dashboard",
            "description": "Create custom dashboards with widgets for metrics visualization, log analysis, and service monitoring. Supports multiple widget types, template variables, and sharing permissions. Returns dashboard configuration and access URLs.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Dashboard title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Dashboard description"
                    },
                    "widgets": {
                        "type": "array",
                        "description": "Dashboard widgets configuration"
                    },
                    "template_variables": {
                        "type": "array",
                        "description": "Template variables"
                    }
                },
                "required": [
                    "title",
                    "widgets"
                ]
            },
            "type": "write"
        },
        {
            "name": "datadog.get_dashboard_data",
            "description": "Retrieve data for existing dashboards including widget values, time-series data, and current status information. Supports data export, snapshot generation, and automated reporting.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dashboard_id": {
                        "type": "string",
                        "description": "Dashboard to retrieve"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for data"
                    },
                    "template_variables": {
                        "type": "object",
                        "description": "Template variable values"
                    }
                },
                "required": [
                    "dashboard_id"
                ]
            },
            "type": "read"
        }
    ],
    "pagerduty": [
        {
            "name": "pagerduty.create_incident",
            "description": "Create new incident alert with comprehensive details including severity, team, service association, and initial responder assignment. Supports automatic escalation triggers, stakeholder notifications, and integration with external monitoring systems. Returns incident details and response team assignments.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Incident title"
                    },
                    "service_id": {
                        "type": "string",
                        "description": "Service associated with incident"
                    },
                    "urgency": {
                        "type": "string",
                        "description": "Incident urgency (high, low)"
                    },
                    "body": {
                        "type": "string",
                        "description": "Incident description"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Initial assignee user ID"
                    },
                    "escalation_policy": {
                        "type": "string",
                        "description": "Escalation policy to use"
                    }
                },
                "required": [
                    "title",
                    "service_id",
                    "urgency"
                ]
            },
            "type": "write"
        },
        {
            "name": "pagerduty.get_incidents",
            "description": "Retrieve incidents with comprehensive filtering and sorting options. Returns incident details, timeline, responder information, and resolution status. Supports filtering by service, urgency, status, time range, and team assignment.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "array",
                        "description": "Incident status filter (triggered, acknowledged, resolved)"
                    },
                    "service_ids": {
                        "type": "array",
                        "description": "Filter by specific services"
                    },
                    "urgency": {
                        "type": "string",
                        "description": "Filter by urgency level"
                    },
                    "since": {
                        "type": "string",
                        "description": "Start time for incident search"
                    },
                    "until": {
                        "type": "string",
                        "description": "End time for incident search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum incidents to return"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "pagerduty.update_incident",
            "description": "Update incident status, assignments, priority, and other properties with comprehensive change tracking and notification management. Supports bulk updates, automated workflows, and stakeholder communication.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "string",
                        "description": "Incident to update"
                    },
                    "status": {
                        "type": "string",
                        "description": "New incident status"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "New assignee"
                    },
                    "urgency": {
                        "type": "string",
                        "description": "Updated urgency"
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Resolution notes"
                    }
                },
                "required": [
                    "incident_id"
                ]
            },
            "type": "write"
        },
        {
            "name": "pagerduty.add_incident_note",
            "description": "Add detailed notes and updates to incidents including investigation findings, action items, and status updates. Supports rich text formatting, file attachments, and automatic timeline integration.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "string",
                        "description": "Incident to add note to"
                    },
                    "content": {
                        "type": "string",
                        "description": "Note content"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Note channel (web, api, manual)"
                    }
                },
                "required": [
                    "incident_id",
                    "content"
                ]
            },
            "type": "write"
        },
        {
            "name": "pagerduty.get_oncall_schedule",
            "description": "Retrieve current and upcoming on-call schedules with detailed coverage information, escalation levels, and override details. Returns schedule entries, rotation patterns, and coverage gaps with notification preferences.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "schedule_id": {
                        "type": "string",
                        "description": "Specific schedule to query"
                    },
                    "since": {
                        "type": "string",
                        "description": "Start time for schedule lookup"
                    },
                    "until": {
                        "type": "string",
                        "description": "End time for schedule lookup"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by specific user"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "pagerduty.create_override",
            "description": "Create temporary on-call schedule overrides for coverage during absences, special events, or maintenance windows. Supports recurring overrides, partial coverage, and automatic notifications to affected team members.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "schedule_id": {
                        "type": "string",
                        "description": "Schedule to override"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User taking over on-call"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Override start time"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Override end time"
                    }
                },
                "required": [
                    "schedule_id",
                    "user_id",
                    "start_time",
                    "end_time"
                ]
            },
            "type": "write"
        },
        {
            "name": "pagerduty.manage_escalation_policy",
            "description": "Create and configure escalation policies defining response procedures, timeout intervals, and escalation levels. Supports complex escalation rules, notification methods, and integration with team structures.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action (create, update, delete)"
                    },
                    "policy_name": {
                        "type": "string",
                        "description": "Escalation policy name"
                    },
                    "escalation_rules": {
                        "type": "array",
                        "description": "Escalation rule configuration"
                    },
                    "num_loops": {
                        "type": "integer",
                        "description": "Number of escalation loops"
                    }
                },
                "required": [
                    "action",
                    "policy_name",
                    "escalation_rules"
                ]
            },
            "type": "write"
        },
        {
            "name": "pagerduty.get_services",
            "description": "List all services with configuration details, integration status, and incident statistics. Returns service health metrics, escalation policy associations, and team ownership information with maintenance status.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "team_ids": {
                        "type": "array",
                        "description": "Filter by specific teams"
                    },
                    "include": {
                        "type": "array",
                        "description": "Additional data to include"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query for services"
                    }
                },
                "required": []
            },
            "type": "read"
        },
        {
            "name": "pagerduty.create_service",
            "description": "Create new services for incident management with integration setup, escalation policy assignment, and team ownership configuration. Supports service dependencies, maintenance windows, and monitoring integration.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Service name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Service description"
                    },
                    "escalation_policy_id": {
                        "type": "string",
                        "description": "Associated escalation policy"
                    },
                    "alert_creation": {
                        "type": "string",
                        "description": "Alert creation mode"
                    }
                },
                "required": [
                    "name",
                    "escalation_policy_id"
                ]
            },
            "type": "write"
        },
        {
            "name": "pagerduty.manage_service_dependencies",
            "description": "Configure and manage service dependencies for impact analysis and cascading incident management. Supports dependency mapping, impact assessment, and automated incident correlation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "string",
                        "description": "Service to configure"
                    },
                    "dependencies": {
                        "type": "array",
                        "description": "Service dependencies"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (add, remove, update)"
                    }
                },
                "required": [
                    "service_id",
                    "dependencies",
                    "action"
                ]
            },
            "type": "write"
        },
        {
            "name": "pagerduty.get_analytics",
            "description": "Retrieve comprehensive analytics including incident metrics, response times, service performance, and team effectiveness. Provides trend analysis, benchmark comparisons, and performance optimization recommendations.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "metric_type": {
                        "type": "string",
                        "description": "Type of analytics to retrieve"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Analytics filters"
                    },
                    "aggregate_unit": {
                        "type": "string",
                        "description": "Time aggregation unit"
                    },
                    "time_zone": {
                        "type": "string",
                        "description": "Timezone for results"
                    }
                },
                "required": [
                    "metric_type"
                ]
            },
            "type": "read"
        },
        {
            "name": "pagerduty.generate_incident_report",
            "description": "Generate detailed incident reports including timeline analysis, response effectiveness, and lessons learned. Supports custom report templates, automated scheduling, and stakeholder distribution.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "incident_id": {
                        "type": "string",
                        "description": "Specific incident to report on"
                    },
                    "date_range": {
                        "type": "object",
                        "description": "Date range for report"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report to generate"
                    },
                    "include_metrics": {
                        "type": "boolean",
                        "description": "Include performance metrics"
                    }
                },
                "required": [
                    "date_range",
                    "report_type"
                ]
            },
            "type": "read"
        },
        {
            "name": "pagerduty.manage_integrations",
            "description": "Configure and manage integrations with monitoring tools, ticketing systems, and communication platforms. Supports integration health monitoring, configuration validation, and automated setup.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "string",
                        "description": "Service for integration"
                    },
                    "integration_type": {
                        "type": "string",
                        "description": "Type of integration"
                    },
                    "action": {
                        "type": "string",
                        "description": "Integration action"
                    },
                    "configuration": {
                        "type": "object",
                        "description": "Integration configuration"
                    }
                },
                "required": [
                    "service_id",
                    "integration_type",
                    "action"
                ]
            },
            "type": "write"
        }
    ],
    "zendesk": [
        {
"name": "zendesk.search_tickets",
"description": "Search tickets by customer, status, tags, priority, requester, assignee, custom fields, and time windows. Useful for triage and account overviews.",
"inputSchema": {
"type": "object",
"properties": {
"query": {
"type": "string",
"description": "Zendesk search query (supports field operators, e.g., status:open tags:vip"
},
"page": {
"type": "integer",
"description": "Page number for pagination"
},
"per_page": {
"type": "integer",
"description": "Results per page (max per API limits)"
},
"sort_by": {
"type": "string",
"description": "Sort field (e.g., created_at, updated_at, priority)"
},
"sort_order": {
"type": "string",
"description": "asc or desc"
}
},
"required": [
"query"
]
},
"type": "read"
},
{
"name": "zendesk.create_ticket",
"description": "Create a Zendesk ticket for customer requests, onboarding tasks, or proactive outreach.",
"inputSchema": {
"type": "object",
"properties": {
"subject": { "type": "string", "description": "Ticket subject" },
"comment": { "type": "string", "description": "Initial public comment" },
"requester_id": { "type": "string", "description": "Requester user ID" },
"assignee_id": { "type": "string", "description": "Assignee user ID" },
"priority": { "type": "string", "description": "Priority (low, normal, high, urgent)" },
"status": { "type": "string", "description": "Initial status (new, open, pending, on-hold)" },
"tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to attach" },
"custom_fields": { "type": "object", "description": "Custom field id:value map" }
},
"required": [
"subject",
"comment",
"requester_id"
]
},
"type": "write"
},
{
"name": "zendesk.update_ticket",
"description": "Update a ticket’s status, priority, fields, assignee, priority, or add tags. Supports internal/public comments.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID to update" },
"status": { "type": "string", "description": "new, open, pending, on-hold, solved, closed" },
"priority": { "type": "string", "description": "low, normal, high, urgent" },
"assignee_id": { "type": "string", "description": "New assignee user ID" },
"group_id": { "type": "string", "description": "Assign to a group" },
"tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to add" },
"remove_tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to remove" },
"custom_fields": { "type": "object", "description": "Custom field id:value map" },
"public_comment": { "type": "string", "description": "Public reply to requester" },
"internal_note": { "type": "string", "description": "Private note for agents only" }
},
"required": [
"ticket_id"
]
},
"type": "write"
},
{
"name": "zendesk.add_internal_note",
"description": "Add a private internal note to a ticket (e.g., account context, renewal details, escalation notes).",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"note": { "type": "string", "description": "Private note content" },
"author_id": { "type": "string", "description": "Agent user ID authoring the note" }
},
"required": [
"ticket_id",
"note"
]
},
"type": "write"
},
{
"name": "zendesk.list_views",
"description": "List Zendesk views available to the current user to understand queues and workload.",
"inputSchema": {
"type": "object",
"properties": {
"include_tickets_count": { "type": "boolean", "description": "If true, include counts per view" }
}
},
"type": "read"
},
{
"name": "zendesk.get_view_tickets",
"description": "Retrieve tickets belonging to a specific view (e.g., ‘VIP pending’, ‘Renewals this month’).",
"inputSchema": {
"type": "object",
"properties": {
"view_id": { "type": "string", "description": "View ID" },
"page": { "type": "integer", "description": "Page number" },
"per_page": { "type": "integer", "description": "Results per page" }
},
"required": [
"view_id"
]
},
"type": "read"
},
{
"name": "zendesk.bulk_update_tickets",
"description": "Bulk update ticket fields, status, assignees, and tags—useful for campaign follow-ups or mass reassignments.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_ids": { "type": "array", "items": { "type": "string" }, "description": "Ticket IDs to update" },
"status": { "type": "string", "description": "Set a new status" },
"assignee_id": { "type": "string", "description": "Assign to an agent" },
"tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to add" },
"remove_tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to remove" },
"custom_fields": { "type": "object", "description": "Custom field id:value map" }
},
"required": [
"ticket_ids"
]
},
"type": "write"
},
{
"name": "zendesk.apply_macro",
"description": "Apply a macro to a ticket to standardize responses or field updates.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"macro_id": { "type": "string", "description": "Macro ID to apply" },
"placeholders": { "type": "object", "description": "Optional placeholder variables to fill" }
},
"required": [
"ticket_id",
"macro_id"
]
},
"type": "write"
},
{
"name": "zendesk.list_macros",
"description": "List available macros for the current user or group to speed up responses.",
"inputSchema": {
"type": "object",
"properties": {
"scope": { "type": "string", "description": "personal, shared, group" },
"page": { "type": "integer", "description": "Page number" },
"per_page": { "type": "integer", "description": "Results per page" }
}
},
"type": "read"
},
{
"name": "zendesk.users.get",
"description": "Retrieve a user by id or email to view contact details, roles, and identity mapping.",
"inputSchema": {
"type": "object",
"properties": {
"user_id": { "type": "string", "description": "Zendesk user ID" },
"email": { "type": "string", "description": "User email (alternative to user_id)" }
}
},
"type": "read"
},
{
"name": "zendesk.users.update",
"description": "Update user properties such as role, tags, notes, or custom fields (e.g., success plan tier).",
"inputSchema": {
"type": "object",
"properties": {
"user_id": { "type": "string", "description": "Zendesk user ID" },
"name": { "type": "string", "description": "Display name" },
"role": { "type": "string", "description": "end-user, agent, admin" },
"tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to add" },
"remove_tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to remove" },
"custom_fields": { "type": "object", "description": "Custom field id:value map" },
"notes": { "type": "string", "description": "Internal notes about the user" }
},
"required": [
"user_id"
]
},
"type": "write"
},
{
"name": "zendesk.organizations.get",
"description": "Fetch organization details including domains, notes, custom fields, satisfaction, and ticket history summary.",
"inputSchema": {
"type": "object",
"properties": {
"organization_id": { "type": "string", "description": "Organization ID" }
},
"required": [
"organization_id"
]
},
"type": "read"
},
{
"name": "zendesk.organizations.update",
"description": "Update organization tags, notes, and custom fields (e.g., ARR, lifecycle stage, CSM owner).",
"inputSchema": {
"type": "object",
"properties": {
"organization_id": { "type": "string", "description": "Organization ID" },
"tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to add" },
"remove_tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to remove" },
"notes": { "type": "string", "description": "Internal org notes" },
"custom_fields": { "type": "object", "description": "Custom field id:value map" }
},
"required": [
"organization_id"
]
},
"type": "write"
},
{
"name": "zendesk.ticket_events.get",
"description": "Retrieve a ticket’s event audit trail for timeline analyses and escalation reviews.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"page": { "type": "integer", "description": "Page number" }
},
"required": [
"ticket_id"
]
},
"type": "read"
},
{
"name": "zendesk.escalate_ticket",
"description": "Escalate a ticket to a higher-tier group, add critical tags, and notify stakeholders.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"target_group_id": { "type": "string", "description": "Escalation group ID" },
"reason": { "type": "string", "description": "Reason/context for escalation" },
"notify_user_ids": { "type": "array", "items": { "type": "string" }, "description": "Agent IDs to @notify" },
"add_tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to add on escalation" }
},
"required": [
"ticket_id",
"target_group_id",
"reason"
]
},
"type": "write"
},
{
"name": "zendesk.satisfaction.list",
"description": "List CSAT survey results and ratings by ticket, requester, or time window.",
"inputSchema": {
"type": "object",
"properties": {
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"requester_id": { "type": "string", "description": "Filter by requester" },
"organization_id": { "type": "string", "description": "Filter by organization" },
"score": { "type": "string", "description": "good or bad" },
"page": { "type": "integer", "description": "Page number" }
}
},
"type": "read"
},
{
"name": "zendesk.satisfaction.request_survey",
"description": "Trigger or resend a satisfaction survey for a solved ticket (subject to Zendesk settings).",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Solved ticket ID" },
"channel": { "type": "string", "description": "email or messenger" }
},
"required": [
"ticket_id"
]
},
"type": "write"
},
{
"name": "zendesk.explore.export_report",
"description": "Export Explore (analytics) dashboards or queries for CSAT, SLA, backlog, and response metrics.",
"inputSchema": {
"type": "object",
"properties": {
"dashboard_id": { "type": "string", "description": "Explore dashboard ID to export" },
"query_id": { "type": "string", "description": "Explore query ID (alternative to dashboard)" },
"format": { "type": "string", "description": "Export format (csv, pdf, json)" },
"filters": { "type": "object", "description": "Key:value filter overrides (e.g., date range, groups)" },
"email_to": { "type": "array", "items": { "type": "string" }, "description": "Optional list of recipients" }
},
"required": [
"format"
]
},
"type": "read"
},
{
"name": "zendesk.manage_sla_policies",
"description": "Create or update SLA policies for response and resolution targets by priority or channel.",
"inputSchema": {
"type": "object",
"properties": {
"action": { "type": "string", "description": "create, update, delete" },
"policy_id": { "type": "string", "description": "SLA policy ID (for update/delete)" },
"name": { "type": "string", "description": "Policy name" },
"targets": { "type": "object", "description": "Target map (e.g., { first_reply_time: '4h', next_reply_time: '8h' })" },
"conditions": { "type": "object", "description": "Ticket conditions for the policy" }
},
"required": [
"action"
]
},
"type": "write"
},
{
"name": "zendesk.triggers.manage",
"description": "Create, enable/disable, or update triggers for routing, notifications, and tagging automation.",
"inputSchema": {
"type": "object",
"properties": {
"action": { "type": "string", "description": "create, update, enable, disable, delete" },
"trigger_id": { "type": "string", "description": "Trigger ID (for update/enable/disable/delete)" },
"name": { "type": "string", "description": "Trigger name" },
"conditions": { "type": "object", "description": "All/any conditions definition" },
"actions": { "type": "array", "items": { "type": "object" }, "description": "List of trigger actions" }
},
"required": [
"action"
]
},
"type": "write"
},
{
"name": "zendesk.automations.manage",
"description": "Create or update time-based automations (e.g., pending > 3 days -> reminder).",
"inputSchema": {
"type": "object",
"properties": {
"action": { "type": "string", "description": "create, update, enable, disable, delete" },
"automation_id": { "type": "string", "description": "Automation ID for modify operations" },
"name": { "type": "string", "description": "Automation name" },
"conditions": { "type": "object", "description": "All/any conditions definition" },
"actions": { "type": "array", "items": { "type": "object" }, "description": "List of automation actions" }
},
"required": [
"action"
]
},
"type": "write"
},
{
"name": "zendesk.views.export",
"description": "Export a view’s results for offline analysis (e.g., backlog by account).",
"inputSchema": {
"type": "object",
"properties": {
"view_id": { "type": "string", "description": "View ID" },
"format": { "type": "string", "description": "csv or json" },
"include_fields": { "type": "array", "items": { "type": "string" }, "description": "Fields to include" }
},
"required": [
"view_id",
"format"
]
},
"type": "read"
},
{
"name": "zendesk.talk.call_logs",
"description": "Retrieve Zendesk Talk call logs for a customer or timeframe to correlate with ticket history.",
"inputSchema": {
"type": "object",
"properties": {
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"caller_number": { "type": "string", "description": "Filter by caller phone" },
"agent_id": { "type": "string", "description": "Filter by agent" },
"page": { "type": "integer", "description": "Page number" }
}
},
"type": "read"
},
{
"name": "zendesk.chat.transcripts",
"description": "Fetch live chat or messaging transcripts for a user, ticket, or timeframe for QBRs and RCA.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Associated ticket ID" },
"visitor_id": { "type": "string", "description": "Visitor/user ID" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" }
}
},
"type": "read"
},
{
"name": "zendesk.help_center.search_articles",
"description": "Search Help Center articles for enablement and self-serve guidance to share with customers.",
"inputSchema": {
"type": "object",
"properties": {
"query": { "type": "string", "description": "Full-text query" },
"locale": { "type": "string", "description": "Locale code (e.g., en-us)" },
"label_names": { "type": "array", "items": { "type": "string" }, "description": "Filter by labels" },
"section_id": { "type": "string", "description": "Restrict to a section" }
},
"required": [
"query"
]
},
"type": "read"
},
{
"name": "zendesk.help_center.create_article",
"description": "Create a Help Center article draft for onboarding guides, FAQs, or playbooks.",
"inputSchema": {
"type": "object",
"properties": {
"section_id": { "type": "string", "description": "Target section ID" },
"title": { "type": "string", "description": "Article title" },
"body": { "type": "string", "description": "HTML or Markdown body" },
"locale": { "type": "string", "description": "Locale code" },
"labels": { "type": "array", "items": { "type": "string" }, "description": "Labels to attach" },
"draft": { "type": "boolean", "description": "Create as draft (true) or publish (false)" }
},
"required": [
"section_id",
"title",
"body",
"locale"
]
},
"type": "write"
},
{
"name": "zendesk.help_center.update_article",
"description": "Update or publish an existing Help Center article (e.g., add release notes, fix steps).",
"inputSchema": {
"type": "object",
"properties": {
"article_id": { "type": "string", "description": "Article ID" },
"title": { "type": "string", "description": "New title" },
"body": { "type": "string", "description": "Updated body" },
"labels": { "type": "array", "items": { "type": "string" }, "description": "Labels to add/replace" },
"draft": { "type": "boolean", "description": "Set draft state" }
},
"required": [
"article_id"
]
},
"type": "write"
},
{
"name": "zendesk.followup.create",
"description": "Create a follow-up ticket from a closed ticket for proactive checks or action items.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Closed ticket ID" },
"subject": { "type": "string", "description": "Follow-up subject" },
"comment": { "type": "string", "description": "Initial public comment" },
"assignee_id": { "type": "string", "description": "Assignee user ID" },
"tags": { "type": "array", "items": { "type": "string" }, "description": "Tags to attach" }
},
"required": [
"ticket_id",
"subject",
"comment"
]
},
"type": "write"
},
{
"name": "zendesk.tags.report",
"description": "Aggregate tag usage across tickets to surface themes (bugs, feature requests, onboarding issues).",
"inputSchema": {
"type": "object",
"properties": {
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"top_n": { "type": "integer", "description": "Limit results to top N tags" },
"organization_id": { "type": "string", "description": "Filter by org" }
}
},
"type": "read"
},
{
"name": "zendesk.workspace.assign_tickets",
"description": "Bulk assign tickets to agents or groups based on rules (round-robin, capacity, specialty).",
"inputSchema": {
"type": "object",
"properties": {
"ticket_ids": { "type": "array", "items": { "type": "string" }, "description": "Tickets to assign" },
"assignee_id": { "type": "string", "description": "Agent user ID" },
"group_id": { "type": "string", "description": "Group ID" },
"strategy": { "type": "string", "description": "round_robin, load_balance, manual" }
},
"required": [
"ticket_ids"
]
},
"type": "write"
},
{
"name": "zendesk.requests.list_for_customer",
"description": "List all requests created by or for a specific customer to prepare for EBR/QBRs.",
"inputSchema": {
"type": "object",
"properties": {
"requester_id": { "type": "string", "description": "Requester user ID" },
"organization_id": { "type": "string", "description": "Filter by organization" },
"status": { "type": "string", "description": "new, open, pending, on-hold, solved, closed" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"page": { "type": "integer", "description": "Page number" }
}
},
"type": "read"
},
{
"name": "zendesk.sunshine.profiles.get",
"description": "Retrieve Sunshine custom profiles (accounts, contacts) to enrich the customer 360 view.",
"inputSchema": {
"type": "object",
"properties": {
"profile_type": { "type": "string", "description": "Type key (e.g., account, contact)" },
"external_id": { "type": "string", "description": "External system identifier" }
},
"required": [
"profile_type",
"external_id"
]
},
"type": "read"
},
{
"name": "zendesk.sunshine.events.list",
"description": "List Sunshine events (e.g., product usage, billing milestones) for an account timeline.",
"inputSchema": {
"type": "object",
"properties": {
"profile_id": { "type": "string", "description": "Profile ID to query events for" },
"event_type": { "type": "string", "description": "Optional event type filter" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"page": { "type": "integer", "description": "Page number" }
},
"required": [
"profile_id"
]
},
"type": "read"
},
{
"name": "zendesk.ticket_side_conversations.create",
"description": "Start a side conversation (email/Slack) with internal/external stakeholders from a ticket.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"channel": { "type": "string", "description": "email or slack" },
"recipients": { "type": "array", "items": { "type": "string" }, "description": "Emails or Slack channel IDs" },
"subject": { "type": "string", "description": "Subject for side conversation" },
"message": { "type": "string", "description": "Message body" },
"private": { "type": "boolean", "description": "Whether to keep transcript internal" }
},
"required": [
"ticket_id",
"channel",
"recipients",
"message"
]
},
"type": "write"
},
{
"name": "zendesk.ticket_attachments.upload",
"description": "Upload and attach files (logs, screenshots, QBR decks) to a ticket.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"file_path": { "type": "string", "description": "Path or reference to file" },
"filename": { "type": "string", "description": "Filename override" },
"content_type": { "type": "string", "description": "MIME type" }
},
"required": [
"ticket_id",
"file_path"
]
},
"type": "write"
},
{
"name": "zendesk.nps.send_survey",
"description": "Send an NPS survey to a list of users or an organization and track responses.",
"inputSchema": {
"type": "object",
"properties": {
"recipient_user_ids": { "type": "array", "items": { "type": "string" }, "description": "Users to survey" },
"organization_id": { "type": "string", "description": "Optional org to survey" },
"campaign_id": { "type": "string", "description": "NPS campaign identifier" },
"channel": { "type": "string", "description": "email, messenger" },
"language": { "type": "string", "description": "Locale for the survey" }
},
"required": [
"campaign_id"
]
},
"type": "write"
},
{
"name": "zendesk.nps.results",
"description": "Retrieve NPS results and breakdown (promoters, passives, detractors) over time.",
"inputSchema": {
"type": "object",
"properties": {
"campaign_id": { "type": "string", "description": "Campaign identifier" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"organization_id": { "type": "string", "description": "Filter by org" }
}
},
"type": "read"
},
{
"name": "zendesk.ticket_fields.manage",
"description": "Create or update custom ticket fields used for success plans, churn risk, or onboarding stage.",
"inputSchema": {
"type": "object",
"properties": {
"action": { "type": "string", "description": "create, update, delete" },
"field_id": { "type": "string", "description": "Field ID (for update/delete)" },
"type": { "type": "string", "description": "text, textarea, checkbox, dropdown, date, decimal, integer" },
"title": { "type": "string", "description": "Field display name" },
"key": { "type": "string", "description": "Programmatic key" },
"options": { "type": "array", "items": { "type": "object" }, "description": "Dropdown options if relevant" },
"required_on_statuses": { "type": "array", "items": { "type": "string" }, "description": "Statuses where field is required" }
},
"required": [
"action"
]
},
"type": "write"
},
{
"name": "zendesk.ticket_merge",
"description": "Merge duplicate tickets (e.g., multiple emails from same user) while preserving comments and attachments.",
"inputSchema": {
"type": "object",
"properties": {
"primary_ticket_id": { "type": "string", "description": "Ticket to keep" },
"secondary_ticket_ids": { "type": "array", "items": { "type": "string" }, "description": "Tickets to merge into primary" },
"comment": { "type": "string", "description": "Optional merge note" }
},
"required": [
"primary_ticket_id",
"secondary_ticket_ids"
]
},
"type": "write"
},
{
"name": "zendesk.subscriptions.ticket_updates",
"description": "Subscribe to ticket updates that match a filter and stream changes for real-time account monitoring.",
"inputSchema": {
"type": "object",
"properties": {
"filter_query": { "type": "string", "description": "Search syntax defining which tickets to watch" },
"events": { "type": "array", "items": { "type": "string" }, "description": "created, updated, solved, satisfaction_changed" },
"callback_url": { "type": "string", "description": "Webhook endpoint to receive updates" }
},
"required": [
"filter_query",
"callback_url"
]
},
"type": "read"
},
{
"name": "zendesk.side_load_customer_timeline",
"description": "Compile a customer timeline (tickets, calls, chats, Sunshine events) for QBR/EBR packets.",
"inputSchema": {
"type": "object",
"properties": {
"organization_id": { "type": "string", "description": "Organization to compile" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"include_channels": { "type": "array", "items": { "type": "string" }, "description": "tickets, talk, chat, sunshine" }
},
"required": [
"organization_id"
]
},
"type": "read"
},
{
"name": "zendesk.integrations.link_ticket",
"description": "Link a Zendesk ticket to external systems (e.g., Jira issue, Salesforce case) and sync metadata.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Zendesk ticket ID" },
"external_system": { "type": "string", "description": "jira, salesforce, linear, github" },
"external_id": { "type": "string", "description": "External record ID" },
"sync_fields": { "type": "object", "description": "Field map for synchronization" }
},
"required": [
"ticket_id",
"external_system",
"external_id"
]
},
"type": "write"
},
{
"name": "zendesk.schedule_qbr_report",
"description": "Generate and schedule a QBR/EBR packet using Zendesk Explore and Help Center content for a given account.",
"inputSchema": {
"type": "object",
"properties": {
"organization_id": { "type": "string", "description": "Account to report on" },
"date_range": { "type": "object", "description": "Time window for metrics and activity" },
"include_sections": { "type": "array", "items": { "type": "string" }, "description": "tickets, csat, nps, sla, themes, changelog" },
"delivery": { "type": "object", "description": "Schedule and recipients (cron or RRULE, emails)" },
"format": { "type": "string", "description": "pdf or pptx" }
},
"required": [
"organization_id",
"date_range"
]
},
"type": "read"
},
{
"name": "zendesk.requests.create_onboarding",
"description": "Create a structured onboarding request set (tickets + tasks) for a new customer with templates.",
"inputSchema": {
"type": "object",
"properties": {
"organization_id": { "type": "string", "description": "Customer organization ID" },
"owner_id": { "type": "string", "description": "CSM owner user ID" },
"template_id": { "type": "string", "description": "Onboarding template to use" },
"due_date": { "type": "string", "description": "Overall due date (ISO8601)" },
"custom_fields": { "type": "object", "description": "Additional field overrides" }
},
"required": [
"organization_id",
"owner_id",
"template_id"
]
},
"type": "write"
},
{
"name": "zendesk.audit_logs.search",
"description": "Search admin audit logs for configuration changes affecting workflows or SLAs.",
"inputSchema": {
"type": "object",
"properties": {
"actor_id": { "type": "string", "description": "Filter by actor (admin/agent) ID" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"event_type": { "type": "string", "description": "Field or object changed" },
"page": { "type": "integer", "description": "Page number" }
}
},
"type": "read"
}
    ],
    "hubspot": [
        {
"name": "hubspot.contacts.search",
"description": "Search contacts by email, name, lifecycle stage, owner, domain, or custom properties.",
"inputSchema": {
"type": "object",
"properties": {
"filters": {
"type": "array",
"description": "List of filter objects (property, operator, value)",
"items": { "type": "object" }
},
"query": { "type": "string", "description": "Free-text query across contact fields" },
"properties": {
"type": "array",
"items": { "type": "string" },
"description": "Specific properties to return"
},
"limit": { "type": "integer", "description": "Max records to return" },
"after": { "type": "string", "description": "Pagination cursor" },
"sorts": {
"type": "array",
"items": { "type": "string" },
"description": "List of sort keys, e.g., -lastmodifieddate"
}
}
},
"type": "read"
},
{
"name": "hubspot.contacts.get",
"description": "Get a single contact by ID or email with selected properties.",
"inputSchema": {
"type": "object",
"properties": {
"contact_id": { "type": "string", "description": "Contact ID" },
"email": { "type": "string", "description": "Contact email (alternative to contact_id)" },
"properties": { "type": "array", "items": { "type": "string" }, "description": "Properties to include" }
}
},
"type": "read"
},
{
"name": "hubspot.contacts.create_or_update",
"description": "Create or update a contact (upsert by email) including custom properties and owner assignment.",
"inputSchema": {
"type": "object",
"properties": {
"email": { "type": "string", "description": "Primary email (used for upsert)" },
"properties": { "type": "object", "description": "Key:value map of contact properties" },
"owner_id": { "type": "string", "description": "HubSpot owner ID" }
},
"required": ["email"]
},
"type": "write"
},
{
"name": "hubspot.contacts.merge",
"description": "Merge a secondary contact into a primary contact, preserving history and associations.",
"inputSchema": {
"type": "object",
"properties": {
"primary_contact_id": { "type": "string", "description": "ID of the contact to keep" },
"secondary_contact_id": { "type": "string", "description": "ID of the contact to merge into primary" }
},
"required": ["primary_contact_id", "secondary_contact_id"]
},
"type": "write"
},
{
"name": "hubspot.companies.search",
"description": "Search companies by name, domain, owner, lifecycle stage, ARR, or custom properties.",
"inputSchema": {
"type": "object",
"properties": {
"filters": { "type": "array", "items": { "type": "object" }, "description": "Filter objects" },
"query": { "type": "string", "description": "Free-text query" },
"properties": { "type": "array", "items": { "type": "string" }, "description": "Properties to return" },
"limit": { "type": "integer", "description": "Max records" },
"after": { "type": "string", "description": "Pagination cursor" },
"sorts": { "type": "array", "items": { "type": "string" }, "description": "Sort keys" }
}
},
"type": "read"
},
{
"name": "hubspot.companies.create_or_update",
"description": "Create or update a company (upsert by domain) and set CSM-related properties (e.g., tier, risk).",
"inputSchema": {
"type": "object",
"properties": {
"domain": { "type": "string", "description": "Company domain (used for upsert)" },
"properties": { "type": "object", "description": "Key:value map of company properties" },
"owner_id": { "type": "string", "description": "HubSpot owner ID" }
},
"required": ["domain"]
},
"type": "write"
},
{
"name": "hubspot.associations.link",
"description": "Create or update associations between records (e.g., contact↔company, ticket↔company).",
"inputSchema": {
"type": "object",
"properties": {
"from_object_type": { "type": "string", "description": "contacts, companies, deals, tickets, custom_object" },
"from_object_id": { "type": "string", "description": "Source object ID" },
"to_object_type": { "type": "string", "description": "contacts, companies, deals, tickets, custom_object" },
"to_object_id": { "type": "string", "description": "Target object ID" },
"association_type": { "type": "string", "description": "Association label/type where applicable" }
},
"required": ["from_object_type", "from_object_id", "to_object_type", "to_object_id"]
},
"type": "write"
},
{
"name": "hubspot.deals.search",
"description": "Search deals by pipeline, stage, amount, renewal date, or company.",
"inputSchema": {
"type": "object",
"properties": {
"filters": { "type": "array", "items": { "type": "object" }, "description": "Filter objects" },
"properties": { "type": "array", "items": { "type": "string" }, "description": "Deal properties to return" },
"limit": { "type": "integer", "description": "Max records" },
"after": { "type": "string", "description": "Pagination cursor" }
}
},
"type": "read"
},
{
"name": "hubspot.deals.create_or_update",
"description": "Create or update a deal (e.g., renewal or expansion) and associate to company/contacts.",
"inputSchema": {
"type": "object",
"properties": {
"properties": { "type": "object", "description": "Deal properties (amount, pipeline, stage, close date)" },
"associations": { "type": "object", "description": "Associations to company/contact IDs" }
},
"required": ["properties"]
},
"type": "write"
},
{
"name": "hubspot.tickets.search",
"description": "Search Service Hub tickets by status, pipeline, SLA, priority, or customer.",
"inputSchema": {
"type": "object",
"properties": {
"filters": { "type": "array", "items": { "type": "object" }, "description": "Filter objects" },
"properties": { "type": "array", "items": { "type": "string" }, "description": "Ticket properties to return" },
"limit": { "type": "integer", "description": "Max records" },
"after": { "type": "string", "description": "Pagination cursor" }
}
},
"type": "read"
},
{
"name": "hubspot.tickets.create_or_update",
"description": "Create or update a ticket and associate it with company, contact, and deal where relevant.",
"inputSchema": {
"type": "object",
"properties": {
"properties": { "type": "object", "description": "Ticket properties (status, priority, pipeline, subject, content)" },
"associations": { "type": "object", "description": "Associations to company/contact/deal IDs" }
},
"required": ["properties"]
},
"type": "write"
},
{
"name": "hubspot.tasks.create",
"description": "Create tasks for follow-ups, onboarding steps, or renewal prep and assign to owners with due dates.",
"inputSchema": {
"type": "object",
"properties": {
"title": { "type": "string", "description": "Task title" },
"notes": { "type": "string", "description": "Task details" },
"due_date": { "type": "string", "description": "ISO8601 due date/time" },
"owner_id": { "type": "string", "description": "HubSpot owner ID" },
"associations": { "type": "object", "description": "Associated record IDs (contact, company, deal, ticket)" },
"priority": { "type": "string", "description": "low, medium, high" }
},
"required": ["title"]
},
"type": "write"
},
{
"name": "hubspot.engagements.log_note",
"description": "Log a note on a contact, company, deal, or ticket (e.g., meeting summary, risk update).",
"inputSchema": {
"type": "object",
"properties": {
"body": { "type": "string", "description": "Note content (plain text or markdown)" },
"associations": { "type": "object", "description": "Record IDs to associate (contact/company/deal/ticket)" },
"timestamp": { "type": "string", "description": "ISO8601 event time (optional)" }
},
"required": ["body", "associations"]
},
"type": "write"
},
{
"name": "hubspot.meetings.create_engagement",
"description": "Create a past or scheduled meeting engagement with attendees and outcomes.",
"inputSchema": {
"type": "object",
"properties": {
"title": { "type": "string", "description": "Meeting title" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"attendee_emails": { "type": "array", "items": { "type": "string" }, "description": "Attendee emails" },
"outcome": { "type": "string", "description": "Scheduled, Completed, No show, etc." },
"associations": { "type": "object", "description": "Associated record IDs" },
"notes": { "type": "string", "description": "Meeting notes" }
},
"required": ["title", "start_time", "end_time"]
},
"type": "write"
},
{
"name": "hubspot.properties.get",
"description": "Get property definitions for a given object type (contacts, companies, deals, tickets, custom).",
"inputSchema": {
"type": "object",
"properties": {
"object_type": { "type": "string", "description": "contacts, companies, deals, tickets, custom_object" }
},
"required": ["object_type"]
},
"type": "read"
},
{
"name": "hubspot.properties.manage",
"description": "Create, update, or archive a property on a standard or custom object.",
"inputSchema": {
"type": "object",
"properties": {
"action": { "type": "string", "description": "create, update, archive" },
"object_type": { "type": "string", "description": "contacts, companies, deals, tickets, custom_object" },
"property_name": { "type": "string", "description": "Internal name (for update/archive)" },
"definition": { "type": "object", "description": "Property schema (label, type, fieldType, options)" }
},
"required": ["action", "object_type"]
},
"type": "write"
},
{
"name": "hubspot.workflows.enroll",
"description": "Enroll records into a HubSpot workflow (e.g., onboarding, renewal nurture, escalation alerts).",
"inputSchema": {
"type": "object",
"properties": {
"workflow_id": { "type": "string", "description": "Workflow ID" },
"object_type": { "type": "string", "description": "contacts, companies, deals, tickets" },
"record_ids": { "type": "array", "items": { "type": "string" }, "description": "IDs to enroll" }
},
"required": ["workflow_id", "object_type", "record_ids"]
},
"type": "write"
},
{
"name": "hubspot.workflows.manage",
"description": "Enable/disable a workflow and update enrollment triggers or actions.",
"inputSchema": {
"type": "object",
"properties": {
"workflow_id": { "type": "string", "description": "Workflow ID" },
"action": { "type": "string", "description": "enable, disable, update" },
"updates": { "type": "object", "description": "Workflow configuration updates" }
},
"required": ["workflow_id", "action"]
},
"type": "write"
},
{
"name": "hubspot.lists.search_static",
"description": "Find or create static lists for outreach cohorts (e.g., VIP customers, at-risk accounts).",
"inputSchema": {
"type": "object",
"properties": {
"query": { "type": "string", "description": "Search by list name" },
"create_if_missing": { "type": "boolean", "description": "Create list if not found" },
"list_name": { "type": "string", "description": "Name for new list" }
}
},
"type": "write"
},
{
"name": "hubspot.lists.add_records",
"description": "Add records (contacts/companies) to a static list by IDs or emails/domains.",
"inputSchema": {
"type": "object",
"properties": {
"list_id": { "type": "string", "description": "Static list ID" },
"object_type": { "type": "string", "description": "contacts or companies" },
"ids": { "type": "array", "items": { "type": "string" }, "description": "Record IDs" },
"identifiers": { "type": "array", "items": { "type": "string" }, "description": "Emails or domains" }
},
"required": ["list_id", "object_type"]
},
"type": "write"
},
{
"name": "hubspot.sequences.enroll_contacts",
"description": "Enroll contacts into a sales/service sequence for onboarding nudges or renewal reminders.",
"inputSchema": {
"type": "object",
"properties": {
"sequence_id": { "type": "string", "description": "Sequence ID" },
"contact_ids": { "type": "array", "items": { "type": "string" }, "description": "Contact IDs to enroll" },
"owner_id": { "type": "string", "description": "Sequence sender/owner" },
"send_immediately": { "type": "boolean", "description": "Start right away if true" }
},
"required": ["sequence_id", "contact_ids"]
},
"type": "write"
},
{
"name": "hubspot.feedback_surveys.send",
"description": "Send CSAT/NPS/CES feedback surveys and associate responses to contacts/companies.",
"inputSchema": {
"type": "object",
"properties": {
"survey_id": { "type": "string", "description": "Feedback survey ID" },
"contact_ids": { "type": "array", "items": { "type": "string" }, "description": "Recipients" },
"channel": { "type": "string", "description": "email, web" },
"locale": { "type": "string", "description": "Locale code (e.g., en)" }
},
"required": ["survey_id", "contact_ids"]
},
"type": "write"
},
{
"name": "hubspot.feedback_surveys.results",
"description": "Retrieve survey results and time-series breakdown for CSAT/NPS/CES.",
"inputSchema": {
"type": "object",
"properties": {
"survey_id": { "type": "string", "description": "Survey ID" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"aggregate": { "type": "boolean", "description": "Return aggregates only if true" }
}
},
"type": "read"
},
{
"name": "hubspot.playbooks.log_call_note",
"description": "Open a playbook and log structured notes to a record (contact/company/deal/ticket).",
"inputSchema": {
"type": "object",
"properties": {
"playbook_id": { "type": "string", "description": "Playbook ID" },
"associations": { "type": "object", "description": "Record associations" },
"responses": { "type": "object", "description": "Captured answers/fields" }
},
"required": ["playbook_id", "associations"]
},
"type": "write"
},
{
"name": "hubspot.quotes.create",
"description": "Create a quote for renewal or expansion and associate to deals/companies/contacts.",
"inputSchema": {
"type": "object",
"properties": {
"deal_id": { "type": "string", "description": "Associated deal ID" },
"line_items": { "type": "array", "items": { "type": "object" }, "description": "Product line items" },
"valid_until": { "type": "string", "description": "ISO8601 expiration" },
"properties": { "type": "object", "description": "Quote properties" }
},
"required": ["deal_id", "line_items"]
},
"type": "write"
},
{
"name": "hubspot.products.list",
"description": "List products and price book entries for packaging renewals or expansions.",
"inputSchema": {
"type": "object",
"properties": {
"query": { "type": "string", "description": "Search by name/SKU" },
"limit": { "type": "integer", "description": "Max results" },
"after": { "type": "string", "description": "Pagination cursor" }
}
},
"type": "read"
},
{
"name": "hubspot.line_items.add_to_deal",
"description": "Attach product line items to a deal (quantity, term, discounts).",
"inputSchema": {
"type": "object",
"properties": {
"deal_id": { "type": "string", "description": "Deal ID" },
"line_items": { "type": "array", "items": { "type": "object" }, "description": "List of line item specs" }
},
"required": ["deal_id", "line_items"]
},
"type": "write"
},
{
"name": "hubspot.pipelines.stages.update",
"description": "Update a pipeline stage (e.g., Deal or Ticket stages) and stage order.",
"inputSchema": {
"type": "object",
"properties": {
"object_type": { "type": "string", "description": "deals or tickets" },
"pipeline_id": { "type": "string", "description": "Pipeline ID" },
"stage_id": { "type": "string", "description": "Stage ID" },
"updates": { "type": "object", "description": "Label, probability, displayOrder, metadata" }
},
"required": ["object_type", "pipeline_id", "stage_id", "updates"]
},
"type": "write"
},
{
"name": "hubspot.reports.export",
"description": "Export a HubSpot report or dashboard to CSV/PDF with optional filters for QBR packs.",
"inputSchema": {
"type": "object",
"properties": {
"dashboard_id": { "type": "string", "description": "Dashboard ID" },
"report_id": { "type": "string", "description": "Report ID (alternative to dashboard)" },
"format": { "type": "string", "description": "csv or pdf" },
"filters": { "type": "object", "description": "Date range, owners, pipelines, etc." },
"email_to": { "type": "array", "items": { "type": "string" }, "description": "Recipients for emailed export" }
},
"required": ["format"]
},
"type": "read"
},
{
"name": "hubspot.timeline.events.list",
"description": "List recent activities across objects (emails, calls, meetings, notes) for an account timeline.",
"inputSchema": {
"type": "object",
"properties": {
"company_id": { "type": "string", "description": "Company ID to anchor the timeline" },
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"limit": { "type": "integer", "description": "Max events to return" }
},
"required": ["company_id"]
},
"type": "read"
},
{
"name": "hubspot.subscription_preferences.update",
"description": "Update a contact’s email subscription preferences (e.g., service updates, renewal reminders).",
"inputSchema": {
"type": "object",
"properties": {
"contact_id": { "type": "string", "description": "Contact ID" },
"subscriptions": { "type": "array", "items": { "type": "object" }, "description": "List of subscription updates" }
},
"required": ["contact_id", "subscriptions"]
},
"type": "write"
},
{
"name": "hubspot.tickets.sla_breaches.report",
"description": "Report on SLA breaches and at-risk tickets by pipeline, owner, or company.",
"inputSchema": {
"type": "object",
"properties": {
"start_time": { "type": "string", "description": "ISO8601 start" },
"end_time": { "type": "string", "description": "ISO8601 end" },
"owner_id": { "type": "string", "description": "Filter by owner ID" },
"company_id": { "type": "string", "description": "Filter by company ID" }
}
},
"type": "read"
},
{
"name": "hubspot.custom_objects.search",
"description": "Search custom objects (e.g., subscriptions, projects, usage) tied to CSM workflows.",
"inputSchema": {
"type": "object",
"properties": {
"object_type": { "type": "string", "description": "Fully qualified name of custom object" },
"filters": { "type": "array", "items": { "type": "object" }, "description": "Filter objects" },
"properties": { "type": "array", "items": { "type": "string" }, "description": "Properties to return" },
"limit": { "type": "integer", "description": "Max records" }
},
"required": ["object_type"]
},
"type": "read"
},
{
"name": "hubspot.custom_objects.create_or_update",
"description": "Create or update a custom object record (e.g., Success Plan, Subscription) and manage associations.",
"inputSchema": {
"type": "object",
"properties": {
"object_type": { "type": "string", "description": "Custom object type" },
"properties": { "type": "object", "description": "Property map" },
"associations": { "type": "object", "description": "Associations to standard/custom objects" },
"id": { "type": "string", "description": "Existing record ID for update" }
},
"required": ["object_type", "properties"]
},
"type": "write"
},
{
"name": "hubspot.integrations.salesforce.sync_status",
"description": "Check Salesforce↔HubSpot sync health for a record or object type (helpful for data parity before QBRs).",
"inputSchema": {
"type": "object",
"properties": {
"object_type": { "type": "string", "description": "contacts, companies, deals" },
"record_id": { "type": "string", "description": "Optional specific record ID" }
},
"required": ["object_type"]
},
"type": "read"
},
{
"name": "hubspot.emails.send_template",
"description": "Send a templated email from a connected inbox to contacts with personalization tokens.",
"inputSchema": {
"type": "object",
"properties": {
"template_id": { "type": "string", "description": "Email template ID" },
"from_owner_id": { "type": "string", "description": "HubSpot owner/sender ID" },
"to_contact_ids": { "type": "array", "items": { "type": "string" }, "description": "Recipient contact IDs" },
"cc": { "type": "array", "items": { "type": "string" }, "description": "CC emails" },
"bcc": { "type": "array", "items": { "type": "string" }, "description": "BCC emails" },
"personalization": { "type": "object", "description": "Token values to merge" },
"attachments": { "type": "array", "items": { "type": "object" }, "description": "Files to attach" }
},
"required": ["template_id", "to_contact_ids"]
},
"type": "write"
},
{
"name": "hubspot.owners.list",
"description": "List HubSpot owners (users) for assignment, territory routing, and reporting.",
"inputSchema": {
"type": "object",
"properties": {
"include_inactive": { "type": "boolean", "description": "Include deactivated owners" }
}
},
"type": "read"
},
{
"name": "hubspot.deals.renewal_forecast",
"description": "Generate a renewal/expansion forecast from deals by close date, stage, and probability.",
"inputSchema": {
"type": "object",
"properties": {
"start_date": { "type": "string", "description": "ISO8601 start" },
"end_date": { "type": "string", "description": "ISO8601 end" },
"pipelines": { "type": "array", "items": { "type": "string" }, "description": "Deal pipeline IDs" },
"include_expansion": { "type": "boolean", "description": "Include upsell/cross-sell" }
}
},
"type": "read"
},
{
"name": "hubspot.tickets.bulk_update",
"description": "Bulk update ticket properties (status, priority, owner) for backlog grooming and triage.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_ids": { "type": "array", "items": { "type": "string" }, "description": "Ticket IDs" },
"properties": { "type": "object", "description": "Properties to set" }
},
"required": ["ticket_ids", "properties"]
},
"type": "write"
},
{
"name": "hubspot.webhooks.subscribe",
"description": "Subscribe a webhook to record changes (tickets, deals, contacts) to power real-time alerts.",
"inputSchema": {
"type": "object",
"properties": {
"object_types": { "type": "array", "items": { "type": "string" }, "description": "Objects to watch" },
"events": { "type": "array", "items": { "type": "string" }, "description": "PropertyChange, Creation, Deletion" },
"callback_url": { "type": "string", "description": "Target webhook endpoint" },
"secret": { "type": "string", "description": "Optional signing secret" }
},
"required": ["object_types", "events", "callback_url"]
},
"type": "read"
},
{
"name": "hubspot.imports.bulk_upsert",
"description": "Import CSV data to upsert contacts/companies/deals/tickets with property mappings.",
"inputSchema": {
"type": "object",
"properties": {
"object_type": { "type": "string", "description": "contacts, companies, deals, tickets" },
"file_path": { "type": "string", "description": "Path to CSV file" },
"mappings": { "type": "object", "description": "CSV column → property name" },
"unique_property": { "type": "string", "description": "Unique key for upsert (e.g., email, domain)" },
"associations": { "type": "object", "description": "Optional association rules" }
},
"required": ["object_type", "file_path", "mappings"]
},
"type": "write"
},
{
"name": "hubspot.ticket_snippets.apply",
"description": "Insert a saved snippet into a ticket reply for standardized responses.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"snippet_id": { "type": "string", "description": "Snippet ID" },
"placeholders": { "type": "object", "description": "Optional placeholder variables" }
},
"required": ["ticket_id", "snippet_id"]
},
"type": "write"
},
{
"name": "hubspot.kb.search_articles",
"description": "Search Knowledge Base articles to share with customers for faster resolution.",
"inputSchema": {
"type": "object",
"properties": {
"query": { "type": "string", "description": "Full-text search" },
"category_id": { "type": "string", "description": "Filter by category" },
"language": { "type": "string", "description": "Language code" },
"limit": { "type": "integer", "description": "Max results" }
},
"required": ["query"]
},
"type": "read"
},
{
"name": "hubspot.success_plans.generate",
"description": "Create or refresh a Success Plan custom object with goals, milestones, owners, and risks.",
"inputSchema": {
"type": "object",
"properties": {
"company_id": { "type": "string", "description": "Company to attach the plan" },
"goals": { "type": "array", "items": { "type": "object" }, "description": "List of goal objects" },
"milestones": { "type": "array", "items": { "type": "object" }, "description": "Key milestones and due dates" },
"risks": { "type": "array", "items": { "type": "object" }, "description": "Known risks with owners/mitigations" }
},
"required": ["company_id"]
},
"type": "write"
},
{
"name": "hubspot.renewals.watchlist.build",
"description": "Compile a watchlist of renewals and risk signals (usage drop, low CSAT, no activity) across accounts.",
"inputSchema": {
"type": "object",
"properties": {
"start_date": { "type": "string", "description": "ISO8601 start for renewal window" },
"end_date": { "type": "string", "description": "ISO8601 end for renewal window" },
"include_risk_signals": { "type": "boolean", "description": "If true, include heuristic risk scoring" },
"pipelines": { "type": "array", "items": { "type": "string" }, "description": "Deal pipelines to include" }
}
},
"type": "read"
},
{
"name": "hubspot.user_events.usage_ingest",
"description": "Upsert product usage or events (by contact or company) into a custom timeline or object.",
"inputSchema": {
"type": "object",
"properties": {
"entity": { "type": "string", "description": "contact or company" },
"entity_id": { "type": "string", "description": "HubSpot ID of entity" },
"events": { "type": "array", "items": { "type": "object" }, "description": "List of usage events" },
"schema": { "type": "object", "description": "Event schema if dynamic" }
},
"required": ["entity", "entity_id", "events"]
},
"type": "write"
},
{
"name": "hubspot.files.upload",
"description": "Upload files (QBR decks, proposals, guides) and associate to records.",
"inputSchema": {
"type": "object",
"properties": {
"file_path": { "type": "string", "description": "Local path to file" },
"folder_path": { "type": "string", "description": "Destination folder path in HubSpot Files" },
"associations": { "type": "object", "description": "Record associations" },
"access": { "type": "string", "description": "PUBLIC_INDEXABLE, PUBLIC_NOT_INDEXABLE, PRIVATE" }
},
"required": ["file_path"]
},
"type": "write"
},
{
"name": "hubspot.tickets.side_conversations.create",
"description": "Start a side conversation (email/Slack) from a ticket and keep transcript in HubSpot.",
"inputSchema": {
"type": "object",
"properties": {
"ticket_id": { "type": "string", "description": "Ticket ID" },
"channel": { "type": "string", "description": "email or slack" },
"recipients": { "type": "array", "items": { "type": "string" }, "description": "Emails or Slack channel IDs" },
"subject": { "type": "string", "description": "Subject line" },
"message": { "type": "string", "description": "Message body" },
"private": { "type": "boolean", "description": "Keep internal if true" }
},
"required": ["ticket_id", "channel", "recipients", "message"]
},
"type": "write"
},
{
"name": "hubspot.alerts.create_risk_alert",
"description": "Create a risk alert (internal task/email) when churn signals are detected for a company.",
"inputSchema": {
"type": "object",
"properties": {
"company_id": { "type": "string", "description": "Company ID" },
"signals": { "type": "array", "items": { "type": "string" }, "description": "Signals (low usage, tickets spiking, unpaid invoice)" },
"notify_owner": { "type": "boolean", "description": "Notify company owner" },
"additional_recipients": { "type": "array", "items": { "type": "string" }, "description": "Extra emails to notify" }
},
"required": ["company_id", "signals"]
},
"type": "write"
}
]
}