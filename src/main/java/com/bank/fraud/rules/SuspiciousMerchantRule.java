package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;

import java.util.Arrays;
import java.util.List;

public class SuspiciousMerchantRule implements FraudRule {

    private static final List<String> BLACKLISTED_MERCHANTS =
            Arrays.asList("DARKWEB_STORE", "SCAM_PAY", "ILLEGAL_SHOP");

    @Override
    public boolean evaluate(Transaction transaction) {

        if (transaction.getMerchant() == null) {
            return false;
        }

        return BLACKLISTED_MERCHANTS.contains(
                transaction.getMerchant().toUpperCase()
        );
    }

    @Override
    public String ruleName() {
        return "SUSPICIOUS_MERCHANT_RULE";
    }

    @Override
    public double riskScore() {
        return 0.6;
    }
}
