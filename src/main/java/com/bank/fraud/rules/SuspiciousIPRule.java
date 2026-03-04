package com.bank.fraud.rules;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudRuleConfigService;

@Component
public class SuspiciousIPRule extends BaseRule {

    private static final List<String> BLACKLISTED_IPS =
            List.of("192.168.0.10", "10.0.0.66", "172.16.0.5");

    public SuspiciousIPRule(FraudRuleConfigService configService) {
        super(configService);
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        String ip = transaction.getIpAddress();

        if (ip != null && BLACKLISTED_IPS.contains(ip)) {
            return riskScore();   // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "SUSPICIOUS_IP_RULE";
    }
}