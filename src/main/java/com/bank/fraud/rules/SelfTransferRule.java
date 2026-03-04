package com.bank.fraud.rules;

import java.math.BigDecimal;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudRuleConfigService;

@Component
public class SelfTransferRule extends BaseRule {

    public SelfTransferRule(FraudRuleConfigService configService) {
        super(configService);
    }

    @Override
    public BigDecimal evaluate(Transaction transaction) {

        if (!isActive()) return BigDecimal.ZERO;

        String sender = transaction.getSenderAccountNumber();
        String receiver = transaction.getReceiverAccountNumber();

        if (sender != null && sender.equals(receiver)) {
            return riskScore();   // return rule weight
        }

        return BigDecimal.ZERO;
    }

    @Override
    public String ruleName() {
        return "SELF_TRANSFER_RULE";
    }
}