package com.bank.fraud.rules;

import java.math.BigDecimal;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudRuleConfigService;

@Component
public class HighAmountRule extends BaseRule {

    public HighAmountRule(FraudRuleConfigService configService) {
        super(configService);
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        BigDecimal threshold = getThreshold();

        if (threshold == null) return BigDecimal.ZERO;

        if (transaction.getAmount().compareTo(threshold) > 0) {
            return riskScore();  // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "HIGH_AMOUNT_RULE";
    }
}