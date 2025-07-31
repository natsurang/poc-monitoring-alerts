import pulumi_gcp as gcp


def create_sql_saturation_high_alert(
    prefix_name: str,
    project_id: str,
    system_name: str,
    instance_id: str,
    # notification_channels: List[pulumi.Output[str]],
    # opts: pulumi.ResourceOptions = None
) -> gcp.monitoring.AlertPolicy:
    alert_name = f"{prefix_name}:infra:sql:saturation-high:warn"
    database_id = f"{project_id}:{instance_id}"

    return gcp.monitoring.AlertPolicy(
        alert_name,
        display_name=alert_name,
        combiner="OR",
        conditions=[
            {
                "condition_threshold": {
                    "aggregations": [
                        {
                            "alignment_period": "300s",
                            "per_series_aligner": "ALIGN_INTERPOLATE",
                        }
                    ],
                    "comparison": "COMPARISON_GT",
                    "duration": "60s",
                    "filter": f'resource.type = "cloudsql_database" AND resource.labels.database_id = "{database_id}" AND metric.type = "cloudsql.googleapis.com/database/cpu/utilization"',
                    "threshold_value": 0.7,
                    "trigger": {
                        "count": 1,
                    },
                },
                "display_name": "DB Master: CPU ",
            },
            {
                "condition_threshold": {
                    "aggregations": [
                        {
                            "alignment_period": "300s",
                            "per_series_aligner": "ALIGN_INTERPOLATE",
                        }
                    ],
                    "comparison": "COMPARISON_GT",
                    "duration": "0s",
                    "filter": f'resource.type = "cloudsql_database" AND resource.labels.database_id = "{database_id}" AND metric.type = "cloudsql.googleapis.com/database/network/connections"',
                    "threshold_value": 3600,  # should set by max_connections config or spec of engine
                    "trigger": {
                        "count": 1,
                    },
                },
                "display_name": "DB Master: Connection",
            },
            {
                "condition_threshold": {
                    "aggregations": [
                        {
                            "alignment_period": "300s",
                            "per_series_aligner": "ALIGN_MEAN",
                        }
                    ],
                    "comparison": "COMPARISON_GT",
                    "duration": "0s",
                    "filter": f'resource.type = "cloudsql_database" AND resource.labels.database_id = "{database_id}" AND metric.type = "cloudsql.googleapis.com/database/memory/utilization"',
                    "threshold_value": 0.9,
                    "trigger": {
                        "count": 1,
                    },
                },
                "display_name": "DB Master: Memory",
            },
        ],
        documentation={
            "content": """### Summary
  This alert triggers when one of the following conditions is met for the **od-at-home** Cloud SQL instances (master and replica):

  CPU Utilization:
  - Master instance CPU utilization exceeds 70% for more than 60 seconds.
  - Replica instance CPU utilization exceeds 98% for more than 300 seconds.

  Connections:
  - Master instance connections exceed 3,600.
  - Replica instance connections exceed 180.

  Memory Utilization:
  - Master instance memory utilization exceeds 90%.
  - Replica instance memory utilization exceeds 90%.

  ### Severity
  Warning

  The database is under significant load. This could slow down or even take down the entire application. should investigate the cause immediately

  ---
  #### Link
  - [Playbook](https://docs.google.com/document/d/1nGyQyTaYiiitKWdAV171wuVx4fadw6qsEUjwLMckRrk/edit?tab=t.0#heading=h.vklx4ojk7z0o)
  - [Cloud SQL dashboard](https://console.cloud.google.com/sql/instances/od-at-home/system-insights/mysql?inv=1&invt=Ab3fkA&project=ondemand-athome)
  - [Cloud SQL Query Insights](https://console.cloud.google.com/sql/instances/od-at-home/insights?inv=1&invt=Ab3fkA&project=ondemand-athome)""",
            "subject": f"[{system_name}] {alert_name}",
            "mime_type": "text/markdown",
        },
        severity="WARNING",
        user_labels={
            "support-level": "testing",
        },
    )
