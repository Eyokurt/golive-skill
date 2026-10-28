# Field Extension: Cloud & SaaS

> **Objective**: Address the specific operational, security, financial, and architectural requirements of multi-tenant or managed single-tenant applications deployed to public or private cloud platforms (AWS, GCP, Azure, Kubernetes, serverless).

---

## 1. Action Items

### A. Infrastructure as Code (IaC)
- [ ] **Fully Declarative Resources**: All cloud infrastructure (VPCs, subnets, managed databases, load balancers, object storage) must be declared using Terraform, OpenTofu, Pulumi, or AWS CDK.
- [ ] **No ClickOps**: Manual changes in cloud provider web consoles are strictly forbidden. Running `terraform plan` must yield zero configuration drift.
- [ ] **Encrypted Remote State & Locking**: Persist IaC state files in versioned, encrypted remote stores (e.g., S3 with DynamoDB state locking).

### B. DNS, Domains & Automated TLS
- [ ] **Automated TLS Lifecycle**: SSL/TLS certificates must be managed via automated renewal mechanisms (AWS ACM, Let's Encrypt, Cloudflare) with enforced HSTS.
- [ ] **Reduced DNS TTL**: Prior to go-live, reduce DNS record TTLs to 60-300 seconds to allow rapid traffic re-routing in case of operational issues.

### C. Autoscaling & Workload Isolation
- [ ] **Horizontal Autoscaling (HPA / ASG)**: Configure autoscaling policies based on CPU utilization (> 70%), request rates, or queue depths with conservative scale-in cool-downs.
- [ ] **Kubernetes Resource Requests & Limits**: Define explicit `requests` and `limits` for CPU and memory on every container. Unbounded containers are strictly prohibited.

### D. Cloud FinOps & Cost Controls
- [ ] **Budget Alerts**: Set up automated budget alerts at 50%, 80%, and 100% of expected monthly cloud spend with routing to billing channels.
- [ ] **Idle Resource Pruning**: Identify and delete unattached EBS volumes, idle NAT Gateways, and orphaned staging environments.

### E. Canary & Weighted Ingress Routing
- [ ] Configure ingress controllers, API gateways, or service meshes (AWS ALB, Cloudflare, Istio) to support weighted canary routing (e.g., 95% stable v1, 5% canary v2).

---

## 2. Exit Gate (Field Gate: Cloud/SaaS)

Cloud production deployment cannot proceed until **all** of the following criteria are satisfied:
1. All Cloud/SaaS checklist items are completed in `GOLIVE.md`.
2. Running `terraform plan` outputs `No changes. Infrastructure is up-to-date.`
3. Active TLS certificates verified via HTTPS with valid expiration and HSTS headers.
4. Cloud provider budget alerts verified active with configured notification channels.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Strict IaC Enforcement | Manual console changes are easily forgotten during disaster recovery, making it impossible to reconstruct infrastructure in an alternate region. |
| Low DNS TTL | If server IPs or ingress endpoints change during release, high TTLs (e.g., 24h) cause half of user traffic to route to decommissioned instances. |
| Resource Requests & Limits | A single memory-leaking container on Kubernetes will consume all node memory, causing the node to evict critical co-located database and ingress pods. |
| FinOps Cost Alarms | Unmonitored autoscaling loops or DDoS traffic can easily result in thousands of dollars in surprise cloud provider bills. |

---

## 4. Common Pitfalls

- ❌ **Making "Quick" Console Tweaks**: Modifying security group rules in the cloud console without committing them to IaC, causing state drift.
- ❌ **Committing State Files to Git**: Pushing `terraform.tfstate` containing cleartext database passwords into source control.
- ❌ **Orphaned NAT Gateway Expenses**: Provisioning idle NAT Gateways in multiple unused availability zones, incurring unnecessary recurring monthly costs.
- ❌ **Underestimating Autoscaling Spin-up Time**: Expecting new compute nodes to handle sudden traffic spikes instantly without accounting for 3-5 minute boot and provisioning delays.
