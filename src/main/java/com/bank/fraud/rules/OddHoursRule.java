package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;

public class OddHoursRule implements FraudRule {

    @Override
    public boolean evaluate(Transaction transaction) {

        if (transaction.getTransactionTime() == null) {
            return false;
        }

        int hour = transaction.getTransactionTime().getHour();

        // Between 12 AM and 5 AM
        return hour >= 0 && hour <= 5;
    }

    @Override
    public String ruleName() {
        return "ODD_HOURS_RULE";
    }

    @Override
    public double riskScore() {
        return 0.5;
    }
}
