package com.bank.fraud.rules;

import java.math.BigDecimal;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudRuleConfigService;

@Component
public class IPLocationMismatchRule extends BaseRule {

    public IPLocationMismatchRule(FraudRuleConfigService configService) {
        super(configService);
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        if (transaction.getIpAddress() != null
                && transaction.getLocation() != null
                && !transaction.getIpAddress()
                        .equalsIgnoreCase(transaction.getLocation())) {

            return riskScore();  // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "IP_LOCATION_MISMATCH_RULE";
    }
}