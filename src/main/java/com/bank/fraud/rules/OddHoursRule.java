package com.bank.fraud.rules;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudRuleConfigService;

@Component
public class OddHoursRule extends BaseRule {

    public OddHoursRule(FraudRuleConfigService configService) {
        super(configService);
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        LocalDateTime time = transaction.getTransactionTime();
        if (time == null) return BigDecimal.ZERO;

        int hour = time.getHour();

        if (hour >= 0 && hour <= 5) {
            return riskScore();   // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "ODD_HOURS_RULE";
    }
}