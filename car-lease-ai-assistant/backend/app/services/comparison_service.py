def normalize(value, min_val, max_val, reverse=False):
    if max_val == min_val:
        return 1.0
    score = (value - min_val) / (max_val - min_val)
    return 1 - score if reverse else score


def score_contracts(contracts):
    leases = [c["fair_lease_pricing"]["fair_monthly_lease"] for c in contracts]
    residuals = [c["residual_value"]["final_value"] for c in contracts]
    aprs = [c["fair_lease_pricing"]["apr"] for c in contracts]

    min_lease, max_lease = min(leases), max(leases)
    min_res, max_res = min(residuals), max(residuals)
    min_apr, max_apr = min(aprs), max(aprs)

    scored = []

    for c in contracts:
        lease_score = normalize(
            c["fair_lease_pricing"]["fair_monthly_lease"],
            min_lease, max_lease, reverse=True
        )

        residual_score = normalize(
            c["residual_value"]["final_value"],
            min_res, max_res
        )

        apr_score = normalize(
            c["fair_lease_pricing"]["apr"],
            min_apr, max_apr, reverse=True
        )

        total_score = (
            lease_score * 0.40 +
            residual_score * 0.30 +
            apr_score * 0.15 +
            0.10 +  # fixed lease-term factor (36 default)
            0.05    # MSRP stability factor
        )

        scored.append({
            **c,
            "score": round(total_score * 100, 2)
        })

    return sorted(scored, key=lambda x: x["score"], reverse=True)
