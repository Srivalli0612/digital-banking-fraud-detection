package com.bank.fraud.rules;

import java.math.BigDecimal;
import java.util.Set;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudRuleConfigService;

@Component
public class ForeignLocationRule extends BaseRule {

    private static final Set<String> INDIAN_LOCATIONS =
            Set.of("INDIA", "KOLKATA", "DELHI", "MUMBAI",
                   "BANGALORE", "CHENNAI", "HYDERABAD", "PATNA");

    public ForeignLocationRule(FraudRuleConfigService configService) {
        super(configService);
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        String location = transaction.getLocation();

        if (location == null ||
                !INDIAN_LOCATIONS.contains(location.toUpperCase())) {

            return riskScore();   // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "FOREIGN_LOCATION_RULE";
    }
}