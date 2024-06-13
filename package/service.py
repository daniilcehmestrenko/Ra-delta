
def delivery_cost_calculation(weight, cost_in_usd, usd_rate_in_rub):
    return (float(weight) * 0.5 + float(cost_in_usd) * 0.01) * usd_rate_in_rub
