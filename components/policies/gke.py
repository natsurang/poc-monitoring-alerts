import pulumi_gcp as gcp

# Helper function (ถ)
# def _create_base_alert_policy(
#     name: str,
#     display_name: str,
#     condition: gcp.monitoring.AlertPolicyConditionArgs,
#     notification_channels: List[pulumi.Output[str]],
#     project_id: str,
#     documentation_content: str,
#     opts: pulumi.ResourceOptions = None
# ) -> gcp.monitoring.AlertPolicy:
#     """
#     A helper function to create a generic AlertPolicy with common settings.
#     """
#     return gcp.monitoring.AlertPolicy(name,
#         display_name=display_name,
#         combiner="OR",
#         conditions=[condition],
#         notification_channels=notification_channels,
#         documentation=gcp.monitoring.AlertPolicyDocumentationArgs(
#             content=documentation_content,
#             mime_type="text/markdown",
#         ),
#         enabled=True,
#         project=project_id,
#         opts=opts
#     )


def create_gke_alert(
    prefix_name: str,
    system_name: str,
    pool_name: str,
    namespace_name: str,
    cpu_threshold_value: float = 0.8,
    # duration: str,
    # notification_channels: List[pulumi.Output[str]],
    # opts: pulumi.ResourceOptions = None
) -> None:
    create_gke_saturation_high_alert(
        prefix_name=prefix_name,
        system_name=system_name,
        pool_name=pool_name,
        namespace_name=namespace_name,
        cpu_threshold_value=cpu_threshold_value,
    )
    create_gke_storage_usage_high_alert(
        prefix_name=prefix_name, system_name=system_name, pool_name=pool_name
    )


def create_gke_saturation_high_alert(
    prefix_name: str,
    # project_id: str,
    system_name: str,
    pool_name: str,
    namespace_name: str,
    cpu_threshold_value: float = 0.8,
    # duration: str,
    # notification_channels: List[pulumi.Output[str]],
    # opts: pulumi.ResourceOptions = None
) -> gcp.monitoring.AlertPolicy:
    alert_name = f"{prefix_name}:infra:gke:saturation-high:warn"
    display_name = alert_name
    documentation = """### Summary
This alert triggers when following conditions is met for the **GKE**
- **Node CPU**: CPU utilization exceeds 80%
- **Container Memory**: container memory utilization exceeds 85% of its limit


### Severity
Warning

The GKE cluster is overloaded. This could slow down or even shut down the core services both frontoffice and backoffice. We need to find and fix the problem right away. 

---
#### Link
- [Playbook](https://docs.google.com/document/d/1nGyQyTaYiiitKWdAV171wuVx4fadw6qsEUjwLMckRrk/edit?tab=t.0#heading=h.1pg992jyden3)
- [Deployment Repo](https://github.com/Skooldio/od-at-home-deployment)
"""

    subject = f"[{system_name}] {alert_name}"

    cpu_condition = gcp.monitoring.AlertPolicyConditionArgs(
        display_name="Node Pool CPU utilization",
        condition_threshold=gcp.monitoring.AlertPolicyConditionConditionThresholdArgs(
            filter=f'resource.type = "gce_instance" AND metric.type = "compute.googleapis.com/instance/cpu/utilization" AND metadata.user_labels.goog-k8s-node-pool-name = "{pool_name}"',
            aggregations=[
                gcp.monitoring.AlertPolicyConditionConditionThresholdAggregationArgs(
                    alignment_period="300s",
                    per_series_aligner="ALIGN_MEAN",
                )
            ],
            threshold_value=0.8,
            comparison="COMPARISON_GT",
            duration="0s",
            trigger=gcp.monitoring.AlertPolicyConditionConditionThresholdTriggerArgs(
                count=1,
            ),
        ),
    )

    memory_condition = gcp.monitoring.AlertPolicyConditionArgs(
        display_name="Container Memory utilization",
        condition_threshold=gcp.monitoring.AlertPolicyConditionConditionThresholdArgs(
            filter=f'resource.type = "k8s_container" AND resource.labels.namespace_name = "{namespace_name}" AND metric.type = "kubernetes.io/container/memory/limit_utilization"',
            aggregations=[
                gcp.monitoring.AlertPolicyConditionConditionThresholdAggregationArgs(
                    alignment_period="600s",
                    per_series_aligner="ALIGN_MEAN",
                    cross_series_reducer="REDUCE_MAX",
                    group_by_fields=[
                        "metadata.system_labels.top_level_controller_name"
                    ],
                )
            ],
            threshold_value=0.85,
            comparison="COMPARISON_GT",
            duration="0s",
            trigger=gcp.monitoring.AlertPolicyConditionConditionThresholdTriggerArgs(
                count=1,
            ),
        ),
    )
    return gcp.monitoring.AlertPolicy(
        alert_name,
        display_name=display_name,
        combiner="OR",
        conditions=[cpu_condition, memory_condition],
        # notification_channels=notification_channels,
        documentation=gcp.monitoring.AlertPolicyDocumentationArgs(
            content=documentation, mime_type="text/markdown", subject=subject
        ),
        enabled=True,
        # opts=opts,
        severity="WARNING",
        user_labels={"support-level": "testing"},
    )


def create_gke_storage_usage_high_alert(
    prefix_name: str,
    # project_id: str,
    system_name: str,
    pool_name: str,
    # duration: str,
    # notification_channels: List[pulumi.Output[str]],
    # opts: pulumi.ResourceOptions = None
) -> gcp.monitoring.AlertPolicy:
    alert_name = f"{prefix_name}:infra:gke:storage-usage-high:warn"

    return gcp.monitoring.AlertPolicy(
        alert_name,
        display_name=alert_name,
        combiner="OR",
        conditions=[
            {
                "condition_prometheus_query_language": {
                    "duration": "0s",
                    "evaluation_interval": "30s",
                    "query": f"""(
    avg_over_time({{"__name__"="kubernetes_io:node_ephemeral_storage_used_bytes","monitored_resource"="k8s_node","metadata_user_cloud.google.com/gke-nodepool"="{pool_name}"}}[5m])
    /
    avg_over_time({{"__name__"="kubernetes_io:node_ephemeral_storage_total_bytes","monitored_resource"="k8s_node","metadata_user_cloud.google.com/gke-nodepool"="{pool_name}"}}[5m])
    ) >= 0.85
    """,
                },
                "display_name": "storage utilization",
            }
        ],
        documentation={
            "content": """### Summary
    This alert warns **ephemeral storage on a server GKE node pool is over 85%** 

    ### Severity
    Warning

    The system is getting close to a serious problem. If the disk fills up completely, it can cause pods to crash or shut down, leading to slow performance or a complete outage for the entire application. should investigate to prevent.

    ---
    #### Link
    - [Playbook](https://docs.google.com/document/d/1nGyQyTaYiiitKWdAV171wuVx4fadw6qsEUjwLMckRrk/edit?tab=t.0#heading=h.uw66pvc18zvo)
    - [GKE Node](https://console.cloud.google.com/kubernetes/clusters/details/asia-southeast1-a/at-home-cluster/nodes?inv=1&invt=Ab3itQ&project=ondemand-athome)""",
            "subject": f"[{system_name}] {alert_name}",
            "mime_type": "text/markdown",
        },
        severity="WARNING",
        user_labels={
            "support-level": "testing",
        },
    )
