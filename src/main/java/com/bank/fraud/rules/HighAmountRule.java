package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;

public class HighAmountRule implements FraudRule {

    private static final double THRESHOLD = 75000.0;

    @Override
    public boolean evaluate(Transaction transaction) {
        return transaction.getAmount() != null &&
               transaction.getAmount() > THRESHOLD;
    }

    @Override
    public String ruleName() {
        return "HIGH_AMOUNT_RULE";
    }

    @Override
    public double riskScore() {
        return 0.8;
    }
}
