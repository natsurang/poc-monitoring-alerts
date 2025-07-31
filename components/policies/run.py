import pulumi_gcp as gcp


def create_run_saturation_high_alert(
    prefix_name: str,
) -> gcp.monitoring.AlertPolicy:
    alert_name = f"{prefix_name}:infra:run:saturation-high:warn"

    return gcp.monitoring.AlertPolicy(
        alert_name,
        display_name=alert_name,
        combiner="OR",
        conditions=[
            gcp.monitoring.AlertPolicyConditionArgs(
                display_name="CPU Utilization Exceeds 80%",
                condition_threshold=gcp.monitoring.AlertPolicyConditionConditionThresholdArgs(
                    filter='resource.type = "cloud_run_revision" AND metric.type = "run.googleapis.com/container/cpu/utilizations"',
                    duration="60s",
                    aggregations=[
                        gcp.monitoring.AlertPolicyConditionConditionThresholdAggregationArgs(
                            alignment_period="300s",
                            per_series_aligner="ALIGN_PERCENTILE_99",
                        )
                    ],
                    threshold_value=0.8,
                    comparison="COMPARISON_GT",
                ),
            )
        ],
        documentation=gcp.monitoring.AlertPolicyDocumentationArgs(
            content="This alert fires when the CPU utilization of a GCE instance exceeds 80% for 1 minute.",
            mime_type="text/markdown",
        ),
        enabled=False,
    )
